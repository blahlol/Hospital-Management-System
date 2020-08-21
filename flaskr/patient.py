from flask import Flask,Blueprint,redirect,render_template,session,flash,request,url_for
import sqlite3
import random,datetime

bp=Blueprint('patient',__name__,url_prefix='/patient')
P_Id=0

def connection():
    conn=sqlite3.connect('patient.db')
    cur=conn.cursor()
    return conn,cur

#patient registration
@bp.route('/PatientRegistration',methods=["GET","POST"])
def pat_reg():
    if request.method=="POST":
        conn,cur=connection()
        for i in range(100):
            pid=random.randint(100000000,999999999)  #random generation of PID
            cur.execute("select pid from patient where pid=?",[pid])
            p_id=cur.fetchall()
            if len(p_id) <=0:
                break

        pname=request.form['pname']
        p_age=int(request.form['p_age'])
        DateofAdmission=request.form['doa']
        BedType=request.form['btype']
        Address=request.form['addr']
        city=request.form['city']
        state=request.form['state']
        #inserting to the database
        cur.execute("insert into patient (pid,pname,age,doj,BedType,Address,City,State,Status) values(?,?,?,?,?,?,?,?,'active')",(pid,pname,p_age,DateofAdmission,BedType,Address,city,state))
        conn.commit()
    
        return render_template('patient/Patient_Registration.html',s="Registration successful",pid=pid,string="Patient ID:")
    else:
        if 'username' in session:  #checking if user is logged in otherwise redirect to login page if someone tries to access this route directly without login
            return render_template("patient/Patient_Registration.html")
        else:
            flash('Please Login to continue')
            return redirect(url_for('login'))

@bp.route('/PatientUpdation',methods=['GET','POST'])
def pat_up():
    if request.method=="POST":
        conn,cur=connection()
        global P_Id
        P_Id=request.form['PId']
        if len(P_Id)<9: #PID length must be 9 chars otherwise display error message
            flash('Invalid PID: Patient ID should be 9 digits in length')
            return render_template('patient/Patient_Update1.html')
        cur.execute("select * from patient where pid = ?",[P_Id])
        update=cur.fetchall()
        #sample format for update = [(123456789,"hank",30,"2020-06-25","Single room","adyar","chennai","TN","active")]

        if len(update)>0: # checking if record is fetched. If not prmopt user to enter valid id
            return render_template('patient/Patient_Update2.html',p_id=update[0][0],p_name=update[0][1],p_a=update[0][2],p_d=update[0][3],p_ad=update[0][5],p_c=update[0][6],p_s=update[0][7])
        else:
            flash('Enter Valid Patient ID')
            return render_template('patient/Patient_Update1.html')
    else:
        if 'username' in session: #checking if user is logged in
            return render_template('patient/Patient_Update1.html')
        else:
            flash('Please Login to continue')
            return redirect(url_for('login'))

@bp.route('/Patient_Update2',methods=['GET','POST'])
def patientUpdate2():
    if request.method=="POST":
        conn,cur=connection()
        pname=request.form['pname']
        p_age=int(request.form['p_age'])
        DateofAdmission=request.form['doa']
        BedType=request.form['btype']
        Address=request.form['addr']
        city=request.form['city']
        state=request.form['state']
        #updating patient details with newly entered data
        cur.execute("update patient set pname=?,age=?,doj=?,BedType=?,Address=?,City=?,State=? where pid=?",(pname,p_age,DateofAdmission,BedType,Address,city,state,P_Id))
        conn.commit()
        return redirect(url_for('patient.pat_up'))

    else:
        if 'username' in session:  #checking if user is logged in
            return redirect(url_for('patient.pat_up'))
        else:
            flash('Please Login to continue')
            return redirect(url_for('login'))

@bp.route('/search',methods=['GET','POST'])
def search():
    if request.method=="POST":
        conn,cur=connection()
        P_Id=request.form['PId']

        if len(P_Id)<9: #pid lenght must be 9 chars
            flash('Invalid PID: Patient ID should be 9 digits in length')
            return render_template('patient/search.html')

        cur.execute("select * from patient where pid = ?",[P_Id])
        update=cur.fetchall()
        #order in which the fields exist in the update var
        l=["Patiend Id","Patient Name","Patient Age","Date of Admission","Bed Type","Address","City","State","Status"]

        if len(update)>0: #checking is records are fetched
            return render_template('patient/search.html',info=update,msg=l)
        else:
            flash('Enter valid Patient ID')
            return render_template('patient/search.html')
    else:
        if 'username' in session: #checking if user is logged in 
            return render_template("patient/search.html")
        else:
            flash('Please Login to continue')
            return redirect(url_for('login'))

@bp.route('/viewall')
def viewall():
    if 'username' in session:  #checking if user is logged in
        conn,cur=connection()
        cur.execute("select * from patient where Status='active'")
        viewall2=cur.fetchall()
        return render_template("patient/viewall.html",info1=viewall2)
    else:
        flash('Please Login to continue')
        return redirect(url_for('login'))

@bp.route('/patientdelete',methods=['GET','POST'])
def delete():
    if request.method=="POST":
        conn,cur=connection()
        global P_Id
        P_Id=request.form['PId']

        if len(P_Id)<9: #checking pid length
            flash('Invalid PID: Patient ID should be 9 digits in length')
            return render_template('patient/patient_delete1.html')

        cur.execute("select * from patient where pid = ?",[P_Id])
        update=cur.fetchall()
        l=["Patiend Id","Patient Name","Patient Age","Date of Admission","Bed Type","Address","City","State","Status"]

        if len(update)>0: #checking if records are fetched.
            return render_template('patient/patient_delete2.html',info=update,msg=l)
        else:
            flash('Enter valid Patient ID')
            return render_template('patient/patient_delete1.html')
    else:
        if 'username' in session: #checking if user is logged in
            return render_template("patient/patient_delete1.html")
        else:
            flash('Please login to continue')
            return redirect(url_for('login'))

#deleting patient
@bp.route('/patient_delete2',methods=['GET','POST'])
def patientdelete2():
    if request.method=="POST":
        conn,cur=connection()
        cur.execute("delete from patient where pid=?",[P_Id])
        conn.commit()
        return redirect(url_for('patient.delete'))
    else:
        if 'username' in session: #checking if user is logged in
            return redirect(url_for('patient.delete'))
        else:
            flash('Please Login to continue')
            redirect(url_for('login'))

@bp.route('/Billing',methods=['GET','POST'])
def billing():
    if request.method=="POST":
        bill1=0
        bill2=0
        bill3=0
        total=0
        conn,cur=connection()
        P_Id=request.form['PId']
        if len(P_Id)<9:
            flash('Invalid PID: Patient ID should be 9 digits in length')
            return render_template('patient/billing.html')

        cur.execute("select * from patient where pid = ?",[P_Id])
        update=cur.fetchall()
        l=["Patiend Id","Patient Name","Patient Age","Date of Admission","Bed Type","Address","City","State","Status"]
        if len(update)>0:
            cur.execute('select medicines.mname,patient_meds.quantity,medicines.rate,medicines.rate*patient_meds.quantity from patient_meds,medicines where patient_meds.mid=medicines.mid and pid=?',[P_Id])
            meds=cur.fetchall()
            cur.execute('select diagnosis.tname,diagnosis.rate from diagnosis,patient_diagnosis where patient_diagnosis.tid=diagnosis.tid and pid=?',[P_Id])
            d=cur.fetchall()
            update1=update[0][3].split("-")
            firstdate=datetime.date(int(update1[0]),int(update1[1]),int(update1[2]))
            seconddate=datetime.date.today()
            dates=str(seconddate-firstdate)
            c=""
            for i in dates:
                if i !=" ":
                    c+=i
                else:
                    break
            c=int(c)
            #calculating room charges
            if update[0][4]=="General ward":
                bill1=c*2000
            elif update[0][4]=="Semi sharing":
                bill1=c*4000
            elif update[0][4]=="Single room":
                bill1=c*8000
            
            #medicine charges
            for i in meds:
                bill2+=int(i[3])
                
            #diagnosis charges
            for j in d:
                bill3+=int(j[1])
            total=bill1+bill2+bill3
            days="Number of Days in Hospital:"+str(c)
            return render_template('patient/billing.html',info=update,msg=l,d=d,meds=meds,bill1=bill1,bill2=bill2,bill3=bill3,total=total,days=days)
        else:
            flash('Enter Valid Patient ID')
            return render_template('patient/billing.html')
    else:
        if 'username' in session: #checking if user is logged in
            return render_template("patient/billing.html")
        else:
            flash('Please Login to continue')
            return redirect(url_for('login'))

@bp.route('/confirmation/<int:pid>')
def confirm(pid):
    conn,cur=connection()
    cur.execute('update patient set status="discharged" where pid=?',[pid])#changing the status of the patient to discharged
    conn.commit()
    flash('Patient Discharged')
    return redirect(url_for('patient.pat_reg'))