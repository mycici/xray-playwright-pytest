import pytest
from playwright.sync_api import sync_playwright
import os
from datetime import datetime
import inspect

# Global dictionary to store screenshot paths for each test
# This will be accessed by the pytest_jira_plugin
_test_screenshots = {}

def save_screenshot(page, name, test_params=None):
    """Helper function to save a screenshot and store the path in a global dictionary
    keyed by the current test name"""
    global _test_screenshots
    
    # Try to get the calling test function name
    current_test = None
    for frame in inspect.stack():
        if frame.function.startswith('test_'):
            current_test = frame.function
            break
        
    # If we couldn't determine the test, use the name parameter
    if not current_test:
        current_test = name
    
    # For parameterized tests, create a unique key
    test_key = current_test
    if test_params:
        param_str = "_".join(str(v) for v in test_params if v is not None)
        if param_str:
            test_key = f"{current_test}_{param_str}"
    
    directory = "screenshots"
    os.makedirs(directory, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{name}_{timestamp}.png"
    filepath = os.path.join(directory, filename)
    page.screenshot(path=filepath)
    print(f"Screenshot saved to: {filepath} for test {test_key}")
    
    # Store the screenshot path in the dictionary
    if test_key not in _test_screenshots:
        _test_screenshots[test_key] = []
    _test_screenshots[test_key].append(filepath)
    
    return filepath

def launch_browser():
    """Helper function to launch browser with appropriate settings for the environment"""
    
    # Determine if we're running in CI
    is_ci = os.environ.get('CI', 'false').lower() == 'true' or os.environ.get('BITBUCKET_PIPELINE_UUID') is not None
    
    # Default launch options
    browser_args = {
        'headless': is_ci  # Headless in CI, regular in dev
    }
    
    return browser_args

@pytest.mark.jira('SCRUM-8')
def test_github_title():
    print("\nStarting GitHub test...")
    with sync_playwright() as p:
        browser_args = launch_browser()
        browser = p.chromium.launch(**browser_args)
        page = browser.new_page()
        page.goto("https://github.com")
        assert "GitHub" in page.title()
        browser.close()
    print("GitHub test completed.")

@pytest.mark.jira('SCRUM-9')
def test_failing_with_screenshot():
    """Deliberately failing test that will capture a screenshot as evidence."""
    print("\nStarting deliberately failing test with screenshot...")
    with sync_playwright() as p:
        browser_args = launch_browser()
        browser = p.chromium.launch(**browser_args)
        page = browser.new_page()
        
        # Navigate to a page
        page.goto("https://www.example.com")
        print(f"Loaded page with title: {page.title()}")
        
        # Take some action before intentionally failing
        page.evaluate("document.body.style.backgroundColor = 'yellow'")
        page.wait_for_timeout(500)  # Short delay to see the change
        
        try:
            # Check if test will fail (we know it will in this case)
            page_title = page.title()
            if "This will fail" not in page_title:
                # Capture screenshot when test is about to fail
                save_screenshot(page, "pre_failure")
                print("Captured failure screenshot")
            
            # Now perform the actual assertion
            assert "This will fail" in page_title, "This test is designed to fail and generate a screenshot"
        finally:
            browser.close()
    print("Test completed.")

@pytest.mark.jira('SCRUM-17')
@pytest.mark.parametrize("url,expected_title", [
    ("https://www.python.org", "Python"),
    ("https://www.docker.com", "Docker"),
    ("https://www.kubernetes.io", "Docker"),  # This will fail as the title is different
])
def test_website_titles(url, expected_title):
    print(f"\nStarting test for {url}...")
    with sync_playwright() as p:
        browser_args = launch_browser()
        browser = p.chromium.launch(**browser_args)
        page = browser.new_page()
        page.goto(url)
        
        try:
            # Try to perform the assertion
            actual_title = page.title()
            if expected_title not in actual_title:
                # If assertion would fail, capture screenshot before raising the assertion error
                screenshot_name = f"failure_{url.replace('https://www.', '').replace('.', '_')}"
                save_screenshot(page, screenshot_name, test_params=[url, expected_title])
                print(f"Captured failure screenshot for {url}")
                
            # Now perform the actual assertion
            assert expected_title in actual_title, f"Expected '{expected_title}' in title, got '{actual_title}'"
        finally:
            browser.close()
    print(f"Test completed for {url}")
