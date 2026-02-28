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
    
    return render_template('home.html',groceries=row)
 
@app.route('/cart',methods=['POST','GET'])
def cart():

    if 'cart' not in session:
        session['cart']=[]

    if request.method=='POST':
        foodId=int(request.form.get('id'))
        if foodId:
            session['cart'].append(foodId)
        print(session['cart'])
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
        return redirect('/sigin.html')

    return render_template('login.html')

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
        return redirect('/')
    
    return render_template('signin.html')

@app.route('/cartview')
def cartview():

    db=get_db()
    cursor=db.cursor()
    if session['cart']:
        placeholder=','.join(['?' for i in session['cart']])
        
        cursor.execute(f'SELECT * FROM grocery WHERE si_no IN ({placeholder})',tuple(session['cart']))
        row=cursor.fetchall()
        print(row)
    else:
        row=[]
    return render_template('cart.html',cart=row)

@app.route('/clearcart')
def clearcart():
    session['cart']=[]
    return redirect('/cartview')