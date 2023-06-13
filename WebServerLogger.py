from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

@app.before_request
def log_request():
    ip_address = request.remote_addr
    method = request.method
    path = request.path
    user_agent = request.user_agent.string
    timestamp = get_timestamp()

    log_entry = f"[{timestamp}] IP: {ip_address} - Method: {method} - Path: {path} - User-Agent: {user_agent}"
    with open("access.log", "a") as log_file:
        log_file.write(log_entry + "\n")

@app.route("/")
def hello_world():
    timestamp = get_timestamp()
    log_entry = f"[{timestamp}] Visited homepage"
    with open("access.log", "a") as log_file:
        log_file.write(log_entry + "\n")
    
    return "Hello, World!"

def get_timestamp():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    app.run()
