# Xray Playwright Pytest Integration

This project demonstrates the integration of Playwright with Pytest and Xray Cloud for automated testing.

## Features

- Automated web testing using Playwright
- Integration with Xray Cloud for test result reporting
- Support for parameterized tests
- JUnit XML reporting
- Detailed logging of test execution

## Prerequisites

- Python 3.8 or higher
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
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install
```

## Configuration

1. Update the Xray Cloud credentials in `pytest_jira_plugin.py`:
```python
XRAY_CLIENT_ID = "your_client_id"
XRAY_CLIENT_SECRET = "your_client_secret"
```

## Running Tests

1. Run all tests:
```bash
pytest tests/ -v -s
```

2. Run tests with JUnit XML reporting:
```bash
pytest tests/ -v -s --junitxml=test-results.xml
```

## Project Structure

```
xray-playwright-pytest/
├── tests/
│   └── test_example.py      # Example test cases
├── pytest_jira_plugin.py    # Xray Cloud integration plugin
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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 