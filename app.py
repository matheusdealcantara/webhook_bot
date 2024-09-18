import os

import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)
DATABASE_URL = os.environ.get('DATABASE_URL')

# Conexão com o banco de dados
connection = psycopg2.connect(DATABASE_URL, sslmode='verify-full', sslrootcert='root.crt')
cur = connection.cursor()

@app.route('/test', methods=['GET', 'POST'])
def index():
    headers = request.headers

    id_pix = headers.get('webhook-resource-id')
    print(id_pix)

    # Atualizar o status da notificação de pagamento para 'PAID'
    try:
        cur.execute(f"UPDATE notificacoes_pagamento SET status='PAID' WHERE id_pix='{id_pix}'")
        cur.execute(f"SELECT valor, user_id FROM notificacoes_pagamento WHERE id_pix='{id_pix}'")
        valor, user_id = cur.fetchone()
        cur.execute(f"SELECT saldo FROM users WHERE user_id='{user_id}'")
        saldo = cur.fetchone()[0]
        cur.execute(f"UPDATE users SET saldo={saldo+valor} WHERE user_id='{user_id}'")
        connection.commit()
    except Exception as e:
        print(e)
        connection.rollback()

    print("Headers Recebidos:")
    for header, value in headers.items():
        print(f'{header}: {value}')

    # Retornar uma resposta para a requisição
    response = {
        "status": "success",
        "message": "Webhook received successfully!"
    }
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
