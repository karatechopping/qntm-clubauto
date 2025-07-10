import os
import json
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

CLIENT_SECRET = os.environ.get("DAXKO_CLIENT_SECRET")
if not CLIENT_SECRET:
    raise ValueError("DAXKO_CLIENT_SECRET environment variable not set")

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    return "OK", 200

@app.route('/webhook', methods=['POST'])
def webhook_receiver():
    data = request.get_json()
    print(f"Received webhook: {data}")

    system_id = data.get('system_id')
    if not system_id:
        return jsonify({"error": "system_id is required in the webhook payload"}), 400

    # 1. Get the access token
    token_url = 'https://api.partners.daxko.com/auth/token'
    token_data = {
        "client_id": "prod_qntmfitlife",
        "client_secret": CLIENT_SECRET,
        "scope": "CA_qntmfitlife",
        "grant_type": "client_credentials"
    }

    try:
        token_response = requests.post(token_url, json=token_data)
        token_response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        token = token_response.json().get('access_token')
        print(f"Access token: {token}")
        with open("access_token.log", "w") as f:
            f.write(token)
    except requests.exceptions.RequestException as e:
        print(f"Error getting access token: {e}")
        return jsonify({"error": str(e)}), 500

    # 2. Update the user profile
    update_url = f'https://api.partners.daxko.com/api/v1/users/{system_id}/profile'
    update_headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
        'Cookie': 'PHPSESSID=4ihjqa5192t6095apukhmngnrb'  # Consider removing hardcoded cookie
    }
    update_data = {
        "liabilityWaiver": True
    }

    try:
        update_response = requests.put(update_url, headers=update_headers, json=update_data)
        update_response.raise_for_status()
        print(f"Update response: {update_response.json()}")
        return jsonify(update_response.json()), 200
    except requests.exceptions.RequestException as e:
        print(f"Error updating user profile: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
