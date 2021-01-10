import os
import boto3

from flask import Flask, jsonify, request
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Key
app = Flask(__name__)

OTP_TABLE = os.environ['OTP_TABLE']
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(OTP_TABLE)


@app.route("/otp")
def get_otp():
    from_time_stamp = datetime.timestamp(datetime.now() - timedelta(seconds=30))
    resp = table.scan(
        TableName=OTP_TABLE,
        Select='ALL_ATTRIBUTES',
        FilterExpression=Key('timestamp').gt(str(from_time_stamp))
    )
    items = resp.get('Items')
    if not items:
        return jsonify([])
    else:
        result = []
        for item in items:
            result.append({
                'datetime': str(datetime.fromtimestamp(float(item['timestamp']))),
                'timestamp': item['timestamp'],
                'otp': item['otp']
            })
        
        return jsonify(result)


@app.route("/message-content", methods=["POST"])
def post_message_content():
    timestamp = datetime.timestamp(datetime.now())
    otp = request.json.get('otp')
    if not otp:
        return jsonify({'error': 'Please provide otp'}), 400

    table.put_item(
        Item = {
        'timestamp': str(timestamp),
        'otp': otp
        }
    )

    return jsonify({
        'timestamp': timestamp,
        'otp': otp
    })


@app.route("/message-sms", methods=["POST"])
def post_message_sms():
    return jsonify({"error": "not implemented"}), 501


@app.route("/message/<string:timestamp>", methods=["DELETE"])
def delete_message(timestamp):
    resp = table.delete_item(
        Key={
            'timestamp': timestamp
        }
    )