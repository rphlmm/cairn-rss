import nodriver
import logging
import pickle
import asyncio
import contextlib
import aiohttp
from datetime import datetime, timedelta
from pathlib import Path
import pytz
from feedgen.feed import FeedGenerator
from urllib.parse import urljoin, urlparse
import re
import signal
from typing import AsyncGenerator, Dict, Set, Optional
from time import perf_counter
import html

# Configuration
BASE_URL = "https://shs.cairn.info"
PUBLICATIONS_URL = f"{BASE_URL}/publications?tab=revues&sort=date-mise-en-ligne&discipline=11"
CACHE_FILE = "feed_cache.pkl"
FEED_FILE = "cairn_feed.atom"
LOG_FILE = "feed_updates.log"
PARIS_TZ = pytz.timezone('Europe/Paris')
BATCH_SIZE = 50
MAX_RETRIES = 3
MAX_CACHE_AGE_DAYS = 30
REQUEST_TIMEOUT = 30

# Sélecteurs CSS
SELECTORS = {
    'discipline': "a.discipline",
    'title': "h1.publication-title",
    'subtitle': "h2.font-serif",
    'link': "a.publication-link",
    'publisher': "span.font-bold.text-sm",
    'image': "img.publication-cover",
    'date': "time.publication-date"
}

class CacheEntry:
    def __init__(self, url: str, timestamp: datetime):
        self.url = url
        self.timestamp = timestamp

class CairnFeedGenerator:
    def __init__(self):
        self._setup_logging()
        self.cache: Dict[str, CacheEntry] = self._load_cache()
        self.browser = None
        self.page = None
        self.fg = None
        self.new_entries = 0
        self.metrics = {
            'start_time': None,
            'total_processed': 0,
            'successful_extractions': 0,
            'failed_extractions': 0
        }

    def _setup_logging(self):
        """Configure le système de logging avec fichier et console."""
        logging.basicConfig(
            filename=LOG_FILE,
            filemode='a',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            encoding='utf-8'
        )
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)
        logging.info("Démarrage du générateur de flux Atom Cairn")

    def _log_warning(self, message: str) -> None:
        """Fonction centralisée pour les avertissements de logs."""
        logging.warning(message)

    def _load_cache(self) -> Dict[str, CacheEntry]:
        """Charge le cache des URLs déjà traitées."""
        try:
            with open(CACHE_FILE, 'rb') as f:
                cache_data = pickle.load(f)
                return {url: entry for url, entry in cache_data.items()
                       if (datetime.now(PARIS_TZ) - entry.timestamp).days < MAX_CACHE_AGE_DAYS}
        except (FileNotFoundError, pickle.UnpicklingError):
            self._log_warning("Cache non trouvé ou corrompu. Création d'un nouveau cache.")
            return {}

    def _save_cache(self) -> None:
        """Sauvegarde le cache des URLs traitées."""
        try:
            with open(CACHE_FILE, 'wb') as f:
                pickle.dump(self.cache, f)
            logging.info(f"Cache sauvegardé avec succès ({len(self.cache)} entrées)")
        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde du cache: {e}")

    def _clean_old_cache_entries(self) -> None:
        """Nettoie les entrées anciennes du cache."""
        current_time = datetime.now(PARIS_TZ)
        self.cache = {
            url: entry for url, entry in self.cache.items()
            if (current_time - entry.timestamp).days < MAX_CACHE_AGE_DAYS
        }

    def _validate_url(self, url: str) -> bool:
        """Valide une URL."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def _sanitize_text(self, text: str) -> str:
        """Nettoie et sanitize un texte."""
        if not text:
            return ""
        return html.escape(
            text.strip()
            .replace('\x00', '')
            .replace('\r', ' ')
            .replace('\n', ' ')
            .replace('\t', ' ')
        )

    async def _with_retry(self, coro, max_retries: int = MAX_RETRIES):
        """Exécute une coroutine avec retry en cas d'échec."""
        for attempt in range(max_retries):
            try:
                return await coro
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = 2 ** attempt
                logging.warning(f"Tentative {attempt + 1}/{max_retries} échouée. Attente de {wait_time}s. Erreur: {e}")
                await asyncio.sleep(wait_time)

    @contextlib.asynccontextmanager
    async def _browser_context(self) -> AsyncGenerator:
        """Gestion du contexte du navigateur avec async context manager."""
        try:
            self.browser = await nodriver.start(
                headless=True,
                browser_args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--disable-gpu'
                ],
                timeout=REQUEST_TIMEOUT
            )
            logging.info("Navigateur démarré")
            yield self.browser
        finally:
            if self.browser:
                await self.browser.close()
                logging.info("Navigateur fermé proprement")
                self.browser = None
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

    async def parse_date(self, date_text: str) -> datetime:
        """Parse une date de publication Cairn."""
        try:
            date_match = re.search(r"(\d{2})/(\d{2})/(\d{4})", self._sanitize_text(date_text))
            if date_match:
                jour, mois, annee = map(int, date_match.groups())
                return datetime(annee, mois, jour, tzinfo=PARIS_TZ)
        except Exception as e:
            self._log_warning(f"Impossible de parser la date: {date_text}. {e}")
        return datetime.now(PARIS_TZ)

    async def extract_publication_info(self, publication):
        """Extrait les informations d'une publication avec les méthodes correctes de sélection DOM."""
        try:
            if not publication:
                self._log_warning("Publication invalide (None)")
                return None

            self.metrics['total_processed'] += 1

            # Vérification de la discipline avec querySelector
            discipline_elem = await publication.querySelector(SELECTORS['discipline'])
            if discipline_elem is not None:
                discipline_text = await discipline_elem.evaluate('element => element.textContent')
                if "sociologie" not in discipline_text.lower():
                    logging.debug("Publication non sociologique ignorée")
                    return None
            else:
                return None

            # Extraction du titre
            title_elem = await publication.querySelector(SELECTORS['title'])
            if title_elem is None:
                self._log_warning("Titre manquant dans la publication")
                return None
            title_text = self._sanitize_text(
                await title_elem.evaluate('element => element.textContent')
            )

            # Extraction du sous-titre
            subtitle_text = ""
            subtitle_elem = await publication.querySelector(SELECTORS['subtitle'])
            if subtitle_elem is not None:
                subtitle_text = self._sanitize_text(
                    await subtitle_elem.evaluate('element => element.textContent')
                )

            # Extraction du lien
            link_elem = await publication.querySelector(SELECTORS['link'])
            if link_elem is None:
                self._log_warning("Lien manquant dans la publication")
                return None
            url = await link_elem.evaluate('element => element.href')
            if not url or not self._validate_url(url):
                self._log_warning("URL invalide dans la publication")
                return None
            full_url = urljoin(BASE_URL, url)

            # Extraction de l'éditeur
            publisher_text = "Éditeur inconnu"
            publisher_elem = await publication.querySelector(SELECTORS['publisher'])
            if publisher_elem is not None:
                publisher_text = self._sanitize_text(
                    await publisher_elem.evaluate('element => element.textContent')
                )

            # Extraction de l'image
            cover_url = ""
            img_elem = await publication.querySelector(SELECTORS['image'])
            if img_elem is not None:
                src = await img_elem.evaluate('element => element.src')
                if src and self._validate_url(src):
                    cover_url = urljoin(BASE_URL, src)

            # Extraction de la date
            pub_date = datetime.now(PARIS_TZ)
            date_elem = await publication.querySelector(SELECTORS['date'])
            if date_elem is not None:
                date_text = await date_elem.evaluate('element => element.textContent')
                if date_text:
                    pub_date = await self.parse_date(date_text)

            # Construction du dictionnaire uniquement si les éléments essentiels sont présents
            if not all([title_text, full_url]):
                self._log_warning("Données essentielles manquantes dans la publication")
                self.metrics['failed_extractions'] += 1
                return None

            self.metrics['successful_extractions'] += 1
            return {
                'title': f"{title_text} - {subtitle_text}".strip(' -'),
                'url': full_url,
                'publisher': publisher_text,
                'cover_url': cover_url,
                'pub_date': pub_date
            }

        except Exception as e:
            logging.error(f"Erreur lors de l'extraction des informations: {e}")
            self.metrics['failed_extractions'] += 1
            return None

    def add_feed_entry(self, info: dict) -> bool:
        """Ajoute une entrée au flux Atom de manière synchrone."""
        if not info or info['url'] in self.cache:
            return False

        try:
            # Création de l'entrée dans le flux
            fe = self.fg.add_entry()
            fe.id(info['url'])
            fe.title(info['title'])
            fe.link(href=info['url'])
            fe.author({'name': info['publisher']})
            fe.published(info['pub_date'])
            fe.updated(info['pub_date'])

            # Construction sécurisée du contenu HTML
            content_html = ['<div>']
            if info['cover_url']:
                content_html.append(
                    f'<img src="{html.escape(info["cover_url"])}" alt="Couverture" />'
                )
            content_html.append(
                f'<p><strong>Éditeur:</strong> {html.escape(info["publisher"])}</p>'
            )
            content_html.append('</div>')

            # Assemblage du contenu HTML
            fe.content(content=''.join(content_html), type='html')

            # Mise à jour du cache et compteur
            self.cache[info['url']] = CacheEntry(info['url'], datetime.now(PARIS_TZ))
            self.new_entries += 1
            
            logging.info(f"Nouvelle publication ajoutée: {info['title']}")
            return True

        except Exception as e:
            logging.error(f"Erreur lors de l'ajout de l'entrée au flux: {e}")
            return False

    def _save_feed(self):
        """Sauvegarde le flux Atom dans un fichier."""
        try:
            atom_feed = self.fg.atom_str(pretty=True)
            with open(FEED_FILE, 'wb') as f:
                f.write(atom_feed)
            logging.info(f"Flux Atom sauvegardé avec {self.new_entries} nouvelles entrées")
        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde du flux: {e}")
            raise

    async def generate_feed(self):
        """Génère le flux Atom complet avec gestion appropriée des ressources."""
        self.metrics['start_time'] = perf_counter()
        try:
            async with self._browser_context() as browser:
                self.page = await browser.get(PUBLICATIONS_URL)
                self._initialize_feed()
                self._clean_old_cache_entries()

                publications = await self._with_retry(
                    self.page.querySelectorAll("div.grid.h-full")
                )
                
                if not publications:
                    self._log_warning("Aucune publication trouvée")
                    return

                logging.info(f"Traitement de {len(publications)} publications")

                # Traitement par lots
                for i in range(0, len(publications), BATCH_SIZE):
                    batch = publications[i:i + BATCH_SIZE]
                    for publication in batch:
                        info = await self._with_retry(
                            self.extract_publication_info(publication)
                        )
                        if info:
                            self.add_feed_entry(info)
                    
                    # Petit délai entre les lots pour éviter la surcharge
                    if i + BATCH_SIZE < len(publications):
                        await asyncio.sleep(1)

                if self.new_entries > 0:
                    self._save_feed()
                
                self._save_cache()

                # Log des métriques
                execution_time = perf_counter() - self.metrics['start_time']
                logging.info(
                    f"Exécution terminée en {execution_time:.2f} secondes\n"
                    f"Publications traitées: {self.metrics['total_processed']}\n"
                    f"Extractions réussies: {self.metrics['successful_extractions']}\n"
                    f"Extractions échouées: {self.metrics['failed_extractions']}"
                )

        except Exception as e:
            logging.error(f"Erreur pendant la génération du flux: {e}")
            raise

async def cleanup(generator: CairnFeedGenerator):
    """Nettoyage des ressources."""
    if generator.browser:
        await generator.browser.close()
        logging.info("Nettoyage effectué suite à interruption")

async def main():
    """Point d'entrée principal avec gestion appropriée des interruptions."""
    generator = CairnFeedGenerator()
    
    # Gestion des signaux d'interruption
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(
            sig,
            lambda s=sig: asyncio.create_task(
                cleanup(generator)
            )
        )

    try:
        await generator.generate_feed()
    except Exception as e:
        logging.error(f"Erreur dans l'exécution principale: {e}")
        raise
    finally:
        # Restauration des gestionnaires de signaux
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.remove_signal_handler(sig)

def run():
    """Fonction de démarrage avec gestion appropriée de la boucle asyncio."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Interruption utilisateur détectée")
    except Exception as e:
        logging.error(f"Erreur fatale: {e}")
        raise
    finally:
        logging.info("Fin du programme")

if __name__ == "__main__":
    run()