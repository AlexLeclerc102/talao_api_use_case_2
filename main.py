# Talao.co API Demo 2 v0.1
# Usecase 2


from urllib.parse import urlencode
import requests
from flask import Flask, redirect, request, render_template_string, session, send_from_directory
from flask import redirect, render_template
import json
import os
import jwt

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Hello"

if __name__ == '__main__':
    app.run(host = "127.0.0.1", port= 5000, debug = True)
