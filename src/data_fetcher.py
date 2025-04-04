# src/data_fetcher.py
import requests
import os
import sys
from datetime import datetime

PAGESIZE = 1000
MAXPAGES = 10


class DataFetcher:
    def __init__(self, criteria_fields=None):
        self.client_id = "prod_qntmfitlife"
        self.client_secret = os.getenv("CLIENT_SECRET")
        if not self.client_secret:
            print("Error: CLIENT_SECRET environment variable not set.")
            sys.exit(1)
        self.scope = "CA_qntmfitlife"
        self.grant_type = "client_credentials"
        self.page_size = PAGESIZE
        self.criteria_fields = criteria_fields or {"user": {"gender": "0"}}

    def get_access_token(self):

        auth_url = "https://api.partners.daxko.com/auth/token"
        headers = {"Content-Type": "application/json"}
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": self.scope,
            "grant_type": self.grant_type,
        }

        try:
            response = requests.post(auth_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            access_token = data.get("access_token")
            if not access_token:
                print("Access token not found in the response.")
                sys.exit(1)
            return access_token
        except requests.exceptions.RequestException as e:
            print(f"Error obtaining access token: {e}")
            sys.exit(1)

    def get_data(self, input_fields, max_pages=MAXPAGES):
        access_token = self.get_access_token()
        report_url = "https://api.partners.daxko.com/api/v1/reports/1"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        all_data = []
        page_number = 1

        while True:
            payload = {
                "id": 1,
                "outputFields": input_fields,
                "criteriaFields": self.criteria_fields,
                "pageSize": self.page_size,
                "pageNumber": page_number,
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
                    break

                # Ensure 'data' is a list
                if not isinstance(data, list):
                    print(
                        f"Unexpected data format on page {page_number}. Expected a list but got {type(data)}."
                    )
                    sys.exit(1)

                if not data:
                    print(f"No data found on page {page_number}. Ending pagination.")
                    break

                all_data.extend(data)
                print(f"Fetched page {page_number} with {len(data)} records.")

                # If the number of records fetched is less than the page size, it's likely the last page
                if len(data) < self.page_size:
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

        return {
            "data": all_data
        }  # Maintaining the same structure as single page response
