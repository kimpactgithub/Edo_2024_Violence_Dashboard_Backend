from flask import Flask
from dotenv import load_dotenv
from src.main import getViolenceData
from flask_cors import CORS

app = Flask(__name__)

cors = CORS(app)

@app.route("/", methods=["GET"])
def index():
    return "<p>Welcome to the NEVR Live Dashboard</p>"

@app.route("/oauth2callback")
def oathCallback():
    return "<p>You're now signed in</p>"

@app.route("/data/live", methods=["GET"])
def getData():
    try:
        data = getViolenceData()
        return data
    except Exception as e:
        print("An error occurred: ", e)
        print({
            "error": "An error occurred while handling your request"
        })

if __name__ == "__main__":
    print("\nStarting server...")
    app.run(debug=True)