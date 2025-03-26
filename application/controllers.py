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
    # this_user = User.query.filter_by(type="admin").first()
    # all_info = Info.query.all()
    # users= len(User.query.all())-1
    # requests = len(Info.query.filter_by(atr_value="requested").all())
    # generated = len(Info.query.filter_by(atr_value="generated").all())
    # return render_template("admin_dash.html", this_user=this_user, all_info=all_info,users=users,requests=requests,generated=generated)
    return render_template("admin/admin_dashboard.html")