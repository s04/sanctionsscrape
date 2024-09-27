import json
from time import sleep
from playwright.sync_api import sync_playwright
import time


# Function to extract table data
def extract_table_data(page):
    # Select the table using the provided XPath
    table_xpath = '//*[@id="content"]/div/div[5]/div/div/div[1]/table'

    # Get all the rows in the table
    rows = page.query_selector_all(f"{table_xpath}//tr")

    data = []
    headers = [
        header.inner_text() for header in rows[0].query_selector_all("th")
    ]  # Get table headers

    # Loop through the rows and extract cell data
    for row in rows[1:]:
        cells = row.query_selector_all("td")
        if len(cells) == len(headers):  # Ensure row length matches header length
            data.append(
                {headers[i]: cells[i].inner_text() for i in range(len(headers))}
            )

    return data


# Main Playwright script
def scrape_table_to_json():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://sanctionslist.ofac.treas.gov/Home/DeltaFileArchive")
        time.sleep(10)
        # Wait for the table to load with a longer timeout (30 seconds)
        page.wait_for_selector(
            'xpath=//*[@id="content"]/div/div[5]/div/div/div[1]/table', timeout=30000
        )

        # Extract table data and convert to JSON
        table_data = extract_table_data(page)

        # Save data as JSON
        with open("table_data.json", "w") as f:
            json.dump(table_data, f, indent=4)

        browser.close()


if __name__ == "__main__":
    scrape_table_to_json()
