# src/output_handlers/ghl_handler.py

import os
import requests
import time


class GHLHandler:
    def __init__(self):
        self.api_key = os.environ.get("GHL_API")
        self.location_id = os.environ.get("GHL_LOCATION")
        if not self.api_key or not self.location_id:
            raise ValueError(
                "GHL_API and GHL_LOCATION environment variables must be set"
            )

        self.base_url = "https://services.leadconnectorhq.com"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Version": "2021-04-15",
        }

    def test_upsert(self):
        """Test function to upsert two hardcoded contacts"""
        test_contacts = [
            {
                "firstName": "Rosan",
                "lastName": "Deo3",
                "email": "rosan@deoss22.com",
                "locationId": self.location_id,
                "gender": "male",
                "phone": "+1 888-888-9999",
                "address1": "3535 1st St N",
                "city": "Dolomite",
                "tags": ["brett-api"],
            },
            {
                "firstName": "Sarah",
                "lastName": "Smith",
                "email": "sarah@deoss22.com",
                "locationId": self.location_id,
                "gender": "female",
                "phone": "+1 888-888-0000",
                "address1": "4242 2nd St S",
                "city": "Brighton",
                "tags": ["brett-api"],
            },
        ]

        results = []
        for contact in test_contacts:
            try:
                response = requests.post(
                    f"{self.base_url}/contacts/upsert",
                    headers=self.headers,
                    json=contact,
                )
                response.raise_for_status()
                results.append(response.json())
                print(
                    f"Successfully upserted {contact['firstName']} {contact['lastName']}"
                )
                print(f"Response: {response.json()}")
                time.sleep(0.1)  # Small delay between requests

            except requests.exceptions.RequestException as e:
                print(f"Error upserting contact: {e}")
                if hasattr(e, "response") and e.response is not None:
                    print(f"Response text: {e.response.text}")

        return results
