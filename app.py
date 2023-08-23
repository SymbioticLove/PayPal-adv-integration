from flask import Flask, render_template, jsonify, request
import requests
import base64

app = Flask(__name__)

# PayPal API config
CLIENT_ID = "AQ_5NUKt79k6GOTABGNTPkahj_GsnshHwIENAmEj-eHCLU2GQm6lMeLncq1ZgxX0Li2wgqyUmVFwilsO"
APP_SECRET = "ECm3IugDnzsgcFw03htnf2vr5H4vmgwSZbySlL3pf1LdHaADWncKPyGwA2oJNbAwXiVYWepPsc_QgXIN"
BASE_URL = "https://api-m.sandbox.paypal.com"

@app.route("/")
def index():
    return render_template("checkout.html", client_id=CLIENT_ID, client_token=generate_client_token())

@app.route("/api/orders", methods=["POST"])
def create_order():
    try:
        order = create_paypal_order()
        return jsonify(order)
    except Exception as e:
        return str(e), 500
    
@app.route("/api/orders/<order_id>/capture",  methods=["POST"])
def capture_order(order_id):
    try:
        capture_data = capture_paypal_payment(order_id)
        return jsonify(capture_data)
    except Exception as e:
        return str(e), 500
    
@app.route("/api/process-credit-card", methods=["POST"])
def process_credit_card():
    try:
        payment_data = request.get_json()
        # Credit card processing logic here
        success = True
        response_data = {"success": success}
        return jsonify(response_data)
    except Exception as e:
        return str(e), 500
    
    
def generate_access_token():
    credentials = f"{CLIENT_ID}:{APP_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    response = requests.post(f"{BASE_URL}/v1/oauth2/token", data="grant_type=client_credentials", headers={
        "Authorization": f"Basic {encoded_credentials}",
        "Accept-Language": "en_US",
        "Content-Type": "application/x-www-form-urlencoded"
    })
    response_data = response.json()
    return response_data["access_token"]

def generate_client_token():
    access_token = generate_access_token()
    response = requests.post(f"{BASE_URL}/v1/identity/generate-token", headers={
        "Authorization": f"Bearer {access_token}",
        "Accept-Language": "en_US",
        "Content-Type": "application/json"
    })
    response_data = response.json()
    print("Response Data:", response_data)
    
    # Extract the client token from the response data
    client_token = response_data["client_token"]

    print(client_token)
    
    # Return the client token directly
    return client_token

def create_paypal_order():
    purchase_amount = "100.00" # TODO: Pull prices from a database
    access_token = generate_access_token()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "amount": "USD",
                "value": purchase_amount,
            }
        ]
    }
    response = requests.post(f"{BASE_URL}/v2/checkout/orders", json=payload, headers=headers)
    response_data = response.json()
    return response_data

def capture_paypal_payment(order_id):
    access_token = generate_access_token()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.post(f"{BASE_URL}/v2/checkout/orders/{order_id}/capture", headers=headers)
    response_data = response.json()
    return response_data
if __name__ == "__main__":
    app.run(port=8888)


