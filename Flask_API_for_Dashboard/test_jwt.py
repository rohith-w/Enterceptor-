# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 11:18:06 2019

@author: rohit.wardole
"""
from flask import Flask, request, make_response, jsonify
import jwt
import datetime
app = Flask(__name__)
app.config['SECRET_KEY'] = 'eternussolutions'

@app.route('/unprotected')
def unprotected():
    return ''

@app.route('/protected')
def protected():
    return ''

@app.route('/login')
def login():
    auth = request.authorization
    if auth and auth.password == "espl@1234":
        token = jwt.encode({'user' : auth.username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes = 30)}, app.config['SECRET_KEY'])
        return jsonify({'token' : token.decode('UTF-8')})
    return make_response("Could not verify your login!",401,{'WWW-Authenticate' : 'Basic realm = "Login Required"'})

if __name__ == '__main__':
    app.run()