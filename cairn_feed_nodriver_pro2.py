import nodriver
import logging
import pickle
import asyncio
import aiohttp
import contextlib
from datetime import datetime, timedelta
from pathlib import Path
import pytz
from feedgen.feed import FeedGenerator
from urllib.parse import urljoin, urlparse
import re
import signal
import html
from typing import AsyncGenerator, Dict, Set, Optional

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
DEFAULT_DATE = datetime(1970, 1, 1, tzinfo=PARIS_TZ)

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

# Exceptions personnalisées
class InvalidDateError(Exception):
    """Exception personnalisée pour les dates invalides."""
    pass

class MissingSelectorError(Exception):
    """Exception pour les sélecteurs manquants."""
    pass

class InvalidPublicationError(Exception):
    """Exception pour les publications invalides."""
    pass

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

    def _get_selector(self, key: str) -> str:
        """Récupère un sélecteur CSS avec vérification."""
        if key not in SELECTORS:
            raise MissingSelectorError(f"Sélecteur '{key}' non défini")
        return SELECTORS[key]

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
        """Exécute une coroutine avec retry et gestion spécifique des erreurs réseau."""
        for attempt in range(max_retries):
            try:
                return await coro
            except aiohttp.ClientError as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = 2 ** attempt
                logging.warning(
                    f"Erreur réseau (tentative {attempt + 1}/{max_retries}). "
                    f"Attente de {wait_time}s. Erreur: {e}"
                )
                await asyncio.sleep(wait_time)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = 2 ** attempt
                logging.warning(
                    f"Erreur inattendue (tentative {attempt + 1}/{max_retries}). "
                    f"Attente de {wait_time}s. Erreur: {e}"
                )
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

    async def parse_date(self, date_text: str) -> Optional[datetime]:
        """Parse une date de publication Cairn."""
        try:
            if not date_text:
                raise InvalidDateError("Date vide")
            
            date_match = re.search(r"(\d{2})/(\d{2})/(\d{4})", self._sanitize_text(date_text))
            if not date_match:
                raise InvalidDateError("Format de date invalide")
            
            jour, mois, annee = map(int, date_match.groups())
            
            # Validation basique des valeurs
            if not (1 <= jour <= 31 and 1 <= mois <= 12 and 1900 <= annee <= datetime.now().year):
                raise InvalidDateError("Valeurs de date hors limites")
            
            return datetime(annee, mois, jour, tzinfo=PARIS_TZ)
        except InvalidDateError as e:
            self._log_warning(f"Date invalide: {date_text}. {e}")
            return None
        except Exception as e:
            self._log_warning(f"Erreur lors du parsing de la date: {date_text}. {e}")
            return None

    async def extract_publication_info(self, publication):
        """Extrait les informations d'une publication avec gestion améliorée des erreurs."""
        try:
            if not publication:
                raise InvalidPublicationError("Publication invalide (None)")

            self.metrics['total_processed'] += 1

            try:
                discipline_elem = await publication.querySelector(self._get_selector('discipline'))
                if discipline_elem is not None:
                    discipline_text = await discipline_elem.evaluate('element => element.textContent')
                    if "sociologie" not in discipline_text.lower():
                        logging.debug("Publication non sociologique ignorée")
                        return None
                else:
                    raise InvalidPublicationError("Élément discipline non trouvé")
            except MissingSelectorError as e:
                logging.error(f"Erreur de sélecteur: {e}")
                return None

            # Extraction du titre
            title_elem = await publication.querySelector(self._get_selector('title'))
            if title_elem is None:
                raise InvalidPublicationError("Titre manquant")
            title_text = self._sanitize_text(
                await title_elem.evaluate('element => element.textContent')
            )

            # Extraction du sous-titre
            subtitle_text = ""
            subtitle_elem = await publication.querySelector(self._get_selector('subtitle'))
            if subtitle_elem is not None:
                subtitle_text = self._sanitize_text(
                    await subtitle_elem.evaluate('element => element.textContent')
                )

            # Extraction du lien
            link_elem = await publication.querySelector(self._get_selector('link'))
            if link_elem is None:
                raise InvalidPublicationError("Lien manquant")
            url = await link_elem.evaluate('element => element.href')
            if not url or not self._validate_url(url):
                raise InvalidPublicationError("URL invalide")
            full_url = urljoin(BASE_URL, url)

            # Extraction de l'éditeur
            publisher_text = "Éditeur inconnu"
            try:
                publisher_elem = await publication.querySelector(self._get_selector('publisher'))
                if publisher_elem is not None:
                    publisher_text = self._sanitize_text(
                        await publisher_elem.evaluate('element => element.textContent')
                    )
            except Exception as e:
                logging.warning(f"Erreur lors de l'extraction de l'éditeur: {e}")

            # Extraction de l'image
            cover_url = ""
            try:
                img_elem = await publication.querySelector(self._get_selector('image'))
                if img_elem is not None:
                    src = await img_elem.evaluate('element => element.src')
                    if src and self._validate_url(src):
                        cover_url = urljoin(BASE_URL, src)
            except Exception as e:
                logging.warning(f"Erreur lors de l'extraction de l'image: {e}")

            # Extraction de la date
            pub_date = DEFAULT_DATE
            try:
                date_elem = await publication.querySelector(self._get_selector('date'))
                if date_elem is not None:
                    date_text = await date_elem.evaluate('element => element.textContent')
                    if date_text:
                        parsed_date = await self.parse_date(date_text)
                        if parsed_date:
                            pub_date = parsed_date
            except Exception as e:
                logging.warning(f"Erreur lors de l'extraction de la date: {e}")

            self.metrics['successful_extractions'] += 1
            return {
                'title': f"{title_text} - {subtitle_text}".strip(' -'),
                'url': full_url,
                'publisher': publisher_text,
                'cover_url': cover_url,
                'pub_date': pub_date
            }

        except aiohttp.ClientError as e:
            logging.error(f"Erreur réseau lors de l'extraction: {e}")
            self.metrics['failed_extractions'] += 1
            return None
        except InvalidPublicationError as e:
            logging.warning(f"{e}")
            self.metrics['failed_extractions'] += 1
            return None
        except Exception as e:
            logging.error(f"Erreur inattendue lors de l'extraction: {e}")
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