import time
import json
import csv
import random
import logging
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup
import os

class CairnScraper:
    def __init__(self, proxy=None, output_format="json"):
        self.output_format = output_format
        self.data = []
        self.proxy = proxy
        self.logger = self.setup_logger()
        self.setup_environment()

    def setup_environment(self):
        # Configurer les patches de rebrowser pour l'isolation avancée
        os.environ["REBROWSER_PATCHES_RUNTIME_FIX_MODE"] = "alwaysIsolated"
        os.environ["REBROWSER_PATCHES_DEBUG"] = "1"  # Activer le debug si besoin
        os.environ["REBROWSER_PATCHES_UTILITY_WORLD_NAME"] = "cairn_world"

    def setup_logger(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='cairn_scraper.log',
            filemode='a'
        )
        return logging.getLogger(__name__)

    def run(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, args=self.browser_args(), timeout=30000)
            context = self.setup_browser_context(browser)
            self.load_cookies(context)
            page = context.new_page()
            
            # Configurer les timeouts pour la navigation et les éléments
            page.set_default_timeout(30000)
            page.set_default_navigation_timeout(30000)

            max_retries = 3
            for attempt in range(max_retries):
                try:
                    page.goto("https://shs.cairn.info/publications?lang=fr&tab=revues&content-domain=shs&sort=date-mise-en-ligne")
                    self.handle_captcha(page)
                    self.scrape_publication_data(page)
                    break
                except PlaywrightTimeoutError as e:
                    if attempt == max_retries - 1:
                        self.logger.error(f"Page loading failed after {max_retries} attempts.")
                        raise e
                    self.logger.warning(f"Retry {attempt + 1}/{max_retries} due to timeout.")
                    time.sleep(5)  # Wait before retrying

            self.export_data()
            self.save_cookies(context)
            browser.close()

    def browser_args(self):
        return [
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-infobars",
            "--window-size=1920,1080",
            "--disable-gpu",
            "--disable-features=IsolateOrigins,site-per-process",
            "--hide-scrollbars"
        ]

    def setup_browser_context(self, browser):
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
        ]
        context = browser.new_context(
            user_agent=random.choice(user_agents),
            proxy={"server": self.proxy} if self.proxy else None,
            viewport={'width': 1920, 'height': 1080}
        )
        return context

    def human_delay(self, min_time=1.5, max_time=3.5):
        delay = random.uniform(min_time, max_time)
        time.sleep(delay)

    def handle_captcha(self, page):
        try:
            captcha_check = page.wait_for_selector("[data-captcha]", timeout=5000, state="attached")
            if captcha_check:
                self.logger.info("CAPTCHA detected. Please solve it manually.")
                page.wait_for_selector("[data-captcha]", state="detached", timeout=300000)
                self.logger.info("CAPTCHA solved. Resuming scraping...")
        except PlaywrightTimeoutError:
            self.logger.info("No CAPTCHA detected, continuing...")

    async def scrape_publication_data(self, page):
        try:
            cards = await page.query_selector_all(".bg-white.hover\\:bg-concrete-50")
            for card in cards:
                data = await card.evaluate("""
                    card => ({
                        title: card.querySelector('h1.leading-5.font-bold')?.textContent?.trim() || 'N/A',
                        subtitle: card.querySelector('span.font-bold.text-sm')?.textContent?.trim() || 'N/A',
                        link: card.querySelector('a.underline.text-cairn-main')?.href || 'N/A',
                        cover: card.querySelector('img')?.src || 'N/A',
                        publisher: card.querySelector('div.text-xs.leading-4.font-bold')?.textContent?.trim() || 'N/A'
                    })
                """)
                self.data.append({**data, "scrape_date": datetime.now().isoformat()})
                self.human_delay()

        except Exception as e:
            self.logger.error(f"Error during data scraping: {e}")
            await page.screenshot(path="error_screenshot.png")

    def export_data(self):
        file_name = f"cairn_publications.{self.output_format}"
        try:
            if self.output_format == "json":
                with open(file_name, "w", encoding="utf-8") as json_file:
                    json.dump(self.data, json_file, ensure_ascii=False, indent=4)
                self.logger.info(f"Data exported to {file_name}")
            elif self.output_format == "csv":
                with open(file_name, "w", newline='', encoding="utf-8") as csv_file:
                    writer = csv.DictWriter(csv_file, fieldnames=self.data[0].keys())
                    writer.writeheader()
                    writer.writerows(self.data)
                self.logger.info(f"Data exported to {file_name}")
            elif self.output_format == "txt":
                with open(file_name, "w", encoding="utf-8") as txt_file:
                    for entry in self.data:
                        txt_file.write(f"{entry}\n")
                self.logger.info(f"Data exported to {file_name}")
            else:
                self.logger.error(f"Unsupported format: {self.output_format}. Supported formats are JSON, CSV, TXT.")

        except IOError as e:
            self.logger.error(f"Error exporting data: {e}")

    def save_cookies(self, context):
        cookies = context.cookies()
        with open("cookies.json", "w") as f:
            json.dump(cookies, f)
        self.logger.info("Cookies saved to cookies.json")

    def load_cookies(self, context):
        try:
            with open("cookies.json", "r") as f:
                cookies = json.load(f)
                context.add_cookies(cookies)
            self.logger.info("Cookies loaded from cookies.json")
        except FileNotFoundError:
            self.logger.info("No cookies file found. Starting new session.")

if __name__ == "__main__":
    # Configure proxy if necessary, e.g., "http://proxy-server:port"
    proxy = None  # Remplacer par un proxy si nécessaire
    scraper = CairnScraper(proxy=proxy, output_format="csv")  # Format choisi: json, csv, txt
    scraper.run()
