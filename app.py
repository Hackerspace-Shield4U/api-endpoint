import os
import subprocess
import threading
import requests
from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest

app = Flask(__name__)


def send_result_to_callback(callback_url: str, result_payload: dict):
    """최종 결과를 컨트롤러의 Callback URL로 POST 전송합니다."""
    try:
        response = requests.post(callback_url, json=result_payload, timeout=30)
        response.raise_for_status()
        print(f"{callback_url} sent successfully")
    except requests.exceptions.RequestException as e:
        print(f"Error: {callback_url} failed: {e}")

def parse_output(output: str) -> list[str]:
    found_endpoints = []
    if "Vulnerable:" in output:
        lines = output.split("Vulnerable:")[1].strip().split('\n')
        for line in lines:
            if line.strip().startswith("[+]"):
                found_endpoints.append(line.strip().split(" ")[1])
    return found_endpoints

def run_scan_and_callback(payload: dict):
    target_url = payload.get("target_url")
    callback_url = payload.get("callback_url")
    job_id = payload.get("job_id")

    apidetector_path = os.path.join("apidetector", "apidetector.py")
    result_payload = {
        "jobId": job_id,
        "targetUrl": target_url,
        "status": "processing",
    }

    try:
        process = subprocess.run(
            ["python3", apidetector_path, "-d", target_url],
            capture_output=True, text=True, timeout=300
        )
        if process.returncode == 0:
            result_payload["status"] = "completed"
            result_payload["endpoints"] = parse_output(process.stdout)
        else:
            result_payload["status"] = "failed"
            result_payload["error"] = process.stderr
    except Exception as e:
        result_payload["status"] = "failed"
        result_payload["error"] = str(e)

    send_result_to_callback(callback_url, result_payload)

# --- API Endpoints ---

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/scan", methods=["POST"])
def start_scan_task():
    """
    Body(JSON):
    {
      "target_url": "https://example.com",
      "callback_url": "http://controller.com/callback",
      "job_id": "job-123" (optional)
    }
    """
    if not request.is_json:
        raise BadRequest("Content-Type must be application/json")

    payload = request.get_json() or {}
    target_url = payload.get("target_url")
    callback_url = payload.get("callback_url")

    if not target_url or not callback_url:
        raise BadRequest("'target_url' and 'callback_url' are required")

    thread = threading.Thread(target=run_scan_and_callback, args=(payload,))
    thread.start()

    response = {"message": "Scan task accepted and is running in the background."}
    return jsonify(response), 202


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)