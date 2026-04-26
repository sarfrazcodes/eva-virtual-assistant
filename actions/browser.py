from playwright.sync_api import sync_playwright
import time
import os
import urllib.request
import re
from pathlib import Path
from eva.utils.logger import get_logger

logger = get_logger("EVA.actions.browser")

class BrowserManager:
    def __init__(self):
        self.playwright = None
        self.browser = None
        
    def __enter__(self):
        self.playwright = sync_playwright().start()
        # Use persistent context to maintain login states
        user_data_dir = Path(os.environ['USERPROFILE']) / "eva_browser_profile"
        
        try:
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(user_data_dir),
                headless=False,
                channel="chrome" # Tries to use actual Chrome, falls back safely
            )
        except Exception:
            # Fallback if chrome channel fails
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(user_data_dir),
                headless=False
            )
            
        return self.context
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.context:
            self.context.close()
        if self.playwright:
            self.playwright.stop()

def search_google(query: str) -> str:
    """Opens Chrome, searches, returns top result titles + URLs."""
    try:
        with BrowserManager() as context:
            page = context.pages[0] if context.pages else context.new_page()
            page.goto("https://www.google.com")
            page.fill("textarea[name='q']", query)
            page.press("textarea[name='q']", "Enter")
            page.wait_for_selector("div#search", timeout=10000)
            
            # Simple scraping of results
            results = page.locator("div.g")
            count = results.count()
            found = []
            
            for i in range(min(3, count)):
                title_el = results.nth(i).locator("h3")
                link_el = results.nth(i).locator("a").first
                if title_el.count() > 0 and link_el.count() > 0:
                    found.append(f"{title_el.inner_text()} - {link_el.get_attribute('href')}")
                    
            if not found:
                return "Kuch mila nahi yaar google pe."
                
            return "Top results mil gaye:\n" + "\n".join(found)
    except Exception as e:
        logger.error(f"Search google error: {e}")
        return "Google search fail ho gaya."

def scrape_page(url: str) -> str:
    """Fetches and returns cleaned text content from a URL."""
    try:
        with BrowserManager() as context:
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(url)
            page.wait_for_load_state("networkidle")
            text = page.evaluate("document.body.innerText")
            return text[:2000] # Cap length
    except Exception as e:
        logger.error(f"Scrape URL error: {e}")
        return ""

def navigate_to(url: str) -> None:
    """Opens browser to a specific URL and keeps it open."""
    from subprocess import run
    try:
        run(["start", url], shell=True)
    except Exception as e:
        logger.error(f"Navigate error: {e}")

def play_on_youtube(query: str) -> str:
    """Searches YouTube and instantly plays the first video in the default browser."""
    try:
        search_query = str(query).replace(" ", "+")
        req = urllib.request.Request(
            f"https://www.youtube.com/results?search_query={search_query}",
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        html = urllib.request.urlopen(req).read().decode()
        
        # YouTube modern HTML stores the video ID in JSON format
        video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
        
        if video_ids:
            # Filter out duplicate IDs and grab the first actual result
            video_id = video_ids[0]
            navigate_to(f"https://www.youtube.com/watch?v={video_id}")
            return f"Playing {query} on YouTube."
            
        return "YouTube pe gaana nahi mila."
    except Exception as e:
        logger.error(f"YouTube play error: {e}")
        return "Gaana play karne mein network error aaya."

def take_screenshot(url: str, save_path: str) -> str:
    """Captures screenshot of a URL."""
    try:
        with BrowserManager() as context:
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(url)
            page.screenshot(path=save_path)
            return f"Screenshot saved at {save_path}"
    except Exception as e:
        logger.error(f"Screenshot error: {e}")
        return "Screenshot lene mein diqqat hui."

if __name__ == "__main__":
    print("Testing Google Search...")
    print(search_google("Playwright Python API"))

