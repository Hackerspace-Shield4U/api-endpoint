# API Endpoint Scanner #
An asynchronous, callback-based web service to discover vulnerable API endpoints in web applications using the power of `apidetector`.


<br>

## Overview 
This project provides a simple Flask-based web server that exposes an API to initiate scans for API endpoints on a given target URL. It's designed to be asynchronous. You provide a target and a callback URL, and the service will perform the scan in the background. Once the scan is complete, it sends the results back to your specified callback URL.

This is particularly useful for integrating automated security scanning into a larger workflow or a CI/CD pipeline without blocking processes.

<br>

## Features
* **Asynchronous Scanning** : Initiates scans in a background thread, immediately returning a 202 Accepted response.

* **Callback Mechanism**: Pushes scan results to a predefined callback URL.

* **Simple REST API**: Easy to integrate with other services with a straightforward JSON-based API.

* **Powered by apidetector**: Leverages the apidetector tool to find potentially vulnerable API endpoints.

<br>


## How It Works
1. You send a `POST` request to the `/scan` endpoint with a `target_url` and a `callback_url`.

2. The server validates the request and starts a new background thread to run the `apidetector` scan against the target.

3. The server immediately responds with a `202 Accepted` to let you know the task has been received.

3. When the scan is finished, the server parses the output from apidetector.

4. Finally, it sends a `POST` request to your `callback_ur` with the results of the scan, including the status and any discovered endpoints.
<br>
<br>

### API Documentation
Start a Scan
* Endpoint: `/scan`

* Method: `POST`

* Description: Accepts a new scan task.
<br>


**Request Body (JSON)**:

```
{
  "target_url": "https://example.com",
  "callback_url": "https://your-service.com/results-handler",
  "job_id": "scan-001"
}
```
<br>

* `target_url` (string, required): The URL of the web application to scan.

* `callback_url` (string, required): The URL to which the scan results will be sent.

* `job_id` (string, optional): A unique identifier you can provide to track the job.
<br>

**Success Response (202 Accepted)**:
  
```
{
  "message": "Scan task accepted and is running in the background."
}
```

Health Check
Endpoint: `/health`

Method: `GET`

Description: Checks the health of the service.
<br>
**Success Response (200 OK)**:
```
{
  "status": "ok"
}
```
<br>
<br>

### Callback Payload
When a scan is complete or fails, the service will send a POST request to the callback_url you provided. 

### Example
* Successful Scan:
```
  
  {
  "jobId": "scan-001",
  "targetUrl": "https://example.com",
  "status": "completed",
  "endpoints": [
    "/api/v1/users",
    "/api/v1/products",
    "/api/v1/orders"
  ]
}

```

<br>

## Setup and Installation
1. Clone the repository:

```
git clone https://github.com/your-username/api-endpoint-scanner.git
cd api-endpoint-scanner
```

2. Install apidetector:
This service depends on apidetector. Make sure it's installed and accessible in your environment. You can clone it from its repository:

```
git clone https://github.com/brinhosa/apidetector.git
```

Ensure the apidetector.py script is located in a directory named apidetector within the project root, or update the path in the script.

3. Install Python dependencies:
```
pip install -r requirements.txt
```
Your requirements.txt file should contain:
```
Flask
requests
Werkzeug
```

4. Run the application:
```
python app.py
```
The server will start on http://0.0.0.0:8000.

<br>
<br>

## Example Usage
Here is an example of how to start a scan using curl:
```
curl -X POST \
  http://localhost:8000/scan \
  -H 'Content-Type: application/json' \
  -d '{
    "target_url": "http://testphp.vulnweb.com/",
    "callback_url": "https://webhook.site/your-unique-webhook-id",
    "job_id": "job-456"
  }'
```
You can use a service like webhook.site to easily inspect the callback results.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
