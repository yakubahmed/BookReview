import os

from flask import Flask, session, render_template, request, redirect, url_for, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests
from helpers import login_required

from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/img'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Set up database
engine = create_engine('postgresql://postgres:Me.Yakub@localhost:5432/coding_news')
db = scoped_session(sessionmaker(bind=engine))

app = Flask(__name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/', methods=['POST','GET'])
def index():
    post = db.execute('select * from tbl_post_view by(post_id)  order by(post_id) DESC').fetchall()
    top_5_post = db.execute("select * from tbl_post_view order by(post_id) DESC LIMIT 5").fetchall()
    if request.method == "POST":
        sval = request.form.get('searchval')
        post = db.execute("select * from tbl_post_view where post_title like :ptitle or\
             post_content like :pcontent or createdby like :user or category_name like :cname "\
            ,{"ptitle": '%' + sval +'%', "ptitle": '%' + sval + '%', "pcontent":'%' + sval + '%' \
             ,"user": '%' + sval + '%', "cname": '%' + sval + '%'}).fetchall()
    return render_template('index.html',posts=post, top5p=top_5_post)
    

    return render_template('index.html',posts=post, top5p=top_5_post)

@app.route('/view/<int:pid>')
def post_view(pid):
    post = db.execute('select * from tbl_post_view where post_id=:pid', {"pid":pid}).fetchall()

    rel_post = db.execute(' select * from tbl_post where  cat_id in (select cat_id from tbl_post_category) LIMIT 5', {"pid":pid}).fetchall()
    return render_template('single-page.html',posts=post, rel_posts=rel_post)

@app.route('/admin/categories', methods=['POST','GET'])
@login_required
def categories():
    categories = db.execute('select * from tbl_post_category').fetchall()

    if request.method == "POST":
        category_name = request.form.get('cname')

        category = db.execute('select * from tbl_post_category where category_name=:cname',{"cname":category_name}).fetchone()
        if category is not None:
            return render_template('categories.html', msg="SORRY!, that category is found please try another one", style="danger")

        if db.execute('INSERT INTO tbl_post_category (category_name) VALUES (:cname)', {"cname":category_name}):
            db.commit()
            flash("Category created successfully")
            return redirect(url_for('categories'))
        else:
            return render_template('categories.html', msg="Something is wrong please try again")
    return render_template('categories.html', style="", c=categories)

@app.route('/admin/category/delete/<int:id>')
@login_required
def del_category(id):
    if db.execute('delete from tbl_post_category where cat_id=:uid ', {'uid':id}):
        db.commit()
        flash("category deleted succesfully")
        return redirect(url_for('categories'))

@app.route('/admin/post/delete/<int:pid>')
@login_required
def del_post(pid):
    if db.execute('delete from tbl_post where post_id=:pid ', {'pid':pid}):
        db.commit()
        flash("Post deleted succesfully")
        return redirect(url_for('manage_post'))

@app.route('/admin/language/delete/<int:id>')
@login_required
def del_lang(id):
    if db.execute('delete from tbl_langauges where lang_id=:uid ', {'uid':id}):
        db.commit()
        flash('Language deleted successfully')
        return redirect(url_for('addlangauge'))

@app.route('/admin/category/update/<int:id>',methods=['POST','GET'])
@login_required
def update_category(id):

    c = db.execute('select * from tbl_post_category where cat_id=:cid',{"cid":id}).fetchone()
    

    cname = request.form.get('cname')
    if request.method == "POST":
        if db.execute('Update tbl_post_category SET category_name=:cname where cat_id=:uid ', {'uid':id,"cname":cname}):
            db.commit()
            flash("category updated successfully")
            return redirect(url_for('categories'))
    return render_template('edit-category.html', c=c, id=id)

@app.route('/admin/language/update/<int:id>',methods=['POST','GET'])
@login_required
def update_lang(id):

    langs = db.execute('select * from tbl_langauges where lang_id=:lid',{"lid":id}).fetchone()
    
    position = request.form.get('position')
    rate = request.form.get('rating')
    lang = request.form.get('lang')

    if request.method == 'POST':
        if db.execute("UPDATE tbl_langauges SET position=:position, lang_name=:lname, rating=:rat where lang_id=:id",\
                 {"position":position, "lname":lang,"rat":rate, 'id':id}):
            db.commit()
            flash("Upated successfully")
            return redirect(url_for('addlangauge'))
        return render_template('edit-language.html',msg="Failed to update")

    return render_template('edit-language.html', lan=langs, id=id)

@app.route('/admin/post/update/<int:id>',methods=['POST','GET'])
def update_post(id):

    cid = request.form.get("cat_id")
    ptitle = request.form.get("ptitle")

    pcontent = request.form.get('pcontent')
    
    category = db.execute('select * from tbl_post_category').fetchall()
    post = db.execute("select * from tbl_post where post_id =:pid",{"pid":id}).fetchone()
    if request.method == "POST":
        pimage = request.files['pimage']
        
        if db.execute("UPDATE tbl_post SET post_title =:ptitle, cat_id =:cid, post_content =:pcontent, \
            post_image =:pimage where post_id=:pid",{"ptitle":ptitle,"cid":cid,"pcontent":pcontent, "pimage":pimage.filename, "pid":id}):
            db.commit()
            file = request.files['pimage']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                flash('Post Updated successfully!')
                return redirect(url_for('manage_post'))
            return render_template('edit-post.html',msg="Only image with jpg, jpeg, png extensions are allowed")

    return render_template('edit-post.html',   p=post, id=id, categ=category)

@app.route('/languages')
def languages():
    lang = db.execute('select * from tbl_langauges').fetchall()
    return render_template('languages.html', languages=lang)

@app.route('/admin/login', methods=['POST','GET'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    if request.method == "POST":
        user = db.execute('select * from tbl_user where email=:email and password =:password',{'email': email, "password":password}).fetchone()
        if not user:
            return render_template('login.html', msg="Invalid username or password")
        else:
            session['user_id'] = user['user_id']
            session['full_name'] = user['full_name']
            return redirect(url_for('home'))
    return render_template('login.html')


@app.route('/admin/')
@login_required
def home():
    return render_template('admin-home.html')

@app.route('/admin/user/new', methods=['POST','GET'])
def newuser():
    fullname = request.form.get('fname')
    email = request.form.get('email')
    password = request.form.get('password')
    cpassword  = request.form.get('cpassword')
    mail = db.execute("select * from tbl_user where email =:email", {"email": email}).fetchone()
    if not mail is None :
        return render_template('users.html', dangere="danger", msg="The email that you entered is allready taken please try another one")
    if password !=  cpassword :
        return render_template('users.html', msg="Both password does't match", dangerp="danger", dangere="success")
    if db.execute("INSERT INTO tbl_user (full_name, email, password) Values(:fname,:mail,:pwd)", {"fname":fullname, "mail":email, "pwd":password}):
        db.commit()
        flash("User created successfully")
        return redirect(url_for('users'))
    else :
        return render_template('users.html', msg="Something is wrong please try again")

        

    return render_template('users.html')

@app.route('/admin/users')
@login_required
def users():
    users = db.execute('select * from tbl_user').fetchall()

    return render_template('users.html', users=users)


@app.route('/admin/users/delete/<int:id>')
@login_required
def del_user(id):
    if id == session['user_id']:
        return render_template('error.html' , msg = "you can't delete your self")
    if db.execute('delete from tbl_user where user_id=:uid ', {'uid':id}):
        db.commit()
        return redirect(url_for('users'))

@app.route('/admin/add-post', methods=['POST', 'GET'])
@login_required
def addpost():
    post_cat = db.execute("SELECT * from tbl_post_category").fetchall()
    if request.method == "POST":
        cat_id = request.form.get('cat_id')
        post_content = request.form.get('pcontent')

        post_title = request.form.get('ptitle')
        fname =  session['full_name']
        pimage = request.files['pimage']
        image = request.form.get('pimage')
        if db.execute("INSERT INTO tbl_post (post_title,post_image,post_content,cat_id,createdby) VALUES (:ptitle,:pimage,:pcontent,:cid,:user)",{"ptitle":post_title, "pimage":pimage.filename, "pcontent":post_content, "cid":cat_id,"user":fname}):
            db.commit()
            file = request.files['pimage']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                flash('Post added successfully!')
                return redirect(url_for('addpost'))
            return render_template('add-post.html',msg="The file format that you have enter is not allowed,only png,jpg,jpeg  are allowed")

            return render_template('add-post.html',msg="Successfully added")
        return render_template('add-post.html',msg="Failed added")
        
    return render_template('add-post.html',postcat=post_cat)

@app.route('/admin/add-language', methods=['POST','GET'])
@login_required
def addlangauge():
    position = request.form.get('position')
    lang = request.form.get('lang')
    rate = request.form.get('rating')

    language = db.execute("select * from tbl_langauges order by(position) ASC ").fetchall()

    if request.method == "POST":
        if db.execute('INSERT INTO tbl_langauges (Position,lang_name, rating ) VALUES (:position,:lang,:rating) ', {"position":position,"lang":lang,"rating":rate}):
            db.commit()
            flash("langauge added successfully")
            return redirect(url_for('addlangauge')) 
        return render_template('add-language.html',msg="Something went is wrong try again")
    return render_template('add-language.html', language=language)

@app.route('/admin/post/list')
@login_required
def manage_post():
    post = db.execute('select * from tbl_post_view').fetchall()
    return render_template('manage-post.html',posts=post)

@app.route("/logout")
@login_required
def logout():
    session.pop("user_id",None)
    session.pop("full_name",None)
    return redirect(url_for('login'))




if __name__ == "__main__":
    app.secret_key = "coding_newss"
    app.run(debug=True, port=8000)