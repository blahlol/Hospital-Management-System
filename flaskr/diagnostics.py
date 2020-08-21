from flask import Flask,Blueprint,redirect,render_template,session,flash,url_for,request
import sqlite3

bp=Blueprint('diagnostics',__name__,url_prefix='/diagnostics')

def connection():
    conn=sqlite3.connect('patient.db')
    cur=conn.cursor()
    return conn,cur

@bp.route('/get_diagnosis',methods=['GET','POST'])
def get_diagnosis():
    if request.method=='GET': #checking if user is logged in
        if 'username' in session:
            return render_template('diagnostics/get_diagnosis.html')
        else:
            flash('Please Login to continue')
            return redirect(url_for('login'))

    elif request.method=='POST':
        pid=request.form['pid']
 
        if len(pid)<9: #checking pid length
            flash('Invalid PID: Patient ID should be 9 digits in length')
            return render_template('diagnostics/get_diagnosis.html')

        conn,cur=connection()
        cur.execute('select * from patient where pid=?',[pid])
        result=cur.fetchall()

        if len(result)==0: #cheking if records are fetched
            flash('Enter Valid Patient ID')
            return render_template('diagnostics/get_diagnosis.html')
        else:
            cur.execute('select diagnosis.tname,diagnosis.rate from diagnosis,patient_diagnosis where patient_diagnosis.tid=diagnosis.tid and pid=?',[pid])
            d=cur.fetchall()
            return render_template('diagnostics/get_diagnosis.html',result=result[0],d=d)

@bp.route('/add_diagnosis/<int:pid>',methods=['GET','POST'])
def add_diagnosis(pid):
    tests=[]
    test_names=[]
    conn,cur=connection()
    cur.execute('select tname from diagnosis') #geting the test details from db
    result=cur.fetchall()
    for i in result:test_names.append(i[0])
    if request.method=='POST':
        for i in range(len(request.form)):
            test=request.form['test'+str(i+1)]
            cur.execute('select rate,tid from diagnosis where tname=?',[test])
            result=cur.fetchall()
            cur.execute('insert into patient_diagnosis values(?,?)',(pid,result[0][1])) #updating patient records
            tests.append([test,result[0][0]])
        conn.commit()
        return render_template('diagnostics/add_diagnosis.html',pid=pid,tests=tests,test_names=test_names)
    
    else:
        if 'username' in session: #checking if user is logged in
            return render_template('diagnostics/add_diagnosis.html',pid=pid,test_names=test_names)
        else:
            flash('Please Login to continue')
            return redirect(url_for('login'))
