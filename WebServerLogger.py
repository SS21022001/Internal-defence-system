from flask import Flask, request

app = Flask(__name__)

@app.before_request
def log_request():
    ip_address = request.remote_addr
    method = request.method
    path = request.path
    user_agent = request.user_agent.string
    
    log_entry = f"IP: {ip_address} - Method: {method} - Path: {path} - User-Agent: {user_agent}"
    with open("access.log", "a") as log_file:
        log_file.write(log_entry + "\n")

@app.route("/")
def hello_world():
    return "Hello, World!"

if __name__ == "__main__":
    app.run()
