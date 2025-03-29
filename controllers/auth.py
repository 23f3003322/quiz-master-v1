from flask import Flask,Blueprint,render_template,redirect,request, session, flash , url_for
from flask import current_app as app
from functools import wraps
from models import *
from database import db
from datetime import datetime
from werkzeug.security import check_password_hash,generate_password_hash

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")




@auth_bp.route("/logout",methods=["GET","POST"])
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


@auth_bp.route("/login",methods=["GET","POST"])
def login(): 
    if 'user_id' in session:
        flash("You are already logged in!", "info")
        if session.get("role")!="admin":
            return redirect(url_for("user.user_dash"))    
        return redirect(url_for('admin.admin_dash'))

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
                    return redirect(url_for('user.user_dash'))
            else:
                return render_template("incorrect_password.html")
        else:
            return render_template("not_exist.html")
    
    return render_template("login.html")


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        flash("You are already logged in!", "info")
        if session.get("role")!="admin":
            return redirect(url_for("user.user_dash"))    
        return redirect(url_for('admin.admin_dash'))


    if request.method == 'POST':
        username = request.form.get('username')
        fullName = request.form.get('fullname')
        dob = request.form.get('dob')
        qualification = request.form.get('qualification')
        password = request.form.get('password')

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_user = User(username=username.lower(), fullName=fullName,DOB=dob,qualification=qualification, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('user.user_dash'))

    return render_template('register.html')  # Show register page only if not logged in

