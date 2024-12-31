import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Chrome options configure karein
chrome_options = Options()
chrome_options.add_argument("--start-maximized")

# Chrome browser initialize karein
driver = webdriver.Chrome(options=chrome_options)

# Step 1: Open Google Maps and search for hospitals
def search_hospitals():
    driver.get("https://www.google.com/maps")
    print("Google Maps opened successfully.")

    search_box = driver.find_element(By.ID, "searchboxinput")  # Google Maps search bar
    search_box.send_keys("Nearby me hospitals")
    search_box.send_keys(Keys.RETURN)  # Press Enter
    print("Searched for 'Nearby me hospitals'.")
    time.sleep(5)  # Wait for search results to load

    # Step 2: Locate hospital search results container
    results = driver.find_elements(By.CLASS_NAME, "Nv2PK")  # Locate result elements by class
    print(f"Found {len(results)} hospitals.")

    hospitals_data = []  # List to store hospital names and links

    # Step 3: Loop to keep scrolling and extracting data
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

        # Step 4: Scroll the last element to trigger loading of new data
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

    # Save hospital names and links to CSV
    with open('hospitals_data.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Link"])  # Header row with name and link
        writer.writerows(hospitals_data)

    print("Hospital names and links have been saved to 'hospitals_data.csv'.")

    # Step 5: Remove duplicates from the CSV using pandas
    df = pd.read_csv('hospitals_data.csv')
    df_new = df.drop_duplicates()
    df_new.to_csv('hospitals_data_unique.csv', index=False)
    print("Duplicate rows have been removed from 'hospitals_data_unique.csv'.")

# Step 6: Extract detailed information from the hospital links
def extract_hospital_data():
    input_file = 'hospitals_data_unique.csv'
    output_file = 'extracted_hospital_data.csv'

    try:
        with open(input_file, mode='r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header row
            links = [row[1] for row in csv_reader if row[1]]  # Extract non-empty links
    except FileNotFoundError:
        print(f"Error: File {input_file} not found. Make sure it exists in the script's directory.")
        driver.quit()
        exit()

    print(f"Found {len(links)} links.")

    data = []  # To store extracted data

    for index, link in enumerate(links):
        try:
            print(f"\nOpening hospital link {index + 1} of {len(links)}: {link}")
            driver.get(link)  # Open the link

            # Extract name
            try:
                name_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1.DUwDvf.lfPIob"))
                )
                name = name_element.text
            except Exception:
                name = "N/A"

            # Extract address
            try:
                address_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-item-id='address'] .Io6YTe"))
                )
                address = address_element.text
            except Exception:
                address = "N/A"

            # Extract website (href attribute)
            try:
                website_element = driver.find_element(By.CSS_SELECTOR, "a[data-item-id='authority']")
                website = website_element.get_attribute("href")  # Get the href attribute
            except Exception:
                website = "N/A"

            # Extract phone number (href attribute)
            try:
                phone_element = driver.find_element(By.CSS_SELECTOR, "a[href^='tel:']")
                phone = phone_element.get_attribute("href")  # Extract "tel:" link
                phone = phone.replace("tel:", "") if phone else "N/A"  # Clean up the phone number
            except Exception:
                phone = "N/A"

            # Save extracted data
            data.append([name, address, website, phone])
            print(f"Extracted: Name: {name}, Address: {address}, Website: {website}, Phone: {phone}")

        except Exception as e:
            print(f"Error processing link {index + 1}: {e}")
            data.append(["N/A", "N/A", "N/A", "N/A"])  # Save placeholder data for failed links

    # Save the data to a new CSV file
    try:
        with open(output_file, mode='w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Address", "Website", "Phone Number"])  # Write header
            writer.writerows(data)  # Write data
        print(f"Extracted data saved to {output_file}.")
    except Exception as e:
        print(f"Error saving data to {output_file}: {e}")

# Main execution flow
if __name__ == "__main__":
    # Step 1: Search and extract hospital links
    search_hospitals()

    # Step 2: Extract detailed information for each hospital
    extract_hospital_data()

    # Close the browser at the end
    driver.quit()
