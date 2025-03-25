import pytest
import requests
import json
import os
from datetime import datetime, UTC

# Xray Cloud API configuration
# Default values are provided for development, but should be overridden in CI/CD
# In Bitbucket Pipelines, set these as repository variables:
# Repository Settings > Pipelines > Repository variables
XRAY_CLIENT_ID = os.environ.get("XRAY_CLIENT_ID", "")
XRAY_CLIENT_SECRET = os.environ.get("XRAY_CLIENT_SECRET", "")
XRAY_CLOUD_BASE_URL = "https://xray.cloud.getxray.app/api/v1"  # Using v1 API

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Global variable to store test results
test_results = []

def log_message(message):
    """Log message to both console and file"""
    print(message)
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = f"logs/xray_integration_{timestamp}.txt"
    with open(log_file, "a") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def format_xray_json(test_results):
    """Format test results in Xray JSON format for v1 API"""
    # Format datetime in ISO 8601 format with Z suffix for UTC time
    current_time = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ").replace('.000000Z', 'Z')
    # Extract project key from first test case ID
    project_key = test_results[0]['jira_id'].split('-')[0] if test_results else "SCRUM"
    
    # Group test results by jira_id to handle parameterized tests
    grouped_results = {}
    for result in test_results:
        jira_id = result['jira_id']
        if jira_id not in grouped_results:
            grouped_results[jira_id] = {
                'jira_id': jira_id,
                'start_time': result['start_time'].replace('+00:00Z', 'Z'),
                'finish_time': result['finish_time'].replace('+00:00Z', 'Z'),
                'status': result['status'],
                'comment': f"Test execution completed with status: {result['status']}",
                'iterations': [],
                'has_failure': False  # Track if any iteration failed
            }
        
        # Track if any iteration failed
        if result['status'] == 'FAILED':
            grouped_results[jira_id]['has_failure'] = True
        
        # Add iteration if parameters exist
        if 'parameters' in result:
            iteration = {
                'name': f"Iteration {len(grouped_results[jira_id]['iterations']) + 1}",
                'parameters': [
                    {
                        'name': key,
                        'value': value
                    }
                    for key, value in result['parameters'].items()
                ],
                'status': result['status'],
                'log': f"Test execution completed with status: {result['status']}"
            }
            grouped_results[jira_id]['iterations'].append(iteration)
    
    # Convert grouped results to Xray format
    tests = []
    for result in grouped_results.values():
        # If any iteration failed, mark the entire test as failed
        if result['has_failure']:
            result['status'] = 'FAILED'
            result['comment'] = "Test execution FAILED - One or more iterations failed"
        
        test_data = {
            "testKey": result['jira_id'],
            "start": result['start_time'],
            "finish": result['finish_time'],
            "status": result['status'],
            "comment": result['comment']
        }
        
        # Add iterations if they exist
        if result['iterations']:
            test_data['iterations'] = result['iterations']
            
        tests.append(test_data)
    
    # The main JSON structure for Xray API v1
    return {
        "info": {
            "summary": f"Ditto Regression {datetime.now().strftime('%Y-%m-%d')}",
            "description": "Automated test execution with Playwright",
            "startDate": current_time,
            "finishDate": current_time,
            "project": project_key
        },
        "tests": tests
    }

def get_xray_cloud_token():
    """Get authentication token from Xray Cloud API"""
    auth_url = f"{XRAY_CLOUD_BASE_URL}/authenticate"
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        'client_id': XRAY_CLIENT_ID,
        'client_secret': XRAY_CLIENT_SECRET
    }
    
    try:
        log_message("\nAuthenticating with Xray Cloud API...")
        response = requests.post(auth_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            token = response.text.strip('"')
            log_message("Successfully authenticated with Xray Cloud API")
            return token
        else:
            log_message(f"Authentication error with Xray Cloud API: {response.status_code}")
            log_message(f"Response: {response.text}")
            return None
    except Exception as e:
        log_message(f"Error during Xray Cloud authentication: {str(e)}")
        return None

def upload_to_xray_cloud(test_results):
    """Upload test execution results to Xray Cloud API v1"""
    if not test_results:
        log_message("No test results to upload to Xray Cloud")
        return False
        
    token = get_xray_cloud_token()
    if not token:
        log_message("Cannot upload results to Xray Cloud: authentication failed")
        # Save results locally even if authentication failed
        save_results_locally(test_results)
        return False
    
    data = format_xray_json(test_results)
    upload_url = f"{XRAY_CLOUD_BASE_URL}/import/execution"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    try:
        log_message("\nUploading test results to Xray Cloud...")
        log_message(f"Upload URL: {upload_url}")
        log_message(f"Using API version: v1")
        
        # Pretty print the JSON for easier debugging
        log_message(f"Request data: {json.dumps(data, indent=2)}")
        
        response = requests.post(upload_url, headers=headers, json=data)
        
        status_code = response.status_code
        log_message(f"Response status code: {status_code}")
        
        if status_code == 200:
            response_data = response.json()
            test_execution_key = response_data.get('key', 'Unknown')
            log_message(f"Results successfully uploaded to Xray Cloud - Test Execution: {test_execution_key}")
            log_message(f"Response: {response.text}")
            return True
        else:
            log_message(f"Error uploading results to Xray Cloud: {status_code}")
            log_message(f"Response: {response.text}")
            # Save results locally if upload failed
            save_results_locally(test_results)
            return False
    except Exception as e:
        log_message(f"Error during Xray Cloud upload: {str(e)}")
        # Save results locally if an exception occurred
        save_results_locally(test_results)
        return False

def save_results_locally(test_results):
    """Save test results locally when they can't be uploaded to Xray"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"logs/test_results_{timestamp}.json"
    
    try:
        data = format_xray_json(test_results)
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        log_message(f"Test results saved locally to: {filename}")
        
        # Also save the raw test results for debugging
        debug_filename = f"logs/test_results_raw_{timestamp}.json"
        
        # Create a safe version without binary data for debugging
        safe_results = []
        for result in test_results:
            result_copy = result.copy()
            safe_results.append(result_copy)
            
        with open(debug_filename, 'w') as f:
            json.dump(safe_results, f, indent=2)
        log_message(f"Raw test results saved locally to: {debug_filename}")
        
    except Exception as e:
        log_message(f"Error saving test results locally: {str(e)}")

def pytest_configure(config):
    """Register the jira marker"""
    config.addinivalue_line("markers", "jira: mark test as associated with a Jira test case")

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_makereport(item, call):
    """Collect test results"""
    if call.when == "call":  # Only process the test after it's completed
        jira_id = next((mark.args[0] for mark in item.iter_markers(name="jira")), None)
        if jira_id:
            # Map pytest status to Xray Cloud status
            status = 'PASSED' if call.excinfo is None else 'FAILED'
            # Format datetime in ISO 8601 format with Z suffix for UTC time
            current_time = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ").replace('.000000Z', 'Z')
            
            # Create test result data
            result_data = {
                'jira_id': jira_id,
                'status': status,
                'start_time': current_time,
                'finish_time': current_time
            }
            
            # Add parameters if the test is parameterized
            if hasattr(item, 'funcargs'):
                parameters = {}
                for param_name, param_value in item.funcargs.items():
                    if param_name not in ['request', 'item']:  # Skip internal pytest parameters
                        parameters[param_name] = str(param_value)
                if parameters:
                    result_data['parameters'] = parameters
            
            test_results.append(result_data)
            log_message(f"\nTest {jira_id} completed with status: {status}")

def pytest_sessionfinish(session, exitstatus):
    """Handle test results upload after all tests are completed"""
    if test_results:
        # Upload test results to Xray Cloud
        upload_to_xray_cloud(test_results) 