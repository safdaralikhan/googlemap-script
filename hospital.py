import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configure Chrome options
chrome_options = Options()
chrome_options.add_argument("--start-maximized")

# WebDriver setup
driver = webdriver.Chrome(options=chrome_options)

# Step 1: Read the CSV file to get hospital links
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

# Step 2: Open each link one by one and extract data
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

# Close the browser after visiting all the links
driver.quit()
print("\nAll links have been processed.")

# Step 3: Save the data to a new CSV file
try:
    with open(output_file, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Address", "Website", "Phone Number"])  # Write header
        writer.writerows(data)  # Write data
    print(f"Extracted data saved to {output_file}.")
except Exception as e:
    print(f"Error saving data to {output_file}: {e}")
