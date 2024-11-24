from playwright.sync_api import sync_playwright
import json
import time
import random

def random_delay(min_seconds=2, max_seconds=5):
    time.sleep(random.uniform(min_seconds, max_seconds))

def scrape_publications():
    publications = []
    
    with sync_playwright() as p:
        # Configuration du navigateur avec Rebrowser
        browser = p.chromium.launch(
            headless=False,  # Mode non-headless recommandé
        )
        
        # Configuration du contexte avec des paramètres réalistes
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='fr-FR',
            timezone_id='Europe/Paris'
        )

        page = context.new_page()
        
        # Configuration des en-têtes supplémentaires
        page.set_extra_http_headers({
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        })

        for page_num in range(1, 12):
            try:
                print(f"Traitement de la page {page_num}/11...")
                
                # Navigation avec gestion d'erreur
                try:
                    page.goto(
                        f'https://shs.cairn.info/publications?lang=fr&tab=revues&page={page_num}',
                        wait_until='networkidle',
                        timeout=30000
                    )
                except Exception as e:
                    print(f"Erreur lors de la navigation page {page_num}: {str(e)}")
                    continue

                random_delay(3, 6)  # Délai aléatoire entre les pages

                # Extraction des publications
                cards = page.query_selector_all('.bg-white.hover\\:bg-concrete-50')
                
                for card in cards:
                    try:
                        # Extraction avec gestion des erreurs pour chaque champ
                        try:
                            title = card.query_selector('.font-serif.font-bold').inner_text().strip()
                        except:
                            title = None

                        try:
                            subtitle_el = card.query_selector('.font-serif:not(.font-bold)')
                            subtitle = subtitle_el.inner_text().strip() if subtitle_el else None
                        except:
                            subtitle = None

                        try:
                            publisher = card.query_selector('.text-sm.font-bold').inner_text().strip()
                        except:
                            publisher = None

                        try:
                            img = card.query_selector('img')
                            cover_image = img.get_attribute('src') if img else None
                        except:
                            cover_image = None

                        try:
                            url = card.query_selector('a[href*="revue"]').get_attribute('href')
                            pub_id = url.split('revue-')[1].split('?')[0] if 'revue-' in url else None
                        except:
                            url = None
                            pub_id = None

                        if title and url:  # Ne sauvegarde que si on a au moins le titre et l'URL
                            publication = {
                                'id': pub_id,
                                'title': title,
                                'subtitle': subtitle,
                                'publisher': publisher,
                                'coverImage': cover_image,
                                'url': url
                            }
                            publications.append(publication)
                            print(f"Publication extraite: {title}")

                    except Exception as e:
                        print(f"Erreur lors de l'extraction d'une publication: {str(e)}")
                        continue

                # Sauvegarde intermédiaire après chaque page
                save_publications(publications, f'publications_page_{page_num}.json')
                random_delay(2, 4)  # Délai aléatoire avant la page suivante

            except Exception as e:
                print(f"Erreur lors du traitement de la page {page_num}: {str(e)}")
                continue

        browser.close()
        
    return publications

def save_publications(publications, filename='publications.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(
            {
                'total': len(publications),
                'publications': publications,
                'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
            }, 
            f, 
            ensure_ascii=False, 
            indent=2
        )

if __name__ == "__main__":
    print("Démarrage du scraping des publications Cairn.info...")
    try:
        publications = scrape_publications()
        print(f"Scraping terminé avec succès - {len(publications)} publications extraites")
        save_publications(publications)
        print(f"Données sauvegardées dans publications.json")
    except Exception as e:
        print(f"Erreur lors du scraping: {str(e)}")
