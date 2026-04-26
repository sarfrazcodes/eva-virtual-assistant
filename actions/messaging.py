from playwright.sync_api import sync_playwright
import time
import os
from pathlib import Path
from eva.utils.logger import get_logger
from eva.actions.browser import BrowserManager

logger = get_logger("EVA.actions.messaging")

def _search_contact(page, contact_name: str):
    """Helper to find and click a contact."""
    page.goto('https://web.whatsapp.com')
    
    # Wait for the first contenteditable box (this is always the search box in WhatsApp Web)
    search_box = page.locator('div[contenteditable="true"]').first
    search_box.wait_for(state="visible", timeout=60000)
    time.sleep(1)
    
    # Search contact
    search_box.fill(contact_name)
    time.sleep(2)
    
    # Click first result
    page.keyboard.press("Enter")
    time.sleep(2)

def send_whatsapp_message(contact_name: str, message: str) -> str:
    """Opens WhatsApp Web, searches for contact, asks for confirmation, and sends message."""
    from eva.voice.speaker import speak
    from eva.voice.listener import listen_once
    
    try:
        with BrowserManager() as b_context:
            page = b_context.pages[0] if b_context.pages else b_context.new_page()
            _search_contact(page, contact_name)
            
            # The message box is typically the last contenteditable element on the page
            msg_box = page.locator('div[contenteditable="true"]').last
            msg_box.wait_for(state="visible", timeout=10000)
            msg_box.fill(message)
            time.sleep(1)
            
            # Ask for voice confirmation
            speak(f"Maine {contact_name} ka chat khol diya hai. Kya main message bhej doon?")
            print("\n[WhatsApp Confirmation] Listening for yes/no...")
            
            confirmation = listen_once()
            
            if confirmation and any(word in confirmation.lower() for word in ["yes", "haan", "send", "bhej"]):
                page.keyboard.press("Enter")
                time.sleep(2)
                logger.info(f"Sent message to {contact_name}")
                return f"Done! {contact_name} ko message bhej diya."
            else:
                return "Message send cancel kar diya gaya."
    except Exception as e:
        logger.error(f"WhatsApp send error: {e}")
        return "WhatsApp bhejne mein issue hua. Please ensure you are logged in."

def send_whatsapp_file(contact_name: str, file_path: str, caption: str = "") -> str:
    """Sends file attachment."""
    path = Path(file_path)
    if not path.exists():
        return "File hi nahi mili."
        
    try:
        with BrowserManager() as b_context:
            page = b_context.pages[0] if b_context.pages else b_context.new_page()
            _search_contact(page, contact_name)
            
            # Click attach button
            page.locator('div[title="Attach"]').click()
            time.sleep(1)
            
            # Upload file
            with page.expect_file_chooser() as fc_info:
                page.locator('input[accept="*"]').click(force=True)
            file_chooser = fc_info.value
            file_chooser.set_files(file_path)
            time.sleep(2)
            
            if caption:
                page.keyboard.type(caption)
                
            page.keyboard.press("Enter")
            time.sleep(3)
            return "File bhej di!"
    except Exception as e:
        logger.error(f"WhatsApp file send error: {e}")
        return "File bhejne mein gadbad hui."

def check_whatsapp_messages(contact_name: str) -> list[str]:
    """Returns last 5 messages from a contact."""
    try:
        with BrowserManager() as b_context:
            page = b_context.pages[0] if b_context.pages else b_context.new_page()
            _search_contact(page, contact_name)
            
            messages_loc = page.locator('div.message-in')
            # Wait a bit for messages to load
            time.sleep(3)
            count = messages_loc.count()
            
            last_5 = []
            for i in range(max(0, count-5), count):
                el = messages_loc.nth(i).locator('span.selectable-text')
                if el.count() > 0:
                    last_5.append(el.inner_text())
            return last_5
    except Exception as e:
        logger.error(f"Check WA messages error: {e}")
        return []
