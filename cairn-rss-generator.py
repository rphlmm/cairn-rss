import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import datetime
import pytz
import hashlib

class CairnRSSGenerator:
    def __init__(self):
        self.url = "https://shs.cairn.info/publications?lang=fr&tab=revues&sort=date-mise-en-ligne"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def fetch_page(self):
        """Récupère le contenu de la page des revues"""
        response = requests.get(self.url, headers=self.headers)
        return response.text

    def parse_revues(self, html_content):
        """Parse le HTML pour extraire les informations des revues"""
        soup = BeautifulSoup(html_content, 'html.parser')
        revues = []
        
        # Trouve tous les blocs de revues
        for revue_block in soup.find_all('div', class_='bg-white hover:bg-concrete-50'):
            try:
                # Extrait les informations de base
                titre = revue_block.find('h1', class_='leading-5').text.strip()
                
                # Tente d'extraire le sous-titre s'il existe
                sous_titre = revue_block.find('h2', class_='font-serif')
                sous_titre = sous_titre.text.strip() if sous_titre else ''
                
                # Trouve l'éditeur
                editeur = revue_block.find('span', class_='font-bold text-sm').text.strip()
                
                # Trouve l'URL de la couverture
                img = revue_block.find('img', class_='border')
                cover_url = img['src'] if img else ''
                
                # Trouve le lien vers la revue
                link = revue_block.find('a', class_='underline')
                url = f"https://shs.cairn.info{link['href']}" if link else ''
                
                revues.append({
                    'titre': titre,
                    'sous_titre': sous_titre,
                    'editeur': editeur,
                    'cover_url': cover_url,
                    'url': url
                })
            except Exception as e:
                print(f"Erreur lors du parsing d'une revue: {e}")
                continue
                
        return revues

    def generate_feed(self, revues):
        """Génère le flux RSS à partir des données des revues"""
        fg = FeedGenerator()
        fg.title('Nouvelles revues Cairn.info')
        fg.description('Flux RSS des dernières revues publiées sur Cairn.info')
        fg.link(href=self.url)
        fg.language('fr')
        
        paris_tz = pytz.timezone('Europe/Paris')
        current_time = datetime.datetime.now(paris_tz)

        for revue in revues:
            fe = fg.add_entry()
            # Crée un ID unique basé sur l'URL de la revue
            entry_id = hashlib.sha256(revue['url'].encode()).hexdigest()
            
            fe.id(entry_id)
            fe.title(revue['titre'])
            
            # Construit une description HTML complète
            description = f"""
                <h2>{revue['titre']}</h2>
                {f"<h3>{revue['sous_titre']}</h3>" if revue['sous_titre'] else ''}
                <p>Éditeur: {revue['editeur']}</p>
                <img src="{revue['cover_url']}" alt="Couverture {revue['titre']}" style="max-width: 200px;"/>
                <p><a href="{revue['url']}">Consulter la revue sur Cairn.info</a></p>
            """
            
            fe.description(description)
            fe.link(href=revue['url'])
            fe.published(current_time)
            
        return fg

    def save_feed(self, feed, output_path='cairn_revues.xml'):
        """Sauvegarde le flux RSS dans un fichier"""
        feed.rss_file(output_path)

def main():
    generator = CairnRSSGenerator()
    html_content = generator.fetch_page()
    revues = generator.parse_revues(html_content)
    feed = generator.generate_feed(revues)
    generator.save_feed(feed)

if __name__ == "__main__":
    main()
