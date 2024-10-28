%npm install rebrowser-puppeteer

# Importations nécessaires pour Puppeteer et le reste du script
import asyncio
from pyppeteer import launch  # pyppeteer pour Puppeteer
import logging
import pickle
from datetime import datetime
from pathlib import Path
import pytz
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

# Configuration des URLs et fichiers
BASE_URL = "https://shs.cairn.info"
PUBLICATIONS_URL = f"{BASE_URL}/publications?tab=revues&sort=date-mise-en-ligne&discipline=11"
CACHE_FILE = "feed_cache.pkl"
FEED_FILE = "cairn_feed.atom"
LOG_FILE = "feed_updates.log"
PARIS_TZ = pytz.timezone('Europe/Paris')

class CairnFeedGenerator:
    def __init__(self):
        self._setup_logging()
        self.cache = self._load_cache()
        self.fg = None
        self.new_entries = 0

    def _setup_logging(self):
        """Configure le système de logging avec fichier et console."""
        logging.basicConfig(
            filename=LOG_FILE,
            filemode='a',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)
        logging.info("Démarrage du script de génération du flux Atom Cairn")

    def _load_cache(self):
        """Charge le cache des URLs déjà traitées."""
        try:
            with open(CACHE_FILE, 'rb') as f:
                return pickle.load(f)
        except (FileNotFoundError, pickle.UnpicklingError):
            logging.warning("Cache non trouvé ou corrompu. Création d'un nouveau cache.")
            return set()

    def _save_cache(self):
        """Sauvegarde le cache des URLs traitées."""
        try:
            with open(CACHE_FILE, 'wb') as f:
                pickle.dump(self.cache, f)
            logging.info("Cache sauvegardé avec succès")
        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde du cache: {e}")

    async def _get_html_content(self):
        """Utilise Puppeteer via Pyppeteer pour récupérer le contenu HTML de la page des publications."""
        browser = await launch(
            headless=True,
            args=['--no-sandbox'],
            executablePath='/path/to/node_modules/.bin/rebrowser-puppeteer'  # Remplacez par le chemin correct
        )
        page = await browser.newPage()
        await page.goto(PUBLICATIONS_URL)
        content = await page.content()
        await browser.close()
        return content

    def _initialize_feed(self):
        """Initialise le générateur de flux Atom."""
        self.fg = FeedGenerator()
        self.fg.id(PUBLICATIONS_URL)
        self.fg.title('Dernières publications Cairn.info - Sociologie')
        self.fg.subtitle('Nouvelles revues de sociologie sur Cairn.info')
        self.fg.author({'name': 'Cairn.info'})
        self.fg.language('fr')
        self.fg.link(href=PUBLICATIONS_URL, rel='alternate')
        self.fg.link(href=f'{BASE_URL}/feed.atom', rel='self')
        self.fg.updated(datetime.now(PARIS_TZ))

    def _extract_publication_info(self, pub):
        """Extrait les informations d'une publication."""
        try:
            title_element = pub.find('h1', class_='font-serif')
            subtitle_element = pub.find('h2', class_='font-serif')
            publisher_element = pub.find('span', class_='font-bold text-sm')
            cover_img = pub.find('img', class_='border')
            link_element = pub.find('a', class_='underline text-cairn-main')

            title = title_element.text.strip() if title_element else ''
            subtitle = subtitle_element.text.strip() if subtitle_element else ''
            full_title = f"{title} - {subtitle}" if subtitle else title
            issue_number = cover_img['src'].split('/')[-3] if cover_img else ''
            revue_url = f"{BASE_URL}{link_element['href']}" if link_element else ''
            publisher = publisher_element.text.strip() if publisher_element else ''
            cover_url = cover_img['src'] if cover_img else ''

            return {
                'title': full_title,
                'url': revue_url,
                'publisher': publisher,
                'cover_url': cover_url,
                'issue_number': issue_number
            }
        except Exception as e:
            logging.error(f"Erreur lors de l'extraction des informations: {e}")
            return None

    def _add_feed_entry(self, info):
        """Ajoute une entrée au flux Atom."""
        if not info or info['url'] in self.cache:
            return False

        try:
            fe = self.fg.add_entry()
            fe.id(info['url'])
            fe.title(info['title'])
            fe.link(href=info['url'])
            fe.author({'name': info['publisher']})
            fe.updated(datetime.now(PARIS_TZ))

            description = f"""
            <div>
                <img src="{info['cover_url']}" alt="Couverture" />
                <p><strong>Éditeur:</strong> {info['publisher']}</p>
                <p><strong>Numéro:</strong> {info['issue_number']}</p>
            </div>
            """
            fe.content(content=description, type='html')

            self.cache.add(info['url'])
            self.new_entries += 1
            logging.info(f"Nouvelle publication ajoutée: {info['title']}")
            return True
        except Exception as e:
            logging.error(f"Erreur lors de l'ajout de l'entrée au flux: {e}")
            return False

    async def generate_feed(self):
        """Génère le flux Atom complet en utilisant Puppeteer pour récupérer le contenu."""
        try:
            self._initialize_feed()
            html_content = await self._get_html_content()
            soup = BeautifulSoup(html_content, 'html.parser')
            publications = soup.find_all('div', class_='bg-white hover:bg-concrete-50')

            for pub in publications:
                info = self._extract_publication_info(pub)
                self._add_feed_entry(info)

            atom_feed = self.fg.atom_str(pretty=True)
            with open(FEED_FILE, 'wb') as f:
                f.write(atom_feed)

            self._save_cache()
            logging.info(f"Génération du flux terminée. {self.new_entries} nouvelles publications ajoutées.")
        except Exception as e:
            logging.error(f"Erreur lors de la génération du flux: {e}")
            raise

def main():
    generator = CairnFeedGenerator()
    asyncio.run(generator.generate_feed())

if __name__ == "__main__":
    main()
