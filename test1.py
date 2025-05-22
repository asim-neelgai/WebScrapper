from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time

try:
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    # Maximize the browser window (optional but can help with visibility)
    driver.maximize_window()

    url = "https://www.carnegiehall.org/Events"
    driver.get(url)

    # Click the "Show More" button until no more events are loaded
    while True:
        try:
            show_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//a[@href="#list-more" and contains(@class, "ch-cta-button")]'))
            )
            driver.execute_script("arguments[0].scrollIntoView();", show_more_button)
            show_more_button.click()
            time.sleep(5)
        except Exception as e:
            print("No more 'Show More' button found or all events loaded.")
            break

    events = []

    date_elements = driver.find_elements(By.XPATH, '//div[@class="h3 date"]')
    time_elements = driver.find_elements(By.XPATH, '//span[@class="time"]')
    location_elements = driver.find_elements(By.XPATH, '//span[@class="location"]')
    presenter_elements = driver.find_elements(By.XPATH, '//span[@x-html="event.licenseename"]')
    url_elements = driver.find_elements(By.XPATH, '//a[@class="event-item"]')
    image_elements = driver.find_elements(By.XPATH, '//img[@class="lazyload"]')

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
    driver.quit()
