import json
import os
from playwright.sync_api import sync_playwright
import time


# Function to extract table data and handle downloads
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
    for row_index, row in enumerate(rows[1:], start=1):
        cells = row.query_selector_all("td")
        if len(cells) == len(headers):  # Ensure row length matches header length
            row_data = {
                headers[i]: cells[i].inner_text() for i in range(len(headers) - 1)
            }  # Exclude last column for now

            # Handle the download button by simulating a click
            with page.expect_download() as download_info:
                download_button = row.query_selector(
                    f"td:nth-child(4) button"
                )  # Assuming it's the 4th column
                download_button.click()

            download = download_info.value
            download_path = download.path()  # Get the download path
            download_url = download.url  # Get the download URL

            row_data["Download Link"] = download_url  # Add the download URL to the data

            data.append(row_data)

    return data


# Main Playwright script
def scrape_table_to_json():
    download_dir = "./downloads"
    os.makedirs(download_dir, exist_ok=True)  # Ensure the directory exists

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set headless=False for debugging
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        page.goto("https://sanctionslist.ofac.treas.gov/Home/DeltaFileArchive")

        # Wait for the page to load fully
        time.sleep(10)

        # Wait for the table to load with a longer timeout (30 seconds)
        page.wait_for_selector(
            'xpath=//*[@id="content"]/div/div[5]/div/div/div[1]/table', timeout=30000
        )

        # Extract table data and convert to JSON
        table_data = extract_table_data(page)

        # Save data as JSON
        with open("table_data_with_download_links.json", "w") as f:
            json.dump(table_data, f, indent=4)

        browser.close()


if __name__ == "__main__":
    scrape_table_to_json()
