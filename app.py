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
import json
import os, json
from tinytag import TinyTag


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)



# conectar a la base de datos y crear la sesion
engine = create_engine('postgresql://alermpp:ramoscpii@localhost/usuarios')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


#-----------------------------INICIAR SESION----------------------[OK]

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'GET':
		state = ''.join(random.choice(
				string.ascii_uppercase + string.digits) for x in range(32))
		
		login_session['state'] = state
		return render_template('login.html', STATE = state)
	else:
		if request.method == 'POST':
			
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
		
		login_session['state'] = state
		return render_template('loginControl.html', STATE = state)
	else:
		if request.method == 'POST':
			
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
			#Compara las contraseñas, y ve la longitud de la contraseña que se ingresa
			if request.form['password'] == request.form['repeatpassword']:
				if len(request.form['password']) <8:
					return render_template('register.html', errregister = "La contraseña debe tener mas de 8 caracteres")
				else: 
					username = request.form['username']
					password=request.form['password']
					email = request.form['email']
					# Hashea el password
					pw_hash = make_pw_hash(username, password)
					nuevoUsuario = User(
							username = username,
							email = email,
							pw_hash=pw_hash) 
					session.add(nuevoUsuario)
					session.commit()
					# Agrega un nuevo registro a la base de datos
					login_session['username'] = request.form['username']
					return redirect(url_for('firstPage'))
			else:
				return render_template('register.html', errregister = "Las contraseñas no coinciden")

@app.route('/logout')
def logout():
	if 'username' in login_session:
		del login_session['username']
		return redirect(url_for('firstPage'))
	else:
		return redirect(url_for('firstPage'))


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
			
			if request.form['guardarbtn'] == 'btnvalue':
				userscamp = request.form['nombreUsuario']
				passwcamp = request.form['passwordnew']
				mailcamp = request.form['mail']
				
				user = session.query(User).filter_by(id = id).first()
				if user and valid_pw(request.form['nombreUsuario'],
										request.form['password'],
										user.pw_hash):
					if request.form['passwordnew'] != request.form['passwordrepeat']:
					
						return render_template('configs.html', username=username, errormensaje = errormensaje, email=correo, id=id)
						
					else:
						pw_hash = make_pw_hash(userscamp, passwcamp)
						session.query(User).filter_by(id=id).update(dict(username=userscamp,pw_hash=pw_hash, email=mailcamp))
						session.commit()
						del login_session['username']
						return redirect(url_for('login'))
				else:
					return render_template('configs.html', username=username, errormensaje=errormensaje, email=correo, id=id)


@app.route('/directorios', methods=['GET', 'POST'])
def newdirectorios():
	if 'username' in login_session:
		username = login_session['username']
		# Se obtiene la ruta actual
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
				#id_con = items.id
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
					variable = True
				else:
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


@app.route('/playMusic/<path:filename>')
def songRender(filename):
	if 'username' in login_session:
		username = login_session['username']
		consultaD = session.query(User).filter_by(username=username).first()
		consultaD = consultaD.id
		consultaD2 = session.query(Paths).filter_by(usuarioId=consultaD).first() 
		folderPath = consultaD2.directorio

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



@app.route('/cd')
def cd():
	if 'username' in login_session:
		username = login_session['username']
		# run 'level up' command
		os.chdir(request.args.get('path'))
		currentuser = session.query(User).filter_by(username=username).first()
		id = currentuser.id
		
		return redirect(url_for('directorios', id=id))	

@app.route('/cds')
def cds():
	# run 'level up' command
	os.chdir(request.args.get('path'))
	
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


if __name__ == '__main__':
	socketio.run(app, host='0.0.0.0', debug = True)