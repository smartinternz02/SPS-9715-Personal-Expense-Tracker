from flask import Flask, request, render_template, url_for, session, redirect
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re,datetime
from sendemail import forgotemail,limitexceed
from monthgen import monthgen

app = Flask(__name__)

app.secret_key ='budgetbuddy'

app.config['MYSQL_HOST'] = 'remotemysql.com'
app.config['MYSQL_USER'] = 'VEuBGLb0Us'
app.config['MYSQL_PASSWORD'] = "WCxSJVDEBC"
app.config['MYSQL_DB'] = 'VEuBGLb0Us'

mysql = MySQL(app)

@app.route('/')
def homepage():
    return render_template("home.html")
    
@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/registerdata',methods=["POST","GET"])
def register():
    msg=""
    alert=""
    count = 0
    if request.method == "POST":
        name = request.form['firstname'] +" "+ request.form['lastname']
        fname = request.form['firstname']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        cpassword = request.form['cpassword']
        mobile = request.form['mobile']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = % s",(email,))
        account = cursor.fetchone()
        cursor.execute("SELECT * FROM users WHERE username = % s",(username,))
        user = cursor.fetchone()
        if(user):
            msg = "Sorry a member with username %s exists"%(user[2])
            count =  1
        elif(account):
            msg = "You're already a member with email %s"%(account[3])
            count =  1
        elif not re.match(r'[^@]+@[^@]+\.[^@]+',email):
            msg="Please Enter a Valid E-mail ID"
            count = 1
        elif not re.match(r'^[A-Za-z0-9_.-]*$',username):
            msg="Please Enter Valid Username"
            count = 1
        elif not (password == cpassword):
            msg="Please make sure your passwords match."
            count = 1
        elif not (request.form.get('checkbox')):
            msg="Please tick accept to terms and conditions "
            count = 1
        else:
            cursor.execute("INSERT INTO users VALUES(NULL,% s,% s,% s,% s,% s)",(name,username,email,password,mobile,))
            msg = "Congratulations, Dear %s You've Successfully Registered."%(fname)
            cursor.connection.commit()
        if(count == 1):
            alert="failure"
        else:
            alert="success"
        return render_template('signup.html',msg=msg,indicator=alert)

@app.route('/login')
def login():    
    return render_template('login.html',title="Login")

@app.route('/loginauth',methods=["POST","GET"])
def loginauth():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users where username =% s AND password = % s",(username,password,))
        account = cursor.fetchone()
        if(account):
            session['loggedin'] = True
            session['id'] = account[0]
            session['name'] = account[1]
            session['username'] = account[2]
            session['email'] = account[3]
            username = account[2]
            return redirect(url_for('home'))
        else:
            msg="Incorrect Username/Email and Password Combination"
            return render_template("login.html",msg=msg,indicator="failure",title="Login")
    else:
        return render_template("login")

@app.route('/forgot',methods=["POST","GET"])
def forgot():
    return render_template("forgot.html",title = "Forgot")

@app.route('/forgotpassword',methods=["POST","GET"])
def forgotpassword():
    msg=""
    if request.method=="POST":
        email = request.form['username']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = % s OR username = % s",(email,email,))
        account = cursor.fetchone()
        if(account):
            TEXT = """\
                    <!DOCTYPE html>
                    <html>
                    <body>
                        <div class="containter" style="display: block;">
                            <span style="font-size: 48px;left: 20px;font-weight:bold; font-family:Arial, Helvetica, sans-serif; color:#7048a9;">Budget Buddy!</span>
                            <h3 style="font-size: 24px; font-family:serif"> Dear """+account[1]+""", </h3>
                            <div class="side" style="width: 400px; height: 150px; border: 2px solid #7048a9; padding:30px; border-radius:10px; position:relative; left:100px;" >
                                <div class="details"style="position:relative; top:20px; left:60px; font-size:20px; font-family:'Courier New', Courier, monospace;text-align:left   ;">
                                    <p >Username : <span style="color: green; font-weight:bold;">"""+ account[2]+"""</span> </p>
                                    <p>Password : <span style="color: green; font-weight:bold;">"""+account[4]+"""</span> </p>
                                </div>
                            </div>
                        </div>
                    </body>
                    </html>"""
            msg="Your login credentials are sent to your registered mail id"
            forgotemail(TEXT,email)
            return render_template("forgot.html",msg=msg,indicator="success",title = "Forgot")
        else:
            msg="No account found with Email %s"%(email)
            return render_template("forgot.html",msg=msg,indicator="failure",title = "Forgot")
    else:
        return redirect(url_for("forgot"))

@app.route('/monthlylimit')
def monlimit():
    if 'id' in session:
        name= session['name']
        username= session['username']
        email = session['email']
        return render_template("setlimit.html",username=username,email=email,name=name,title="Set monthly limit")
    else:
        return redirect(url_for('login'))
@app.route('/updatelimit')
def updatelimit():
    if 'id' in session:
        name= session['name']
        username= session['username']
        email = session['email']
        return render_template("updatelimit.html",username=username,email=email,name=name,title="Update monthly limit")
    else:
        return redirect(url_for('login'))

@app.route('/setlimit',methods=["POST","GET"])
def setlimit():
    if 'id' in session:
        name= session['name']
        username= session['username']
        email = session['email']
        msg=""
        count = 0
        alert=""
        userid = session['id']
        if request.method=="POST":
            mon=request.form.get('month')
            month = mon+"-01"
            value=request.form.get('limit')
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM mlimit WHERE month = % s AND id = % s",(month,userid,))
            found = cursor.fetchone()
            if(found):
                msg="You've already set limit for the month"
                count = 1
            elif not re.match(r'^[0-9]*$',value):
                msg="Please Enter only Numeric Values"
            else:
                cursor.execute("INSERT INTO mlimit VALUES(NULL,% s,% s,% s)",(userid,month,value,))
                msg="Successful...!"
                cursor.connection.commit()
            if(count==1):
                alert='failure'
            else:
                alert='success'
            return render_template("setlimit.html",username=username,email=email,name=name,msg=msg,indicator=alert,title="Set monthly limit")
    else:
        return redirect(url_for('login'))    
    
@app.route('/setupdatelimit',methods=["POST","GET"])
def setupdate():
    if 'id' in session:
        name= session['name']
        username= session['username']
        email = session['email']
        if request.method == "POST":
            mon=request.form.get('month')
            month = mon+"-01"
            value=request.form.get('limit')
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM mlimit WHERE month = % s",(month,))
            account = cursor.fetchone()
            if(account):
                cursor.execute("UPDATE mlimit SET value = % s WHERE month = % s",(value,month,))
                msg="Successful...!"
                cursor.connection.commit()
                return render_template("updatelimit.html",username=username,email=email,name=name,msg=msg,indicator="success",title="Update monthly limit")    
            else:
                msg="Please set limit before update"
                return render_template("updatelimit.html",username=username,email=email,name=name,msg=msg,indicator="failure",title="Update monthly limit")    
    else:
        return redirect(url_for('login'))    


@app.route('/changepwd')
def changepwd():
    if 'id' in session:
        name= session['name']
        username= session['username']
        email = session['email']
        return render_template("changepassword.html",username=username,email=email,name=name,title="Change password")

@app.route('/changepassword',methods=["POST","GET"])
def changepassword():
    if 'id' in session:
        name= session['name']
        username= session['username']
        email = session['email']
        userid = session['id']
        msg=""
        count = 0
        current = request.form.get('password')
        new = request.form.get('npassword')
        confirm = request.form.get('cpassword')
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = % s",(userid,))
        acc = cursor.fetchone()
        if not (new == confirm):
            msg="New passwords doesnt match"
            count = 1
        elif not (current==acc[4]):
            msg="You've enterd wrong Current password"
            count= 1
        else:
            cursor.execute("UPDATE users SET password = % s WHERE id = % s",(new,userid))
            cursor.connection.commit()
            msg="Password updated Successfully.!"
        if(count==1):
            alert="failure"
        else:
            alert="success"
        return render_template('changepassword.html',username=username,email=email,name=name,indicator=alert,msg=msg,title="Change password")
    else:
        return redirect(url_for('login'))    

        
@app.route('/budget')
def budget():
    if 'id' in session:
        name= session['name']
        username= session['username']
        email = session['email']
        return render_template("addbudget.html",username=username,email=email,name=name,title="Add Budget")
    else:
        return redirect(url_for('login'))    

@app.route('/addbudget',methods=["POST","GET"])
def addbudget():
    if 'id' in session:
        name= session['name']
        username= session['username']
        email = session['email']
        userid = session['id']
        count = 0
        c=0
        sum=0
        dt = datetime.datetime.now()
        mn = { '01':"January",
                '02':"February",
                '03':"March",
                '04':"April",
                '05':"May",
                '06':"June",
                '07':"July",
                '08':"August",
                '09':"September",
                '10':"October",
                '11':"November",
                '12':"December"}
        if request.method=="POST":
            date = request.form.get('date')+""
            da = date.split("-")
            daa = da[0]+"-"+da[1]+"%"
            op = request.form.get('select')+""
            des = request.form.get('description')
            value = request.form.get('value')
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM mlimit WHERE id = % s and month LIKE % s",(userid,daa,))
            dat = cursor.fetchone()
            if(dat):
                mlimit = dat[3]
                if(op=='+'):
                    cursor.execute("INSERT INTO income VALUES(NULL,% s,% s,% s,% s,% s)",(userid,date,des,value,dt))
                    count = 1
                    cursor.connection.commit()
                elif(op=='-'):
                    cursor.execute("INSERT INTO expense VALUES(NULL,% s,% s,% s,% s,% s)",(userid,date,des,value,dt))
                    cursor.connection.commit()                
                cursor.execute("SELECT * FROM income WHERE date = % s AND id = % s",(date,userid))
                inc = cursor.fetchall()
                cursor.connection.commit()
                cursor.execute("SELECT * FROM expense WHERE date = % s  AND id = % s",(date,userid))
                exp = cursor.fetchall()
                cursor.connection.commit()
                for i in inc:
                    sum = sum+i[4]
                fi = sum
                sum = 0
                for j in exp:
                    sum= sum+j[4]
                ex = sum
                cursor.execute("SELECT * FROM expense WHERE id = % s and date LIKE % s",(userid,daa,))
                mexp = cursor.fetchall()
                cursor.connection.commit()
                sum = 0
                for k in mexp:
                    sum = sum+k[4]
                monthexp = sum
                if(monthexp > mlimit):
                    TEXT = """\
                            <!DOCTYPE html>
                            <html>
                            <body>
                                <div class="limit">
                                    <span style="font-size: 48px;left: 20px;font-weight:bold; font-family:Arial, Helvetica, sans-serif; color:#7048a9;">Budget Buddy!</span>
                                    <h3 style="font-size: 24px; font-family:serif">Dear """+ name+""", </h3>
                                    <div class="side" style="position:relative; left:100px;" >
                                        <div class="details"style="position:relative; top:20px; left:60px; font-size:20px; font-family:'Courier New', Courier, monospace;text-align:left; font-weight:bold;">
                                            <p style="color: red;">Your Monthly limit of """+ mn[da[1]] +""" has been Exceeded</p>
                                            <p>Limit  : <span style="color: green;"> %s </span> </p>
                                            <p>Expenses  : <span style="color: red;"> %s</span> </p>
                                            <p style=" color:#7048a9;">Please update your limit accordingly.....</p>
                                        </div>
                                    </div>
                                </div>
                            </body>
                            </html>"""%(mlimit,monthexp)
                    limitexceed(TEXT,email)     
                    c=1
                    cursor.connection.commit()
                if(fi>ex):
                    total = "%.2f"%(fi-ex)
                    total = "+ "+total
                elif(ex>fi):
                    total = "%.2f"%(ex-fi)
                    total = "- "+total
                else:
                    total=0
                if(count==1):
                    return render_template("addbudget.html",username=username,email=email,name=name,month=mn[da[1]],year=da[0],day=da[2],fincome=fi,fexpense=ex,incomes=inc,expenses=exp,finalamount=total,title="Add Budget")
                elif(count==0 and c==0):
                    return render_template("addbudget.html",username=username,email=email,name=name,month=mn[da[1]],year=da[0],day=da[2],fexpense=ex,fincome=fi,incomes=inc,expenses=exp,finalamount=total,title="Add Budget")
                else:
                    return render_template("addbudget.html",username=username,email=email,name=name,month=mn[da[1]],year=da[0],day=da[2],fexpense=ex,fincome=fi,incomes=inc,expenses=exp,finalamount=total,title="Add Budget")
            else:
                return render_template("addbudget.html",username=username,email=email,name=name,month=mn[da[1]],year=da[0],day=da[2],notice="You've not set monthly limit",title="Add Budget")

    else:
        return redirect(url_for('login'))    

@app.route('/mbudget')
def mbudget():
    if 'id' in session:
        name= session['name']
        username= session['username']
        email = session['email']
        return render_template("budgethistory.html",username=username,email=email,name=name,title="Manage Budget")
    else:
        return redirect(url_for('login'))    

@app.route('/history', methods=["POST","GET"])
def history():
    if 'id' in session:
        name= session['name']
        username= session['username']
        email = session['email']
        userid = session['id']
        msg=""
        mn = { '01':"January",
                '02':"February",
                '03':"March",
                '04':"April",
                '05':"May",
                '06':"June",
                '07':"July",
                '08':"August",
                '09':"September",
                '10':"October",
                '11':"November",
                '12':"December"}
        if request.method == "POST":
            date=request.form.get('date')+""
            da = date.split('-')
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM income WHERE date = % s and id = % s ",(date,userid))
            inc = cursor.fetchall()
            cursor.execute("SELECT * FROM expense WHERE date= % s and id = % s",(date,userid))
            exp = cursor.fetchall()
            cursor.connection.commit()
            if(not(inc) and not(exp)):
                msg="No Items Found...!"
            return render_template("budgethistory.html",username=username,email=email,name=name,income=inc,expense=exp,day=da[2],month=mn[da[1]],year=da[0],notify=msg,title="Manage Budget")
    else:
        return redirect(url_for('login'))    

@app.route('/remove/i<no>')
def removei(no):
    if 'id' in session:
        name= session['name']
        username= session['username']
        email = session['email']
        Tid = int(no)
        cursor= mysql.connection.cursor()
        cursor.execute("DELETE FROM income WHERE Tid = % s",(Tid,))
        cursor.connection.commit()
        return render_template("budgethistory.html",username=username,email=email,name=name,notify="Item Removed Successfully..!",title="Manage Budget")
    else:
        return redirect(url_for('login'))    

@app.route('/remove/e<no>')
def removee(no):
    if 'id' in session:
        name= session['name']
        username= session['username']
        email = session['email']
        Tid = int(no)
        cursor= mysql.connection.cursor()
        cursor.execute("DELETE FROM expense WHERE Tid = % s",(Tid,))
        cursor.connection.commit()
        return render_template("budgethistory.html",username=username,email=email,name=name,notify="Item Removed Successfully..!",title="Manage Budget")
    else:
        return redirect(url_for('login'))    

@app.route('/home')
def home():
    if 'id' in session: 
        name= session['name']
        username= session['username']
        email = session['email']
        sum=0
        userid = session['id']
        name= session['name']
        username= session['username']
        email = session['email']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM mlimit WHERE id = % s ORDER BY month DESC LIMIT 1",(userid,))
        dat = cursor.fetchone()
        if(dat):
            y = dat[2].strftime("%Y")
            m = dat[2].strftime("%m")
            month = dat[2].strftime("%B")
            str1 = y+"-"+m
            daa = str1+"%"
            cursor.execute("SELECT * FROM income WHERE id = % s AND date LIKE % s",(userid,daa))
            inc = cursor.fetchall()
            cursor.execute("SELECT * FROM expense WHERE id = % s AND date LIKE % s",(userid,daa))
            exp = cursor.fetchall()
            cursor.connection.commit()
            year = int(y)
            mon = int(m)
            labels = monthgen(mon,year)
            cursor.execute("SELECT * FROM income WHERE id = % s AND date LIKE % s",(userid,daa))
            incc = cursor.fetchall()
            x = []
            for i in incc:
                yea = i[2].strftime("%Y")
                mont = i[2].strftime("%m")
                day = i[2].strftime("%d")
                date = yea+"-"+mont+"-"+day
                x.append(date)
            xx = set(x)
            incomes = [0]*len(labels)
            xy = [0]*(len(labels)-len(xx))
            xxx = list(xx)
            xyy = xxx+xy
            for j in range(len(labels)):
                if labels[j] in xyy:
                   cursor.execute("SELECT * FROM income WHERE id = % s AND date = % s",(userid,labels[j]))
                   expp = cursor.fetchall()
                   sum = 0
                   for i in expp:
                       sum = sum + i[4]
                   incomes[j]=(sum)
                else:
                    incomes[j]=(0)
            sum=0
            cursor.execute("SELECT * FROM expense WHERE id = % s AND date LIKE % s",(userid,daa))
            expp = cursor.fetchall()
            x = []
            for i in expp:
                yea = i[2].strftime("%Y")
                mont = i[2].strftime("%m")
                day = i[2].strftime("%d")
                date = yea+"-"+mont+"-"+day
                x.append(date)
            xx = set(x)
            expenses = [0]*len(labels)
            xy = [0]*(len(labels)-len(xx))
            xxx = list(xx)
            xyy = xxx+xy
            for j in range(len(labels)):
                if labels[j] in xyy:
                   cursor.execute("SELECT * FROM expense WHERE id = % s AND date = % s",(userid,labels[j]))
                   expp = cursor.fetchall()
                   sum = 0
                   for i in expp:
                       sum = sum + i[4]
                   expenses[j]=(sum)
                else:
                    expenses[j]=(0)
            sum=0
            for i in inc:
                sum = sum+i[4]
            fi = sum
            sum = 0
            for j in exp:
                sum= sum+j[4]
            ex = sum
            avail = dat[3]-ex
            if(avail<0):
                alert='expensec'
            else:
                alert='incomec'
            return render_template("dashboard.html",username=username,email=email,name=name,month=month,year=y,totali=fi,totale=ex,monthlyl=dat[3],availl=avail,msg="Recent analytics of ",alert=alert,title="Dashboard",labels=labels,incomes=incomes,expenses=expenses)
        else:
            return render_template("dashboard.html",username=username,email=email,name=name,totali=0,totale=0,monthlyl=0,availl=0,msg="Welcome to Our Platform..!",title="Dashboard")
    else:
        return redirect(url_for('login'))
    
@app.route('/check',methods=["POST","GET"])
def check():
    if 'id' in session:
        name= session['name']
        username= session['username']
        email = session['email']
        sum=0
        userid = session['id']
        name= session['name']
        username= session['username']
        email = session['email']
        m = request.form.get('month')+'-01'
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM mlimit WHERE id = % s and month = % s",(userid,m))
        dat = cursor.fetchone()
        if(dat):
            y = dat[2].strftime("%Y")
            m = dat[2].strftime("%m")
            month = dat[2].strftime("%B")
            str1 = y+"-"+m
            daa = str1+"%"
            cursor.execute("SELECT * FROM income WHERE id = % s AND date LIKE % s",(userid,daa))
            inc = cursor.fetchall()
            cursor.execute("SELECT * FROM expense WHERE id = % s AND date LIKE % s",(userid,daa))
            exp = cursor.fetchall()
            cursor.connection.commit()
            year = int(y)
            mon = int(m)
            labels = monthgen(mon,year)
            cursor.execute("SELECT * FROM income WHERE id = % s AND date LIKE % s",(userid,daa))
            incc = cursor.fetchall()
            x = []
            for i in incc:
                yea = i[2].strftime("%Y")
                mont = i[2].strftime("%m")
                day = i[2].strftime("%d")
                date = yea+"-"+mont+"-"+day
                x.append(date)
            xx = set(x)
            incomes = [0]*len(labels)
            xy = [0]*(len(labels)-len(xx))
            xxx = list(xx)
            xyy = xxx+xy
            for j in range(len(labels)):
                if labels[j] in xyy:
                   cursor.execute("SELECT * FROM income WHERE id = % s AND date = % s",(userid,labels[j]))
                   expp = cursor.fetchall()
                   sum = 0
                   for i in expp:
                       sum = sum + i[4]
                   incomes[j]=(sum)
                else:
                    incomes[j]=(0)
            sum=0
            cursor.execute("SELECT * FROM expense WHERE id = % s AND date LIKE % s",(userid,daa))
            expp = cursor.fetchall()
            x = []
            for i in expp:
                yea = i[2].strftime("%Y")
                mont = i[2].strftime("%m")
                day = i[2].strftime("%d")
                date = yea+"-"+mont+"-"+day
                x.append(date)
            xx = set(x)
            expenses = [0]*len(labels)
            xy = [0]*(len(labels)-len(xx))
            xxx = list(xx)
            xyy = xxx+xy
            for j in range(len(labels)):
                if labels[j] in xyy:
                   cursor.execute("SELECT * FROM expense WHERE id = % s AND date = % s",(userid,labels[j]))
                   expp = cursor.fetchall()
                   sum = 0
                   for i in expp:
                       sum = sum + i[4]
                   expenses[j]=(sum)
                else:
                    expenses[j]=(0)
            sum=0
            for i in inc:
                sum = sum+i[4]
            fi = sum
            sum = 0
            for j in exp:
                sum= sum+j[4]
            ex = sum
            avail = dat[3]-ex
            if(avail<0):
                alert='expensec'
            else:
                alert='incomec'
            return render_template("dashboard.html",username=username,email=email,name=name,month=month,year=y,totali=fi,totale=ex,monthlyl=dat[3],availl=avail,msg="Recent analytics of ",alert=alert,title="Dashboard",labels=labels,incomes=incomes,expenses=expenses)
        else:
            return render_template("dashboard.html",username=username,email=email,name=name,totali=0,totale=0,monthlyl=0,availl=0,title="Dashboard")
    else:
        return redirect(url_for('login'))
    
@app.route('/logout')
def logout():
    if 'id' in session:
        session.pop('id',None)
        session.pop('username',None)
        session.pop('email',None)
        session.pop('name',None)
        return redirect(url_for('homepage'))
    
if(__name__ == '__main__'):
    app.run(host="0.0.0.0",port=8080)
