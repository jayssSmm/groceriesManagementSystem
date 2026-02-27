from flask import Flask,redirect,request,g,render_template,session
import sqlite3
from flask_session import Session

app = Flask(__name__)

app.config['SESSION_PERMANENT']=False
app.config['SESSION_TYPE']='filesystem'
Session(app)

DATABASE = 'groceries.db'

def get_db():
    if 'db' not in g:
        g.db=sqlite3.connect(DATABASE)
        g.db.row_factory=sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

@app.route('/', methods=['POST','GET'])
def index():
    db=get_db()
    cursor=db.cursor()
    cursor.execute('SELECT * FROM grocery')
    row=cursor.fetchall()

    if session['signin_success']:
        signin=True
    else:
        signin=False
    print(signin)

    return render_template('home.html',groceries=row,signin=signin)
 
@app.route('/cart',methods=['POST'])
def cart():

    if 'cart' not in session:
        session['cart']=[]

    if request.method=='POST':
        foodId=request.form.get('id')
        if foodId:
            session['cart'].append(foodId)
    return redirect('/')

@app.route('/login',methods=['POST','GET'])
def login():

    if 'user' not in session:
        session['user']={}

    if request.method=='POST':  
        name=request.form.get('name')
        passwd=request.form.get('passwd')

        db=get_db()
        cursor=db.cursor()
        cursor.execute('SELECT * FROM customer WHERE name=? AND passwd=?',(name,str(passwd)))
        user=cursor.fetchone()
        
        if user: 
            session['user']={'user_id':user['id']}
            return redirect('/')
        return render_template('login.html',error='true')

    return render_template('login.html',error='')

@app.route('/signin',methods=['POST','GET'])
def signin():
        
    if request.method=='POST':
        name=request.form.get('name')
        passwd=request.form.get('passwd')

        db=get_db()
        cursor=db.cursor()
        cursor.execute('INSERT INTO customer("name","passwd") VALUES(?,?)',(name,str(passwd)))
        db.commit()
        id=cursor.lastrowid

        session['user']={'user_id':id}
        session['signin_success'] = True
        return redirect('/')
    
    return render_template('signin.html')