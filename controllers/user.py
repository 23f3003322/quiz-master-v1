from flask import Blueprint,Flask,render_template,redirect,request, session, flash , url_for
from sqlalchemy import func
import pytz 
user_bp = Blueprint("user", __name__)  


from models import *
from database import db
from datetime import datetime
from utils.helpers import is_quiz_active
from controllers.utils import  login_required


IST = pytz.timezone('Asia/Kolkata')

def fetch_subject_and_chapters(subject_id):
    """Fetch subject and related chapters."""
    subject = Subject.query.get_or_404(subject_id)
    chapters = Chapter.query.filter_by(subject_id=subject.id).all()
    return subject, chapters



@user_bp.route("/")
@login_required
def user_dash():
    subjects = Subject.query.all() 
    return render_template("user/user_dashboard.html",subjects=subjects)



@user_bp.route('/subject/<int:subject_id>', methods=['GET'])
@login_required
def get_subject(subject_id):
    """User route to view a subject."""
    subject, chapters = fetch_subject_and_chapters(subject_id)
    return render_template('user/view_subject.html', subject=subject, chapters=chapters)


@user_bp.route('/chapter/<int:chapter_id>', methods=['GET'])
@login_required
def get_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    Quizes = Quiz.query.filter_by(chapter_id=chapter.id).all() 

    return render_template('user/view_chapter.html',  chapter=chapter, quizes=Quizes)

@user_bp.route('/start_quiz/<int:quiz_id>', methods=['POST'])
@login_required
def start_quiz(quiz_id):
    user_id = session["user_id"]
    quiz = Quiz.query.get_or_404(quiz_id)

    # Check if the quiz is active
    is_active, error_message = is_quiz_active(quiz)
    if not is_active:
        flash(error_message, "danger")
        return redirect(url_for('user.get_chapter', chapter_id=quiz.chapter_id))
    
    print(quiz.questions)
    if not quiz.questions or len(quiz.questions) == 0:
        flash("This quiz has no questions! Please contact the administrator.", "danger")
        return redirect(url_for('user.get_chapter', chapter_id=quiz.chapter_id))

    try:
        # Get current time in IST
        utc_now = datetime.utcnow()
        ist_now = utc_now.replace(tzinfo=pytz.utc).astimezone(IST)

        # Create a new quiz attempt
        new_attempt = QuizAttempt(user_id=user_id, quiz_id=quiz_id, time_started=ist_now)
        db.session.add(new_attempt)
        db.session.commit()

        flash("Quiz started successfully!", "success")
        return redirect(url_for('user.quiz_questions', quiz_id=quiz_id, attempt_id=new_attempt.id))

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(url_for('user.user_dash'))




@user_bp.route('/quiz/<int:quiz_id>/attempt/<int:attempt_id>', methods=['GET', 'POST'])
@login_required
def quiz_questions(quiz_id, attempt_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    return render_template('user/quiz.html', quiz=quiz, questions=questions, attempt_id=attempt_id)



@user_bp.route('/quiz/<int:quiz_id>/submit/<int:attempt_id>', methods=['POST'])
@login_required
def submit_quiz(quiz_id, attempt_id):
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    if not attempt:
        flash("Invalid quiz attempt.", "danger")
        return redirect(url_for('dashboard'))
    
    total_score = 0
    
    for question in questions:

        correct_options = Option.query.filter_by(question_id=question.id, is_correct=True).all()
        

        if question.question_type == 'mcq':

            selected_option_id = request.form.get(f"question_{question.id}")
            
            if not selected_option_id:

                score = 0
            else:
                selected_option = Option.query.get(int(selected_option_id))
                

                if selected_option and selected_option.is_correct:
                    score = question.score
                else:
                    score = 0
        
        elif question.question_type == 'msq':

            selected_option_ids = request.form.getlist(f"question_{question.id}")
            
            if not selected_option_ids:

                score = 0
            else:

                selected_option_ids = [int(option_id) for option_id in selected_option_ids]
                

                selected_options = Option.query.filter(Option.id.in_(selected_option_ids)).all()
                

                correct_selected = sum(1 for option in selected_options if option.is_correct)
                incorrect_selected = sum(1 for option in selected_options if not option.is_correct)
                total_correct = len(correct_options)
                
                if incorrect_selected > 0:
                    
                    score = 0
                else:
                    
                    score = (correct_selected / total_correct) * question.score
        

        user_answer = UserAnswer(
            attempt_id=attempt_id,
            question_id=question.id,
            selected_option_id=selected_option_id if question.question_type == 'mcq' else ','.join(map(str, selected_option_ids)),
            score=score
        )
        db.session.add(user_answer)
        

        total_score += score

    utc_now = datetime.utcnow()
    ist_now = utc_now.replace(tzinfo=pytz.utc).astimezone(IST)

    score_entry = Scores(
        user_id=attempt.user_id,
        quiz_id=quiz_id,
        attempt_id=attempt_id,
        time_stamp_of_attempt=ist_now,
        total_scored=total_score
    )
    db.session.add(score_entry)
    
    utc_now = datetime.utcnow()
    ist_now = utc_now.replace(tzinfo=pytz.utc).astimezone(IST)
    attempt.status = "completed"
    attempt.time_completed = ist_now
    

    db.session.commit()
    
    flash(f"Quiz submitted! You scored {total_score} points.", "success")
    return redirect(url_for('user.user_dash'))

@user_bp.route('/scores')
@login_required
def scores():
    user_id = session['user_id']
    user_attempts = Scores.query.filter_by(user_id=user_id).order_by(Scores.time_stamp_of_attempt.desc()).all()
    return render_template('user/scores.html', user_attempts=user_attempts)


@user_bp.route('/quiz/<int:quiz_id>/results/<int:attempt_id>')
@login_required
def quiz_results(quiz_id, attempt_id):
    user_id = session['user_id']
    attempt = QuizAttempt.query.filter_by(id=attempt_id, user_id=user_id).first_or_404()
    quiz = Quiz.query.get_or_404(quiz_id)
    user_answers = UserAnswer.query.filter_by(attempt_id=attempt_id).all()
    for answer in user_answers:
        print(answer.__dict__)

    return render_template('user/quiz_results.html', attempt=attempt, quiz=quiz, user_answers=user_answers)





@user_bp.route('/summary', methods=['GET'])
@login_required
def summary():
    user_id = session.get('user_id')  
    if not user_id:
        flash("User not logged in", "danger")
        return redirect(url_for("auth.login"))


    total_attempts = db.session.query(func.count(QuizAttempt.id)).filter(QuizAttempt.user_id == user_id).scalar() or 0


    
    avg_score = db.session.query(func.avg(Scores.total_scored)).filter(Scores.user_id == user_id).scalar() or 0
    avg_score = round(avg_score, 2)


    total_questions_answered = db.session.query(func.count(UserAnswer.id))\
        .join(QuizAttempt, UserAnswer.attempt_id == QuizAttempt.id)\
        .filter(QuizAttempt.user_id == user_id).scalar() or 0




    total_time_spent = db.session.query(
        func.sum(func.strftime('%s', QuizAttempt.time_completed) - func.strftime('%s', QuizAttempt.time_started))
    ).filter(
        QuizAttempt.user_id == user_id,
        QuizAttempt.time_completed.isnot(None) 
    ).scalar() or 0
    total_time_spent = round(total_time_spent / 60, 2) 


    best_quiz = db.session.query(Quiz.title, Scores.total_scored)\
        .join(Scores, Quiz.id == Scores.quiz_id)\
        .filter(Scores.user_id == user_id)\
        .order_by(Scores.total_scored.desc())\
        .first()


    worst_quiz = db.session.query(Quiz.title, Scores.total_scored)\
        .join(Scores, Quiz.id == Scores.quiz_id)\
        .filter(Scores.user_id == user_id)\
        .order_by(Scores.total_scored.asc())\
        .first()


    subjects = db.session.query(Subject.title, func.avg(Scores.total_scored))\
        .join(Chapter, Subject.id == Chapter.subject_id)\
        .join(Quiz, Chapter.id == Quiz.chapter_id)\
        .join(Scores, Quiz.id == Scores.quiz_id)\
        .filter(Scores.user_id == user_id)\
        .group_by(Subject.id)\
        .all()

    return render_template(
        'user/summary.html',
        total_attempts=total_attempts,
        avg_score=avg_score,
        total_questions_answered=total_questions_answered,
        total_time_spent=total_time_spent,
        best_quiz=best_quiz,
        worst_quiz=worst_quiz,
        subjects=subjects
    )


@user_bp.route("/search",methods=["GET"])
@login_required
def search():
    search_word = request.args.get("search_word")
    key = request.args.get("key")

    if key == "subject":
        results = Subject.query.filter(Subject.title.ilike(f"%{search_word.lower()}%")).all()
    elif key == "chapter":
        results = Chapter.query.filter(Chapter.title.ilike(f"%{search_word.lower()}%")).all()
    elif key == "quiz":
        results = Quiz.query.filter(Quiz.title.ilike(f"%{search_word.lower()}%")).all()
    else:
        flash("invalid key","danger")
        return redirect(url_for("user.user_dash"))
    
    return render_template("user/results.html",results = results, key=key)
