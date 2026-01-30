from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
CORS(app)

mongo_url = os.getenv("MONGO_URL")
#print("Loaded MONGO_URL:", mongo_url)  # Debug

if not mongo_url:
    raise RuntimeError("MONGO_URL environment variable is not set.")
client = MongoClient(mongo_url)
db = client.github_events
collection = db.logs


def parse_event(event_type, payload):
    """Create a uniform DB document from GitHub events"""

    # PUSH EVENT
    if event_type == "push":
        branch = payload["ref"].split("/")[-1]
        return {
            "request_id": payload["after"],
            "author": payload["pusher"]["name"],
            "action": "PUSH",
            "from_branch": branch,
            "to_branch": branch,
            "timestamp": datetime.utcnow().isoformat()
        }

    # PULL REQUEST OPENED
    if event_type == "pull_request" and payload["action"] == "opened":
        pr = payload["pull_request"]
        return {
            "request_id": str(pr["id"]),
            "author": pr["user"]["login"],
            "action": "PULL_REQUEST",
            "from_branch": pr["head"]["ref"],
            "to_branch": pr["base"]["ref"],
            "timestamp": datetime.utcnow().isoformat()
        }

    # MERGE EVENT
    if event_type == "pull_request" and payload["action"] == "closed" and payload["pull_request"]["merged"]:
        pr = payload["pull_request"]
        return {
            "request_id": str(pr["id"]),
            "author": pr["merged_by"]["login"],
            "action": "MERGE",
            "from_branch": pr["head"]["ref"],
            "to_branch": pr["base"]["ref"],
            "timestamp": datetime.utcnow().isoformat()
        }

    return None


@app.route("/webhook", methods=["POST"])
def webhook():
    event_type = request.headers.get("X-GitHub-Event")
    payload = request.get_json(silent=True)

    app.logger.info(f"Received event: {event_type}")

    data = parse_event(event_type, payload)
    if data:
        try:
            collection.insert_one(data)
            app.logger.info("Event inserted into DB")
        except Exception:
            app.logger.exception("Failed to insert event into DB")

    return jsonify({"status": "received"}), 200


@app.route("/logs", methods=["GET"])
def logs():
    logs = list(collection.find().sort("_id", -1).limit(50))
    for log in logs:
        log["_id"] = str(log["_id"])
    return jsonify(logs)


@app.route("/", methods=["GET"])
def home():
    return "GitHub Webhook Receiver Active"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
