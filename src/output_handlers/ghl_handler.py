# src/output_handlers/ghl_handler.py
import os
import requests
import time
import random


class GHLHandler:
    SAMPLE_SIZE = 10  # -1 means process all records, any positive number processes that many records

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

    def process_contacts(self, transformed_contacts):
        """Process transformed contacts, either all or a sample"""
        if self.SAMPLE_SIZE == -1:
            contacts_to_process = transformed_contacts
            print(f"\nProcessing all {len(transformed_contacts)} contacts")
        else:
            contacts_to_process = random.sample(
                transformed_contacts, min(self.SAMPLE_SIZE, len(transformed_contacts))
            )
            print(f"\nProcessing {len(contacts_to_process)} randomly selected contacts")
            if self.SAMPLE_SIZE <= 10:
                print("Selected contacts:")
                for contact in contacts_to_process:
                    print(
                        f"- {contact.get('firstName', '')} {contact.get('lastName', '')} ({contact.get('email', 'no email')})"
                    )
                print()

        successful_updates = 0
        results = []

        for contact in contacts_to_process:
            try:
                # Separate standard fields from custom fields
                custom_fields = []
                ghl_contact = {
                    "locationId": self.location_id,
                    "tags": ["brett-api-test"],
                }

                # Add all standard fields that exist in the contact
                standard_fields = [
                    "firstName",
                    "lastName",
                    "email",
                    "phone",
                    "address1",
                    "city",
                    "state",
                    "gender",
                    "postalCode",
                ]

                for field in standard_fields:
                    if field in contact:
                        ghl_contact[field] = contact[field]

                # Process custom fields
                for key, value in contact.items():
                    if key.endswith("_id"):  # This is a custom field ID
                        field_name = key[:-3]  # Remove '_id' to get the field name
                        if field_name in contact:  # If we have a value for this field
                            custom_fields.append(
                                {"id": value, "value": contact[field_name]}
                            )

                ghl_contact["customFields"] = custom_fields

                response = requests.post(
                    f"{self.base_url}/contacts/upsert",
                    headers=self.headers,
                    json=ghl_contact,
                )
                response.raise_for_status()
                results.append(response.json())
                successful_updates += 1
                print(
                    f"Successfully upserted {ghl_contact['firstName']} {ghl_contact['lastName']}"
                )
                print(f"Response: {response.json()}")
                time.sleep(0.1)  # Small delay between requests

            except requests.exceptions.RequestException as e:
                print(f"Error upserting contact: {e}")
                if hasattr(e, "response") and e.response is not None:
                    print(f"Response text: {e.response.text}")

        print(
            f"\nCompleted GHL updates: {successful_updates} contacts successfully processed"
        )
        return results
