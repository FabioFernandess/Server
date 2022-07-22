import psycopg2
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


# Connect to your PostgreSQL database on a remote server
conn = psycopg2.connect(host="localhost", port="5432",
                        dbname="db_fres", user="postgres", password="fabio")

# Open a cursor to perform database operations
cur = conn.cursor()


@app.route('/listarFresadoras')
def listarFresadoras():
    cur.execute("SELECT f.id,f.nome,a.status_analise FROM fresadora f left join (SELECT * FROM analise a1 WHERE data_analise = (SELECT max(data_analise) FROM analise a2 where a2.id_fresadora=a1.id_fresadora)) a on a.id_fresadora = f.id order by f.nome asc;")
    retorno = []
    # Retrieve query results
    records = cur.fetchall()
    for x in records:
        dado = {}
        dado['id'] = x[0]
        dado['nome'] = x[1]
        dado['status'] = x[2]
        retorno.append(dado)

    return jsonify(retorno)


@app.route('/buscarHistorico/<id>')
def getHistoricoFresadora(id):
    return buscarHistorico(id)


@app.route('/listaConfigFresadoras')
def listaConfigFresadoras():
    cur.execute("SELECT f.id,f.nome,f.valor FROM fresadora f order by f.nome asc;")
    retorno = []
    # Retrieve query results
    records = cur.fetchall()
    for x in records:
        dado = {}
        dado['id'] = x[0]
        dado['nome'] = x[1]
        dado['valor'] = x[2]
        retorno.append(dado)

    return jsonify(retorno)


def buscarHistorico(id):
    if id != 'null':
        where = ' where id_fresadora = '+id
    else:
        where = ' where 1=1'

    cur.execute("select a.id,status_analise,TO_CHAR(a.data_analise, 'DD/MM/YYYY HH24:MI:SS'),f.nome from analise a inner join fresadora f on a.id_fresadora = f.id "+where+" order by a.data_analise desc;")
    retorno = []
    # Retrieve query results
    records = cur.fetchall()
    for x in records:
        dado = {}
        dado['id'] = x[0]
        dado['nome_fresadora'] = x[3]
        if x[1] == 'O' : 
          dado['status'] ='OK'
        else:
          dado['status'] = 'ATENÇÃO'
        dado['data_analise'] = x[2]
        retorno.append(dado)

    return jsonify(retorno)


# @app.route('/incomes', methods=['POST'])
# def add_income():
#   incomes.append(request.get_json())
#   return '', 204
