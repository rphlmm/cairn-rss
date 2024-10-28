%pip install nodriver feedgen pytz

import nodriver as uc
from feedgen.feed import FeedGenerator
from datetime import datetime
import pytz
import logging
import re
from urllib.parse import urljoin
import asyncio

# Configuration du logging
logging.basicConfig(
    filename="updates.log",
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding='utf-8'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

async def load_existing_entries(feed_file):
    """Charge les identifiants des entrées existantes depuis un fichier de flux Atom."""
    try:
        fg = FeedGenerator()
        fg.load_atom(feed_file)
        return {entry.link[0].href for entry in fg.entry() if entry.link}
    except FileNotFoundError:
        logging.info("Aucun flux existant trouvé. Création d'un nouveau flux.")
        return set()
    except Exception as e:
        logging.error(f"Erreur lors du chargement du flux existant: {e}")
        return set()

async def parse_date(date_text):
    """Extrait et parse la date de publication."""
    try:
        # Format attendu sur Cairn : "Mise en ligne DD/MM/YYYY"
        date_match = re.search(r"(\d{2})/(\d{2})/(\d{4})", date_text)
        if date_match:
            jour, mois, annee = map(int, date_match.groups())
            return datetime(annee, mois, jour, tzinfo=pytz.timezone('Europe/Paris'))
    except Exception as e:
        logging.warning(f"Impossible de parser la date: {date_text}. Utilisation de la date actuelle.")
    return datetime.now(pytz.timezone('Europe/Paris'))

async def scrape_cairn_publications():
    """Scrape les publications de Cairn.info et génère un flux Atom."""
    # Configuration de base
    base_url = "https://shs.cairn.info"
    url = urljoin(base_url, "/publications")
    
    try:
        # Démarrage du navigateur avec nodriver
        browser = await uc.start(
            headless=True,  # Mode sans interface
            browser_args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu'
            ]
        )
        
        # Navigation vers la page
        page = await browser.get(url + "?tab=revues&sort=date-mise-en-ligne&discipline=11")
        logging.info("Page chargée avec succès")

        # Initialiser le générateur de flux Atom
        fg = FeedGenerator()
        fg.id(url)
        fg.title("Dernières publications de revues sur Cairn.info - Sociologie")
        fg.link(href=url, rel='alternate')
        fg.language('fr')
        fg.updated(datetime.now(pytz.timezone('Europe/Paris')))

        # Charger les entrées existantes
        existing_urls = await load_existing_entries("publications_cairn.atom")
        new_entries = 0

        # Attendre que les publications soient chargées
        publications = await page.select_all("div.grid.h-full")
        
        for pub in publications:
            try:
                # Vérification de la discipline (sociologie)
                discipline_elem = await pub.select("a.discipline")
                if discipline_elem:
                    discipline_text = await discipline_elem.get_text()
                    if "sociologie" not in discipline_text.lower():
                        continue

                # Extraction des éléments
                title_elem = await pub.select("h1.publication-title")
                title = await title_elem.get_text() if title_elem else "Titre inconnu"
                
                link_elem = await pub.select("a.publication-link")
                link = urljoin(base_url, await link_elem.get_property('href')) if link_elem else url
                
                editor_elem = await pub.select("span.font-bold")
                editor = await editor_elem.get_text() if editor_elem else "Éditeur inconnu"
                
                # Image de couverture
                img_elem = await pub.select("img")
                if img_elem:
                    cover_img = urljoin(base_url, await img_elem.get_property('src'))
                else:
                    cover_img = None
                
                # Date de publication
                date_elem = await pub.select("time.publication-date")
                if date_elem:
                    date_text = await date_elem.get_text()
                    pub_date = await parse_date(date_text)
                else:
                    pub_date = datetime.now(pytz.timezone('Europe/Paris'))

                # Vérifier les doublons
                if link not in existing_urls:
                    fe = fg.add_entry()
                    fe.id(link)
                    fe.title(title)
                    fe.link(href=link)
                    fe.author({"name": editor})
                    fe.published(pub_date)
                    
                    if cover_img:
                        fe.content(f"<img src='{cover_img}' alt='Couverture de {title}' />", type="html")
                    
                    logging.info(f"Nouvelle publication ajoutée: {title}")
                    new_entries += 1
                else:
                    logging.info(f"Doublon ignoré: {title}")

            except Exception as e:
                logging.error(f"Erreur lors du traitement d'une publication: {e}")
                continue

        # Enregistrer le flux Atom mis à jour
        if new_entries > 0:
            try:
                atom_feed = fg.atom_str(pretty=True)
                with open("publications_cairn.atom", "wb") as f:
                    f.write(atom_feed)
                logging.info(f"Flux Atom mis à jour avec {new_entries} nouvelles entrées.")
            except Exception as e:
                logging.error(f"Erreur lors de l'enregistrement du flux Atom: {e}")
        else:
            logging.info("Aucune nouvelle publication ajoutée au flux.")

    except Exception as e:
        logging.error(f"Erreur lors du scraping: {e}")
    
    finally:
        # Fermeture du navigateur
        try:
            await browser.close()
        except:
            pass

async def main():
    await scrape_cairn_publications()

if __name__ == "__main__":
    uc.loop().run_until_complete(main())