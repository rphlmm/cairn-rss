import asyncio
import os
from rebrowser_playwright.async_api import async_playwright

# Configuration des patches anti-détection
os.environ['REBROWSER_PATCHES_RUNTIME_FIX_MODE'] = 'addBinding'
os.environ['REBROWSER_PATCHES_UTILITY_WORLD_NAME'] = 'util'
os.environ['REBROWSER_PATCHES_DEBUG'] = '1'

async def test_rebrowser_bot_detector():
    print("Démarrage du test avec rebrowser-bot-detector...")

    async with async_playwright() as p:
        try:
            # Lancer le navigateur
            print("Lancement du navigateur Chromium...")
            browser = await p.chromium.launch(headless=False)
            print("Navigateur lancé.")

            # Créer un contexte avec des paramètres réalistes
            print("Création d'un contexte...")
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                java_script_enabled=True,
                timezone_id='Europe/Paris',
                locale='fr-FR',
                geolocation={'latitude': 48.8566, 'longitude': 2.3522},  # Paris
                has_touch=False
            )
            print("Contexte créé.")

            # Ajouter des scripts initiaux pour masquer l'automatisation
            await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = {runtime: {}};
            """)

            # Créer une page
            print("Création d'une nouvelle page...")
            page = await context.new_page()
            print("Page créée avec succès.")

            # Ajouter des fonctions nécessaires pour déclencher les tests
            print("Ajout de la fonction dummyFn dans le contexte principal...")
            await page.evaluate("window.dummyFn = () => console.log('dummyFn called')")
            
            print("Exposition de la fonction exposedFn...")
            await page.expose_function('exposedFn', lambda: print('exposedFn call'))

            # Naviguer vers rebrowser-bot-detector
            print("Navigation vers rebrowser-bot-detector...")
            await page.goto('https://bot-detector.rebrowser.net/', wait_until='networkidle')
            print("Navigation réussie.")

            # Appeler dummyFn dans le contexte principal
            print("Appel de dummyFn...")
            await page.evaluate("window.dummyFn()")

            # Vérification de sourceUrlLeak
            print("Vérification de sourceUrlLeak...")
            await page.evaluate("document.getElementById('detections-json')")

            # Exécution dans le contexte principal (isolatedRealm non pris en charge directement par Playwright)
            print("Exécution dans le contexte principal...")
            await page.evaluate("document.getElementsByClassName('div')")

            # Pause pour observer les résultats
            print("Attente pour observer les résultats...")
            await page.wait_for_timeout(5000)

            # Capture d'écran des résultats
            screenshot_path = 'rebrowser_bot_test.png'
            await page.screenshot(path=screenshot_path)
            print(f"Capture d'écran sauvegardée : {screenshot_path}")

        except Exception as e:
            print(f"Erreur détectée : {e}")
        finally:
            await context.close()
            await browser.close()
            print("Contexte et navigateur fermés.")

# Exécution principale
async def main():
    try:
        await test_rebrowser_bot_detector()
        print("\nTest terminé. Vérifiez les résultats dans la capture d'écran.")
    except Exception as e:
        print(f"Erreur lors de l'exécution du script principal : {e}")

if __name__ == "__main__":
    asyncio.run(main())
