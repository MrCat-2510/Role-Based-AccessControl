from flask import Flask, Blueprint, redirect, url_for, render_template, request, redirect, session,flash
from init import db
from models import User, Role, Note
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

views = Blueprint('views', __name__)
ses = Session()

# Login Page
@views.route("/", methods = ['GET','POST'])
def base():
    return redirect(url_for('views.login'))
# Login Page
@views.route("/login", methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        u = request.form['username'].strip().replace(" ","")
        p = request.form['password'].strip().replace(" ","")
        user = User.query.filter_by(username=u, password=p).first()
        if user is not None:
            login_user(user, remember=True)
            session['role'] = user.role[0].name
            flash('Logged in successfully.')
            if session.get('role') == 'Admin':
                return redirect(url_for('views.admin'))
            elif session.get('role') == 'Read':
                return redirect(url_for('views.read'))
            else:
                return redirect(url_for('views.homepage'))         
        else:
            flash('Wrong username or password. Please try again!')

    return render_template("login.html")

# Register Page
@views.route("/register", methods = ['GET','POST'])
def register():
    if request.method == 'POST':
        try:
            username=request.form.get('username').strip().replace(" ","")
            password=request.form.get('password').strip().replace(" ","")
            role_name = request.form.get('role')
            user = User.query.filter_by(username=username).first()
            admin = Role.query.filter_by(name='Admin').first()
            if user:
                flash('Account Already Exists')
            elif len(password) < 3:
                flash('Password too small')
            elif role_name == None:
                flash('Role is not defined')
            elif role_name=='Admin' and admin:
                flash('There only 1 admin account can be created. Please choose another role')
            elif role_name!='Admin' and not admin:
                flash('You should create admin account first')
            else:
                try:
                    new_user = User(username=username, password=password)
                    new_user.role.append(Role(name=role_name))
                except:
                    flash("New_User cannot created")
                db.session.add(new_user)
                db.session.commit()
                flash('Create account successfully.')
                return redirect(url_for('views.login'))
        except:
            flash('Register Error.')

        
    return render_template("register.html")

#ReadWrite User
@views.route("/homepage",methods=['GET','POST'])
@login_required
def homepage():
    if request.method == 'POST':
        note_content = request.form.get('content')
        if len(note_content) < 5:
            return "<h1>The note was too short</h1>"
        else:
            try:
                new_note = Note(content=str(note_content), user_id = current_user.id,user_name=current_user.username)
            except:
                return "<h1>There is something wrong with new_note</h1>"
            try:
                db.session.add(new_note)
                db.session.commit()
                return redirect(url_for('views.homepage'))
            except:
                return "<h1>There is something wrong when add and commit</h1>"
            
    else:
        if session.get('role') == 'Admin':
            return redirect(url_for('views.admin'))
        notes = Note.query.order_by(Note.date.desc()).all()
        return render_template("homepage.html", user=current_user, notes=notes, role=session.get('role'))

#Admin User
@views.route("/admin",methods=['GET','POST'])
@login_required
def admin():
    if request.method == 'POST':
        note_content = request.form.get('content')
        if len(note_content) < 5:
            return "<h1>The note was too short</h1>"
        else:
            try:
                new_note = Note(content=str(note_content), user_id = current_user.id,user_name=current_user.username)
            except:
                return "<h1>There is something wrong with new_note</h1>"
            try:
                db.session.add(new_note)
                db.session.commit()
                return redirect(url_for('views.admin'))
            except:
                return "<h1>There is something wrong when add and commit</h1>"
    else:
        accounts = User.query.join(User.role).filter(Role.name != 'Admin').order_by(User.id).all()
        notes = Note.query.order_by(Note.date.desc()).all()
        return render_template("admin.html", accounts = accounts, user=current_user,notes=notes)

#Delete User
@views.route('/delete-account/<account_id>', methods=['GET','POST'])
@login_required
def delete_account(account_id):
    if session.get('role') == 'Admin':
        try:
            account_to_delete = User.query.get(account_id)
            account_role = account_to_delete.role[0].name
            if account_role == 'Admin':
                return "<h1>You cannot delete admin account</h1>"
            else:
                db.session.delete(account_to_delete)
                db.session.commit()
                return redirect(url_for('views.admin'))
        except:
            return "<h1>Cannot Deleted</h1>"
    else:
        return "<h1>You don't have authorize to delete account. Only Admin can delete it</h1>"

#Update User
@views.route('/update-account/<account_id>', methods=['GET','POST'])
@login_required
def update_account(account_id):
    if session.get('role') == 'Admin':
        account = User.query.get(account_id)
        account_role = account.role[0].name
        if request.method == 'POST':
            if account_role == 'Admin':
                return "<h1>You can not edit admin account</h1>"
            else:
                username=request.form.get('username').strip().replace(" ","")
                password=request.form.get('password').strip().replace(" ","")
                role_name = request.form.get('role')
                try:    
                    account.username=username
                    account.password=password
                    account.role[0].name = role_name
                    account.date = func.now()
                    db.session.commit()
                    return redirect(url_for('views.admin'))
                except:
                    return "<h1>Cannot Updated. Please try again</h1>"
        else:
            return render_template('update_account.html', account=account,account_role=account_role)
    else:
        return "<h1>You don't have authorize to delete account. Only Admin can delete it</h1>"

#Read User
@views.route("/read",methods=['GET','POST'])
@login_required
def read():
    notes = Note.query.order_by(Note.date.desc()).all()
    return render_template("read.html",user=current_user, notes=notes)

#Logout user
@views.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.login'))

#Delete Note
@views.route('/delete/<note_id>', methods=['GET','POST'])
@login_required
def delete(note_id):
    if session.get('role') != 'Read':
        task_to_delete = Note.query.get(note_id)
        try:
            db.session.delete(task_to_delete)
            db.session.commit()
            if session.get('role') == 'Admin':
                return redirect(url_for('views.admin'))
            else:
                return redirect(url_for('views.homepage'))
        except:
            return "Cannot Deleted"
    else:
        return "<h1>You don't have authorize to delete notes. Only Admin and Read Write can delete it</h1>"

#Update Note
@views.route('/update/<note_id>', methods=['GET','POST'])
@login_required
def update(note_id):
    if session.get('role') != 'Read':
        note = Note.query.get(note_id)
        if request.method == 'POST':
            try:
                update_note = request.form['content']
                if len(update_note) < 5:
                    return "<h1>The note was too short</h1>"
                else:
                    note.date = func.now()
                    note.content = request.form['content']
                    db.session.commit()
                    if session.get('role') == 'Admin':
                        return redirect(url_for('views.admin'))
                    else:
                        return redirect(url_for('views.homepage'))
            except:
                flash('There was an issue updating your note')
                return "Cannot Updated"

        return render_template('update.html', note=note, user=current_user)
    else:
        return "<h1>You don't have authorize to update notes. Only Admin and Read Write can delete it</h1>"



    