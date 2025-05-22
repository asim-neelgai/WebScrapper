import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import pytz

# Function to convert date format
def convert_to_iso8601(date_str):
    eastern = pytz.timezone('America/New_York')
    
    date_obj = datetime.strptime(date_str, "%B %d at %I:%M %p")

    date_obj = date_obj.replace(year=2024)
    
    localized_date = eastern.localize(date_obj)

    return localized_date.isoformat()

try:
    print("Initializing WebDriver...")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    driver.maximize_window()

    url = "https://bargemusic.org/calendar-tickets/?tribe_paged=1&tribe_event_display=list&tribe-bar-date=2024-09-01"
    print(f"Opening URL: {url}")
    driver.get(url)

    driver.implicitly_wait(10)

    print("Looking for event titles, dates, performers, and compositions...")
    event_titles = driver.find_elements(By.XPATH, '//h3[@class="tribe-events-list-event-title"]')
    event_dates = driver.find_elements(By.XPATH, '//span[@class="tribe-event-date-start"]')
    composer_piece_elements = driver.find_elements(By.XPATH, '//div[@class="tribe-events-list-event-description tribe-events-content description entry-summary"]/p[1]')
    performer_elements = driver.find_elements(By.XPATH, '//div[@class="tribe-events-list-event-description tribe-events-content description entry-summary"]/p[2]')
    event_ticket_urls = driver.find_elements(By.CLASS_NAME, "tribe-event-url")

    print(f"Found {len(event_titles)} events.")

    city = "Brooklyn, NY"
    venue_name = "Fulton Ferry Landing, Brooklyn, NY 11201, United States"
    latitude = 40.703277
    longitude = -73.995502
    latlon = f"{latitude}, {longitude}"
    presenter = "Bargemusic"

    events = []

    for event_id, (title, date, composer_piece_element, performer_element, ticket_url_element) in enumerate(
            zip(event_titles, event_dates, composer_piece_elements, performer_elements, event_ticket_urls), start=1):

        composer_piece_text = composer_piece_element.get_attribute("innerText").replace("\xa0", " ").strip().split('\n')

        iso8601_date = convert_to_iso8601(date.text.strip())

        performer_text = performer_element.get_attribute("innerText").replace("\xa0", " ").strip()
        
        performer_parts = [performer.strip() for performer in performer_text.split('\n') if performer]
        
        performers = ' | '.join([part.split(',')[0].strip() for part in performer_parts])
        roles = ' | '.join([part.split(',')[1].strip() for part in performer_parts if ',' in part])

        ticket_url = ticket_url_element.get_attribute("href")

        for line in composer_piece_text:
            if line:
                parts = line.split(' ', 1)
                composer = parts[0]
                piece = parts[1] if len(parts) > 1 else ''

                events.append({
                    'event_id': event_id,
                    'ticket_url': ticket_url,
                    'city': city,
                    'venue_name': venue_name,
                    'latlon': latlon,
                    'title': title.text.strip(),
                    'dates': iso8601_date,
                    'performers': performers,
                    'roles': roles,
                    'composer': composer,
                    'piece_name': piece,
                    'presenter': presenter
                })

    # Writing the data to a CSV file with new headers, including 'presenter'
    csv_file_name = 'bargemusic_events_full.csv'
    with open(csv_file_name, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=[
            'event_id',
            'ticket_url',
            'city',
            'venue_name',
            'latlon',
            'title',
            'dates',
            'performers',
            'roles',
            'composer',
            'piece_name',
            'presenter'
        ])
        writer.writeheader()
        for event in events:
            writer.writerow(event)

    print(f"Event data has been saved to '{csv_file_name}'.")

finally:
    print("Closing WebDriver...")
    driver.quit()
