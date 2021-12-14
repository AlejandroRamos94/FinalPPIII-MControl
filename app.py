import sys, subprocess
from flask import Flask, request,render_template, redirect, url_for, send_from_directory
from flask import session as login_session
from flask_socketio import SocketIO, send, emit
from sqlalchemy.sql.expression import null, true
from pw_hashData import login_required, make_salt, make_pw_hash, valid_pw
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dbtables import Base, User, Paths
import random
import string
import hashlib
import os, json
from tinytag import TinyTag

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Connect to Database and create database session
engine = create_engine('postgresql://alermpp:ramoscpii@localhost/usuarios')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

"""
audio = TinyTag.get("/home/alejandro/Proyectos/Practica_Profesional_III/Final/music/Lonely Day.mp3")
  
print("Title:" + audio.title)"""
# --------------------------------------PASSWORD HASH------------------------------[OK]
"""
def login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if 'username' not in login_session:
			return redirect(url_for('login'))
		return f(*args, **kwargs)
	return decorated_function

def make_salt():
	return ''.join(random.choice(
				string.ascii_uppercase + string.digits) for x in range(32))
		
def make_pw_hash(name, pw, salt = None):
	if not salt:
		salt = make_salt()
	h = hashlib.sha256((name + pw + salt).encode('utf-8')).hexdigest()
	return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
	salt = h.split(',')[0]
	return h == make_pw_hash(name, password, salt)
"""

#-----------------------------INICIAR SESION----------------------[OK]

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'GET':
		state = ''.join(random.choice(
				string.ascii_uppercase + string.digits) for x in range(32))
		# store it in session for later use
		login_session['state'] = state
		return render_template('login.html', STATE = state)
	else:
		if request.method == 'POST':
			#print ("dentro de POST login")
			user = session.query(User).filter_by(
				username = request.form['username']).first()

			if user and valid_pw(request.form['username'],
								request.form['password'],
								user.pw_hash):
			
				login_session['username'] = request.form['username']
				return redirect(url_for('firstPage', ida = user.id))

			else:
				error = "Usuario o clave incorrecta"
				return render_template('login.html', error = error)

@app.route('/controLogin', methods=['GET', 'POST'])
def contrologin():
	if request.method == 'GET':
		state = ''.join(random.choice(
				string.ascii_uppercase + string.digits) for x in range(32))
		# store it in session for later use
		login_session['state'] = state
		return render_template('loginControl.html', STATE = state)
	else:
		if request.method == 'POST':
			#print ("dentro de POST login")
			user = session.query(User).filter_by(
				username = request.form['username']).first()

			if user and valid_pw(request.form['username'],
								request.form['password'],
								user.pw_hash):
			
				login_session['username'] = request.form['username']
				return redirect(url_for('control', ida = user.id))

			else:
				error = "Usuario o clave incorrecta"
				return render_template('loginControl.html', error = error)


#------------------------------REGISTRAR USUARIO--------------------[OK]

@app.route('/register', methods=['GET', 'POST'])
def registrar():
	if request.method == 'GET':
		return render_template('register.html')
	else:
		if request.method == 'POST':
			username = request.form['username']
			password=request.form['password']
			email = request.form['email']
			pw_hash = make_pw_hash(username, password)
			nuevoUsuario = User(
					username = username,
					email = email,
					pw_hash=pw_hash) 
			session.add(nuevoUsuario)
			session.commit()
			login_session['username'] = request.form['username']
			return redirect(url_for('firstPage'))

@app.route('/logout')
def logout():
	if 'username' in login_session:
		del login_session['username']
		return redirect(url_for('firstPage'))
	else:
		return redirect(url_for('firstPage'))

'''

exa = session.query(Paths).filter_by(id=3).first()
print(exa.id, exa.directorio, exa.usuarioId)
'''

@app.route('/configs/<int:id>', methods=['GET', 'POST'])
def configs(id):
	if 'username' in login_session:
		username = login_session['username']
		correo = session.query(User).filter_by(id = id).first()
		correo = correo.email
		errormensaje = "Error al validar las contraseñas"
		rutadir = session.query(Paths).filter_by(usuarioId = id).first()
		
		
		if request.method == 'GET':	
			if rutadir is None:
				return render_template('configs.html', username=username, errormensaje=errormensaje, email=correo, id=id)

			else:
				rutadir = rutadir.directorio
			mail = session.query(User).filter_by(id = id).first()
			mail = mail.email
			return render_template('configs.html', username=username, email=correo, rutadir=rutadir, id=id)
		if request.method == 'POST':
			if request.form.get('guardarbtn'):
			
				users = request.form['nombreUsuario']
				passw = request.form['passwordnew']
				mail = request.form['mail']
				user = session.query(User).filter_by(id = id).first()
				if user and valid_pw(request.form['nombreUsuario'],
										request.form['password'],
										user.pw_hash):
					if request.form['passwordnew'] != request.form['passwordrepeat']:
						return render_template('configs.html', username=username, errormensaje = errormensaje, email=correo, id=id)
						
					else:
						pw_hash = make_pw_hash(users, passw)
						session.query(User).filter_by(id=id).update(dict(username=users,pw_hash=pw_hash, email=mail))
						session.commit()
						del login_session['username']
						return redirect(url_for('login'))
				else:
					return render_template('configs.html', username=username, errormensaje=errormensaje, email=correo, id=id)

@app.route('/directorios', methods=['GET', 'POST'])
def newdirectorios():
	if 'username' in login_session:
		username = login_session['username']
		current_working_directory=os.getcwd()
		if request.method == 'GET':
			if 'win32' in sys.platform or 'win64' in sys.platform:
				file_list=subprocess.check_output('dir', shell=True).decode('utf-8').split('\n') # use 'dir' command on Windows
			else:
				file_list=subprocess.check_output('ls', shell=True).decode('utf-8').split('\n') # use 'dir' command on Windows
				return render_template('firstdirectorios.html', username=username, file_list=file_list, current_working_directory=current_working_directory)
		if request.method == 'POST':
			currentuser = session.query(User).filter_by(username=username).first()
			idUsuario = currentuser.id
			guardarPath = request.form['directorio']
			
			enviarDatos = Paths(
				directorio = guardarPath,
				usuarioId = idUsuario)
			session.add(enviarDatos)
			session.commit()
			return redirect(url_for('firstPage'))

@app.route('/', methods=['GET', 'POST'])
#@app.route('/principal/', methods=['GET','POST'])
def firstPage():
	if 'username' in login_session:	
		username = login_session['username']
		id_user = session.query(User).filter_by(username=username).first()
		id_user = id_user.id
		listJson = []	
		itemsongs = []
		items = session.query(Paths).filter_by(usuarioId=id_user).first()

		
		if request.method == 'GET':
			if items is None:
				return render_template('player.html', username=username, id_user=id_user, newmsg="No hay musica en este directorio")
			else:
				id_con = items.id
				CarpetPath = items.directorio
				items = os.listdir(CarpetPath)		
				items.sort()
			for file in items:
				if(file.endswith(".mp3")) or (file.endswith(".m4a")):
					itemsongs.append(file)

			else: 
				for x in itemsongs:
					audio = TinyTag.get(CarpetPath + "/" + x)
					dictionaryDataSongs = {
							"cancion" : x,
							"titulo" : audio.title,
							"album" : audio.album,
							"artista" : audio.artist
						}
					if dictionaryDataSongs["titulo"] == "" or not dictionaryDataSongs["titulo"]:
						dictionaryDataSongs.update({"titulo": x})
					if dictionaryDataSongs["album"] == "" or not dictionaryDataSongs["album"]:
						dictionaryDataSongs.update({"album": "Album desconocido"})
					if dictionaryDataSongs["artista"] == "" or not dictionaryDataSongs["artista"]:
						dictionaryDataSongs.update({"artista": "Artista desconocido"})
					listJson.append(dictionaryDataSongs)
				variable = 0
				basedir = os.path.abspath(os.path.dirname(__file__))
				file_path = os.path.join(basedir,'static','js', 'songList.js')
				if listJson:
					print("lleno")
					variable = True
				else:
					print("vacio")
					variable = False
				if variable == True:	
					with open(file_path,'w') as file:
						file.write('var listSongs = ')
						file.close()
					with open(file_path,'a') as file:
						json.dump(listJson, file, indent=4)
						file.close()
					return render_template('player.html', username=username, id_user=id_user)
				else:
					return render_template('player.html', username=username, id_user=id_user, messje="No hay musica en este directorio")

	else:
		return redirect(url_for("login"))



@app.route('/control', methods=['GET', 'POST'])
def control():
	if 'username' in login_session:
		username = login_session['username']
		return render_template('playerControl.html', username=username)

@app.route('/listacanciones', methods=['GET', 'POST'])
def listacanciones():
	if 'username' in login_session:
		username = login_session['username']
		return render_template('listacanciones.html', username=username)
	


@app.route('/canciones', methods=['GET', 'POST'])
def canciones():
	if 'username' in login_session:
		username = login_session['username']
		return render_template('canciones.html', username=username)

@app.route('/playMusic/<path:filename>')
def songRender(filename):
	if 'username' in login_session:
		username = login_session['username']
		consultaD = session.query(User).filter_by(username=username).first()
		consultaD = consultaD.id
		consultaD2 = session.query(Paths).filter_by(usuarioId=consultaD).first() 
		folderPath = consultaD2.directorio
		#print(folderPath)
		return send_from_directory(folderPath, filename)
	
	
@app.route('/directorios/<int:id>', methods=['GET', 'POST'])
def directorios(id):
	if 'username' in login_session:
		username = login_session['username']
		current_working_directory=os.getcwd()
		id_user = session.query(Paths).filter_by(usuarioId=id).first()
		id_path = id_user.id
		id_foreignuser = id_user.usuarioId
		print(id_foreignuser)
		if request.method == 'GET':
			if 'win32' in sys.platform or 'win64' in sys.platform:
				file_list=subprocess.check_output('dir', shell=True).decode('utf-8').split('\n') # use 'dir' command on Windows
			else:
				file_list=subprocess.check_output('ls', shell=True).decode('utf-8').split('\n') # use 'dir' command on Windows
				return render_template('directorios.html', username=username, file_list=file_list, current_working_directory=current_working_directory, id=id)
		if request.method == 'POST':
			if id_foreignuser == id:
				guardarPath = request.form['directorio']
				session.query(Paths).filter_by(usuarioId=id).update(dict(directorio=guardarPath))
				session.commit()
				return redirect(url_for('configs',id=id))
			else:
				currentuser = session.query(User).filter_by(username=username).first()
				idUsuario = currentuser.id
				guardarPath = request.form['directorio']
				
				enviarDatos = Paths(
					directorio = guardarPath,
					usuarioId = idUsuario)
				session.add(enviarDatos)
				session.commit()
				return redirect(url_for('configs',id=id))

currentuser = session.query(Paths).filter_by(usuarioId=5).all()
for item in currentuser:
	print(item.id)
	print(item.directorio)
	print(item.usuarioId)

@app.route('/cd')
def cd():
	if 'username' in login_session:
		username = login_session['username']
		# run 'level up' command
		os.chdir(request.args.get('path'))
		currentuser = session.query(User).filter_by(username=username).first()
		id = currentuser.id
		# redirect to file manager
		return redirect(url_for('directorios', id=id))	

@app.route('/cds')
def cds():
	# run 'level up' command
	os.chdir(request.args.get('path'))
	
	# redirect to file manager
	return redirect('directorios')



@socketio.on('message')
def handle_message(data):	
	print(data)
	send(data, broadcast=True)

@socketio.on('volumeC')
def volumenC(data):	
	print(data)
	emit("volumeC",data, broadcast=True)

@socketio.on('songsData')
def songsData(data):
	nomCancion = data['titulo_cancion']
	nomArtista = data['nombre_artista']
	nomAlbum = data['nombre_album']
	nomEstado = data['estado']		
	print(nomCancion,nomArtista,nomAlbum,nomEstado)
	emit('receiveData', (nomCancion,nomArtista,nomAlbum,nomEstado), broadcast=True)
	#send(data, broadcast=True)


if __name__ == '__main__':
	socketio.run(app, host='0.0.0.0', debug = True)