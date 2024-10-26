# Installer les bibliothèques nécessaires : beautifulsoup4, feedgen, requests
# pip install beautifulsoup4 feedgen requests pytz

import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime
import pytz
import logging

# Configurer le logging avec affichage en console et en fichier
logging.basicConfig(
    filename="updates.log",
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

def load_existing_entries(feed_file):
    """Charge les identifiants des entrées existantes depuis un fichier de flux Atom pour éviter les doublons."""
    try:
        fg = FeedGenerator()
        fg.load_atom(feed_file)
        return {entry.id() for entry in fg.entry() if entry.id()}
    except FileNotFoundError:
        logging.info("Aucun flux existant trouvé. Création d'un nouveau flux.")
        return set()

def scrape_cairn_publications():
    # URL de la page des dernières publications
    url = "https://shs.cairn.info/publications?tab=revues&sort=date-mise-en-ligne&discipline=11"
    
    # Configurer les en-têtes pour simuler un navigateur
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # Obtenir et analyser la page HTML
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html_content = response.text
        logging.info("Page HTML récupérée avec succès.")
    except requests.RequestException as e:
        logging.error(f"Erreur lors de la récupération de la page HTML: {e}")
        return

    soup = BeautifulSoup(html_content, 'html.parser')

    # Initialiser le générateur de flux Atom
    fg = FeedGenerator()
    fg.id(url)
    fg.title("Dernières publications de revues sur Cairn.info - Sociologie")
    fg.link(href=url, rel='alternate')
    fg.language('fr')
    fg.updated(datetime.now(pytz.timezone('Europe/Paris')))

    # Charger les entrées existantes pour éviter les doublons
    existing_ids = load_existing_entries("publications_cairn.atom")
    new_entries = 0

    # Extraire et traiter chaque carte de publication
    for pub in soup.find_all("div", class_="grid h-full"):
        try:
            # Extraction des éléments
            title = pub.find("h1").get_text(strip=True) if pub.find("h1") else "Titre inconnu"
            link = pub.find("a", href=True)["href"] if pub.find("a", href=True) else url
            editor = pub.find("span", class_="font-bold text-sm").get_text(strip=True) if pub.find("span", class_="font-bold text-sm") else "Éditeur inconnu"
            cover_img = pub.find("img")["src"] if pub.find("img") else None

            # Vérifier les doublons
            if link not in existing_ids:
                fe = fg.add_entry()
                fe.id(link)
                fe.title(title)
                fe.link(href=link)
                fe.author({"name": editor})
                fe.published(datetime.now(pytz.timezone('Europe/Paris')))
                
                # Ajouter une image de couverture si disponible
                if cover_img:
                    fe.content(f"<img src='{cover_img}' alt='Couverture de {title}' />", type="html")
                
                logging.info(f"Nouvelle publication ajoutée: {title}")
                new_entries += 1
            else:
                logging.info(f"Doublon ignoré: {title}")

        except Exception as e:
            logging.error(f"Erreur lors du traitement d'une publication: {e}")

    # Enregistrer le flux Atom mis à jour
    if new_entries > 0:
        atom_feed = fg.atom_str(pretty=True)
        with open("publications_cairn.atom", "wb") as f:
            f.write(atom_feed)
        logging.info(f"Flux Atom mis à jour avec {new_entries} nouvelles entrées.")
    else:
        logging.info("Aucune nouvelle publication ajoutée au flux.")

if __name__ == "__main__":
    scrape_cairn_publications()
