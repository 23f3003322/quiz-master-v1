from flask import Blueprint,Flask,render_template,redirect,request, session, flash , url_for

user_bp = Blueprint("user", __name__)  # No URL prefix means it's at "/"


from models import *
from database import db
from datetime import datetime

from controllers.utils import  login_required




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

    user_id = session['user_id']

    # Create a new quiz attempt
    new_attempt = QuizAttempt(user_id=user_id, quiz_id=quiz_id, time_started=datetime.utcnow())
    db.session.add(new_attempt)
    db.session.commit()

    flash("Quiz started successfully!", "success")
    
    # Redirect to the quiz page with the new attempt ID
    return redirect(url_for('user.quiz_questions', quiz_id=quiz_id, attempt_id=new_attempt.id))




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
        # Retrieve all correct options for the current question
        correct_options = Option.query.filter_by(question_id=question.id, is_correct=True).all()
        
        # Get user's selected options for this question
        if question.question_type == 'mcq':
            # For MCQ, handle single selection
            selected_option_id = request.form.get(f"question_{question.id}")
            
            if not selected_option_id:
                # No option selected
                score = 0
            else:
                selected_option = Option.query.get(int(selected_option_id))
                
                # Check if the selected option is correct
                if selected_option and selected_option.is_correct:
                    score = question.score
                else:
                    score = 0
        
        elif question.question_type == 'msq':
            # For MSQ, handle multiple selections
            selected_option_ids = request.form.getlist(f"question_{question.id}")
            
            if not selected_option_ids:
                # No options selected
                score = 0
            else:
                # Convert selected option IDs to integers
                selected_option_ids = [int(option_id) for option_id in selected_option_ids]
                
                # Get selected options from database
                selected_options = Option.query.filter(Option.id.in_(selected_option_ids)).all()
                
                # Calculate partial scoring for MSQ
                correct_selected = sum(1 for option in selected_options if option.is_correct)
                incorrect_selected = sum(1 for option in selected_options if not option.is_correct)
                total_correct = len(correct_options)
                
                if incorrect_selected > 0:
                    # If any incorrect option is selected, score is 0
                    score = 0
                else:
                    # Partial scoring based on correct selections
                    score = (correct_selected / total_correct) * question.score
        
        # Create user answer record
        user_answer = UserAnswer(
            attempt_id=attempt_id,
            question_id=question.id,
            selected_option_id=selected_option_id if question.question_type == 'mcq' else ','.join(map(str, selected_option_ids)),
            score=score
        )
        db.session.add(user_answer)
        
        # Add to total score
        total_score += score
    
    # Save total score in Scores table
    score_entry = Scores(
        user_id=attempt.user_id,
        quiz_id=quiz_id,
        attempt_id=attempt_id,
        time_stamp_of_attempt=datetime.utcnow(),
        total_scored=total_score
    )
    db.session.add(score_entry)
    
    # Update attempt status
    attempt.status = "completed"
    attempt.time_completed = datetime.utcnow()
    
    # Commit all changes
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

    return render_template('user/quiz_results.html', attempt=attempt, quiz=quiz, user_answers=user_answers)