from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
from datetime import datetime

# Initialize the web driver
driver = webdriver.Chrome()
driver.get("https://www.bargemusic.org/calendar-tickets/?tribe_event_display=list&tribe-bar-date=2024-09&tribe_redirected=true")

# Wait for the page content to load
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "tribe-events-content"))
)

# Find all event elements
events = driver.find_elements(By.CLASS_NAME, "type-tribe_events")

# Open a CSV file for writing
with open('concerts_data_corrected.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # Define the header
    writer.writerow(["presenter", "event_id", "ticket_url", "city", "venue_name", 
                     "latitude", "longitude", "title", "concert_type", "dates", 
                     "performer", "role", "composer", "piece", "selection", "arranger", "note"])

    # Iterate over each event
    for event in events:
        presenter = "Bargemusic"
        event_id = event.get_attribute("id")  # Unique identifier for the event
        
        # Extract ticket URL
        try:
            ticket_url = event.find_element(By.CLASS_NAME, "tribe-event-url").get_attribute("href")
        except:
            ticket_url = "Not available"

        city = "New York"
        venue_name = "Bargemusic"
        latitude, longitude = 40.7128, -74.0060  # Fixed coordinates for the venue

        # Extract event title
        try:
            title = event.find_element(By.CLASS_NAME, "tribe-events-list-event-title").text
        except:
            title = "Not available"

        # Determine concert type
        concert_type = "Masterworks" if "Masterworks" in title else "Unknown"

        # Extract event date
        try:
            date_element = event.find_element(By.CLASS_NAME, "tribe-event-date-start")
            date_text = date_element.text.strip()
            current_year = datetime.now().year
            date_time_obj = datetime.strptime(f"{date_text} {current_year}", '%B %d at %I:%M %p %Y')
            dates = date_time_obj.isoformat()
        except Exception as e:
            print(f"Error parsing date: {e}")
            dates = "Not available"

        # Extract content block
        try:
            content_block = event.find_element(By.CLASS_NAME, "tribe-events-content").text.split("\n")
        except:
            content_block = []

        performers, roles, composers, pieces, selection, arranger, note = [], [], [], [], "", "", ""

        # Process each line in the content block
        for line in content_block:
            line = line.strip()
            
            # Separate Performers and their roles
            if any(keyword in line.lower() for keyword in ["piano", "violin", "cello"]):
                performer_data = line.split(", ")
                for performer_role in performer_data:
                    performer_details = performer_role.split()
                    if len(performer_details) > 1:
                        performers.append(performer_details[0].strip())
                        roles.append(performer_details[1].strip())
                    else:
                        # If the role is missing, assign "Unknown" as a default
                        performers.append(performer_details[0].strip())
                        roles.append("Unknown")

            # Parse Composer and Piece information
            if ":" in line and "premiere" not in line.lower():
                composer_piece = line.split(": ")
                if len(composer_piece) >= 2:
                    composer_info = composer_piece[0].strip()
                    piece_info = composer_piece[1].strip()

                    if "/" in composer_info:
                        composer, arranger_name = composer_info.split("/")
                        composers.append(composer.strip())
                        arranger = arranger_name.strip()
                    else:
                        composers.append(composer_info)
                    
                    pieces.append(piece_info)

            # Note for premieres
            if "premiere" in line.lower():
                note = line.strip()

        # Ensure unique composers and other attributes are listed
        composers = list(set(composers))

        # Write each performer and piece separately
        for performer, role in zip(performers, roles):
            for composer, piece in zip(composers, pieces):
                # Generate row data
                row_data = [presenter, event_id, ticket_url, city, venue_name, latitude, longitude, 
                            title, concert_type, dates, performer, role, composer, piece, selection, 
                            arranger, note]
                # Write to CSV
                print(f"Writing to CSV: {row_data}")
                writer.writerow(row_data)

# Quit the driver
driver.quit()
