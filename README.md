# Xray Playwright Pytest Integration

This project demonstrates the integration of Playwright with Pytest and Xray Cloud for automated testing.

## Features

- Automated web testing using Playwright
- Integration with Xray Cloud for test result reporting
- Support for parameterized tests
- JUnit XML reporting
- Detailed logging of test execution

## Prerequisites

- Python 3.8 or higher (including Python 3.13)
- Xray Cloud account with API credentials
- Git

## Installation

1. Clone the repository:
```bash
git clone https://github.com/mycici/xray-playwright-pytest.git
cd xray-playwright-pytest
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

   **For Python 3.8-3.12:**
   ```bash
   pip install -r requirements.txt
   ```

   **For Python 3.13:**
   ```bash
   # Update pip and build tools
   pip install --upgrade pip setuptools wheel
   
   # Install pytest and other dependencies
   pip install pytest==8.0.0 requests==2.31.0 pytest-xdist==3.5.0 pytest-timeout==2.2.0
   
   # Install playwright with binary-only option
   pip install playwright --only-binary=:all: --use-pep517
   ```

4. Install Playwright browsers:
```bash
playwright install
```

5. Create logs directory:
```bash
mkdir -p logs
```

## Configuration

1. Update the Xray Cloud credentials in `pytest_jira_plugin.py`:
```python
XRAY_CLIENT_ID = "your_client_id"
XRAY_CLIENT_SECRET = "your_client_secret"
```

Alternatively, you can set environment variables:
```bash
export XRAY_CLIENT_ID="your_client_id"
export XRAY_CLIENT_SECRET="your_client_secret"
```

## Running Tests

1. Run all tests:
```bash
pytest tests/ -v -s
```

2. Run a specific test:
```bash
pytest tests/test_example.py::test_example -v
```

3. Run tests with JUnit XML reporting:
```bash
pytest tests/ -v -s --junitxml=test-results.xml
```

## Project Structure

```
xray-playwright-pytest/
├── tests/
│   └── test_example.py      # Example test cases
├── logs/                    # Test execution logs
├── pytest_jira_plugin.py    # Xray Cloud integration plugin
├── pytest.ini              # Pytest configuration
├── conftest.py             # Pytest hooks configuration
├── requirements.txt         # Project dependencies
├── .gitignore              # Git ignore rules
└── README.md               # Project documentation
```

## Test Marking

Tests are marked with Jira IDs using the `@pytest.mark.jira` decorator:

```python
@pytest.mark.jira('SCRUM-1')
def test_example():
    # Test implementation
```

## Parameterized Tests

The project supports parameterized tests with Xray Cloud integration:

```python
@pytest.mark.jira('SCRUM-17')
@pytest.mark.parametrize("url,expected_title", [
    ("https://example.com", "Example"),
    ("https://google.com", "Google"),
])
def test_website_titles(url, expected_title):
    # Test implementation
```

## Logging

- Test execution logs are saved in the `logs/` directory
- Each test run creates a timestamped log file
- Test results are also saved locally if Xray Cloud upload fails

## Troubleshooting

### Greenlet Installation Issues
If you encounter issues with the greenlet dependency on Python 3.13:
```
pip install playwright --only-binary=:all: --use-pep517
```

### Xray Authentication Issues
If you see an authentication error with Xray Cloud API:
1. Verify your Xray API credentials in the `pytest_jira_plugin.py` file
2. Check your Xray Cloud subscription status
3. Ensure your network allows connections to the Xray Cloud API

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Running Tests in Bitbucket Pipelines

This project is configured to run tests automatically in Bitbucket Pipelines using the `bitbucket-pipelines.yml` configuration file. 

### CI/CD Pipeline

The pipeline will:
1. Set up a Python 3.12 environment
2. Install dependencies from `requirements.txt`
3. Install Playwright with Chromium
4. Run the tests with pytest
5. Upload logs, screenshots, and test reports as artifacts

### Pipeline Variables

For the Xray integration to work in Bitbucket Pipelines, you need to add the following repository variables:

1. Go to Repository Settings > Pipelines > Repository variables
2. Add the following variables:
   - `XRAY_CLIENT_ID`: Your Xray Cloud client ID
   - `XRAY_CLIENT_SECRET`: Your Xray Cloud client secret

### Manual Testing

You can also run a manual pipeline using the "manual-test" custom pipeline to trigger test execution on demand. 

### Viewing Test Results

After your pipeline runs, you can:

1. View test results in the Bitbucket pipeline run
2. Download artifacts to see screenshots and logs
3. Check your Xray Cloud dashboard for updated test executions

Test failures in Bitbucket will include screenshots as artifacts, and the same screenshots will be uploaded to Xray Cloud as evidences for the test execution. 