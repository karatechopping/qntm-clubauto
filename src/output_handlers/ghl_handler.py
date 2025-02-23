# src/output_handlers/ghl_handler.py
import os
import requests
import time
import random
import json


class GHLHandler:
    SAMPLE_SIZE = 10

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

        # Define custom field mappings
        self.custom_field_ids = {
            "homePhone": "SCniAw3rl6DU6SH90OJi",
            "workPhone": "vFOXH73DDi9WOabRLsNp",
            "cellPhone": "OzwZRpooGyR8Ayrc84u4",
            "zip": "TAD26hyktLxWKZa9tOUS",
            "membership_type": "e2f0o6TtMCkoKvLipmrs",
            "member_activeinactive": "a42q57p3xl4uSYKThK5C",
            "member_status": "zsoJAoVViTFLHqgexbLl",
            "member_number": "cewzf3ASjgkju43LCaB0",
            "opt_out_status": "7SXK1pY4CNzPyFndQOAv",
            "delivery_method": "NX3D1NYKLdDmOJYwGlgb",
        }

    def _prepare_contact_data(self, contact):
        """Prepare contact data for GHL API"""
        # Initialize basic contact structure
        ghl_contact = {
            "locationId": self.location_id,
            "tags": ["brett-api-test"],
        }

        # Add standard fields if they exist
        standard_fields = {
            "firstName": "firstName",
            "lastName": "lastName",
            "email": "email",
            "phone": "phone",
            "address1": "address1",
            "city": "city",
            "state": "state",
            "gender": "gender",
            "postalCode": "postalCode",
        }

        for contact_field, ghl_field in standard_fields.items():
            if contact.get(contact_field):
                ghl_contact[ghl_field] = contact[contact_field]

        # Prepare custom fields
        custom_fields = []

        # Phone fields
        if contact.get("homePhone"):
            custom_fields.append(
                {
                    "id": self.custom_field_ids["homePhone"],
                    "value": contact["homePhone"],
                }
            )
        if contact.get("workPhone"):
            custom_fields.append(
                {
                    "id": self.custom_field_ids["workPhone"],
                    "value": contact["workPhone"],
                }
            )
        if contact.get("cellPhone"):
            custom_fields.append(
                {
                    "id": self.custom_field_ids["cellPhone"],
                    "value": contact["cellPhone"],
                }
            )

        # Other custom fields
        if contact.get("postalCode"):
            custom_fields.append(
                {"id": self.custom_field_ids["zip"], "value": contact["postalCode"]}
            )
        if contact.get("membership_type"):
            custom_fields.append(
                {
                    "id": self.custom_field_ids["membership_type"],
                    "value": contact["membership_type"],
                }
            )
        if contact.get("status"):
            custom_fields.append(
                {
                    "id": self.custom_field_ids["member_activeinactive"],
                    "value": contact["status"],
                }
            )
            custom_fields.append(
                {
                    "id": self.custom_field_ids["member_status"],
                    "value": contact["status"],
                }
            )
        if contact.get("member_number"):
            custom_fields.append(
                {
                    "id": self.custom_field_ids["member_number"],
                    "value": contact["member_number"],
                }
            )
        if contact.get("opt_out_status"):
            custom_fields.append(
                {
                    "id": self.custom_field_ids["opt_out_status"],
                    "value": contact["opt_out_status"],
                }
            )
        if contact.get("delivery_method"):
            custom_fields.append(
                {
                    "id": self.custom_field_ids["delivery_method"],
                    "value": contact["delivery_method"],
                }
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
                ghl_contact = self._prepare_contact_data(contact)

                print("\nPrepared GHL contact data:")
                print(json.dumps(ghl_contact, indent=2))

                response = requests.post(
                    f"{self.base_url}/contacts/upsert",
                    headers=self.headers,
                    json=ghl_contact,
                )

                print("\nAPI Response:")
                print(f"Status Code: {response.status_code}")
                print(json.dumps(response.json(), indent=2))

                response.raise_for_status()
                results.append(response.json())
                successful_updates += 1
                print(
                    f"\nSuccessfully upserted {ghl_contact['firstName']} {ghl_contact['lastName']}"
                )

            except requests.exceptions.RequestException as e:
                error_message = str(e)
                if hasattr(e, "response") and e.response is not None:
                    error_detail = e.response.text
                else:
                    error_detail = "No response details available"

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

            time.sleep(0.1)

        print(
            f"\nCompleted GHL updates: {successful_updates} contacts successfully processed"
        )

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
