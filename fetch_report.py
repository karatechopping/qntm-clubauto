import requests
import csv
import sys
import os
import json
from datetime import datetime


def get_access_token(client_id, client_secret, scope, grant_type):
    """
    Fetches the access token from the authentication API.
    """
    auth_url = "https://api.partners.daxko.com/auth/token"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": scope,
        "grant_type": grant_type
    }

    try:
        response = requests.post(auth_url, json=payload, headers=headers)
        response.raise_for_status()  # Raises HTTPError if the response code was unsuccessful
        data = response.json()
        access_token = data.get("access_token")
        if not access_token:
            print("Access token not found in the response.")
            sys.exit(1)
        return access_token
    except requests.exceptions.RequestException as e:
        print(f"Error obtaining access token: {e}")
        sys.exit(1)

def get_report_data(access_token, report_id, output_fields, criteria_fields, page_size=5000, max_pages=None):
    """
    Fetches all report data handling pagination based on API response.
    Continues to fetch pages until 'data' is null or 'success' is false.
    """
    report_url = f"https://api.partners.daxko.com/api/v1/reports/{report_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    all_data = []
    page_number = 1

    while True:
        payload = {
            "id": report_id,
            "outputFields": output_fields,
            "criteriaFields": criteria_fields,
            "pageSize": page_size,
            "pageNumber": page_number
        }

        try:
            response = requests.post(report_url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()

            # Check if 'success' is True and 'data' is not null
            success = result.get("success", False)
            data = result.get("data")

            if not success or data is None:
                error_message = result.get("error", "No error message provided.")
                print(f"No more data to fetch. API Response: {error_message}")
                break  # Exit the loop if no data is returned or success is False

            # Ensure 'data' is a list; if not, handle accordingly
            if not isinstance(data, list):
                print(f"Unexpected data format on page {page_number}. Expected a list but got {type(data)}.")
                sys.exit(1)

            if not data:
                print(f"No data found on page {page_number}. Ending pagination.")
                break  # No more data to fetch

            all_data.extend(data)
            print(f"Fetched page {page_number} with {len(data)} records.")

            # If the number of records fetched is less than the page size, it's likely the last page
            if len(data) < page_size:
                print(f"Last page reached at page {page_number}.")
                break

            page_number += 1

            # Optional: Prevent infinite loops by setting a maximum number of pages
            if max_pages and page_number > max_pages:
                print(f"Maximum pages ({max_pages}) reached. Stopping pagination.")
                break

        except requests.exceptions.RequestException as e:
            print(f"Error fetching report data on page {page_number}: {e}")
            sys.exit(1)

    return all_data

def write_to_csv(data, output_fields, filename="output.csv"):
    """
    Writes the fetched data to a CSV file.
    """
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=output_fields)
            writer.writeheader()
            for row in data:
                # Ensure that each row contains all the output fields
                # If a field is missing in a row, it will be written as empty
                writer.writerow({field: row.get(field, "") for field in output_fields})
        print(f"Data successfully written to {filename}")
    except IOError as e:
        print(f"Error writing to CSV file: {e}")
        sys.exit(1)

def main():
    # Configuration - Replace these values with your actual credentials and parameters
    client_id = "prod_qntmfitlife"
    
        # Retrieve client_secret from environment variable
    client_secret = os.getenv("CLIENT_SECRET")
    if not client_secret:
        print("Error: CLIENT_SECRET environment variable not set.")
        sys.exit(1)
        
    scope = "CA_qntmfitlife"
    grant_type = "client_credentials"

    report_id = 1
    output_fields = [
        "FirstName",
        "LastName",
        "Email",
        "PhoneCell",
        "Gender",
        "Status",
        "OptOutStatus"
    ]
    criteria_fields = {
        "user": {
            "gender": "0"
        }
    }
    page_size = 1000  # Adjust if needed
    output_filename = f"report_data_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.csv"
    max_pages = None  # Set to an integer value if you want to limit the number of pages

    # Step 1: Get Access Token
    print("Obtaining access token...")
    access_token = get_access_token(client_id, client_secret, scope, grant_type)
    print("Access token obtained.")

    # Step 2: Get Report Data with Pagination
    print("Fetching report data...")
    report_data = get_report_data(access_token, report_id, output_fields, criteria_fields, page_size, max_pages)
    print(f"Total records fetched: {len(report_data)}")

    if not report_data:
        print("No data retrieved from the report.")
        sys.exit(0)

    # Step 3: Write Data to CSV
    print("Writing data to CSV...")
    write_to_csv(report_data, output_fields, output_filename)

if __name__ == "__main__":
    main()
