from flask import Flask,render_template,request,redirect
from flask_login import login_required, current_user, login_user, logout_user
from models import UserModel,Entries,db,login
from datetime import datetime
 
app = Flask(__name__)
app.secret_key = 'SherinFatCow'
 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

 
db.init_app(app)
login.init_app(app)
login.login_view = 'login'
 
@app.before_first_request
def create_all():
    db.create_all()
     
@app.route('/add', methods = ['POST', 'GET'])
@login_required
def add():
    email = current_user.email
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['text']
        date = datetime.now()
        entry = Entries(email=email, title=title, content= content, date_posted = date)
        db.session.add(entry)
        db.session.commit()
        return redirect('/add')
    return render_template('add.html')

@app.route('/view', methods = ['POST', 'GET'])
@login_required
def view():
    email = current_user.email
    entry = Entries.query.filter_by(email = email)
    entry = sorted(entry,key = lambda x:x.date_posted,reverse= True)
    return render_template('posts.html',post = entry)

@app.route('/del/<int:pid>')
@login_required
def delete(pid):
    p = Entries.query.filter_by(pid = pid).delete()
    db.session.commit()
    return redirect('/view')
 
@app.route('/login', methods = ['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect('/view')
     
    if request.method == 'POST':
        email = request.form['email']
        user = UserModel.query.filter_by(email = email).first()
        if user is not None and user.check_password(request.form['password']):
            login_user(user)
            return redirect('/view')

    return render_template('login.html')
 
@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect('/view')
     
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
 
        if UserModel.query.filter_by(email=email).first():
            return ('Email already Present')
             
        user = UserModel(email=email, username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')
 
 
@app.route('/logout')
def logout():
    logout_user()
    return redirect('/blogs')
app.run()
