import os
import requests
import time
import random
import json
from datetime import datetime, timedelta


class GHLHandler:
    SAMPLE_SIZE = 200
    RATE_LIMIT = 100
    RATE_WINDOW = 10

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

        # Add failed contacts tracking
        self.failed_contacts = []

    def _make_api_call(self, contact_data):
        """Make API call"""
        return requests.post(
            f"{self.base_url}/contacts/upsert", headers=self.headers, json=contact_data
        )

    def _prepare_contact_data(self, contact):
        """Prepare contact data for GHL API"""
        # Validate required fields
        if not contact.get("email") and not contact.get("phone"):
            raise ValueError("Contact must have either email or phone number")

        ghl_contact = {
            "locationId": self.location_id,
            "tags": ["brett-api-test"],
        }

        # Add standard fields from contact data
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
            if contact.get(field):
                ghl_contact[field] = contact[field]

        # Add custom fields
        custom_fields = []
        for field, value in contact.items():
            if field.endswith("_id") and contact.get(field.replace("_id", "")):
                custom_fields.append(
                    {"id": value, "value": contact[field.replace("_id", "")]}
                )

        if custom_fields:
            ghl_contact["customFields"] = custom_fields

        return ghl_contact

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

        successful_updates = 0
        results = []

        for contact in contacts_to_process:
            try:
                # Prepare GHL contact data
                try:
                    ghl_contact = self._prepare_contact_data(contact)
                except ValueError as ve:
                    # Add to failed contacts when validation fails
                    self.failed_contacts.append(
                        {
                            "name": f"{contact.get('firstName', '')} {contact.get('lastName', '')}",
                            "email": contact.get("email", "No email"),
                            "phone": contact.get("phone", "No phone"),
                            "error": str(ve),
                            "detail": "Validation Error",
                        }
                    )
                    print(
                        f"\nSkipping contact {contact.get('firstName', '')} {contact.get('lastName', '')}: {str(ve)}"
                    )
                    continue

                # Make the API call
                response = self._make_api_call(ghl_contact)

                response.raise_for_status()
                results.append(response.json())
                successful_updates += 1
                print(
                    f"Successfully upserted {ghl_contact.get('firstName', '')} {ghl_contact.get('lastName', '')}"
                )

            except requests.exceptions.RequestException as e:
                error_message = str(e)
                if hasattr(e, "response") and e.response is not None:
                    error_detail = e.response.text
                else:
                    error_detail = "No response details available"

                # Record the failure
                self.failed_contacts.append(
                    {
                        "name": f"{contact.get('firstName', '')} {contact.get('lastName', '')}",
                        "email": contact.get("email", "No email"),
                        "phone": contact.get("phone", "No phone"),
                        "error": error_message,
                        "detail": error_detail,
                    }
                )
                print(f"\nError upserting contact: {error_message}")
                print(f"Response text: {error_detail}")

        # Print summary
        print(
            f"\nCompleted GHL updates: {successful_updates} contacts successfully processed"
        )

        # Print failure report if there were any failures
        if self.failed_contacts:
            print("\n=== FAILED CONTACTS REPORT ===")
            print(f"Total failures: {len(self.failed_contacts)}")
            print("\nDetailed Failures:")
            for idx, failure in enumerate(self.failed_contacts, 1):
                print(f"\n{idx}. Contact: {failure['name']}")
                print(f"   Email: {failure['email']}")
                print(f"   Phone: {failure['phone']}")
                print(f"   Error: {failure['error']}")
                if "Bad Request" not in failure["detail"]:
                    print(f"   Detail: {failure['detail']}")
                print("   " + "-" * 50)

        return results
