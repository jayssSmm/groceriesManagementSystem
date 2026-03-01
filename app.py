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
    
    try:
        user=bool(session['user'])
    except:
        user=False

    return render_template('home.html',groceries=row, user=user)

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

            db=get_db()
            cursor=db.cursor()
            cursor.execute('SELECT * FROM cart WHERE id=?',(user['id'],))
            cart=cursor.fetchall()
            print(list(cart))

            session['cart']=[dict(row) for row in cart]
            return redirect('/')
        
        return redirect('/signin')

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
    
    if 'user_id' not in session['user']: 
        return render_template('signin.html',error=True)
    
    return render_template('signin.html')

@app.route('/cart',methods=['POST','GET'])
def cart():

    if 'user' not in session:
        return redirect('/login')

    if 'cart' not in session:
        session['cart']=[]

    '''cart= [ 
            {user_id,grocery_id,qunatity},
            {},
        ]'''
    
    if request.method=='POST':
        foodId=int(request.form.get('id'))

        cart_groceries=list(map(lambda x:x['grocery_id'],session['cart']))
        if foodId in cart_groceries:
            for i in session['cart']:
                if i['grocery_id']==foodId:
                    i['quantity']+=1
                    break
        else:
            cart={'user_id':session['user']['user_id'],'grocery_id':foodId,'quantity':1}
            session['cart'].append(cart)
            
    return redirect('/')

@app.route('/cartview')
def cartview():

    try:
        placeholder=','.join(['?' for i in session['cart']])

        db=get_db()
        cursor=db.cursor()

        cursor.execute('DELETE FROM cart;')
        for i in session['cart']: 
            cursor.execute('INSERT INTO cart(id,grocery_id,quantity_in_cart) VALUES(?,?,?)',tuple(i.values()))
        db.commit()

        foodId=tuple(map(lambda x:x['grocery_id'],session['cart']))        
        cursor.execute(f'SELECT grocery.*, cart.quantity_in_cart FROM grocery JOIN cart ON grocery.si_no=cart.grocery_id WHERE si_no IN ({placeholder})',foodId)
        row=cursor.fetchall()
    except KeyError:
        row=[]
    return render_template('cart.html',cart=row)

'''cart= [ 
    {user_id,grocery_id,qunatity},
    ]'''
    
@app.route('/removecart',methods=['GET','POST'])
def removecart():
    if request.method == 'POST':
        foodId = int(request.form.get('id'))
        for i in session['cart']:
            if foodId == i['grocery_id']:
                i['quantity'] -= 1
                if i['quantity'] <= 0:
                    session['cart'].remove(i)  
                session.modified = True  # Save changes to session
                break
    return redirect('/cartview')  

@app.route('/clearcart')
def clearcart():
    session['cart']=[]
    return redirect('/cartview')

@app.route('/logout')
def logout():

    if session['cart']==[]:
        db=get_db()
        cursor=db.cursor() 
        cursor.execute('DELETE FROM cart WHERE id=?',(session['user']['user_id'],))
        db.commit()

    session.clear()
    return redirect('/')