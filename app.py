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
 
@app.route('/cart',methods=['POST'])
def cart():

    if 'cart' not in session:
        session['cart']=[]

    if request.method=='POST':
        foodId=request.form.get('id')
        if foodId:
            session['cart'].append(foodId)
    return redirect('/')