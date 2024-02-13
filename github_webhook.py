from flask import Flask, request, jsonify
import logging
from subprocess import STDOUT, check_output

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")


@app.route("/health_check", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200


@app.route("/github-webhook", methods=["POST"])
def github_webhook():
    payload = request.json
    if payload["ref"].lower() == "refs/heads/main":
        try:
            output = check_output(
                ["git", "-C", ".", "pull"],
                stderr=STDOUT
            )
            logging.info(f"Git pull output: {output.decode('utf-8')}")
        except Exception as e:
            logging.error(f"Git pull failed: {e}")
    return jsonify({"message": "Webhook received"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
