import time
import json
import csv
import random
from datetime import datetime
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os

class CairnScraper:
    def __init__(self, proxy=None, output_format="json"):
        self.output_format = output_format
        self.data = []
        self.proxy = proxy
        self.setup_environment()

    def setup_environment(self):
        os.environ["REBROWSER_PATCHES_RUNTIME_FIX_MODE"] = "0"  # Disable some automation signals
        os.environ["REBROWSER_PATCHES_DEBUG"] = "1"  # Debug mode for rebrowser-patches if needed
        os.environ["REBROWSER_PATCHES_UTILITY_WORLD_NAME"] = "cairn_world"

    def run(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, args=self.browser_args())
            context = browser.new_context(
                proxy={"server": self.proxy} if self.proxy else None
            )
            page = context.new_page()
            page.goto("https://shs.cairn.info/publications?lang=fr&tab=revues&content-domain=shs&sort=date-mise-en-ligne")

            self.handle_captcha(page)
            self.scrape_publication_data(page)

            self.export_data()

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

    def human_delay(self, min_time=1.5, max_time=3.5):
        delay = random.uniform(min_time, max_time)
        time.sleep(delay)

    def handle_captcha(self, page):
        if "captcha" in page.content().lower():
            print("CAPTCHA detected. Please solve it manually.")
            while "captcha" in page.content().lower():
                time.sleep(5)  # Wait until the user solves CAPTCHA
            print("CAPTCHA solved. Resuming scraping...")

    def scrape_publication_data(self, page):
        try:
            soup = BeautifulSoup(page.content(), "html.parser")
            cards = soup.find_all("div", class_="bg-white hover:bg-concrete-50")

            for card in cards:
                title = card.find("h1", class_="leading-5 font-bold").get_text(strip=True) if card.find("h1", class_="leading-5 font-bold") else "N/A"
                subtitle = card.find("span", class_="font-bold text-sm").get_text(strip=True) if card.find("span", class_="font-bold text-sm") else "N/A"
                link = card.find("a", class_="underline text-cairn-main").get("href", "N/A") if card.find("a", class_="underline text-cairn-main") else "N/A"
                cover = card.find("img").get("src") if card.find("img") else "N/A"
                publisher = card.find("div", class_="text-xs leading-4 font-bold").get_text(strip=True) if card.find("div", class_="text-xs leading-4 font-bold") else "N/A"

                self.data.append({
                    "title": title,
                    "subtitle": subtitle,
                    "link": link,
                    "cover_image_url": cover,
                    "publisher": publisher,
                    "scrape_date": datetime.now().isoformat()
                })

                self.human_delay()

        except Exception as e:
            print(f"Error during data scraping: {e}")
            page.screenshot(path="error_screenshot.png")  # Capture page screenshot for debugging

    def export_data(self):
        file_name = f"cairn_publications.{self.output_format}"
        try:
            if self.output_format == "json":
                with open(file_name, "w", encoding="utf-8") as json_file:
                    json.dump(self.data, json_file, ensure_ascii=False, indent=4)
                print(f"Data exported to {file_name}")
            elif self.output_format == "csv":
                with open(file_name, "w", newline='', encoding="utf-8") as csv_file:
                    writer = csv.DictWriter(csv_file, fieldnames=self.data[0].keys())
                    writer.writeheader()
                    writer.writerows(self.data)
                print(f"Data exported to {file_name}")
            elif self.output_format == "txt":
                with open(file_name, "w", encoding="utf-8") as txt_file:
                    for entry in self.data:
                        txt_file.write(f"{entry}\n")
                print(f"Data exported to {file_name}")
            else:
                print(f"Unsupported format: {self.output_format}. Supported formats are JSON, CSV, TXT.")

        except IOError as e:
            print(f"Error exporting data: {e}")

if __name__ == "__main__":
    # Configure proxy if necessary, e.g., "http://proxy-server:port"
    proxy = None  # Replace with proxy if needed
    scraper = CairnScraper(proxy=proxy, output_format="csv")  # Set preferred format here (json, csv, txt)
    scraper.run()
