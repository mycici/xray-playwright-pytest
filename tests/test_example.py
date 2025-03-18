import pytest
from playwright.sync_api import sync_playwright

'''@pytest.mark.jira('SCRUM-2')
def test_example():
    print("\nStarting test execution...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://example.com")
        assert page.title() == "Example Domain"
        browser.close()
    print("Test execution completed.")

@pytest.mark.jira('SCRUM-7')
def test_google_search():
    print("\nStarting Google search test...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://www.google.com")
        assert "Google" in page.title()
        browser.close()
    print("Google search test completed.")

@pytest.mark.jira('SCRUM-8')
def test_github_title():
    print("\nStarting GitHub test...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://github.com")
        assert "GitHub" in page.title()
        browser.close()
    print("GitHub test completed.")

@pytest.mark.jira('SCRUM-9')
def test_wikipedia():
    print("\nStarting Wikipedia test...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://www.wikipedia.org")
        assert "Wikipedia" in page.title()
        browser.close()
    print("Wikipedia test completed.")
'''
@pytest.mark.jira('SCRUM-17')
@pytest.mark.parametrize("url,expected_title", [
    ("https://www.python.org", "Python"),
    ("https://www.docker.com", "Docker"),
    ("https://www.kubernetes.io", "Docker"),  # This will fail as the title is different
])
def test_website_titles(url, expected_title):
    print(f"\nStarting test for {url}...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        assert expected_title in page.title(), f"Expected '{expected_title}' in title, got '{page.title()}'"
        browser.close()
    print(f"Test completed for {url}")
