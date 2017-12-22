

from    flask   import  Flask, flash, redirect, render_template, request, session, abort
from    flask_restful   import  Resource,Api,reqparse
from    flaskext.mysql import   MySQL
from    flask_uploads   import  UploadSet, configure_uploads, IMAGES
from    random import randint
import datetime

now=datetime.datetime.now()
app=Flask(__name__,static_url_path="/static")
app.secret_key='ironman'
api=Api(app)
mysql=MySQL()
photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = 'static/users'
configure_uploads(app, photos)

app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='db1'
app.config['MYSQL_DATABASE_HOST']='localhost'
mysql.init_app(app)



@app.route("/register")
def register():
    return render_template("register.html")
@app.route("/login")
def login():
    return render_template("login.html")
@app.route("/")
def home():
    conn=mysql.connect()
    cursor=conn.cursor()
    post_stmt=("SELECT * FROM posts")
    
    cursor.execute(post_stmt)

    posts=cursor.fetchall()
    postli=[]
    for i in posts:
                    view_img=("SELECT imagename FROM imgtbl WHERE pid=%s")
                    id=i[2]
                    usrid=i[0]
                    get_name=("SELECT name FROM user WHERE id=%s")
                    get_data=(usrid)
                    cursor.execute(get_name,get_data)
                    name=cursor.fetchone()
                    uname=str(name)
                    uname=uname[2:-3]
                    view_data2=(id)
                    cursor.execute(view_img,view_data2)
                    img=cursor.fetchone()
                    pth='/static/posts/'
                    nm=str(img)
                    nm=nm[2:-3]
                    postdict={
                    
                    'name':uname,
                    'text':i[1],
                    'date':i[3],
                    
                    'imagepath':pth,
                    'imagename':nm
                    }
                    postli.append(postdict)

    
    return render_template('home.html',**locals())
   
def idgen():
    try:
            conn=mysql.connect()
            cursor=conn.cursor()
    except Exception as e:
            return{'error':str(e)} 

    id=randint(0, 1000)
    select_stmt=("SELECT * FROM user WHERE id=%s")
    select_data=(id)
              
    cursor.execute(select_stmt,select_data)
          
    data=cursor.fetchall()
    if len(data) is 0:
            return id
    else:
            return idgen()

def idgen2():
    try:
            conn=mysql.connect()
            cursor=conn.cursor()
    except Exception as e:
            return{'error':str(e)} 

    id=randint(0, 1000)
    select_stmt=("SELECT * FROM posts WHERE pid=%s")
    select_data=(id)
           
    cursor.execute(select_stmt,select_data)
           
    data=cursor.fetchall()
    if len(data) is 0:
            return id
    else:
            return idgen()







    
@app.route('/Insert_user',methods=['POST'])
def Insert_user():
    if request.method == 'POST' and 'photo' in request.files:
            filename = photos.save(request.files['photo'])

    else:
        pid=0
        message="profile not uploaded"
        return render_template('/diag_res.html',**locals())        
    _userName=request.form['name']
    _userPassword=request.form['password']
    _userEmail=request.form['email']
   
    i=idgen()
    conn=mysql.connect()
    cursor=conn.cursor()
    check_stmt=("SELECT * FROM user WHERE name=%s")
    check_data=(_userName)
    cursor.execute(check_stmt,check_data)
    checkd=cursor.fetchall()
    if len(checkd)>0:
        return render_template('/diag_res.html',message='name already exists')
    else:    
            insert_stmt=("INSERT INTO user VALUES (%s,%s,%s,%s)")
            insert_data=(_userEmail,_userName,i,_userPassword)
           
            cursor.execute(insert_stmt,insert_data)
           
            data=cursor.fetchall()

           
            
            try:
                img_ins=("INSERT INTO imgtbl VALUES (%s,%s,%s,%s)")
                img_data=(i,'-1','/static/users/',filename)
                cursor.execute(img_ins,img_data)

            except Exception as e:
                message=e
                return render_template('/diag_res.html',**locals())      

            if len(data) is 0:
                conn.commit()
                imgpath='/static/users/'+filename
                conn=mysql.connect()
                cursor=conn.cursor()
                view_stmt=("SELECT * FROM user WHERE password=%s AND name=%s")
                view_data=(_userPassword,_userName)
                cursor.execute(view_stmt,view_data)
                data=cursor.fetchall()
                uemail=data[0][0]
                uname=data[0][1]
                upswd=data[0][3]
                uid=data[0][2]
                  
                return render_template('view.html',**locals())

            else:
                return{'status':'failure','msf':str(data[0])}










@app.route('/Show',methods=['POST'])
def Show():
    _userName=request.form['name']
    _userPassword=request.form['password']
    conn=mysql.connect()
    cursor=conn.cursor()
    view_stmt=("SELECT * FROM user WHERE password=%s AND Name=%s")
    view_data=(_userPassword,_userName)
    cursor.execute(view_stmt,view_data)
    data=cursor.fetchall()
    if len(data) is 0:
        pid=0
        message="login failed! try again"
        return render_template('login_fail.html',**locals())
    else:    
        uid=data[0][2]
    

        view_img=("SELECT * FROM imgtbl WHERE id=%s")
        view_idata=(uid)
        cursor.execute(view_img,view_idata)

        img=cursor.fetchall()

    imgpath=(img[0][2]+img[0][3])
    uemail=data[0][0]
    uname=data[0][1]
    upswd=data[0][3]
    uid=data[0][2]
    post_stmt=("SELECT * FROM posts WHERE uid=%s")
    post_data=(uid)
    cursor.execute(post_stmt,post_data)

    posts=cursor.fetchall()
    postli=[]
    for i in posts:
                    view_img=("SELECT imagename FROM imgtbl WHERE pid=%s")
                    id=i[2]
                    view_data2=(id)
                    cursor.execute(view_img,view_data2)
                    img=cursor.fetchone()
                    pth='/static/posts/'
                    nm=str(img)
                    nm=nm[2:-3]
                    postdict={
                    
                    'name':uname,
                    'text':i[1],
                    'date':i[3],
                    
                    'imagepath':pth,
                    'imagename':nm
                    }
                    postli.append(postdict)

    
    return render_template('view.html',**locals())



@app.route('/new_post',methods=['POST'])
def new_post():

    photos = UploadSet('photos', IMAGES)
    app.config['UPLOADED_PHOTOS_DEST'] = 'static/posts'
    configure_uploads(app, photos)
    if request.method == 'POST' and 'photo' in request.files:
            filename = photos.save(request.files['photo'])
            conn=mysql.connect()
            cursor=conn.cursor()
            nameee=request.form['neme']
            paws=request.form['pwd']
            uid=request.form['id']
            text=request.form['text']
            i=idgen2()
            ins_stmtlab=("INSERT INTO posts VALUES (%s,%s,%s,%s)")
            ins_datalab=(uid,text,i,now.strftime("%Y/%m/%d"))
            cursor.execute(ins_stmtlab,ins_datalab)
            data=cursor.fetchall()
            conn.commit()
            try:
                img_ins=("INSERT INTO imgtbl VALUES (%s,%s,%s,%s)")
                img_data=(uid,i,'/static/posts/',filename)
                cursor.execute(img_ins,img_data)
                conn.commit()
            except Exception as e:
                message=e
                return message     

            if len(data) is 0:
                    message="Posted"
                    return render_template('/posted.html',**locals())

    else:
        
            conn=mysql.connect()
            cursor=conn.cursor()
            uid=request.form['id']
            text=request.form['text']
            i=idgen2()
            ins_stmtlab=("INSERT INTO posts VALUES (%s,%s,%s,%s)")
            ins_datalab=(uid,text,i,now.strftime("%Y/%m/%d"))
            cursor.execute(ins_stmtlab,ins_datalab)
            data=cursor.fetchall()
            conn.commit()
            if len(data) is 0:
                    message="Posted"
                    return render_template('/diag_res.html',**locals())
            else:
                    message="error"
                    return render_template('/diag_res.html',**locals())        


            


if __name__=='__main__':
    app.run(host='0.0.0.0',port=80,debug=True)
                
         