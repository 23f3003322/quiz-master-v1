from flask import Flask,render_template,redirect,request, session, flash , url_for
from flask import current_app as app
from functools import wraps
from .models import *
from datetime import datetime
from werkzeug.security import check_password_hash,generate_password_hash


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash("Access denied! Admins only.", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def fetch_subject_and_chapters(subject_id):
    """Fetch subject and related chapters."""
    subject = Subject.query.get_or_404(subject_id)
    chapters = Chapter.query.filter_by(subject_id=subject.id).all()
    return subject, chapters



@app.route("/logout",methods=["GET","POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/login",methods=["GET","POST"])
def login(): 
    if 'user_id' in session:
        flash("You are already logged in!", "info")
        if session.get("role")!="admin":
            return redirect(url_for("user_dash"))    
        return redirect(url_for('admin_dash'))

    if request.method == "POST":
        username = request.form.get("username")
        pwd = request.form.get("password")
        this_user = User.query.filter_by(username=username).first()#LHS attribute name in table, RHS is data fetched from form 
        if this_user:
            if  check_password_hash(this_user.password,pwd):
                session['user_id'] = this_user.id
                session['role'] = this_user.role
                if this_user.role == "admin":
                    return redirect("/admin")
                else:
                    return redirect(url_for('user_dash'))
            else:
                return render_template("incorrect_password.html")
        else:
            return render_template("not_exist.html")
    
    return render_template("login.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    # if 'user_id' in session:
    #     flash("You are already logged in!", "info")
    #     if session.get("role")!="admin":
    #         return redirect(url_for("user_dash"))    
    #     return redirect(url_for('admin_dash'))


    if request.method == 'POST':
        username = request.form.get('username')
        fullName = request.form.get('fullname')
        dob = request.form.get('dob')
        qualification = request.form.get('qualification')
        password = request.form.get('password')

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_user = User(username=username, fullName=fullName,DOB=dob,qualification=qualification, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('user_dash'))

    return render_template('register.html')  # Show register page only if not logged in



@app.route("/")
@login_required
def user_dash():
    subjects = Subject.query.all() 
    return render_template("user/user_dashboard.html",subjects=subjects)


@app.route("/admin")
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




@app.route('/admin/subject/new', methods=['GET','POST'])
# @admin_required

def create_subject():
    if request.method == 'POST':
        subject_title = request.form.get('title')
        subject_description = request.form.get('description')

        # Check if the subject already exists
        existing_subject = Subject.query.filter_by(title=subject_title).first()
        if existing_subject:
            flash("Subject already exists!", "warning")
            return redirect(url_for('create_subject'))

        # Create and save new subject
        new_subject = Subject(title=subject_title, description=subject_description)
        db.session.add(new_subject)
        db.session.commit()

        flash("Subject created successfully!", "success")
        return redirect(url_for('admin_dash')) 
    
    return render_template('admin/create_subject.html') 


@app.route('/admin/subject/update/<int:subject_id>', methods=['GET','POST'])
@admin_required
def update_subject(subject_id):
    print(subject_id)
    subject = Subject.query.get(subject_id)
    print(subject.title)
    print(subject.description)

    if request.method=="POST":
        if not subject:
            flash("Subject not found!", "danger")
            return redirect(url_for('admin_Dash'))

        # Get form data
        title = request.form.get('title')
        description = request.form.get('description')

        if not title:
            flash("Title is required!", "danger")
            return redirect(url_for('update_subject', subject_id=subject_id))

        # Update subject details
        subject.title = title
        subject.description = description
        db.session.commit()

        flash("Subject updated successfully!", "success")
        return redirect(url_for('admin_dash'))

    return render_template('admin/edit_subject.html', subject=subject)


@app.route('/admin/subject/delete/<int:subject_id>', methods=['GET'])
@admin_required
def delete_subject(subject_id):

    subject = Subject.query.get(subject_id)

    if not subject:
        flash("Subject not found!", "danger")
        return redirect(url_for('admin_dash'))

    # Delete the subject from the database
    db.session.delete(subject)
    db.session.commit()

    flash("Subject deleted successfully!", "success")
    return redirect(url_for('admin_dash'))


@app.route('/admin/subject/<int:subject_id>', methods=['GET'])
@admin_required
def get_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)  # Fetch subject by ID
    chapters = Chapter.query.filter_by(subject_id=subject.id).all() 
    return render_template('admin/view_subject.html', subject=subject, chapters=chapters)




@app.route('/admin/subject/<int:subject_id>/chapter/new', methods=['GET', 'POST'])
@admin_required
def create_chapter(subject_id):
    subject = Subject.query.get_or_404(subject_id)

    if request.method == 'POST':
        title = request.form.get('title')

        if not title:
            flash('Title is required', 'danger')
            return redirect(url_for('create_chapter', subject_id=subject_id))

        new_chapter = Chapter(title=title, subject_id=subject_id)
        db.session.add(new_chapter)
        db.session.commit()
        flash('Chapter created successfully!', 'success')
        return redirect(url_for('get_subject',subject_id=subject_id))

    return render_template('admin/chapter/create_chapter.html', subject=subject)




@app.route('/admin/chapter/<int:chapter_id>', methods=['GET'])
@admin_required
def get_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    Quizes = Quiz.query.filter_by(chapter_id=chapter.id).all() 
    return render_template('admin/chapter/view_chapter.html',  chapter=chapter,quizes=Quizes)


@app.route('/admin/chapter/update/<int:chapter_id>', methods=['GET', 'POST'])
@admin_required
def update_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)

    if request.method == 'POST':
        chapter.title = request.form.get('title')
        db.session.commit()
        flash('Chapter updated successfully!', 'success')
        return redirect(url_for('get_subject', subject_id=chapter.subject_id))

    return render_template('admin/chapter/edit_chapter.html', chapter=chapter)



@app.route('/admin/chapter/delete/<int:chapter_id>', methods=['GET'])
@admin_required
def delete_chapter(chapter_id):

    chapter = Chapter.query.get(chapter_id)

    if not chapter:
        flash("Chapter not found!", "danger")
        return redirect(url_for('admin_dash'))

    # Delete the subject from the database
    db.session.delete(chapter)
    db.session.commit()

    flash("chapter deleted successfully!", "success")
    return redirect(url_for('admin_dash'))


@app.route('/admin/chapter/<int:chapter_id>/quiz/new', methods=['GET', 'POST'])
@admin_required
def create_quiz(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)

    if request.method == 'POST':
        print("post request")
        title = request.form['title']
        remarks = request.form.get('remarks', '')  # Optional
        date_of_quiz = request.form['date_of_quiz']
        time_duration = request.form['time_duration']
        is_active = request.form.get('is_active', 'false') == 'true'  # Convert checkbox to boolean

        print(date_of_quiz)
        print(time_duration)
        # Convert date and time from string to Python Date & Time objects
        try:
            date_of_quiz = datetime.strptime(date_of_quiz, '%Y-%m-%d').date()
            time_duration = datetime.strptime(time_duration, '%H:%M:%S').time()
        except ValueError:
            flash('Invalid date or time format', 'danger')
            return redirect(url_for('create_quiz'))

        # Create new Quiz instance
        new_quiz = Quiz(
            title=title,
            remarks=remarks,
            date_of_quiz=date_of_quiz,
            time_duration=time_duration,
            chapter_id=chapter_id,
            is_active=is_active
        )

        # Add to database
        db.session.add(new_quiz)
        db.session.commit()

        flash('Quiz created successfully!', 'success') 
        return redirect(url_for('get_chapter',chapter_id=chapter_id))

    return render_template('admin/quiz/create_quiz.html', chapter=chapter)




@app.route('/admin/quiz/update/<int:quiz_id>', methods=['GET', 'POST'])
def update_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)  # Fetch quiz or return 404 if not found

    if request.method == 'POST':
        quiz.title = request.form['title']
        quiz.remarks = request.form['remarks']
        quiz.is_active = request.form.get('is_active') == 'on'  # Checkbox handling

        # Parse date and time separately
        date_str = request.form['date_of_quiz']
        time_str = request.form['time_duration']

        try:
            quiz.date_of_quiz = datetime.strptime(date_str, "%Y-%m-%d").date()
            quiz.time_duration = datetime.strptime(time_str, "%H:%M:%S").time()
        except ValueError:
            flash("Invalid date or time format. Use YYYY-MM-DD for date and HH:MM:SS for time.", "danger")
            return redirect(request.url)

        db.session.commit()
        flash('Quiz updated successfully!', 'success')
        return redirect(url_for('get_chapter',chapter_id=quiz.chapter_id))  # Redirect to the dashboard or quiz list

    return render_template('admin/quiz/edit_quiz.html', quiz=quiz)


@app.route('/admin/quiz/delete/<int:quiz_id>', methods=['GET'])
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
    return redirect(url_for('admin_dash'))

@app.route('/admin/quiz/<int:quiz_id>', methods=['GET'])
@admin_required
def get_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz.id).all() 
    return render_template('admin/quiz/view_quiz.html',  quiz=quiz,questions=questions)


@app.route('/admin/quiz/<int:quiz_id>/question/new', methods=['GET', 'POST'])
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
            return redirect(url_for('add_question', quiz_id=quiz.id))

        if len(option_texts) < 2:
            flash("You must add at least two options!", "danger")
            return redirect(url_for('add_question', quiz_id=quiz.id))

        if question_type == "mcq" and len(correct_options) != 1:
            flash("MCQ must have exactly one correct option!", "danger")
            return redirect(url_for('add_question', quiz_id=quiz.id))

        if question_type == "msq" and len(correct_options) < 1:
            flash("MSQ must have at least one correct option!", "danger")
            return redirect(url_for('add_question', quiz_id=quiz.id))
        
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
        return redirect(url_for('get_chapter', chapter_id=quiz.chapter_id))

    
    return render_template("admin/question/create_question.html",quiz=quiz)


@app.route('/admin/question/update/<int:question_id>', methods=['GET', 'POST'])
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
            return redirect(url_for('update_question',  question_id=question.id))

        if len(option_texts) < 2:
            flash("You must have at least two options!", "danger")
            return redirect(url_for('update_question',  question_id=question.id))

        if question_type == "mcq" and len(correct_option_indexes) != 1:
            flash("MCQ must have exactly one correct option!", "danger")
            return redirect(url_for('update_question',  question_id=question.id))

        if question_type == "msq" and len(correct_option_indexes) < 1:
            flash("MSQ must have at least one correct option!", "danger")
            return redirect(url_for('update_question',  question_id=question.id))
        
        question.text = question_statement
        question.question_type = question_type
        question.score = score
        db.session.commit()


         # ✅ Update options correctly
        existing_options = list(options)  # Convert to a list to allow index-based access
        updated_options = []
   

        for index, text in enumerate(option_texts,start=1):
            is_correct = index in correct_option_indexes  # ✅ Fix: Ensure correct mapping

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
        return redirect(url_for('get_quiz', quiz_id=question.quiz_id))

    return render_template("admin/question/edit_question.html",  question=question, options=options)



@app.route('/admin/question/delete/<int:question_id>', methods=['GET'])
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
    return redirect(url_for('admin_dash'))




@app.route('/user/subject/<int:subject_id>', methods=['GET'])
@login_required
def user_get_subject(subject_id):
    """User route to view a subject."""
    subject, chapters = fetch_subject_and_chapters(subject_id)
    return render_template('user/view_subject.html', subject=subject, chapters=chapters)


@app.route('/user/chapter/<int:chapter_id>', methods=['GET'])
@login_required
def user_get_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    Quizes = Quiz.query.filter_by(chapter_id=chapter.id).all() 

    return render_template('user/view_chapter.html',  chapter=chapter, quizes=Quizes)

@app.route('/start_quiz/<int:quiz_id>', methods=['POST'])
@login_required
def start_quiz(quiz_id):

    user_id = session['user_id']

    # Create a new quiz attempt
    new_attempt = QuizAttempt(user_id=user_id, quiz_id=quiz_id, time_started=datetime.utcnow())
    db.session.add(new_attempt)
    db.session.commit()

    flash("Quiz started successfully!", "success")
    
    # Redirect to the quiz page with the new attempt ID
    return redirect(url_for('quiz_questions', quiz_id=quiz_id, attempt_id=new_attempt.id))




@app.route('/quiz/<int:quiz_id>/attempt/<int:attempt_id>', methods=['GET', 'POST'])
@login_required
def quiz_questions(quiz_id, attempt_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    return render_template('user/quiz.html', quiz=quiz, questions=questions, attempt_id=attempt_id)



@app.route('/quiz/<int:quiz_id>/submit/<int:attempt_id>', methods=['POST'])
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
    return redirect(url_for('user_dash'))