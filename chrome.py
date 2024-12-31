import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import pandas as pd

# Chrome options configure karein
chrome_options = Options()
chrome_options.add_argument("--start-maximized")

# Chrome browser initialize karein
driver = webdriver.Chrome(options=chrome_options)

try:
    # Step 1: Open Google Maps
    driver.get("https://www.google.com/maps")
    print("Google Maps opened successfully.")

    # Step 2: Search for "Nearby me hospitals"
    search_box = driver.find_element(By.ID, "searchboxinput")  # Google Maps search bar
    search_box.send_keys("Nearby me hospitals")
    search_box.send_keys(Keys.RETURN)  # Press Enter
    print("Searched for 'Nearby me hospitals'.")
    time.sleep(5)  # Wait for search results to load

    # Step 3: Locate hospital search results container
    results = driver.find_elements(By.CLASS_NAME, "Nv2PK")  # Locate result elements by class
    print(f"Found {len(results)} hospitals.")

    hospitals_data = []  # List to store hospital names and links

    # Step 4: Loop to keep scrolling and extracting data
    while True:
        # Process all the hospitals in the current view
        for index, result in enumerate(results):
            try:
                print(f"Processing hospital {index + 1}...")
                # Extract hospital name from the aria-label attribute
                anchor = result.find_element(By.CSS_SELECTOR, "a")
                name = anchor.get_attribute("aria-label")
                link = anchor.get_attribute("href")

                if name and link:
                    hospitals_data.append([name, link])  # Append name and link to the list
                    print(f"Extracted: {name} - {link}")
            except Exception as e:
                print(f"Error processing hospital {index + 1}: {e}")
                continue

        # Step 5: Scroll the last element to trigger loading of new data
        last_result = results[-1]  # Get the last result element in the current view
        driver.execute_script("arguments[0].scrollIntoView(true);", last_result)  # Scroll last element into view
        time.sleep(3)  # Wait for the new data to load

        # Check if new data is loaded by comparing the number of hospitals
        new_results = driver.find_elements(By.CLASS_NAME, "Nv2PK")
        if len(new_results) > len(results):
            print(f"New hospitals loaded: {len(new_results) - len(results)}")
            results = new_results  # Update results with the newly loaded hospitals
        else:
            print("No new hospitals loaded. Scrolling complete.")
            break

    # Step 6: Save data to CSV
    with open('hospitals_data.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Link"])  # Header row with name and link
        writer.writerows(hospitals_data)

    print("Hospital names and links have been saved to 'hospitals_data.csv'.")

    df = pd.read_csv('hospitals_data.csv')
    df_new = df.drop_duplicates()
    df_new.to_csv('hospitals_data_unique.csv', index=False)
    print("Duplicate rows have been removed from 'hospitals_data_unique.csv'.")

finally:
    # Close the browser
    driver.quit()
