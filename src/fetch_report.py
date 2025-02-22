# src/data_fetcher.py
import requests
import os
import sys
from datetime import datetime


class DataFetcher:
    def __init__(self):
        self.client_id = "prod_qntmfitlife"
        self.client_secret = os.getenv("CLIENT_SECRET")
        if not self.client_secret:
            print("Error: CLIENT_SECRET environment variable not set.")
            sys.exit(1)
        self.scope = "CA_qntmfitlife"
        self.grant_type = "client_credentials"

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

    def get_data(self):
        access_token = self.get_access_token()
        report_url = "https://api.partners.daxko.com/api/v1/reports/1"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        output_fields = [
            "FirstName",
            "LastName",
            "Email",
            "PhoneCell",
            "Gender",
            "Status",
            "OptOutStatus",
        ]

        criteria_fields = {"user": {"gender": "0"}}

        payload = {
            "id": 1,
            "outputFields": output_fields,
            "criteriaFields": criteria_fields,
            "pageSize": 1000,
            "pageNumber": 1,
        }

        try:
            response = requests.post(report_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            raise
