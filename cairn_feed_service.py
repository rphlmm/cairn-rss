# cairn_feed_service.py

import time
from pathlib import Path
import json
from typing import Set, Dict

class CairnFeedService:
    """Service de surveillance des publications CAIRN et mise à jour du flux Atom."""
    
    def __init__(self, check_interval: int = 3600):
        """
        Args:
            check_interval: Intervalle de vérification en secondes (défaut: 1h)
        """
        self.check_interval = check_interval
        self.known_publications: Set[str] = set()
        self.load_known_publications()
        
    def load_known_publications(self):
        """Charge l'historique des publications déjà traitées."""
        history_file = Path("output/data/publication_history.json")
        if history_file.exists():
            with open(history_file, "r", encoding="utf-8") as f:
                self.known_publications = set(json.load(f))
    
    def save_known_publications(self):
        """Sauvegarde l'historique des publications."""
        history_file = Path("output/data/publication_history.json")
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(list(self.known_publications), f)
    
    def process_new_publications(self, publications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filtre et retourne uniquement les nouvelles publications."""
        new_publications = []
        
        for pub in publications:
            pub_id = pub["link"]  # URL comme identifiant unique
            if pub_id not in self.known_publications:
                new_publications.append(pub)
                self.known_publications.add(pub_id)
        
        if new_publications:
            self.save_known_publications()
            
        return new_publications
    
    def run_forever(self):
        """Execute le service indéfiniment."""
        while True:
            try:
                # Scrape les données actuelles
                scraper = CairnTurboScraper(output_formats=["atom"])
                scraper.run()
                
                # Vérifie les nouvelles publications
                new_publications = self.process_new_publications(scraper.data)
                
                if new_publications:
                    # Mise à jour du flux atom avec les nouvelles publications uniquement
                    feed_generator = CairnAtomFeedGenerator(Path("output"))
                    for pub in new_publications:
                        feed_generator.add_publication(pub)
                    feed_generator.generate()
                    
                    print(f"Flux Atom mis à jour avec {len(new_publications)} nouvelles publications")
                
                # Attente avant prochaine vérification
                time.sleep(self.check_interval)
                
            except Exception as e:
                print(f"Erreur durant l'exécution : {e}")
                # Attente plus courte en cas d'erreur
                time.sleep(300)  # 5 minutes

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Service de surveillance CAIRN")
    parser.add_argument("--interval", 
                       type=int,
                       default=3600,
                       help="Intervalle de vérification en secondes")
    
    args = parser.parse_args()
    
    service = CairnFeedService(check_interval=args.interval)
    print("Démarrage du service de surveillance CAIRN...")
    service.run_forever()