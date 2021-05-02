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
	# print(global_current_user)
	con = sql.connect('database.db')
	cur=con.cursor()
	# print("getting till 1")
	# cur.execute("CREATE TABLE IF NOT EXISTS " + str(global_current_user))
	cur.execute("SELECT * FROM " + str(global_current_user))
	# print("getting till 2")
	data = cur.fetchall()
	print(data)
	con.commit()
	con.close()
	return data
	# return render_template('welcome.html')


@app.route('/')
def homepage():
	global global_first
	global global_current_user
	if global_first:
		session.clear()
		# print("Destination reached")
		global_first = False
	if 'username' in session:
		session.clear()
		# global_current_user=session['username']
		# data = render_welcome()
		# return render_template("welcome.html",data=data)
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
			# print("CHECK")
			con=sql.connect("database.db")
			cur = con.cursor()
			val=None
			cur.execute("SELECT * FROM users WHERE name = ?", (name,))
			val=cur.fetchone()
			print(val)
			# error=None
			if val[0] == None or val[1] != password:
				# error="Username and Password don't match"
				print("problem")
				return render_template("index.html")
			else:	
				global global_current_user
				print("###")
				print(name)
				session['username']=name
				global_current_user=name
				print("Logged in")
				global global_file_upload
				data = None
				print(data)
				if global_file_upload:
					data = render_welcome()
					return render_template("welcome.html",data=data)
				# render_welcome()
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
	# global global_rand
	global global_pass
	# global global_email
	global_name=request.form['Name']
	# global_email=request.form['ID']
	global_pass=request.form['Password1']
	pass2=request.form['Password2']
	error=None
	try:
		con=sql.connect("database.db")
		cur = con.cursor()
		val=None
		# val2=None
		cur.execute("SELECT * FROM users WHERE Name = ?", (global_name,))
		# print("Working till here")
		# print("not working here")
		# conn.execute('CREATE TABLE users (Name TEXT, Password REAL)')
		val=cur.fetchone()
		con.close()
		# cur.execute("SELECT * FROM users WHERE Email = ?", (global_email,))
		# val2=cur.fetchone()
		if global_name == "users":
			# error="Username cannot be users."
			return render_template("signup.html")
		elif val!=None:
			# error="Username already taken.Given Email ID already has an associated account."
			return render_template("signup.html")
		# elif val!=None:
			# error="Username already taken."
			# return render_template("signup.html",error=error)
		# elif val2!=None:
			# error="Given Email ID already has an associated account."
			# return render_template("signup.html",error=error)	
		elif global_pass != pass2:
			# error="Passwords do not match."
			return render_template("signup.html")
		elif global_pass == "":
			# error="Password cannot be blank"
			return render_template("signup.html")
		# elif global_email[len(global_email)-10:len(global_email)] != "@gmail.com":
			# error="Not a valid Gmail ID"
			# return render_template("signup.html",error=error)
		elif global_name == "":
			# error="Username cannot be blank!"
			return render_template("signup.html")	
		else:
			con=sql.connect("database.db")
			cur = con.cursor()	
			cur.execute("INSERT INTO users (Name,Password)	VALUES (?,?)",(global_name,global_pass))
			# con.execute("CREATE TABLE " + str(global_name) + "(userId INT, id INT, title TEXT, body TEXT)")
			# cur.execute("INSERT INTO " + str(global_name) + " (userId, id, title, body)	VALUES (?,?,?,?)",(1,1,"bleh","bleh"))
			con.commit()
			con.close()
			# print(global_name)
			# print("Added everything")
			return redirect(url_for('homepage'))		
			# return render_template("verification.html",check=None,email=global_email)	
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
		# if file.filename == '':
			# flash('No selected file')
			# return render_template("welcome.html")
		file = request.files['file']
		# if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		# print(filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		# flash('File uploaded')
		render_data(filename)
		data = render_welcome()
		return render_template("welcome.html",data=data)
		# return render_template("welcome.html")

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
