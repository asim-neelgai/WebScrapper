from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time

try:
    # Set up the Selenium WebDriver
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    # Navigate to the Carnegie Hall events page
    url = "https://www.carnegiehall.org/Events"
    driver.get(url)

    # Scroll down to load content
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(10)  # Wait for content to load after scrolling

    # Scroll back up
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(10)  # Ensure content is fully stabilized

    events = []

    # Extract date
    try:
        date_elements = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@class="h3 date"]'))
        )
    except Exception as e:
        print(f"Error finding date elements: {e}")
        date_elements = []

    # Extract time
    try:
        time_elements = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, '//span[@class="time"]'))
        )
    except Exception as e:
        print(f"Error finding time elements: {e}")
        time_elements = []

    # Extract location
    try:
        location_elements = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, '//span[@class="location"]'))
        )
    except Exception as e:
        print(f"Error finding location elements: {e}")
        location_elements = []

    # Extract presenter
    try:
        presenter_elements = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, '//span[@x-html="event.licenseename"]'))
        )
    except Exception as e:
        print(f"Error finding presenter elements: {e}")
        presenter_elements = []

    # Extract event URL
    try:
        url_elements = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, '//a[@class="event-item"]'))
        )
    except Exception as e:
        print(f"Error finding event URL elements: {e}")
        url_elements = []

    # Extract image URL
    try:
        image_elements = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, '//img[@class="lazyload"]'))
        )
    except Exception as e:
        print(f"Error finding image URL elements: {e}")
        image_elements = []

    # Combine extracted data into events list
    for i in range(max(len(date_elements), len(time_elements), len(location_elements), len(presenter_elements), len(url_elements), len(image_elements))):
        event_data = {}

        # Assign each data field to the event, handling cases where lists may be of unequal length
        event_data['date'] = date_elements[i].text.strip() if i < len(date_elements) else None
        event_data['time'] = time_elements[i].text.strip() if i < len(time_elements) else None
        event_data['location'] = location_elements[i].text.strip() if i < len(location_elements) else None
        event_data['presenter'] = presenter_elements[i].text.strip() if i < len(presenter_elements) else None
        event_data['event_url'] = url_elements[i].get_attribute('href') if i < len(url_elements) else None
        event_data['image_url'] = image_elements[i].get_attribute('data-src') if i < len(image_elements) else None

        events.append(event_data)

    # Save the extracted data to a CSV file
    with open('carnegie_hall_events_full.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['date', 'time', 'location', 'presenter', 'event_url', 'image_url'])
        writer.writeheader()
        for event in events:
            writer.writerow(event)

    print("Event data has been saved to 'carnegie_hall_events_full.csv'.")

finally:
    # Ensure the browser is closed at the end
    driver.quit()
