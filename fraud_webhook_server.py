from flask import Flask, request, jsonify, render_template
from collections import deque

app = Flask(__name__)

# Store latest 10 blocked customers (FIFO Queue)
blocked_customers = deque(maxlen=10)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/block-customer", methods=["POST"])
def block_customer():
    data = request.json
    print("⛔ Blocking customer:", data)
    
    # Store the blocked customer
    blocked_customers.append(data)
    
    return jsonify({"status": "blocked", "customer": data}), 200

@app.route("/get-blocked-customers", methods=["GET"])
def get_blocked_customers():
    return jsonify(list(blocked_customers))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
