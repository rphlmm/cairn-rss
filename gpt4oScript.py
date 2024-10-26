# pip install beautifulsoup4 feedgen requests
# cron:
# crontab -e
# 0 * * * * /usr/bin/python3 /chemin/vers/votre_script.py

###

# Gestion des doublons:
from feedgen.entry import FeedEntry

# Charger le flux existant
try:
    existing_feed = fg.atom_file("publications_cairn.atom")
    existing_ids = {entry.id for entry in existing_feed.entries}
except FileNotFoundError:
    existing_ids = set()  # Aucun flux n'existe encore

# Ajouter des entrées uniquement si elles sont nouvelles
for publication in soup.select(".grid .h-full"):
    link = publication.select_one("a[href]")["href"] if publication.select_one("a[href]") else url
    if link not in existing_ids:
        fe = fg.add_entry()
        fe.id(link)
        # Reste des informations de l'entrée...

# Écrire le flux mis à jour
atom_feed = fg.atom_str(pretty=True)
with open("publications_cairn.atom", "wb") as f:
    f.write(atom_feed)

###

# Initialiser un logging
import logging
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

# Configurer le logger
logging.basicConfig(
    filename="updates.log",  # fichier de log
    filemode="a",  # mode ajout pour ne pas écraser les logs existants
    level=logging.INFO,  # niveau de log: INFO et supérieur
    format="%(asctime)s - %(levelname)s - %(message)s"  # format des messages
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

###

# Ajouter le logging dans le script
# URL de la page des publications
url = "https://shs.cairn.info/publications?tab=revues&sort=date-mise-en-ligne&discipline=11"

# Début de l'exécution
logging.info("Début du scraping et de la mise à jour du flux Atom.")

try:
    # Récupérer la page HTML
    response = requests.get(url)
    response.raise_for_status()
    html_content = response.content
    logging.info("Page HTML récupérée avec succès.")

except requests.RequestException as e:
    logging.error(f"Erreur lors de la récupération de la page HTML: {e}")
    exit()

# Analyser le contenu HTML avec BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Initialiser le générateur de flux Atom
fg = FeedGenerator()
fg.id(url)
fg.title("Dernières publications de revues sur Cairn.info - Sociologie")
fg.link(href=url, rel='alternate')
fg.language('fr')
fg.updated(datetime.utcnow())

# Charger les publications existantes pour éviter les doublons
try:
    existing_feed = fg.atom_file("publications_cairn.atom")
    existing_ids = {entry.id for entry in existing_feed.entries}
    logging.info("Flux Atom existant chargé pour éviter les doublons.")
except FileNotFoundError:
    existing_ids = set()
    logging.info("Aucun flux existant. Création d'un nouveau flux Atom.")

# Extraire chaque carte de publication
new_entries = 0
for publication in soup.select(".grid .h-full"):
    title = publication.select_one("h1").get_text(strip=True) if publication.select_one("h1") else "Titre inconnu"
    link = publication.select_one("a[href]")["href"] if publication.select_one("a[href]") else url
    editor = publication.select_one("span.font-bold.text-sm").get_text(strip=True) if publication.select_one("span.font-bold.text-sm") else "Éditeur inconnu"
    cover_img = publication.select_one("img")["src"] if publication.select_one("img") else None

    if link not in existing_ids:
        fe = fg.add_entry()
        fe.id(link)
        fe.title(title)
        fe.link(href=link)
        fe.author({"name": editor})
        fe.published(datetime.utcnow())
        
        # Ajouter une image de couverture si disponible
        if cover_img:
            fe.content(f"<img src='{cover_img}' alt='Couverture de {title}' />", type="html")
        
        logging.info(f"Nouvelle publication ajoutée: {title}")
        new_entries += 1

# Générer et enregistrer le flux Atom
atom_feed = fg.atom_str(pretty=True)
with open("publications_cairn.atom", "wb") as f:
    f.write(atom_feed)

logging.info(f"Mise à jour du flux Atom terminée avec {new_entries} nouvelles entrées.")

###############

import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime

# URL de la page des publications
url = "https://shs.cairn.info/publications?tab=revues&sort=date-mise-en-ligne&discipline=11"

# Envoyer une requête pour récupérer la page HTML
response = requests.get(url)
response.raise_for_status()
html_content = response.content

# Analyser le contenu HTML avec BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Initialiser le générateur de flux Atom
fg = FeedGenerator()
fg.id(url)
fg.title("Dernières publications de revues sur Cairn.info - Sociologie")
fg.link(href=url, rel='alternate')
fg.language('fr')
fg.updated(datetime.utcnow())

# Extraire chaque carte de publication
for publication in soup.select(".grid .h-full"):
    title = publication.select_one("h1").get_text(strip=True) if publication.select_one("h1") else "Titre inconnu"
    link = publication.select_one("a[href]")["href"] if publication.select_one("a[href]") else url
    editor = publication.select_one("span.font-bold.text-sm").get_text(strip=True) if publication.select_one("span.font-bold.text-sm") else "Éditeur inconnu"
    cover_img = publication.select_one("img")["src"] if publication.select_one("img") else None
    
    # Créer une entrée pour chaque publication dans le flux Atom
    fe = fg.add_entry()
    fe.id(link)
    fe.title(title)
    fe.link(href=link)
    fe.author({"name": editor})
    fe.published(datetime.utcnow())
    
    # Ajouter une image de couverture si disponible
    if cover_img:
        fe.content(f"<img src='{cover_img}' alt='Couverture de {title}' />", type="html")

# Générer et enregistrer le flux Atom
atom_feed = fg.atom_str(pretty=True)
with open("publications_cairn.atom", "wb") as f:
    f.write(atom_feed)

print("Le flux Atom a été généré avec succès et sauvegardé sous 'publications_cairn.atom'")

