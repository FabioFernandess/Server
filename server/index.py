import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)


# Connect to your PostgreSQL database on a remote server
conn = psycopg2.connect(host="localhost", port="5432", dbname="db_fres", user="postgres", password="fabio")

# Open a cursor to perform database operations
cur = conn.cursor()



@app.route('/listarFresadoras')
def get_incomes():
  cur.execute("SELECT * FROM fresadora")

  # Retrieve query results
  records = cur.fetchall()

  return jsonify(records)


# @app.route('/incomes', methods=['POST'])
# def add_income():
#   incomes.append(request.get_json())
#   return '', 204