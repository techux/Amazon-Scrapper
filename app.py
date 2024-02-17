from flask import Flask

app = Flask(__name__)
app.json.sort_keys = False

@app.route("/", methods=["GET"])
def home():
    return "Hello, World! ", 200

app.run()
