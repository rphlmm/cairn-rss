from playwright.sync_api import sync_playwright
print("Playwright est bien installé !")

from bs4 import BeautifulSoup
print("BeautifulSoup est bien installé !")

# Test complet
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('https://example.com')
    print("Test de navigation réussi !")
    browser.close()