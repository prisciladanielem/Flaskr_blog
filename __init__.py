import os

from flask import Flask


def create_app(test_config=None):
    # Cria uma instância do Flask. _
    app = Flask(__name__, instance_relative_config=True)  #instance_relative_config informa ao aplicativo que os arquivos de configuração são relativos à pasta da instância
    #Define algumas configurações padrões que a app irá usar
    app.config.from_mapping(
        SECRET_KEY = 'dev', #é usado para segurança dos dados. Se colocar em produção deverá ser trocado por uma chave randomica
        DATABASE = os.path.join(app.instance_path, 'flask.sqlite'), #define o caminho onde o banco de dados sqlite será salvo
        )

    if test_config is None:
        #Substitui as configurações default com valores do arquivo config.py, se ele existir
        app.config.from_pyfile('config.py', silent=True)
    else:
        #load the test config if passed in 
        app.config.from_mapping(test_config)

    #verifica se a pasta do banco de dados existe. O flask não cria essa pasta automaticamente
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    #aplicação simples que imprime Oi mundo
    @app.route('/hello')
    def hello():
        return 'Hello World!'

    # Importa a aplicção qeu cria o banco de dados
    from . import db
    db.init_app(app)

    #importa os blueprint que cria os módulos das views da parte de auth
    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/',endpoint='index')

    return app