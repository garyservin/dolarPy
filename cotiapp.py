# -*- encoding: utf-8 -*-
import json

from flask import Flask, Response, render_template, redirect
from flask_cors import CORS

from coti import get_current_data, update_data

app = Flask(__name__, static_url_path='')
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.route("/")
def index():
    return redirect("https://github.com/garyservin", code=302)


@app.route("/dolar")
def dolar():
    return render_template('dolar_plot.html')


@app.route("/api/1.0/")
def api_root():
    response = ""
    try:
        response = get_current_data()
    except IOError:
        response = update_data()
    return Response(response=response, status=200, mimetype='application/json')


if __name__ == "__main__":
    app.run(host='0.0.0.0', ssl_context='adhoc')
