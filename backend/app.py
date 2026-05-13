from flask import Flask
from config.db import db

app = Flask(__name__)

@app.route('/')
def home():
    return {
        "message": "GetFitX Backend Running Successfully"
    }

if __name__ == '__main__':
    app.run(debug=True)