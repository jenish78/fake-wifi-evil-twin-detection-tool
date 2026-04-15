from flask import Flask, render_template, jsonify, request
from scanner import scan_networks

app = Flask(__name__)

TEST_MODE = False


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/toggle_test", methods=["POST"])
def toggle_test():
    global TEST_MODE
    TEST_MODE = not TEST_MODE
    return jsonify({"test_mode": TEST_MODE})


@app.route("/data")
def data():
    return jsonify(scan_networks(TEST_MODE))


if __name__ == "__main__":
    app.run(debug=True)