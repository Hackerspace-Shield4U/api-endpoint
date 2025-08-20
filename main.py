import uuid
import subprocess
import os
import requests
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Dict, Any

app = FastAPI()

class ScanRequest(BaseModel):
    target_url: str
    callback_url: HttpUrl
    job_id: str | None = None 


def send_result_to_callback(callback_url: str, result_payload: dict):
    try:
        response = requests.post(callback_url, json=result_payload, timeout=30)
        response.raise_for_status() 
        print(f"{callback_url} sent successfully")
    except requests.exceptions.RequestException as e:
        print(f"Error: {callback_url} failed : {e}")

def parse_output(output: str) -> list[str]:
    found_endpoints = []
    if "Vulnerable:" in output:
        lines = output.split("Vulnerable:")[1].strip().split('\n')
        for line in lines:
            if line.strip().startswith("[+]"):
                found_endpoints.append(line.strip().split(" ")[1])
    return found_endpoints

def run_scan_and_callback(request_data: ScanRequest):
    apidetector_path = os.path.join("apidetector", "apidetector.py")
    result_payload = {
        "jobId": request_data.job_id,
        "targetUrl": request_data.target_url,
        "status": "processing",
    }
    
    try:
        process = subprocess.run(
            ["python3", apidetector_path, "-d", request_data.target_url],
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
    
    send_result_to_callback(str(request_data.callback_url), result_payload)

@app.post("/scan", status_code=202)
async def start_scan_task(request: ScanRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_scan_and_callback, request)
    
    return {"message": "Scan task accepted and is running in the background."}
