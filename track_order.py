from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tracking.log"),
        logging.StreamHandler()
    ]
)

def track_shipment(tracking_id):
    logging.info(f"Initializing tracking for ID: {tracking_id}")
    
    # Setup Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') # Run in headless mode for no UI
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--log-level=3') # Suppress warnings
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    result = {"status": "Error", "details": "Unknown error"}

    try:
        url = "https://trackcourier.io/dtdc-tracking"
        logging.info(f"Navigating to {url}")
        driver.get(url)

        # Wait for input field
        wait = WebDriverWait(driver, 20)
        # Corrected selector based on logs: input#trackingNumber
        input_selector = "input#trackingNumber"
        logging.info(f"Waiting for input field: {input_selector}")
        input_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, input_selector)))
        
        logging.info(f"Entering tracking ID: {tracking_id}")
        input_field.clear()
        input_field.send_keys(tracking_id)

        # Find and click track button
        button_selector = "button.btn-info"
        logging.info(f"Waiting for track button: {button_selector}")
        track_button = driver.find_element(By.CSS_SELECTOR, button_selector)
        track_button.click()

        logging.info("Track button clicked. Waiting for results...")
        
        # Wait for URL change or results to appear
        expected_url_part = f"/track-and-trace/dtdc/{tracking_id}"
        wait.until(EC.url_contains(expected_url_part))
        logging.info(f"URL changed to include {expected_url_part}")
        
        # Give a moment for the content to fully render
        time.sleep(5)
        
        logging.info(f"Current Page Title: {driver.title}")
        logging.info(f"Current Page URL: {driver.current_url}")
        
        # Attempt to find status text
        try:
            # Extract current status badge
            status_element = driver.find_element(By.CSS_SELECTOR, "span.modern-status-badge")
            status = status_element.text.strip()
            
            # Extract latest event details
            latest_location = driver.find_element(By.CSS_SELECTOR, "div.modern-timeline-item--first div.modern-timeline-item__location").text.strip()
            latest_activity = driver.find_element(By.CSS_SELECTOR, "div.modern-timeline-item--first div.modern-timeline-item__activity span").text.strip()
            latest_timestamp = driver.find_element(By.CSS_SELECTOR, "div.modern-timeline-item--first div.modern-timeline-item__timestamp").text.strip()
            
            result = {
                "status": status,
                "latest_event": {
                    "activity": latest_activity,
                    "location": latest_location,
                    "timestamp": latest_timestamp
                },
                "details": f"Tracking info found on {driver.current_url}",
                "full_text_snippet": f"{status} - {latest_activity} at {latest_location} on {latest_timestamp}"
            }
            logging.info(f"Tracking Result: {result}")

        except Exception as e:
            logging.error(f"Error parsing status: {e}")
            # Fallback to body text if specific elements fail
            try:
                body_text = driver.find_element(By.TAG_NAME, "body").text
                status = "Unknown"
                if "Delivered" in body_text:
                    status = "Delivered"
                elif "In Transit" in body_text:
                    status = "In Transit"
                result = {
                    "status": status,
                    "details": f"Fallback: Tracking info found on {driver.current_url}",
                    "full_text_snippet": body_text[:200]
                }
            except:
                result = {"status": "Error", "details": f"Error parsing status: {str(e)}"}

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        driver.save_screenshot("error_screenshot.png")
        result = {"status": "Error", "details": f"An error occurred: {str(e)}"}
    finally:
        logging.info("Closing browser...")
        driver.quit()
    
    return result

if __name__ == "__main__":
    TRACKING_ID = "V3500546621"
    print(track_shipment(TRACKING_ID))
