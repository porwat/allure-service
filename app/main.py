import os
import shutil
from uuid import uuid4
from hashlib import sha1
from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
import threading
import json
from allure_commons.model2 import TestResult, Status
from allure_commons.utils import now
from allure_commons.logger import AllureFileLogger


# Define the data model for the POST request
class Result(BaseModel):
    name: str
    fullName: str
    description: str
    status: str
    host: str
    steps: list
    labels: list

app = FastAPI()

@app.post('/submit-results')
async def send_result(data: Result):
    result = data.model_dump()
    if not data:
        return json.dumps({'error': 'Invalid request'}), 400

    # Create an AllureFileLogger instance
    logger = AllureFileLogger('allure-results')

    # Report the result
    status = Status.PASSED if result['status'] == 'passed' else Status.FAILED
    allure_result = TestResult(
        uuid=str(uuid4()),
        historyId=sha1(result['name'].encode('utf-8') + result['fullName'].encode('utf-8') + result['description'].encode('utf-8')).hexdigest(),
        testCaseId=sha1(result['name'].encode('utf-8')).hexdigest(),
        name=result['name'],
        fullName=result['fullName'],
        status=status,
        start=now()-3000,
        stop=now(),
        description=result['description'],
        steps=result['steps'],
        attachments=[],
        labels=result['labels']
    )

    # Save the result
    logger.report_result(allure_result)

    return {"message": "Result saved successfully"}

@app.get("/flush-results")
async def flush_results():
    results_dir = "allure-results"
    # Clean the report directory
    if os.path.exists(results_dir):
        shutil.rmtree(results_dir)

    return {"message": "Results flushed successfully"}

@app.get("/generate-report")
async def generate_report():
    report_dir = "allure-report"
    results_dir = "allure-results"

    # Use historical data in report
    source_dir = os.path.join(report_dir, 'history')
    destination_dir = os.path.join(results_dir, 'history')

    if os.path.exists(destination_dir):
        shutil.rmtree(destination_dir)
    
    if os.path.exists(source_dir):
        shutil.copytree(source_dir, destination_dir)
    

    # Serve the Allure report
    threading.Thread(target=serve_allure_report, args=(report_dir, results_dir,)).start()

    check_process = threading.Thread(target=serve_allure_report, args=(report_dir, results_dir,)).is_alive

    return {"message": "Report is being generated and served."}

def serve_allure_report(report_dir, results_dir):
    # Generate Allure report
    subprocess.run(['allure', 'generate', results_dir, '-o', report_dir, '--clean'])

    # Kill the Allure server if it's running
    subprocess.run(['pkill', '-f', 'allure'])

    # Serve the report
    subprocess.run(['allure', 'open', '-h', '0.0.0.0', '-p', '8090'])
