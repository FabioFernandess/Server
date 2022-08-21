from posixpath import dirname
import psycopg2
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import shutil
import json

app = Flask(__name__)
CORS(app)


# Connect to your PostgreSQL database on a remote server
conn = None

cur = None

parent_dir = "/home/fresadora"


def abrirConexao():
    return psycopg2.connect(host="localhost", port="5432",
                            dbname="db_fres", user="postgres", password="fabio")


@app.route('/listarFresadoras')
def listarFresadoras():
    conn = abrirConexao()
    cur = conn.cursor()

    cur.execute("SELECT f.id,f.nome,a.status_analise FROM fresadora f left join (SELECT * FROM analise a1 WHERE data_analise = (SELECT max(data_analise) FROM analise a2 where a2.id_fresadora=a1.id_fresadora)) a on a.id_fresadora = f.id order by a.status_analise asc, f.nome asc;")
    retorno = []
    # Retrieve query results
    records = cur.fetchall()
    for x in records:
        dado = {}
        dado['id'] = x[0]
        dado['nome'] = x[1]
        dado['status'] = x[2]
        retorno.append(dado)
    cur.close()
    conn.close()
    return jsonify(retorno)


@app.route('/buscar/<id>')
def buscarFresadora(id):
    conn = abrirConexao()
    cur = conn.cursor()

    cur.execute(
        "SELECT f.id,f.nome,f.valor,f.variavel FROM fresadora f where f.id = "+id+";")
    # Retrieve query results
    records = cur.fetchall()
    dado = {}
    for x in records:
        dado['id'] = x[0]
        dado['nome'] = x[1]
        dado['valor'] = x[2]
        dado['variavel'] = x[3]
    cur.close()
    conn.close()
    return jsonify(dado)


@app.route('/buscarHistorico/<id>')
def getHistoricoFresadora(id):
    return buscarHistorico(id)


@app.route('/listaConfigFresadoras')
def listaConfigFresadoras():
    conn = abrirConexao()
    cur = conn.cursor()
    cur.execute(
        "SELECT f.id,f.nome,f.valor,f.variavel FROM fresadora f order by f.nome asc;")
    retorno = []
    # Retrieve query results
    records = cur.fetchall()
    for x in records:
        dado = {}
        dado['id'] = x[0]
        dado['nome'] = x[1]
        dado['valor'] = x[2]
        dado['variavel'] = x[3]
        retorno.append(dado)
    cur.close()
    conn.close()
    return jsonify(retorno)


def buscarHistorico(id):
    conn = abrirConexao()
    cur = conn.cursor()
    if id != 'null':
        where = ' where id_fresadora = '+id
    else:
        where = ' where 1=1'

    cur.execute("select a.id,status_analise,TO_CHAR(a.data_analise, 'DD/MM/YYYY HH24:MI:SS'),f.nome from analise a inner join fresadora f on a.id_fresadora = f.id " +
                where+" order by a.data_analise desc;")
    retorno = []
    # Retrieve query results
    records = cur.fetchall()
    for x in records:
        dado = {}
        dado['id'] = x[0]
        dado['nome_fresadora'] = x[3]
        if x[1] == 'O':
            dado['status'] = 'OK'
        if x[1] == 'E':
            dado['status'] = 'ERRO'
        else:
            dado['status'] = 'ATENÇÃO'
        dado['data_analise'] = x[2]
        retorno.append(dado)
    cur.close()
    conn.close()

    return jsonify(retorno)


@app.route('/save', methods=['POST'])
def novaFresadora():
    conn = abrirConexao()
    cur = conn.cursor()
    data = request.json
    dados = data['dados']

    test = verificaDuplicidade(dados['nome'], None)
    if(test['codeStatus'] == 400):
        return jsonify(test), 400

    cur.execute(
        "INSERT INTO fresadora (nome,valor,variavel) VALUES(%s,%s,%s) RETURNING id;", (dados['nome'], dados['valor'], dados['variavel']))

    conn.commit()
    id = cur.fetchone()[0]
    cur.close()
    conn.close()
    if(criarDiretorio(id) == 200):
        return jsonify('ok'), 200
    else:
        excluirFresadora(id)
        return jsonify({'msg': 'Erro ao criar a pasta associada!'}), 400


@app.route('/edit', methods=['POST'])
def editarFresadora():
    conn = abrirConexao()
    cur = conn.cursor()
    data = request.json
    dados = data['dados']

    test = verificaDuplicidade(dados['nome'], dados['id'])
    if(test['codeStatus'] == 400):
        return jsonify(test), 400
    cur.execute(
        "update fresadora set nome = '%s', valor = %s, variavel = '%s'  where id = %s" % (dados['nome'], dados['valor'], dados['variavel'], dados['id']))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify('ok'), 200


def verificaDuplicidade(nome, id):

    conn = abrirConexao()
    cur = conn.cursor()
    if(id == None):
        cur.execute("select * from fresadora where nome like '%s';" % (nome))
    else:
        cur.execute(
            "select * from fresadora where nome like '%s' and id != %s;" % (nome, id))

    retorno = []
    # Retrieve query results
    records = cur.fetchall()
    cur.close()
    conn.close()
    if len(records) > 0:
        return {'msg': 'Já existe uma fresadora cadastrada com este nome!', 'codeStatus': 400}
    else:
        return {'codeStatus': 200}


@app.route('/excluir/<id>', methods=['DELETE'])
def excluirFresadora(id):
    conn = abrirConexao()
    cur = conn.cursor()

    if(excluirDiretorio(id) == 200):
        cur.execute("DELETE FROM analise WHERE id_fresadora = %s;" % (id))
        cur.execute("DELETE FROM fresadora WHERE ID = %s;" % (id))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify('ok'), 200
    else:
        return jsonify({'msg': 'Erro ao excluir a pasta associada!', 'codeStatus': 400}), 400


def criarDiretorio(f):
    id = str(f)

    if(id == ''):
        return 400

    path = os.path.join(parent_dir, id)
    try:
        os.mkdir(path)
        analisados = os.path.join(path, 'Analisados')
        os.mkdir(analisados)
        return 200
    except OSError as error:
        return 400


def excluirDiretorio(f):
    id = str(f)
    path = os.path.join(parent_dir, id)
    try:
        shutil.rmtree(path)
        return 200
    except FileNotFoundError:
        return 200
    except OSError as error:
        print(error)
        return 400


@app.route('/getArquivo', methods=['POST'])
def getArquivo():
    conn = abrirConexao()
    cur = conn.cursor()
    data = request.json
    id = data['id']
    cur.execute("SELECT id_fresadora, nome_arquivo, valor_padrao, TO_CHAR(a1.data_analise, 'DD/MM/YYYY HH24:MI:SS'), nome, status_analise FROM analise a1 inner join fresadora on a1.id_fresadora = fresadora.id WHERE data_analise = (SELECT max(data_analise) FROM analise a2 where a2.id_fresadora=a1.id_fresadora) and a1.id = %s;" % (id))
    records = cur.fetchall()
    cur.close()
    conn.close()

    if len(records) > 0:
        for x in records:
            dado = {}
            dado['id_fresadora'] = x[0]
            nome_arquivo = x[1]
            dado['valor_padrao'] = x[2]
            dado['data'] = x[3]
            dado['nome_fresadora'] = x[4]
            dado['status_analise'] = x[5]

        with open('/home/fresadora/%s/Analisados/%s' % (dado['id_fresadora'], nome_arquivo)) as f:
            json_data = json.load(f)

        dado['dados'] = json_data
        return jsonify(dado), 200
    else:
        return {}
