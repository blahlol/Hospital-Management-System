from flask import Flask,render_template,request,flash,session,redirect,url_for
import sqlite3
from . import pharmacy
from . import diagnostics
from . import patient

def connection():
    conn=sqlite3.connect('patient.db')
    cur=conn.cursor()
    return conn,cur

def create_app():
    app=Flask(__name__)
    

    @app.route('/',methods=['GET','POST'])
    def login():
        if request.method=='POST':
            username=request.form['username']
            if len(username)<8: #username must be atleast 8 chars in length
                flash('Username must be atleast 8 characters in length') #feedback for user
                return render_template('login.html')

            password=request.form['password']
            if len(password)<10 or len(password)>10: #password must be 10 chars in length
                flash('Password must be 10 characters in length') #feedback for user
                return render_template('login.html')
            
            conn,cur=connection() #connecting to the database
            cur.execute('select password from userstore where username=?',[username])
            result=cur.fetchall()
            #sample format for result = [('karan@1999',)]
            if len(result)==0:  #if no records are fetched
                flash('Invalid Username')
                return render_template('login.html')
            elif password!=result[0][0]: #wrong password
                flash('Wrong Password')
                return render_template('login.html')
            else:
                session['username']=username  #session management. Adding user to the session
                return redirect(url_for('patient.pat_reg'))
        else:
            return render_template('login.html')
        
    @app.route('/logout')
    def logout():
        session.pop('username',None) #removing user from session
        flash('Logged Out Successfully')  
        return redirect(url_for('login'))
    
    app.register_blueprint(pharmacy.bp)
    app.register_blueprint(diagnostics.bp)
    app.register_blueprint(patient.bp)

    return app
