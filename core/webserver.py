from flask import Flask, request, jsonify
from core.webhook import process, list_all_webhooks

app = Flask(__name__)


@app.route('/cross-sell/webhook/order-create', methods=['POST'])
def order_create():
    data = request.json  # Get the JSON data sent with the POST request
    # Here you can process the data as needed
    print(f"Received data: {data}")

    # Respond with a JSON message
    response = process(data)
    return jsonify(response)


@app.route('/cross-sell/webhook/list', methods=['GET'])
def get_webhooks_list():
    return jsonify(list_all_webhooks()), 200
