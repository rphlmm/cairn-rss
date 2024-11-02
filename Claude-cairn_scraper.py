# cairn_turbo_scraper.py

import time
import json
import csv
import random
import logging
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
import os

class CairnTurboScraper:
    """
    Scraper robuste pour CAIRN avec sorties multiples et protection anti-détection.
    Utilise rebrowser-patches pour contourner les protections anti-bot.
    """
    
    VALID_FORMATS = ["txt", "csv", "json"]
    
    def __init__(self, proxy: Optional[str] = None, output_formats: List[str] = ["json"]):
        """
        Initialise le scraper.
        Args:
            proxy: Proxy optionnel (format: "http://host:port")
            output_formats: Liste des formats de sortie souhaités parmi ["txt", "csv", "json"]
        """
        self.validate_formats(output_formats)
        self.setup_directories()
        self.setup_logging()
        self.output_formats = [fmt.lower() for fmt in output_formats]
        self.data: List[Dict] = []
        self.proxy = proxy
        self.setup_environment()
    
    def validate_formats(self, formats: List[str]) -> None:
        """Valide les formats de sortie demandés."""
        invalid_formats = [fmt for fmt in formats if fmt.lower() not in self.VALID_FORMATS]
        if invalid_formats:
            raise ValueError(
                f"Format(s) invalide(s): {invalid_formats}. "
                f"Formats supportés: {self.VALID_FORMATS}"
            )
    
    def setup_directories(self):
        """Crée les répertoires nécessaires."""
        # Obtenir le chemin absolu du répertoire courant
        base_dir = Path(__file__).parent.absolute()
        
        # Créer les répertoires en utilisant des chemins absolus
        (base_dir / "output").mkdir(exist_ok=True)
        (base_dir / "output/screenshots").mkdir(exist_ok=True)
        (base_dir / "output/logs").mkdir(exist_ok=True)
        (base_dir / "output/data").mkdir(exist_ok=True)
        
        # Sauvegarder les chemins pour utilisation ultérieure
        self.base_dir = base_dir
        self.output_dir = base_dir / "output"
    
    def setup_logging(self):
        """Configure le système de logging."""
        log_file = self.output_dir / "logs/cairn_scraper.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(str(log_file), mode='a'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def setup_environment(self):
        """Configure l'environnement pour rebrowser-patches."""
        os.environ["REBROWSER_PATCHES_RUNTIME_FIX_MODE"] = "alwaysIsolated"
        os.environ["REBROWSER_PATCHES_DEBUG"] = "1"
        os.environ["REBROWSER_PATCHES_UTILITY_WORLD_NAME"] = "cairn_world"

    def run(self):
        """Execute le scraping complet."""
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(
                    headless=False,
                    args=self.browser_args(),
                    timeout=30000
                )
                context = self.setup_browser_context(browser)
                self.load_cookies(context)
                
                page = context.new_page()
                page.set_default_timeout(30000)
                page.set_default_navigation_timeout(45000)
                
                # Attendre plus longtemps pour le chargement initial
                page.set_default_timeout(60000)
                
                self.navigate_with_retry(page)
                
                # Attendre que la page soit complètement chargée
                page.wait_for_load_state('networkidle')
                page.wait_for_load_state('domcontentloaded')
                
                # Petite pause pour laisser le JS s'exécuter
                time.sleep(2)
                
                self.handle_captcha(page)
                self.scrape_publication_data(page)
                
                if not self.data:
                    self.logger.error("No data collected! Taking debug screenshot...")
                    page.screenshot(path=str(self.output_dir / "screenshots/empty_data.png"))
                
                self.save_cookies(context)
                self.export_data()
                
            except Exception as e:
                self.logger.error(f"Fatal error: {e}")
                if 'page' in locals():
                    screenshot_path = self.output_dir / f"screenshots/error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    page.screenshot(path=str(screenshot_path))
            finally:
                if 'browser' in locals():
                    browser.close()

    def browser_args(self) -> List[str]:
        """Retourne les arguments de lancement du navigateur."""
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

    def setup_browser_context(self, browser: Browser) -> BrowserContext:
        """Configure le contexte du navigateur avec rotation des User-Agents."""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        return browser.new_context(
            user_agent=random.choice(user_agents),
            proxy={"server": self.proxy} if self.proxy else None,
            viewport={'width': 1920, 'height': 1080}
        )

    def navigate_with_retry(self, page: Page, max_retries: int = 3):
        """Navigue vers la page avec retry en cas d'échec."""
        base_url = "https://shs.cairn.info/publications"
        params = "?lang=fr&tab=revues&content-domain=shs&sort=date-mise-en-ligne"
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Navigation attempt {attempt + 1}/{max_retries}")
                response = page.goto(f"{base_url}{params}")
                
                if response.status == 200:
                    self.logger.info("Navigation successful")
                    page.wait_for_load_state('networkidle')
                    return
                else:
                    self.logger.error(f"Navigation failed with status: {response.status}")
                    
            except Exception as e:
                if attempt == max_retries - 1:
                    raise Exception(f"Failed to load page after {max_retries} attempts: {e}")
                self.logger.warning(f"Retry attempt {attempt + 1} due to: {str(e)}")
                time.sleep(5)

    def handle_captcha(self, page: Page):
        """Gère la détection et résolution de CAPTCHA."""
        try:
            if page.locator("[data-captcha]").count() > 0:
                self.logger.warning("CAPTCHA detected!")
                print("\n⚠️ CAPTCHA detected. Please solve it manually...")
                page.screenshot(path=str(self.output_dir / "screenshots/captcha_detected.png"))
                page.wait_for_selector("[data-captcha]", state="detached", timeout=300000)
                self.logger.info("CAPTCHA solved successfully")
                print("✅ CAPTCHA solved. Continuing...")
        except Exception:
            pass

    def scrape_publication_data(self, page: Page):
        """Extrait les données des publications."""
        try:
            self.logger.info("Starting data scraping...")
            
            # Attendre avec un timeout plus long
            self.logger.info("Waiting for publications to load...")
            page.wait_for_selector(".bg-white.hover\\:bg-concrete-50", 
                                state="visible", 
                                timeout=30000)
            
            # Screenshot pour debug
            page.screenshot(path=str(self.output_dir / "screenshots/page_loaded.png"))
            
            # Vérifier le nombre de cartes
            cards = page.query_selector_all(".bg-white.hover\\:bg-concrete-50")
            count = len(cards)
            self.logger.info(f"Found {count} publication cards")
            
            if count == 0:
                self.logger.error("No publications found! Taking debug screenshot...")
                page.screenshot(path=str(self.output_dir / "screenshots/no_publications.png"))
                return
                
            for i, card in enumerate(cards, 1):
                try:
                    self.logger.info(f"Processing card {i}/{count}")
                    data = card.evaluate("""
                        card => {
                            const getData = (selector, attribute = 'textContent') => {
                                const element = card.querySelector(selector);
                                if (!element) {
                                    console.log(`Element not found for selector: ${selector}`);
                                    return 'N/A';
                                }
                                const value = attribute === 'textContent' ? 
                                    element.textContent.trim() : 
                                    element.getAttribute(attribute);
                                console.log(`Found ${selector}: ${value}`);
                                return value;
                            };
                            
                            return {
                                title: getData('h1.leading-5.font-bold'),
                                subtitle: getData('span.font-bold.text-sm'),
                                link: getData('a.underline.text-cairn-main', 'href'),
                                cover_image_url: getData('img', 'src'),
                                publisher: getData('div.text-xs.leading-4.font-bold')
                            };
                        }
                    """)
                    
                    if all(data.values()):
                        data["scrape_date"] = datetime.now().isoformat()
                        self.data.append(data)
                        self.logger.info(f"Successfully scraped: {data['title']}")
                    else:
                        self.logger.warning(f"Incomplete data found: {data}")
                    
                    self.human_delay()
                    
                except Exception as e:
                    self.logger.error(f"Error processing card {i}: {str(e)}")
                    continue
                    
            self.logger.info(f"Scraping completed. Total publications: {len(self.data)}")
                
        except Exception as e:
            self.logger.error(f"Error during scraping: {str(e)}")
            page.screenshot(path=str(self.output_dir / "screenshots/error_scraping_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"))

    def human_delay(self, min_time: float = 1.5, max_time: float = 3.5):
        """Simule un délai humain entre les actions."""
        delay = random.uniform(min_time, max_time)
        time.sleep(delay)

    def export_data(self):
        """Exporte les données dans tous les formats demandés."""
        if not self.data:
            self.logger.warning("No data to export!")
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for output_format in self.output_formats:
            try:
                if output_format == "txt":
                    file_name = self.output_dir / f"data/cairn_publications_{timestamp}.txt"
                    with open(file_name, "w", encoding="utf-8") as f:
                        # En-tête
                        f.write(f"Publications CAIRN - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                        
                        # Publications
                        for i, entry in enumerate(self.data, 1):
                            f.write(f"Publication {i}:\n")
                            f.write(f"Titre: {entry['title']}\n")
                            f.write(f"Type: {entry.get('publisher', 'Revue').split()[0]}\n")
                            f.write(f"Code: {entry['subtitle']}\n")
                            f.write(f"URL: {entry['link']}\n")
                            f.write(f"Couverture: {entry['cover_image_url']}\n")
                            f.write("-" * 50 + "\n\n")
                        
                elif output_format == "json":
                    file_name = self.output_dir / f"data/cairn_publications_{timestamp}.json"
                    with open(file_name, "w", encoding="utf-8") as f:
                        json.dump(self.data, f, ensure_ascii=False, indent=4)
                        
                elif output_format == "csv":
                    file_name = self.output_dir / f"data/cairn_publications_{timestamp}.csv"
                    with open(file_name, "w", newline='', encoding="utf-8") as f:
                        writer = csv.DictWriter(f, fieldnames=self.data[0].keys())
                        writer.writeheader()
                        writer.writerows(self.data)
                
                self.logger.info(f"Successfully exported {len(self.data)} records to {str(file_name)}")
                
            except Exception as e:
                self.logger.error(f"Error exporting {output_format} data: {e}")
                # Backup save attempt
                backup_file = self.output_dir / f"data/backup_export_{timestamp}.json"
                with open(backup_file, "w", encoding="utf-8") as f:
                    json.dump(self.data, f, ensure_ascii=False)
                    self.logger.info(f"Backup saved to {str(backup_file)}")

    def save_cookies(self, context: BrowserContext):
        """Sauvegarde les cookies de session."""
        cookies = context.cookies()
        cookie_file = self.output_dir / "data/cairn_cookies.json"
        with open(cookie_file, "w") as f:
            json.dump(cookies, f)

    def load_cookies(self, context: BrowserContext):
        """Charge les cookies précédemment sauvegardés."""
        try:
            cookie_file = self.output_dir / "data/cairn_cookies.json"
            with open(cookie_file, "r") as f:
                cookies = json.load(f)
                context.add_cookies(cookies)
        except FileNotFoundError:
            self.logger.info("No cookies file found, starting fresh session")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Cairn Publications Scraper')
    parser.add_argument('--formats', 
                       nargs='+',
                       default=['txt', 'json'],
                       choices=['txt', 'csv', 'json'],
                       help='Format(s) de sortie désirés')
    parser.add_argument('--proxy',
                       help='Proxy (optionnel, format: http://host:port)')
    
    args = parser.parse_args()
    
    scraper = CairnTurboScraper(
        proxy=args.proxy,
        output_formats=args.formats
    )
    scraper.run()