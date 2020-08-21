from flask import Flask,Blueprint,redirect,render_template,session,flash,request,url_for
import sqlite3

bp=Blueprint('pharmacy',__name__,url_prefix='/pharmacy')

def connection():
    conn=sqlite3.connect('patient.db')
    cur=conn.cursor()
    return conn,cur

@bp.route('/get_patient',methods=['GET','POST'])
def get_patient():
    if request.method=="GET": 
        if 'username' in session: #checking if user is logged in
            return render_template('pharmacy/get_patient.html')
        else:
            flash('Please Login to continue')
            return redirect(url_for('login'))

    elif request.method=='POST':
        pid=request.form['pid']

        if len(pid)<9: #checking pid length
            flash('Invalid PID: Patient ID should be 9 digits in length')
            return render_template('pharmacy/get_patient.html')

        conn,cur=connection()
        cur.execute('select * from patient where pid=?',[pid])
        result=cur.fetchall()

        if len(result)==0: #checking if records were fetched
            flash('Enter Valid Patient ID')
            return render_template('pharmacy/get_patient.html')
        else:
            cur.execute('select medicines.mname,patient_meds.quantity,medicines.rate,medicines.rate*patient_meds.quantity from patient_meds,medicines where patient_meds.mid=medicines.mid and pid=?',[pid])
            meds=cur.fetchall()
            return render_template('pharmacy/get_patient.html',result=result[0],meds=meds)
    
@bp.route('/issue_meds/<int:pid>',methods=['GET','POST'])
def issue_meds(pid):
    if request.method=='POST':
        success=[];fail=[]
        conn,cur=connection()

        for i in range(len(request.form)//2):
            medicine=request.form['med'+str(i+1)]
            quantity=request.form['q'+str(i+1)]
            cur.execute('select * from medicines where mname=?',[medicine])
            result=cur.fetchall()
            #sample formate for result [(1,'crocin',10)] => (pid,name,quantity)

            if len(result)==0:
                flash('Invalid medicine name: '+medicine+' . Not present in database.')
                return render_template('pharmacy/issue_meds.html',pid=pid)
            else:    
                if int(quantity)<=result[0][2]: #quantity is at index 2
                    success.append([medicine,quantity,result[0][3],int(quantity)*result[0][3]])
                    cur.execute('insert into patient_meds values(?,?,?)',(pid,result[0][0],int(quantity)))  #updating patient records
                    cur.execute('update medicines set quantity=? where mid=?',(result[0][2]-int(quantity),result[0][0]))
                else:
                    fail.append([medicine,quantity,result[0][2]])

        conn.commit()
        return render_template('pharmacy/issue_meds.html',pid=pid,fail=fail,success=success)
            
    else:
        if 'username' in session: #checking if user is logged in
            return render_template('pharmacy/issue_meds.html',pid=pid)
        else:
            flash('Please Login to continue')
            return redirect(url_for('login'))