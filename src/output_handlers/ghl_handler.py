import os
import asyncio
import aiohttp
import time
import json
import logging
from datetime import datetime

class GHLHandler:
    RATE_LIMIT = 100
    RATE_WINDOW = 10
    CONCURRENT_THREADS = 10
    REQUEST_DELAY = 0.2
    MAX_RETRIES = 3
    RETRY_DELAY = 5
    BURST_THRESHOLD = 25
    SAFETY_BUFFER = 1.0

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_key = os.environ.get("GHL_API")
        self.location_id = os.environ.get("GHL_LOCATION")
        if not self.api_key or not self.location_id:
            raise ValueError("GHL_API and GHL_LOCATION environment variables must be set")

        self.base_url = "https://services.leadconnectorhq.com"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Version": "2021-04-15",
        }

        self.failed_contacts = []
        self.successful_contacts = []
        self.added_contacts = []
        self.updated_contacts = []
        self.request_times = []
        self.remaining_daily = None
        self.remaining_burst = None
        self.interval_ms = None
        self.rate_limit_max = None
        self.last_burst_time = time.time()
        self.window_start_time = time.time()
        self.requests_in_current_window = 0

        self.logger.info("Starting GHL Processing")

    async def _update_rate_limits(self, response):
        """Update rate limit tracking based on response headers"""
        self.remaining_daily = int(response.headers.get('X-RateLimit-Daily-Remaining', 0))
        self.remaining_burst = int(response.headers.get('X-RateLimit-Remaining', 0))
        self.interval_ms = int(response.headers.get('X-RateLimit-Interval-Milliseconds', 10000))
        self.rate_limit_max = int(response.headers.get('X-RateLimit-Max', 100))

    def _prepare_contact_data(self, contact):
        """Prepare contact data for GHL API"""
        if not contact.get("email") and not contact.get("phone"):
            raise ValueError("Contact must have either email or phone number")

        ghl_contact = {
            "locationId": self.location_id,
            "tags": ["api"],
        }

        standard_fields = ["firstName", "lastName", "email", "phone",
                        "address1", "city", "state", "gender", "postalCode"]

        for field in standard_fields:
            if contact.get(field):
                ghl_contact[field] = contact[field]

        custom_fields = []

        for field, value in contact.items():
            if field.endswith("_id") and field.replace("_id", "") in contact:
                base_field = field.replace("_id", "")
                custom_fields.append({
                    "id": value,
                    "value": contact[base_field]
                })

        if custom_fields:
            ghl_contact["customFields"] = custom_fields

        return ghl_contact


    async def _make_api_call(self, session, contact_data, retry_count=0):
        try:
            current_time = time.time()
            time_since_burst = current_time - self.last_burst_time

            if (self.remaining_burst and self.remaining_burst < self.BURST_THRESHOLD) or time_since_burst >= 8:
                wait_time = max(0, (10 - time_since_burst))
                await asyncio.sleep(wait_time + 0.5)
                self.last_burst_time = time.time()
                self.requests_in_current_window = 0

            await asyncio.sleep(0.2)
            self.requests_in_current_window += 1

            async with session.post(
                f"{self.base_url}/contacts/upsert",
                headers=self.headers,
                json=contact_data
            ) as response:
                await self._update_rate_limits(response)
                response_text = await response.text()

                if response.status == 429:
                    if retry_count < self.MAX_RETRIES:
                        await asyncio.sleep(3)
                        return await self._make_api_call(session, contact_data, retry_count + 1)
                    raise aiohttp.ClientError("Max retries exceeded")

                if response.status not in [200, 201]:
                    raise aiohttp.ClientError(f"Status: {response.status}, Error: {response_text}")

                return json.loads(response_text), contact_data

        except Exception as e:
            if retry_count < self.MAX_RETRIES:
                await asyncio.sleep(self.RETRY_DELAY)
                return await self._make_api_call(session, contact_data, retry_count + 1)
            raise

    async def _process_single_contact(self, session, contact, semaphore):
        async with semaphore:
            try:
                ghl_contact = self._prepare_contact_data(contact)
                response_json, contact_data = await self._make_api_call(session, ghl_contact)

                contact_info = {
                    "name": f"{contact.get('firstName', '')} {contact.get('lastName', '')}",
                    "email": contact.get('email', ''),
                    "phone": contact.get('phone', ''),
                    "system_id": contact.get('ca_systemidnum', 'No ID'),
                    "id": response_json.get('contact', {}).get('id'),
                }

                is_new = response_json.get('new', False)
                if is_new:
                    self.added_contacts.append(contact_info)
                    self.logger.info(f"Added: {contact_info['name']} (ID: {contact_info['system_id']})")
                else:
                    self.updated_contacts.append(contact_info)
                    self.logger.info(f"Updated: {contact_info['name']} (ID: {contact_info['system_id']})")

                self.successful_contacts.append(contact_info)
                return response_json

            except Exception as e:
                self.logger.error(
                    f"Failed: {contact.get('firstName', '')} {contact.get('lastName', '')} "
                    f"(ID: {contact.get('ca_systemidnum', 'No ID')}) - {str(e)}"
                )
                self.failed_contacts.append({
                    "name": f"{contact.get('firstName', '')} {contact.get('lastName', '')}",
                    "system_id": contact.get('ca_systemidnum', 'No ID'),
                    "error": str(e)
                })
                return None


    async def _process_all_contacts(self, contacts):
        timeout = aiohttp.ClientTimeout(total=60)
        semaphore = asyncio.Semaphore(self.CONCURRENT_THREADS)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            tasks = [self._process_single_contact(session, contact, semaphore)
                    for contact in contacts]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return [r for r in results if r is not None]

    def process_contacts(self, contacts):
        """Main entry point for processing contacts"""
        print(f"\nProcessing {len(contacts)} contacts...")
        start_time = time.time()

        results = asyncio.run(self._process_all_contacts(contacts))

        end_time = time.time()
        upload_duration = end_time - start_time
        minutes = int(upload_duration // 60)
        seconds = int(upload_duration % 60)

        # Print final summary
        print("\nProcessing Complete:")
        print(f"Added: {len(self.added_contacts)} | Updated: {len(self.updated_contacts)}")
        print(f"Success: {len(self.successful_contacts)} | Failed: {len(self.failed_contacts)}")
        print(f"Total time: {minutes}m {seconds}s")

        if self.failed_contacts:
            print(f"\nWARNING: {len(self.failed_contacts)} contacts failed to process")
            print("See log file for details")

        return {
            'ghl_stats': {
                'success': len(self.successful_contacts),
                'failed': len(self.failed_contacts),
                'added': len(self.added_contacts),
                'updated': len(self.updated_contacts),
                'processing_time': {
                    'minutes': minutes,
                    'seconds': seconds
                }
            }
        }
