from flask import Flask, redirect, url_for, request, render_template, session, flash
from flask_mail import Mail, Message
import sqlite3 as sql
from random import randint
import sys, os, math
from werkzeug.utils import secure_filename
import pandas as pd
import json

app=Flask(__name__)
app.secret_key = 'any random string'
UPLOAD_FOLDER = './'
ALLOWED_EXTENSIONS = {'json'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# conn = sql.connect('database.db')
# curr=conn.cursor()
# conn.execute('CREATE TABLE users (Name TEXT, Password REAL)')
# curr.execute("INSERT INTO  users (Name, Password) VALUES (?,?)",("","",))
# conn.commit()
# conn.close()

global_name=""
global_pass = ""
global_current_user = ""
global_first = True
global_file_upload = False

def render_welcome():
	global global_current_user
	con = sql.connect('database.db')
	cur=con.cursor()
	cursor = con.execute("SELECT * FROM " + str(global_current_user))
	cur.execute("SELECT * FROM " + str(global_current_user))
	data = cur.fetchall()
	lis = []
	for item in cursor.description:
		lis.append(item[0])
	con.commit()
	con.close()
	return data,lis


@app.route('/')
def homepage():
	global global_first
	global global_current_user
	if global_first:
		session.clear()
		global_first = False
	if 'username' in session:
		session.clear()
	return render_template('index.html')

@app.route('/returntohome',methods=['POST'])
def returntohome():
	return redirect(url_for('homepage'))

@app.route('/login',methods=['POST'])
def result():
	try:
		if request.method=='POST':
			name=request.form['ID']
			password=request.form['Password']
			con=sql.connect("database.db")
			cur = con.cursor()
			val=None
			cur.execute("SELECT * FROM users WHERE name = ?", (name,))
			val=cur.fetchone()
			if val[0] == None or val[1] != password:
				return render_template("index.html")
			else:	
				global global_current_user
				session['username']=name
				global_current_user=name
				global global_file_upload
				data = None
				if global_file_upload:
					data,headers = render_welcome()
					return render_template("welcome.html",data=data,headers=headers[1:])
				else:
					return render_template("welcome.html")
			con.close()	
	except:
		con.rollback()

@app.route('/sign_up',methods=['POST'])
def Signup():
	return render_template("signup.html",error=None)

@app.route('/commit_details',methods=['POST'])
def commit_details():
	global global_name
	global global_pass
	global_name=request.form['Name']
	global_pass=request.form['Password1']
	pass2=request.form['Password2']
	error=None
	try:
		con=sql.connect("database.db")
		cur = con.cursor()
		val=None
		cur.execute("SELECT * FROM users WHERE Name = ?", (global_name,))
		val=cur.fetchone()
		con.close()
		if global_name == "users":
			return render_template("signup.html")
		elif val!=None:
			return render_template("signup.html")
		elif global_pass != pass2:
			return render_template("signup.html")
		elif global_pass == "":
			return render_template("signup.html")
		elif global_name == "":
			return render_template("signup.html")	
		else:
			con=sql.connect("database.db")
			cur = con.cursor()	
			cur.execute("INSERT INTO users (Name,Password)	VALUES (?,?)",(global_name,global_pass))
			con.commit()
			con.close()
			return redirect(url_for('homepage'))		
	except:
		con.rollback()	

@app.route('/logout',methods=['POST'])
def logout():
	session.pop('username','None')
	return redirect(url_for('homepage'))


@app.route('/upload',methods=['POST'])	
def upload():
	if request.method == 'POST':
		if 'file' not in request.files:
			flash('No file part')
			return render_template("welcome.html")
		file = request.files['file']
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		render_data(filename)
		data,headers = render_welcome()
		return render_template("welcome.html",data=data,headers=headers[1:])

def render_data(filename):
	global global_current_user
	global global_file_upload
	global_file_upload = True
	with open(filename) as f:
		data = json.load(f)
	df = pd.DataFrame(data)	
	conn = sql.connect('database.db')
	curr=conn.cursor()
	df.to_sql(global_current_user,conn)
	conn.commit()
	conn.close()


if __name__ == '__main__':
	app.run()
