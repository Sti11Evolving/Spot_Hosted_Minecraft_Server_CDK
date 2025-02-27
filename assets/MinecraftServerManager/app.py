from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from app_helper import *
from dataclasses import asdict

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

print("Starting server...")

setup_minecraft_server()
print("servrer started...")

@app.route("/")
@cross_origin()
def index():
    print("recieved request...")
    return jsonify(online_status())

@app.route("/get_players")
@cross_origin()
def list_players():
    return jsonify(get_players())

@app.route("/get_num_players")
@cross_origin()
def num_players():
    return jsonify(get_num_players())

@app.route("/server_info")
@cross_origin()
def server_info():
    return jsonify(asdict(get_server_info()))

@app.route("/say/<string:message>")
@cross_origin()
def say(message: str):
    return jsonify(send_command(f"say {message}"))

@app.route("/shutdown")
@cross_origin()
def shutdown():
    if(shutdown_helper()):
        return jsonify("Shutting down...")
    return jsonify("Shutdown already in progress...")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)