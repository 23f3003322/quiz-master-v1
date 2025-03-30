from flask import Blueprint, render_template,request,flash,redirect,url_for
from .utils import admin_required
from models import *
from database import db
from sqlalchemy import func
from datetime import datetime
from utils.helpers import convert_time_to_db_time, validate_quiz_date
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/")
@admin_required
def admin_dash():
    subjects = Subject.query.all() 
    return render_template("admin/admin_dashboard.html",subjects=subjects)



@admin_bp.route('/subject/new', methods=['GET','POST'])
@admin_required
def create_subject():
    if request.method == 'POST':
        subject_title = request.form.get('title')
        subject_description = request.form.get('description')


        existing_subject = Subject.query.filter_by(title=subject_title).first()
        if existing_subject:
            flash("Subject already exists!", "warning")
            return redirect(url_for('admin.create_subject'))


        new_subject = Subject(title=subject_title.lower(), description=subject_description)
        db.session.add(new_subject)
        db.session.commit()

        flash("Subject created successfully!", "success")
        return redirect(url_for('admin.admin_dash')) 
    
    return render_template('admin/create_subject.html') 


@admin_bp.route('/subject/update/<int:subject_id>', methods=['GET','POST'])
@admin_required
def update_subject(subject_id):
    print(subject_id)
    subject = Subject.query.get(subject_id)
    print(subject.title)
    print(subject.description)

    if request.method=="POST":
        if not subject:
            flash("Subject not found!", "danger")
            return redirect(url_for('admin.admin_Dash'))


        title = request.form.get('title')
        description = request.form.get('description')

        if not title:
            flash("Title is required!", "danger")
            return redirect(url_for('admin.update_subject', subject_id=subject_id))


        subject.title = title.lower()
        subject.description = description
        db.session.commit()

        flash("Subject updated successfully!", "success")
        return redirect(url_for('admin.admin_dash'))

    return render_template('admin/edit_subject.html', subject=subject)


@admin_bp.route('/subject/delete/<int:subject_id>', methods=['GET'])
@admin_required
def delete_subject(subject_id):

    subject = Subject.query.get(subject_id)

    if not subject:
        flash("Subject not found!", "danger")
        return redirect(url_for('admin.admin_dash'))


    db.session.delete(subject)
    db.session.commit()

    flash("Subject deleted successfully!", "success")
    return redirect(url_for('admin.admin_dash'))

@admin_bp.route('/subject/<int:subject_id>', methods=['GET'])
@admin_required
def get_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id) 
    chapters = Chapter.query.filter_by(subject_id=subject.id).all() 
    return render_template('admin/view_subject.html', subject=subject, chapters=chapters)


@admin_bp.route('/subject/<int:subject_id>/chapter/new', methods=['GET', 'POST'])
@admin_required
def create_chapter(subject_id):
    subject = Subject.query.get_or_404(subject_id)

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')

        if not title:
            flash('Title is required', 'danger')
            return redirect(url_for('admin.create_chapter', subject_id=subject_id))
        if not description:
            flash('description is required', 'danger')
            return redirect(url_for('admin.create_chapter', subject_id=subject_id))

        new_chapter = Chapter(title=title.lower(), subject_id=subject_id,description = description)
        db.session.add(new_chapter)
        db.session.commit()
        flash('Chapter created successfully!', 'success')
        return redirect(url_for('admin.get_subject',subject_id=subject_id))

    return render_template('admin/chapter/create_chapter.html', subject=subject)



@admin_bp.route('/chapter/<int:chapter_id>', methods=['GET'])
@admin_required
def get_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    Quizes = Quiz.query.filter_by(chapter_id=chapter.id).all() 
    return render_template('admin/chapter/view_chapter.html',  chapter=chapter,quizes=Quizes)


@admin_bp.route('/chapter/update/<int:chapter_id>', methods=['GET', 'POST'])
@admin_required
def update_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)

    if request.method == 'POST':
        chapter.title = request.form.get('title').lower()
        chapter.description = request.form.get('description')
        db.session.commit()
        flash('Chapter updated successfully!', 'success')
        return redirect(url_for('admin.get_subject', subject_id=chapter.subject_id))

    return render_template('admin/chapter/edit_chapter.html', chapter=chapter)



@admin_bp.route('/chapter/delete/<int:chapter_id>', methods=['GET'])
@admin_required
def delete_chapter(chapter_id):

    chapter = Chapter.query.get(chapter_id)

    if not chapter:
        flash("Chapter not found!", "danger")
        return redirect(url_for('admin.admin_dash'))


    db.session.delete(chapter)
    db.session.commit()

    flash("chapter deleted successfully!", "success")
    return redirect(url_for('admin.admin_dash'))



@admin_bp.route('/chapter/<int:chapter_id>/quiz/new', methods=['GET', 'POST'])
@admin_required
def create_quiz(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)

    if request.method == 'POST':
        print("post request")
        title = request.form['title']
        remarks = request.form.get('remarks', '')  
        date_of_quiz = request.form['date_of_quiz']
        time_duration = request.form['time_duration']
        start_time= request.form['start_time']  
        start_time = convert_time_to_db_time(start_time)
        date_of_quiz = datetime.strptime(date_of_quiz, '%Y-%m-%d').date()


        try:

            error_message = validate_quiz_date(date_of_quiz, start_time)
            if error_message:
                raise ValueError(error_message)  

            # If no error, save quiz
            new_quiz = Quiz(
            title=title.lower(),
            remarks=remarks,
            date_of_quiz=date_of_quiz,
            time_duration=time_duration,
            chapter_id=chapter_id,
            start_time = start_time
        )


            db.session.add(new_quiz)
            db.session.commit()

            flash('Quiz created successfully!', 'success') 
            return redirect(url_for('admin.get_chapter',chapter_id=chapter.id))

        except ValueError:
            flash('Invalid date', 'danger')
            return redirect(url_for('admin.create_quiz',chapter_id= chapter.id))





    return render_template('admin/quiz/create_quiz.html', chapter=chapter)




@admin_bp.route('/quiz/update/<int:quiz_id>', methods=['GET', 'POST'])
def update_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)  

    if request.method == 'POST':
        quiz.title = request.form['title'].lower()
        quiz.remarks = request.form['remarks']
        date_of_quiz = request.form['date_of_quiz']
        time_duration = request.form['time_duration']
        start_time = request.form['start_time']

        try:
            date_of_quiz = datetime.strptime(date_of_quiz, '%Y-%m-%d').date()  
            start_time = convert_time_to_db_time(start_time) 
            error_message = validate_quiz_date(date_of_quiz, start_time)
            if error_message:
                raise ValueError(error_message)  
            

            time_duration = int(time_duration)  
            quiz.start_time = start_time
            quiz.date_of_quiz = date_of_quiz
            quiz.time_duration = time_duration

            db.session.commit()
            flash('Quiz updated successfully!', 'success')
            return redirect(url_for('admin.get_chapter', chapter_id=quiz.chapter_id))  
        except ValueError as e:
            flash(str(e), "danger")  
            return redirect(request.url)



    return render_template('admin/quiz/edit_quiz.html', quiz=quiz)



@admin_bp.route('/quiz/delete/<int:quiz_id>', methods=['GET'])
@admin_required
def delete_quiz(quiz_id):

    quiz = Quiz.query.get(quiz_id)

    if not quiz:
        flash("Chapter not found!", "danger")
        return redirect(url_for('admin_dash'))


    db.session.delete(quiz)
    db.session.commit()

    flash("chapter deleted successfully!", "success")
    return redirect(url_for('admin.admin_dash'))

@admin_bp.route('/quiz/<int:quiz_id>', methods=['GET'])
@admin_required
def get_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz.id).all() 
    return render_template('admin/quiz/view_quiz.html',  quiz=quiz,questions=questions)




@admin_bp.route('/quiz/<int:quiz_id>/question/new', methods=['GET', 'POST'])
@admin_required
def add_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if request.method== "POST":
        question_statement = request.form.get('question_statement')
        question_type = request.form.get('question_type')
        option_texts = request.form.getlist('option_text[]') 
        correct_options = request.form.getlist('is_correct[]')
        score = request.form.get('score')

        if not question_statement or not question_type:
            flash("All fields are required!", "danger")
            return redirect(url_for('admin.add_question', quiz_id=quiz.id))

        if len(option_texts) < 2:
            flash("You must add at least two options!", "danger")
            return redirect(url_for('admin.add_question', quiz_id=quiz.id))

        if question_type == "mcq" and len(correct_options) != 1:
            flash("MCQ must have exactly one correct option!", "danger")
            return redirect(url_for('admin.add_question', quiz_id=quiz.id))

        if question_type == "msq" and len(correct_options) < 1:
            flash("MSQ must have at least one correct option!", "danger")
            return redirect(url_for('admin.add_question', quiz_id=quiz.id))
        
        new_question = Question(
            question_statement = question_statement,
            question_type = question_type,
            quiz_id = quiz_id,
            score = score
        )
        db.session.add(new_question)
        db.session.flush()  

        for index, text in enumerate(option_texts):
            is_correct = str(index) in correct_options  
            new_option = Option(
                option_text=text,
                is_correct=is_correct,
                question_id=new_question.id
            )
            db.session.add(new_option)

        db.session.commit()
        flash("Question added successfully!", "success")
        return redirect(url_for('admin.get_chapter', chapter_id=quiz.chapter_id))

    
    return render_template("admin/question/create_question.html",quiz=quiz)


@admin_bp.route('/question/update/<int:question_id>', methods=['GET', 'POST'])
@admin_required
def update_question(question_id):
    question = Question.query.get_or_404(question_id)
    options = Option.query.filter_by(question_id=question.id).all()

    if request.method == "POST":

        question_statement = request.form.get('question_statement')
        question_type = request.form.get('question_type')
        option_texts = request.form.getlist('option_text[]')
        score = request.form.get('score')
        correct_option_indexes = request.form.getlist('is_correct[]')

        correct_option_indexes = [int(index) for index in correct_option_indexes]




        if not question_statement or not question_type:
            flash("All fields are required!", "danger")
            return redirect(url_for('admin.update_question',  question_id=question.id))

        if len(option_texts) < 2:
            flash("You must have at least two options!", "danger")
            return redirect(url_for('admin.update_question',  question_id=question.id))

        if question_type == "mcq" and len(correct_option_indexes) != 1:
            flash("MCQ must have exactly one correct option!", "danger")
            return redirect(url_for('admin.update_question',  question_id=question.id))

        if question_type == "msq" and len(correct_option_indexes) < 1:
            flash("MSQ must have at least one correct option!", "danger")
            return redirect(url_for('admin.update_question',  question_id=question.id))
        
        question.text = question_statement
        question.question_type = question_type
        question.score = score
        db.session.commit()



        existing_options = list(options)  
        updated_options = []
   

        for index, text in enumerate(option_texts,start=1):
            is_correct = index in correct_option_indexes  

            if index < len(existing_options):

                existing_options[index].option_text = text
                existing_options[index].is_correct = is_correct
                updated_options.append(existing_options[index])
            else:

                new_option = Option(
                    option_text=text,
                    is_correct=is_correct,
                    question_id=question.id
                )
                db.session.add(new_option)
                updated_options.append(new_option)


        for opt in options:
            if opt not in updated_options:
                db.session.delete(opt)

        db.session.commit()
        flash("Question updated successfully!", "success")
        return redirect(url_for('admin.get_quiz', quiz_id=question.quiz_id))

    return render_template("admin/question/edit_question.html",  question=question, options=options)



@admin_bp.route('/question/delete/<int:question_id>', methods=['GET'])
@admin_required
def delete_question(question_id):

    question = Question.query.get_or_404(question_id)

    if not question:
        flash("Chapter not found!", "danger")
        return redirect(url_for('admin_dash'))


    db.session.delete(question)
    db.session.commit()

    flash("chapter deleted successfully!", "success")
    return redirect(url_for('admin.admin_dash'))



@admin_bp.route("/users",methods=['GET'])
@admin_required
def get_users():
    users = User.query.filter_by(role='user').all()

    return render_template('admin/user/view_users.html',users = users)


@admin_bp.route('/user/<int:user_id>', methods=['GET'])
@admin_required  
def get_user_data(user_id):
    user = User.query.get_or_404(user_id)  

    user_attempts = (
        db.session.query(
            Quiz.title.label("quiz_title"),
            QuizAttempt.time_started,
            QuizAttempt.time_completed,
            QuizAttempt.status,
            Scores.total_scored
        )
        .join(Quiz, Quiz.id == QuizAttempt.quiz_id)  
        .outerjoin(Scores, Scores.attempt_id == QuizAttempt.id)  
        .filter(QuizAttempt.user_id == user_id)
        .all()
    )

    return render_template('admin/user/user_data.html', user=user, attempts=user_attempts)



@admin_bp.route('/summary')
def summary():
    total_users = db.session.query(func.count(User.id)).filter(User.role == "user").scalar() or 0
    total_quizzes = db.session.query(func.count(Quiz.id)).scalar() or 0
    total_quiz_attempts = db.session.query(func.count(QuizAttempt.id)).scalar() or 0
    total_questions = db.session.query(func.count(Question.id)).scalar() or 0


    most_active_user = db.session.query(User.username, func.count(QuizAttempt.id))\
        .join(QuizAttempt, User.id == QuizAttempt.user_id)\
        .filter(User.role == "user")\
        .group_by(User.id)\
        .order_by(func.count(QuizAttempt.id).desc())\
        .first()

    avg_quiz_attempts_per_user = round(total_quiz_attempts / total_users, 2) if total_users else 0

    highest_score_user = db.session.query(User.username, func.max(Scores.total_scored))\
        .join(Scores, User.id == Scores.user_id)\
        .filter(User.role == "user")\
        .group_by(User.id)\
        .order_by(func.max(Scores.total_scored).desc())\
        .first()

    lowest_score_user = db.session.query(User.username, func.min(Scores.total_scored))\
        .join(Scores, User.id == Scores.user_id)\
        .filter(User.role == "user")\
        .group_by(User.id)\
        .order_by(func.min(Scores.total_scored).asc())\
        .first()


    most_attempted_quiz = db.session.query(Quiz.title, func.count(QuizAttempt.id))\
        .join(QuizAttempt, Quiz.id == QuizAttempt.quiz_id)\
        .group_by(Quiz.id)\
        .order_by(func.count(QuizAttempt.id).desc())\
        .first()

    least_attempted_quiz = db.session.query(Quiz.title, func.count(QuizAttempt.id))\
        .join(QuizAttempt, Quiz.id == QuizAttempt.quiz_id)\
        .group_by(Quiz.id)\
        .order_by(func.count(QuizAttempt.id).asc())\
        .first()

    best_performing_quiz = db.session.query(Quiz.title, func.avg(Scores.total_scored))\
        .join(Scores, Quiz.id == Scores.quiz_id)\
        .group_by(Quiz.id)\
        .order_by(func.avg(Scores.total_scored).desc())\
        .first()

    worst_performing_quiz = db.session.query(Quiz.title, func.avg(Scores.total_scored))\
        .join(Scores, Quiz.id == Scores.quiz_id)\
        .group_by(Quiz.id)\
        .order_by(func.avg(Scores.total_scored).asc())\
        .first()

    avg_score_per_quiz = db.session.query(Quiz.title, func.avg(Scores.total_scored))\
        .join(Scores, Quiz.id == Scores.quiz_id)\
        .group_by(Quiz.id)\
        .all()

    quiz_titles = [quiz[0] for quiz in avg_score_per_quiz]
    avg_scores = [round(quiz[1], 2) for quiz in avg_score_per_quiz]

    return render_template(
        'admin/summary.html',
        total_users=total_users,
        total_quizzes=total_quizzes,
        total_quiz_attempts=total_quiz_attempts,
        total_questions=total_questions,
        most_active_user=most_active_user,
        avg_quiz_attempts_per_user=avg_quiz_attempts_per_user,
        highest_score_user=highest_score_user,
        lowest_score_user=lowest_score_user,
        most_attempted_quiz=most_attempted_quiz,
        least_attempted_quiz=least_attempted_quiz,
        best_performing_quiz=best_performing_quiz,
        worst_performing_quiz=worst_performing_quiz,
        avg_score_per_quiz=avg_score_per_quiz,
        quiz_titles=quiz_titles,  
        avg_scores=avg_scores 
    )


@admin_bp.route("/search",methods=["GET"])
@admin_required
def search():
    search_word = request.args.get("search_word")
    key = request.args.get("key")

    if key == "subjects":
        results = Subject.query.filter(Subject.title.ilike(f"%{search_word.lower()}%")).all()
    elif key == "chapters":
        results = Chapter.query.filter(Chapter.title.ilike(f"%{search_word.lower()}%")).all()
    elif key == "users":
        results = User.query.filter(User.username.ilike(f"%{search_word.lower()}%")).all()
    elif key == "questions":
        results = Question.query.filter(Question.question_statement.ilike(f"%{search_word.lower()}%")).all()
    elif key == "quizzes":
        results = Quiz.query.filter(Quiz.title.ilike(f"%{search_word.lower()}%")).all()
    else:
        flash("invalid key","danger")
        return redirect(url_for("admin.admin_dash"))
    print(results)
    return render_template("admin/results.html",results = results, key=key)
