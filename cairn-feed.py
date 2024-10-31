from playwright.sync_api import sync_playwright, expect
from bs4 import BeautifulSoup
import os
import time
import random
from typing import Optional
import json
import csv
from datetime import datetime

class CairnScraper:
    def __init__(self):
        # Configuration des patches rebrowser
        os.environ['REBROWSER_PATCHES_RUNTIME_FIX_MODE'] = 'addBinding'
        os.environ['REBROWSER_PATCHES_SOURCE_URL'] = 'app.js'
        os.environ['REBROWSER_PATCHES_UTILITY_WORLD_NAME'] = 'util'
        
        # Paramètres de configuration
        self.USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
        self.BASE_URL = "https://shs.cairn.info"
        self.PROXY = None  # Configurer ici votre proxy si nécessaire : 'http://user:pass@ip:port'

    def human_delay(self, min_seconds: float = 2.0, max_seconds: float = 5.0):
        """Simule un délai humain aléatoire"""
        time.sleep(random.uniform(min_seconds, max_seconds))

    def create_browser_context(self, browser):
        """Configure le contexte du navigateur avec des paramètres réalistes"""
        return browser.new_context(
            viewport={'width': random.randint(1280, 1920), 'height': random.randint(800, 1080)},
            user_agent=self.USER_AGENT,
            locale='fr-FR',
            timezone_id='Europe/Paris',
            permissions=['geolocation'],
            color_scheme='light',
            device_scale_factor=1,
            is_mobile=False,
            has_touch=True,
            java_script_enabled=True,
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'DNT': '1',
                'Upgrade-Insecure-Requests': '1',
                'sec-ch-ua': '"Google Chrome";v="130", "Chromium";v="130", "Not_A Brand";v="99"',
                'sec-ch-ua-platform': '"macOS"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1'
            }
        )

    def handle_captcha(self, page) -> bool:
        """Tente de détecter et gérer la présence d'un CAPTCHA"""
        try:
            captcha = page.query_selector("text=Glissez vers la droite pour compléter le puzzle")
            if captcha:
                print("CAPTCHA détecté! Tentative de gestion...")
                # Ici, on pourrait implémenter une solution de résolution de CAPTCHA
                # Pour l'instant, on attend l'intervention humaine
                print("Action humaine requise pour le CAPTCHA")
                page.pause()  # Permet l'intervention manuelle
                return True
        except Exception as e:
            print(f"Erreur lors de la gestion du CAPTCHA: {e}")
        return False

    def scrape_publication_data(self, card) -> Optional[dict]:
        """Extrait les données d'une carte de publication"""
        try:
            publication = {}
            
            # Image de couverture
            cover = card.select_one('img.border.border-silver-chalice-400.rounded-md')
            if cover:
                publication['cover'] = {
                    'url': cover.get('src'),
                    'alt': cover.get('alt')
                }
            
            # Type de publication
            type_el = card.select_one('h3.grow')
            if type_el:
                publication['type'] = ' '.join(type_el.get_text(strip=True).split())
            
            # Titre
            title = card.select_one('h1.leading-5.font-bold')
            if title:
                publication['title'] = title.get_text(strip=True)
            
            # Code
            code = card.select_one('span.font-bold.text-sm')
            if code:
                publication['code'] = code.get_text(strip=True)
            
            # URL
            link = card.select_one('a.underline.text-cairn-main')
            if link:
                href = link.get('href')
                if href:
                    publication['url'] = self.BASE_URL + href if not href.startswith('http') else href
            
            return publication
        except Exception as e:
            print(f"Erreur lors de l'extraction des données: {e}")
            return None

    def export_data(self, publications, format='json'):
        """Exporte les données dans différents formats"""
        # Créer un dossier 'exports' s'il n'existe pas
        os.makedirs('exports', exist_ok=True)
        
        # Créer un timestamp pour le nom du fichier
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format.lower() == 'json':
            filename = f'exports/cairn_publications_{timestamp}.json'
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(publications, f, ensure_ascii=False, indent=2)
            print(f"Données exportées dans {filename}")

        elif format.lower() == 'csv':
            filename = f'exports/cairn_publications_{timestamp}.csv'
            with open(filename, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['title', 'type', 'code', 'url', 'cover_url', 'cover_alt'])
                writer.writeheader()
                for pub in publications:
                    row = {
                        'title': pub.get('title'),
                        'type': pub.get('type'),
                        'code': pub.get('code'),
                        'url': pub.get('url'),
                        'cover_url': pub.get('cover', {}).get('url'),
                        'cover_alt': pub.get('cover', {}).get('alt')
                    }
                    writer.writerow(row)
            print(f"Données exportées dans {filename}")

        elif format.lower() == 'txt':
            filename = f'exports/cairn_publications_{timestamp}.txt'
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Publications CAIRN - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                for i, pub in enumerate(publications, 1):
                    f.write(f"Publication {i}:\n")
                    f.write(f"Titre: {pub.get('title', 'N/A')}\n")
                    f.write(f"Type: {pub.get('type', 'N/A')}\n")
                    f.write(f"Code: {pub.get('code', 'N/A')}\n")
                    f.write(f"URL: {pub.get('url', 'N/A')}\n")
                    if 'cover' in pub:
                        f.write(f"Couverture: {pub['cover'].get('url', 'N/A')}\n")
                    f.write("-" * 50 + "\n\n")
            print(f"Données exportées dans {filename}")

    def scrape_publications(self):
        """Fonction principale de scraping"""
        with sync_playwright() as p:
            browser_args = [
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu'
            ]

            browser = p.chromium.launch(
                headless=False,  # False pour voir ce qui se passe
                args=browser_args,
                proxy={'server': self.PROXY} if self.PROXY else None
            )

            context = self.create_browser_context(browser)
            page = context.new_page()

            try:
                # Configuration des événements de page
                page.set_default_timeout(60000)
                page.set_default_navigation_timeout(60000)

                # Navigation avec simulation de comportement humain
                url = f"{self.BASE_URL}/publications?lang=fr&tab=revues&content-domain=shs&sort=date-mise-en-ligne"
                print("Navigation vers la page...")
                response = page.goto(url)
                
                if not response or not response.ok:
                    raise Exception(f"Erreur de navigation: {response.status if response else 'No response'}")

                # Attente du chargement initial
                self.human_delay(3, 6)
                
                # Vérification du CAPTCHA
                if self.handle_captcha(page):
                    print("CAPTCHA détecté et géré")
                
                # Attente du chargement complet
                print("Attente du chargement complet...")
                page.wait_for_load_state('networkidle')
                self.human_delay(2, 4)

                # Extraction des données
                print("Extraction des données...")
                content = page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Sélection des cartes de publication
                publication_cards = soup.select('div.grid > div.rounded-xl')
                publications = []

                print(f"Nombre de cartes trouvées: {len(publication_cards)}")

                for card in publication_cards:
                    publication = self.scrape_publication_data(card)
                    if publication:
                        publications.append(publication)
                        self.human_delay(0.5, 1.5)

                # Export et affichage des résultats
                if not publications:
                    print("Aucune publication trouvée")
                    page.screenshot(path="exports/debug_screenshot.png")
                    with open("exports/debug_content.html", "w", encoding="utf-8") as f:
                        f.write(content)
                else:
                    print(f"\nPublications trouvées: {len(publications)}")
                    # Export dans différents formats
                    self.export_data(publications, 'json')
                    self.export_data(publications, 'csv')
                    self.export_data(publications, 'txt')

                return publications

            except Exception as e:
                print(f"Erreur lors du scraping: {e}")
                # Capture d'erreur
                try:
                    page.screenshot(path="exports/error_screenshot.png")
                    with open("exports/error_content.html", "w", encoding="utf-8") as f:
                        f.write(page.content())
                    print("Capture d'erreur sauvegardée dans le dossier exports/")
                except:
                    pass
                return None

            finally:
                context.close()
                browser.close()

def main():
    scraper = CairnScraper()
    publications = scraper.scrape_publications()
    
    if publications:
        print(f"\nScraping terminé avec succès. {len(publications)} publications récupérées.")
        print("Les données ont été exportées dans le dossier 'exports/'")
    else:
        print("\nÉchec du scraping.")

if __name__ == "__main__":
    main()