import os
# Configuration des patches anti-détection
os.environ['REBROWSER_PATCHES_RUNTIME_FIX_MODE'] = 'alwaysIsolated'
os.environ['REBROWSER_PATCHES_UTILITY_WORLD_NAME'] = 'util'
os.environ['REBROWSER_PATCHES_SOURCE_URL'] = 'jquery.min.js'
os.environ['REBROWSER_PATCHES_DEBUG'] = '1'

import asyncio
import json
import random
import time
from pathlib import Path
from typing import List, Dict, Optional, Any
from rebrowser_playwright.async_api import async_playwright, Browser, Page, BrowserContext

# Configuration
CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'  # Ajuster selon l'OS
PROXY_LIST = [
    {'server': 'http://proxy1.example.com:8080', 'username': 'user1', 'password': 'pass1'},
    {'server': 'http://proxy2.example.com:8080', 'username': 'user2', 'password': 'pass2'},
]

USER_AGENTS = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]

class HumanBehaviorSimulator:
    @staticmethod
    async def random_sleep(min_ms: int = 500, max_ms: int = 3000) -> None:
        await asyncio.sleep(random.uniform(min_ms/1000, max_ms/1000))

    @staticmethod
    def generate_human_like_curve(start_point: tuple, end_point: tuple, control_points: int = 3) -> List[tuple]:
        points = [start_point]
        for i in range(control_points):
            x = start_point[0] + (end_point[0] - start_point[0]) * (i + 1) / (control_points + 1)
            y = start_point[1] + (end_point[1] - start_point[1]) * (i + 1) / (control_points + 1)
            # Ajouter un peu de randomisation
            x += random.uniform(-20, 20)
            y += random.uniform(-20, 20)
            points.append((x, y))
        points.append(end_point)
        return points

    @staticmethod
    async def natural_scroll(page: Page) -> None:
        scroll_height = await page.evaluate('() => document.documentElement.scrollHeight')
        viewport_height = await page.evaluate('() => window.innerHeight')
        current_position = 0
        
        while current_position < scroll_height:
            scroll_amount = random.randint(100, 300)
            await page.evaluate(f'window.scrollBy(0, {scroll_amount})')
            current_position += scroll_amount
            await HumanBehaviorSimulator.random_sleep(800, 2000)

    @staticmethod
    async def move_mouse_naturally(page: Page, target_x: int, target_y: int) -> None:
        current_pos = await page.evaluate('() => ({ x: window.mouseX || 0, y: window.mouseY || 0 })')
        points = HumanBehaviorSimulator.generate_human_like_curve(
            (current_pos['x'], current_pos['y']),
            (target_x, target_y)
        )
        
        for point in points:
            await page.mouse.move(point[0], point[1])
            await HumanBehaviorSimulator.random_sleep(10, 50)

class BrowserFingerprintRandomizer:
    @staticmethod
    async def override_canvas_fingerprint(page: Page) -> None:
        await page.add_init_script("""
            const originalGetContext = HTMLCanvasElement.prototype.getContext;
            HTMLCanvasElement.prototype.getContext = function(type, attributes) {
                const context = originalGetContext.call(this, type, attributes);
                if (type === '2d') {
                    const originalFillText = context.fillText;
                    context.fillText = function(...args) {
                        const tiny_offset = Math.random() * 0.1;
                        args[1] += tiny_offset;
                        args[2] += tiny_offset;
                        return originalFillText.apply(this, args);
                    }
                }
                return context;
            }
        """)

    @staticmethod
    async def override_audio_fingerprint(page: Page) -> None:
        await page.add_init_script("""
            Object.defineProperty(AudioBuffer.prototype, 'getChannelData', {
                value: function(channel) {
                    const originalData = Object.getPrototypeOf(this).getChannelData.call(this, channel);
                    const newData = new Float32Array(originalData.length);
                    for (let i = 0; i < originalData.length; i++) {
                        newData[i] = originalData[i] + (Math.random() * 0.0000001);
                    }
                    return newData;
                }
            });
        """)

class UndetectableScraper:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.human_simulator = HumanBehaviorSimulator()
        self.fingerprint_randomizer = BrowserFingerprintRandomizer()
        self.retry_count = 3
        self.retry_delay = 60

    async def init_browser(self) -> None:
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=False,
            executable_path=CHROME_PATH,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--no-sandbox',
            ]
        )

        # Sélection aléatoire du proxy
        proxy_config = random.choice(PROXY_LIST) if PROXY_LIST else None

        self.context = await self.browser.new_context(
            viewport=None,
            user_agent=random.choice(USER_AGENTS),
            proxy=proxy_config,
            locale='fr-FR',
            timezone_id='Europe/Paris',
            permissions=['geolocation'],
            geolocation={'latitude': 48.8566, 'longitude': 2.3522},
            color_scheme='light',
            accept_downloads=True,
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'DNT': '1'
            }
        )

        self.page = await self.context.new_page()
        await self.fingerprint_randomizer.override_canvas_fingerprint(self.page)
        await self.fingerprint_randomizer.override_audio_fingerprint(self.page)

    async def handle_captcha(self) -> bool:
        current_url = self.page.url
        if ("captcha-delivery" in current_url or 
            await self.page.locator("iframe[src*='captcha-delivery']").count() > 0):
            
            print("\n==== CAPTCHA DÉTECTÉ ====")
            print("1. Résolvez le captcha manuellement")
            print("2. Appuyez sur Entrée une fois terminé")
            input("\nAppuyez sur Entrée après résolution...")
            
            await self.page.wait_for_load_state("networkidle")
            await self.human_simulator.random_sleep(2000, 4000)
            
            if "captcha-delivery" in self.page.url:
                return False
                
            print("✅ Captcha résolu")
            return True
        return True

    async def extract_card_info(self, card) -> Dict[str, Any]:
        info = {}
        try:
            # Simulation de mouvement de souris naturel vers la carte
            card_box = await card.bounding_box()
            if card_box:
                await self.human_simulator.move_mouse_naturally(
                    self.page,
                    card_box['x'] + card_box['width']/2,
                    card_box['y'] + card_box['height']/2
                )

            # Extraction des informations avec temps d'attente aléatoires
            img = await card.query_selector("img[src*='/cover/thumbnail']")
            if img:
                info['thumbnail'] = await img.get_attribute('src')
                await self.human_simulator.random_sleep(100, 300)

            title = await card.query_selector("h1.leading-5.font-bold.text-shark-950")
            if title:
                info['title'] = await title.inner_text()
                await self.human_simulator.random_sleep(100, 300)

            subtitle = await card.query_selector("h2.font-serif.leading-5.text-shark-950")
            if subtitle:
                info['subtitle'] = await subtitle.inner_text()
                await self.human_simulator.random_sleep(100, 300)

            journal_info = await card.query_selector("div.mt-auto.pt-1")
            if journal_info:
                text = (await journal_info.inner_text()).split('\n')
                info['journal'] = text[0].strip() if text else None
                info['issue_info'] = text[1].strip() if len(text) > 1 else None

            link = await card.query_selector("a[href*='cairn.info']")
            if link:
                info['url'] = await link.get_attribute('href')

        except Exception as e:
            print(f"Erreur lors de l'extraction d'une carte: {e}")

        return info

    async def scrape_with_retry(self) -> Optional[List[Dict[str, Any]]]:
        cards = []
        
        for attempt in range(self.retry_count):
            try:
                print(f"\nTentative {attempt + 1}/{self.retry_count}")
                
                if not self.browser or not self.browser.is_connected():
                    await self.init_browser()

                # Navigation vers la page
                await self.page.goto(
                    'https://shs.cairn.info/disc-sociologie?lang=fr',
                    wait_until='networkidle',
                    timeout=60000
                )

                if not await self.handle_captcha():
                    continue

                # Attente et comportement humain
                await self.human_simulator.random_sleep(2000, 4000)
                await self.human_simulator.natural_scroll(self.page)

                # Extraction des cartes
                cards_locator = self.page.locator("div.basis-full.shrink-0")
                await cards_locator.first.wait_for(state="visible", timeout=30000)

                for i in range(5):  # 5 pages
                    print(f"Traitement page {i+1}...")
                    
                    cards_elements = await cards_locator.all()
                    for card in cards_elements:
                        if info := await self.extract_card_info(card):
                            cards.append(info)
                            print(f"  - {info.get('title', 'Sans titre')}")
                            
                        await self.human_simulator.random_sleep(500, 1500)

                    await self.human_simulator.natural_scroll(self.page)

                # Sauvegarde et retour des résultats
                if cards:
                    self.save_results(cards)
                    return cards

            except Exception as e:
                print(f"Erreur lors de la tentative {attempt + 1}: {e}")
                if attempt < self.retry_count - 1:
                    delay = random.uniform(self.retry_delay/2, self.retry_delay*1.5)
                    print(f"Nouvelle tentative dans {delay:.1f} secondes...")
                    await asyncio.sleep(delay)
                continue

            finally:
                if self.browser:
                    await self.browser.close()

        return None

    def save_results(self, cards: List[Dict[str, Any]]) -> None:
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)
        
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f'cairn_cards_{timestamp}.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({'cards': cards}, f, ensure_ascii=False, indent=2)
            
        print(f"\nDonnées sauvegardées dans {output_file}")

async def main():
    scraper = UndetectableScraper()
    try:
        cards = await scraper.scrape_with_retry()
        if cards:
            print(f"\n=== Résumé ===")
            print(f"Nombre total de cartes récupérées : {len(cards)}")
    except Exception as e:
        print(f"Erreur finale : {e}")

if __name__ == "__main__":
    asyncio.run(main())