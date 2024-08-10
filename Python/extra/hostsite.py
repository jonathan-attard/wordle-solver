from flask import Flask, request, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("wordle.html")


if __name__ == '__main__':
    app.run(host='192.168.1.64', port=5000, debug=True, threaded=False)
