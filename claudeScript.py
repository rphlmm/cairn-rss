# pip install beautifulsoup4 requests feedgen pytz
# exécuter le script périodiquement avec un cron job:
# 0 */6 * * * python3 /chemin/vers/script.py

###

# Système de cache pour éviter doublons
import pickle

def load_cache():
    try:
        with open('feed_cache.pkl', 'rb') as f:
            return pickle.load(f)
    except:
        return set()

def save_cache(cache):
    with open('feed_cache.pkl', 'wb') as f:
        pickle.dump(cache, f)

# Dans la boucle de traitement:
cache = load_cache()
if revue_url not in cache:
    cache.add(revue_url)
    # Ajouter l'entrée au feed
save_cache(cache)

###

# Suivre les MàJ avec un logging
import logging

logging.basicConfig(
    filename='feed_updates.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# Dans le script:
logging.info(f"Nouvelle publication ajoutée: {full_title}")

#################

from bs4 import BeautifulSoup
import requests
from feedgen.feed import FeedGenerator
from datetime import datetime
import pytz

def scrape_cairn_publications():
    # URL de la page des dernières publications
    url = "https://shs.cairn.info/publications?tab=revues&sort=date-mise-en-ligne&discipline=11"
    
    # Headers pour simuler un navigateur
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # Récupération de la page
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Création du feed Atom
    fg = FeedGenerator()
    fg.id('https://shs.cairn.info/publications')
    fg.title('Dernières publications Cairn.info - Sociologie')
    fg.subtitle('Nouvelles revues de sociologie sur Cairn.info')
    fg.author({'name': 'Cairn.info'})
    fg.language('fr')
    fg.link(href=url, rel='alternate')
    fg.link(href='https://shs.cairn.info/feed.atom', rel='self')
    
    # Timezone Paris pour les dates
    paris_tz = pytz.timezone('Europe/Paris')
    
    # Pour chaque carte de publication
    publications = soup.find_all('div', class_='bg-white hover:bg-concrete-50')
    
    for pub in publications:
        try:
            # Création d'une entrée dans le feed
            fe = fg.add_entry()
            
            # Récupération des informations
            title_element = pub.find('h1', class_='font-serif')
            subtitle_element = pub.find('h2', class_='font-serif')
            publisher_element = pub.find('span', class_='font-bold text-sm')
            cover_img = pub.find('img', class_='border')
            link_element = pub.find('a', class_='underline text-cairn-main')
            
            # Construction du titre complet
            title = title_element.text.strip() if title_element else ''
            subtitle = subtitle_element.text.strip() if subtitle_element else ''
            full_title = f"{title} - {subtitle}" if subtitle else title
            
            # Extraction du numéro de la revue depuis l'URL de la couverture
            issue_number = cover_img['src'].split('/')[-3] if cover_img else ''
            
            # Construction de l'URL complète de la revue
            revue_url = f"https://shs.cairn.info{link_element['href']}" if link_element else ''
            
            # Ajout des informations à l'entrée
            fe.id(revue_url)
            fe.title(full_title)
            fe.link(href=revue_url)
            
            # Construction de la description
            description = f"""
            <div>
                <img src="{cover_img['src'] if cover_img else ''}" alt="Couverture" />
                <p><strong>Éditeur:</strong> {publisher_element.text if publisher_element else ''}</p>
                <p><strong>Numéro:</strong> {issue_number}</p>
            </div>
            """
            fe.content(content=description, type='html')
            
            # Date de mise à jour (utilisation de la date actuelle comme fallback)
            current_time = datetime.now(paris_tz)
            fe.updated(current_time)
            
        except Exception as e:
            print(f"Erreur lors du traitement d'une publication: {e}")
    
    # Génération du feed
    atomfeed = fg.atom_str(pretty=True)
    
    # Sauvegarde dans un fichier
    with open('cairn_feed.atom', 'wb') as f:
        f.write(atomfeed)
    
    return atomfeed

if __name__ == "__main__":
    scrape_cairn_publications()