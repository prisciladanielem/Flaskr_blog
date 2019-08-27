import sqlite3

import click
from flask import current_app, g 
from flask.cli import with_appcontext

def get_db():
    #g é um objeto especial que é unico para cada request. É usado para armazenar dados que podem ser acessados por multiplas funções durante a request.
    #A conexão é armazenada e reusada ao invés de criar uma nova se get_db for chamada duas vezes na mesma request.
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
            )
        g.db.row_factory = sqlite3.Row #Retorna um dicionário de linhas e permite acessar as colunas pelo nome

    return g.db

#Verificar se existe alguma conexão aberta, se existir, ele fecha.
def close_db(e=None):
    db = g.pop('db',None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f: # abre um arquivo
        db.executescript(f.read().decode('utf-8')) # Executa o arquivo

#define um comando que chama init-db que chama a função init_db e mostra ao usuário uma mensagem de sucesso
@click.command('init-db')
@with_appcontext
def init_db_command():
    #Clear the existing data and create new tables.
    init_db()
    click.echo('Banco de dados inicializado!')

def init_app(app):
    app.teardown_appcontext(close_db) #Diz ao flask para chamar a função depois que retornar a response da request.
    app.cli.add_command(init_db_command) #Adiciona um novo comando que pode ser chamado pelo comando flask
