import functools

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for

from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

#Organiza um grupo de views. Usando bp.route a urls vai ficar /auth/url
bp = Blueprint('auth',__name__, url_prefix='/auth')

@bp.route('/register',methods=('GET','POST'))
def register():
    if request.method == 'POST': # Valida se o método enviado no form foi post
        username = request.form['username'] #Captura o username
        password = request.form['password'] #Captura o password
        db = get_db() #Abre a conexão com o banco de dados
        error = None

        #Valida se o campo de username e senha não foram preenchidos vazios
        if not username:
            error = 'Username is required!'
        elif not password:
            error = 'Password is required!'
        #Valida se já existe um usuário cadastrado com esse username
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None: #fetchone uma linha da query, se o resultado for vazio retorna None. Fetchall é usado quando a query retorna vários resultados
            error = 'User {} is already registered!'.format(username)

        #Se a validação ocorrer com sucesso, insere o usuário no banco de dados
        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?,?)',
                (username, generate_password_hash(password)) # generate_password_hash função pra não gravar o password direto no banco
                )
            db.commit() #Faz commit das alteções. Só é necessário em caso de inserção de dados no banco
            return redirect(url_for('auth.login'))#Redireciona o usuário para a tela de login
        #Se ocorrer erro, será mostrao ao usuário. O flash guarda mensagens que podem ser recuperadas na renderização do template.
        flash(error)
    return render_template('auth/register.html')

@bp.route('/login',methods=('GET','POST'))
def login():
    if request.method == 'POST': # Valida se o método enviado no form foi post
        username = request.form['username'] #Captura o username digitado no form
        password = request.form['password'] #Captura o password digitado no form
        db = get_db() #Abre a conexão
        error = None
        user = db.execute( #Faz uma query para buscar o usuário no banco de dados
            'SELECT * FROM user WHERE username = ?',(username,)
            ).fetchone()

        #Valida se o usuário existe e se a senha está correta
        if user is None:
            error = 'Usuário incorreto!'
        elif not check_password_hash(user['password'],password): #check_password_hash checa se o password criptografado está correto
            error = 'Senha incorreta!'

        if error is None:
            session.clear() #Limpa a sessão
            session['user_id'] = user['id'] #Se não ocorrer erro, ele guarda o id do usuário que logou em uma nova sessão. Os dados são guardados em um cookie que é enviado para o browser
            return redirect(url_for('auth.login'))

        flash(error)
    return render_template('auth/login.html')

@bp.before_app_request #Registra um função que executa antes da view, não importando qual URL foi feito a request
def load_logged_in_user(): #Função pra carregar o usuário logado
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None # se não houve id, g.user recebe None
    else:
        g.user = get_db().execute( # Checa se o id do usuário está guardado no session e pega os dados do usuário do banco de dados e guarda no g.user.
            'SELECT *    FROM user WHERE id = ?', (user_id,)
            ).fetchone()

@bp.route('/logout')
def logout():
    session.clear() #Limpa o id do usuário da sessão, fazendo isso a função load_logged_in_user() não vai carregar o usuário
    return redirect(url_for('index'))

#Decorator de login required. Cria uma view que amarra a view solicitada, checa se o usuário está logado, se estiver o fluxo continua normalmente, se não estiver direciona para a página de login
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrapped_view