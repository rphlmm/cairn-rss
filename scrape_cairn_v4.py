import os
# Anti-detection patches
os.environ['REBROWSER_PATCHES_RUNTIME_FIX_MODE'] = 'alwaysIsolated'  # Execute tout dans un contexte isolé
os.environ['REBROWSER_PATCHES_UTILITY_WORLD_NAME'] = 'util'  # Nom générique pour le monde utilitaire
os.environ['REBROWSER_PATCHES_SOURCE_URL'] = 'app.js'  # URL source générique
os.environ['REBROWSER_PATCHES_DEBUG'] = '1'

import asyncio
import json
import random
from rebrowser_playwright.async_api import async_playwright

USER_AGENTS = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0'
]

async def test_bot_detection(page):
    """Test la détection du bot avec tous les tests recommandés"""
    try:
        print("\nTest de détection du bot...")
        await page.goto('https://bot-detector.rebrowser.net/', wait_until='networkidle')
        await page.wait_for_timeout(1000)
        
        tests = []

        # Test 1: dummyFn dans le contexte principal
        try:
            tests.append(await page.evaluate("() => window.dummyFn()"))
        except Exception as e:
            print("Test dummyFn executed")
        
        # Test 2: exposeFunctionLeak
        try:
            tests.append(await page.expose_function('exposedFn', lambda: print('exposedFn call')))
        except Exception as e:
            print("Test exposeFunctionLeak executed")

        # Test 3: sourceUrlLeak
        try:
            tests.append(await page.evaluate("() => document.getElementById('detections-json')"))
        except Exception as e:
            print("Test sourceUrlLeak executed")

        # Test 4: mainWorldExecution dans un contexte isolé
        try:
            tests.append(await page.evaluate("() => document.getElementsByClassName('div')"))
        except Exception as e:
            print("Test mainWorldExecution executed")
        
        # Attendre que les tests soient traités
        await page.wait_for_timeout(2000)

        # Récupérer les résultats
        detections = await page.evaluate("""() => {
            const elem = document.getElementById('detections-json');
            try {
                return elem ? JSON.parse(elem.textContent) : null;
            } catch (e) {
                return null;
            }
        }""")

        if detections:
            print("\nRésultats détaillés :")
            for test, data in detections.items():
                if isinstance(data, dict):
                    rating = data.get('rating', 'N/A')
                    note = data.get('note', 'N/A')
                    status = '✅ OK' if rating <= 0 else '❌ Détecté'
                    print(f"- {test}: {status}")
                    if rating > 0:
                        print(f"  Note: {note}")
                else:
                    status = '❌ Détecté' if data else '✅ OK'
                    print(f"- {test}: {status}")

        return detections

    except Exception as e:
        print(f"Erreur lors du test de détection: {e}")
        return None

async def simulate_human_behavior(page):
    """Simule un comportement humain basique"""
    try:
        await page.mouse.move(
            random.randint(100, 800),
            random.randint(100, 600),
            steps=random.randint(10, 20)
        )
        await page.wait_for_timeout(random.randint(500, 1500))
        
        await page.mouse.wheel(0, random.randint(100, 300))
        await page.wait_for_timeout(random.randint(500, 1500))
        
        await page.mouse.move(
            random.randint(100, 800),
            random.randint(100, 600),
            steps=random.randint(5, 15)
        )
        await page.wait_for_timeout(random.randint(500, 1000))
        
    except Exception as e:
        print(f"Erreur dans simulate_human_behavior: {e}")

async def extract_card_info(card):
    """Extrait les informations d'une carte"""
    info = {}
    try:
        img = await card.wait_for_selector("img[src*='/cover/thumbnail']", timeout=5000)
        if img:
            info['thumbnail'] = await img.get_attribute('src')
        
        title = await card.wait_for_selector("h1.leading-5.font-bold.text-shark-950", timeout=5000)
        if title:
            info['title'] = await title.inner_text()
            
        subtitle = await card.query_selector("h2.font-serif.leading-5.text-shark-950")
        if subtitle:
            info['subtitle'] = await subtitle.inner_text()
        
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

async def scrape_with_context():
    """Effectue le scraping avec gestion des protections anti-bot"""
    print("Démarrage du scraping...")
    cards = []
    browser = None
    
    try:
        async with async_playwright() as p:
            # Lancement avec Chrome stable et flags anti-détection
            browser = await p.chromium.launch(
                headless=False,
                executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",  # Chemin vers Chrome stable
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                ]
            )

            context = await browser.new_context(
                # Pas de viewport fixe pour éviter la détection
                viewport=None,
                user_agent=random.choice(USER_AGENTS),
                locale='fr-FR',
                timezone_id='Europe/Paris',
                permissions=['geolocation'],
                geolocation={'latitude': 48.8566, 'longitude': 2.3522},
                color_scheme='light',
                accept_downloads=True
            )

            page = await context.new_page()

            # Test de détection
            detections = await test_bot_detection(page)
            if detections and any(detections.values()):
                print("\n⚠️  Attention: Le bot est détectable!")
                print("Voulez-vous continuer quand même? (O/n)")
                if input().lower() == 'n':
                    return None

            print("\nNavigation vers Cairn.info...")
            response = await page.goto(
                'https://shs.cairn.info/disc-sociologie?lang=fr',
                wait_until='commit',
                timeout=60000
            )

            if not browser.is_connected():
                raise Exception("Le navigateur a été fermé inopinément")

            # Gestion du captcha
            print("Vérification du captcha...")
            current_url = page.url
            if (response.status in [403, 429, 503] or 
                "captcha-delivery" in current_url or 
                await page.locator("iframe[src*='captcha-delivery']").count() > 0):
                
                print("\n==== ATTENTION: CAPTCHA DÉTECTÉ ====")
                print("1. Résolvez le captcha dans la fenêtre")
                print("2. Appuyez sur Entrée une fois terminé")
                input("\nAppuyez sur Entrée après résolution...")
                
                await page.wait_for_load_state("networkidle")
                await page.wait_for_timeout(2000)

                if "captcha-delivery" in page.url:
                    raise Exception("Captcha non résolu")
                
                print("✅ Captcha résolu")

            print("Attente du chargement...")
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_load_state("load")
            await page.wait_for_load_state("networkidle")
            
            await simulate_human_behavior(page)

            print("Recherche des cartes...")
            cards_locator = page.locator("div.basis-full.shrink-0")
            await cards_locator.first.wait_for(state="visible", timeout=30000)

            for page_num in range(1, 6):
                if not browser.is_connected():
                    raise Exception("Navigateur fermé pendant le scraping")
                    
                print(f"Traitement page {page_num}...")
                await simulate_human_behavior(page)
                
                cards_elements = await cards_locator.all()
                for card in cards_elements:
                    if info := await extract_card_info(card):
                        cards.append(info)
                        print(f"  - {info.get('title', 'Sans titre')}")
                    await page.wait_for_timeout(random.randint(500, 1500))

    except Exception as e:
        print(f"Erreur pendant le scraping: {e}")
        return None
    finally:
        if browser:
            await browser.close()
    
    return cards

async def scrape_with_retry(max_retries=3):
    """Tente le scraping plusieurs fois avec gestion des erreurs"""
    for attempt in range(max_retries):
        try:
            print(f"\nTentative {attempt + 1}/{max_retries}")
            cards = await scrape_with_context()
            if cards is not None:
                return cards
            print(f"Tentative {attempt + 1} n'a pas retourné de résultats")
        except Exception as e:
            print(f"Erreur lors de la tentative {attempt + 1}: {e}")
        
        if attempt < max_retries - 1:
            delay = random.uniform(30, 60)
            print(f"Nouvelle tentative dans {delay:.1f} secondes...")
            await asyncio.sleep(delay)
    
    raise Exception("Échec après toutes les tentatives")

async def main():
    """Fonction principale"""
    try:
        print("Que souhaitez-vous faire ?")
        print("1. Tester la détection du bot uniquement")
        print("2. Lancer le scraping (avec test préalable)")
        choice = input("Votre choix (1/2): ")
        
        if choice == "1":
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=False,
                    executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                    args=['--disable-blink-features=AutomationControlled']
                )
                context = await browser.new_context(viewport=None)
                page = await context.new_page()
                await test_bot_detection(page)
                await browser.close()
                return
                
        elif choice == "2":
            cards = await scrape_with_retry()
            if cards:
                print(f"\n=== Résumé ===")
                print(f"Nombre total de cartes récupérées : {len(cards)}")
                
                output = {"cards": cards}
                with open('cairn_cards.json', 'w', encoding='utf-8') as f:
                    json.dump(output, f, ensure_ascii=False, indent=2)
                print("\nDonnées sauvegardées dans cairn_cards.json")
        else:
            print("Choix invalide")
                
    except Exception as e:
        print(f"Erreur finale : {e}")

if __name__ == "__main__":
    asyncio.run(main())