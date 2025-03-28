from flask import Blueprint, render_template,request,flash,redirect,url_for
from .utils import admin_required
from models import *
from database import db
from datetime import datetime
from utils.helpers import convert_time_to_db_time, validate_quiz_date,convert_to_time
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/")
@admin_required
def admin_dash():
    subjects = Subject.query.all() 
    # this_user = User.query.filter_by(type="admin").first()
    # all_info = Info.query.all()
    # users= len(User.query.all())-1
    # requests = len(Info.query.filter_by(atr_value="requested").all())
    # generated = len(Info.query.filter_by(atr_value="generated").all())
    # return render_template("admin_dash.html", this_user=this_user, all_info=all_info,users=users,requests=requests,generated=generated)
    return render_template("admin/admin_dashboard.html",subjects=subjects)



@admin_bp.route('/subject/new', methods=['GET','POST'])
@admin_required
def create_subject():
    if request.method == 'POST':
        subject_title = request.form.get('title')
        subject_description = request.form.get('description')

        # Check if the subject already exists
        existing_subject = Subject.query.filter_by(title=subject_title).first()
        if existing_subject:
            flash("Subject already exists!", "warning")
            return redirect(url_for('admin.create_subject'))

        # Create and save new subject
        new_subject = Subject(title=subject_title, description=subject_description)
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

        # Get form data
        title = request.form.get('title')
        description = request.form.get('description')

        if not title:
            flash("Title is required!", "danger")
            return redirect(url_for('admin.update_subject', subject_id=subject_id))

        # Update subject details
        subject.title = title
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

    # Delete the subject from the database
    db.session.delete(subject)
    db.session.commit()

    flash("Subject deleted successfully!", "success")
    return redirect(url_for('admin.admin_dash'))

@admin_bp.route('/subject/<int:subject_id>', methods=['GET'])
@admin_required
def get_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)  # Fetch subject by ID
    chapters = Chapter.query.filter_by(subject_id=subject.id).all() 
    return render_template('admin/view_subject.html', subject=subject, chapters=chapters)


@admin_bp.route('/subject/<int:subject_id>/chapter/new', methods=['GET', 'POST'])
@admin_required
def create_chapter(subject_id):
    subject = Subject.query.get_or_404(subject_id)

    if request.method == 'POST':
        title = request.form.get('title')

        if not title:
            flash('Title is required', 'danger')
            return redirect(url_for('admin.create_chapter', subject_id=subject_id))

        new_chapter = Chapter(title=title, subject_id=subject_id)
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
        chapter.title = request.form.get('title')
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

    # Delete the subject from the database
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
        remarks = request.form.get('remarks', '')  # Optional
        date_of_quiz = request.form['date_of_quiz']
        time_duration = request.form['time_duration']
        start_time= request.form['start_time']  
        print(date_of_quiz)
        print(time_duration)
        print(start_time)
        start_time = convert_time_to_db_time(start_time)

        try:
            validate_quiz_date(date_of_quiz)
        except ValueError:
            flash('Invalid date', 'danger')
            return redirect(url_for('admin.create_quiz',chapter_id= chapter.id))

        # Create new Quiz instance

        new_quiz = Quiz(
            title=title,
            remarks=remarks,
            date_of_quiz=date_of_quiz,
            time_duration=time_duration,
            chapter_id=chapter_id,
            start_time = start_time
        )

        # Add to database
        db.session.add(new_quiz)
        db.session.commit()

        flash('Quiz created successfully!', 'success') 
        return redirect(url_for('admin.get_chapter',chapter_id=chapter.id))

    return render_template('admin/quiz/create_quiz.html', chapter=chapter)




@admin_bp.route('/quiz/update/<int:quiz_id>', methods=['GET', 'POST'])
def update_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)  # Fetch quiz or return 404 if not found

    if request.method == 'POST':
        quiz.title = request.form['title']
        quiz.remarks = request.form['remarks']
        date_of_quiz = request.form['date_of_quiz']
        time_duration = request.form['time_duration']
        start_time = request.form['start_time']

        # Validate date
        try:
            validate_quiz_date(date_of_quiz)
        except ValueError as e:
            flash(str(e), "danger")  # Display actual error message
            return redirect(request.url)

        # Convert input values
        date_of_quiz = datetime.strptime(date_of_quiz, '%Y-%m-%d').date()  
        start_time = convert_to_time(start_time)  # Converts HH:MM string to time object
        time_duration = int(time_duration)  # Ensure it's stored as an integer

        # Update quiz attributes
        quiz.start_time = start_time
        quiz.date_of_quiz = date_of_quiz
        quiz.time_duration = time_duration

        db.session.commit()
        flash('Quiz updated successfully!', 'success')
        return redirect(url_for('admin.get_chapter', chapter_id=quiz.chapter_id))  

    return render_template('admin/quiz/edit_quiz.html', quiz=quiz)



@admin_bp.route('/quiz/delete/<int:quiz_id>', methods=['GET'])
@admin_required
def delete_quiz(quiz_id):

    quiz = Quiz.query.get(quiz_id)

    if not quiz:
        flash("Chapter not found!", "danger")
        return redirect(url_for('admin_dash'))

    # Delete the subject from the database
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
        option_texts = request.form.getlist('option_text[]')  # Get all options
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
        # Get form data
        question_statement = request.form.get('question_statement')
        question_type = request.form.get('question_type')
        option_texts = request.form.getlist('option_text[]')
        score = request.form.get('score')
        correct_option_indexes = request.form.getlist('is_correct[]')

        correct_option_indexes = [int(index) for index in correct_option_indexes]



        # ✅ Validation
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


         # ✅ Update options correctly
        existing_options = list(options)  # Convert to a list to allow index-based access
        updated_options = []
   

        for index, text in enumerate(option_texts,start=1):
            is_correct = index in correct_option_indexes  # ✅ F

            if index < len(existing_options):
                # Update existing option
                existing_options[index].option_text = text
                existing_options[index].is_correct = is_correct
                updated_options.append(existing_options[index])
            else:
                # Add new option if more were added
                new_option = Option(
                    option_text=text,
                    is_correct=is_correct,
                    question_id=question.id
                )
                db.session.add(new_option)
                updated_options.append(new_option)

        # ✅ Remove extra options if some were deleted
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

    # Delete the subject from the database
    db.session.delete(question)
    db.session.commit()

    flash("chapter deleted successfully!", "success")
    return redirect(url_for('admin.admin_dash'))
