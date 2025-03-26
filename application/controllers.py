from flask import Flask,render_template,redirect,request, session, flash , url_for
from flask import current_app as app
from functools import wraps
from .models import *
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
                    return render_template("user_dashboard.html",this_user= this_user)
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
    return render_template("user_dashboard.html")


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




# @app.route('/admin/subject/<int:subject_id>/chapters', methods=['GET'])
# @admin_required
# def get_chapters(subject_id):
#     subject = Subject.query.get_or_404(subject_id)
#     return render_template('admin/chapters.html', subject=subject, chapters=subject.chapters)


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


