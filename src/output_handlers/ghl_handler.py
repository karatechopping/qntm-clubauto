import os
import asyncio
import aiohttp
import time
import random
import json
import logging
from datetime import datetime, timedelta

class GHLHandler:
    SAMPLE_SIZE = -1  # Add this back to the class constants
    RATE_LIMIT = 100
    RATE_WINDOW = 10
    CONCURRENT_THREADS = 10
    REQUEST_DELAY = 0.2
    MAX_RETRIES = 3
    RETRY_DELAY = 5
    BURST_THRESHOLD = 25
    SAFETY_BUFFER = 1.0

    def __init__(self):
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
        self.request_times = []
        self.remaining_daily = None
        self.remaining_burst = None
        self.interval_ms = None
        self.rate_limit_max = None
        self.last_burst_time = time.time()
        self.window_start_time = time.time()
        self.requests_in_current_window = 0

        self.setup_logging()

    def setup_logging(self):
        if not os.path.exists('logs'):
            os.makedirs('logs')

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = f'logs/ghl_processing_{timestamp}.log'

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Starting new processing session - Log file: {log_file}")

    async def _update_rate_limits(self, response):
        """Update rate limit tracking based on response headers"""
        old_remaining = self.remaining_burst

        self.remaining_daily = int(response.headers.get('X-RateLimit-Daily-Remaining', 0))
        self.remaining_burst = int(response.headers.get('X-RateLimit-Remaining', 0))
        self.interval_ms = int(response.headers.get('X-RateLimit-Interval-Milliseconds', 10000))
        self.rate_limit_max = int(response.headers.get('X-RateLimit-Max', 100))

        self.logger.info(f"Rate limits updated - Old remaining: {old_remaining}, New remaining: {self.remaining_burst}, " +
                        f"Daily remaining: {self.remaining_daily}, Interval: {self.interval_ms}ms")

    def _prepare_contact_data(self, contact):
        """Prepare contact data for GHL API"""
        if not contact.get("email") and not contact.get("phone"):
            raise ValueError("Contact must have either email or phone number")

        ghl_contact = {
            "locationId": self.location_id,
            "tags": ["brett-api-test"],
        }

        # Map standard fields
        standard_fields = ["firstName", "lastName", "email", "phone",
                         "address1", "city", "state", "gender", "postalCode"]

        for field in standard_fields:
            if contact.get(field):
                ghl_contact[field] = contact[field]

        # Map custom fields
        custom_fields = []
        for field, value in contact.items():
            if field.endswith("_id") and contact.get(field.replace("_id", "")):
                custom_fields.append({
                    "id": value,
                    "value": contact[field.replace("_id", "")]
                })

        if custom_fields:
            ghl_contact["customFields"] = custom_fields

        return ghl_contact

    async def _make_api_call(self, session, contact_data, retry_count=0):
        """Make API call with rate limiting and retries"""
        try:
            current_time = time.time()
            time_since_burst = current_time - self.last_burst_time

            # Check if we need to start a new window
            if (self.remaining_burst and self.remaining_burst < self.BURST_THRESHOLD) or time_since_burst >= 8:
                wait_time = max(0, (10 - time_since_burst))
                self.logger.info(f"Starting new window - waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time + 0.5)  # Added safety buffer
                self.last_burst_time = time.time()
                self.requests_in_current_window = 0

            # Add delay between requests
            await asyncio.sleep(0.2)

            start_time = time.time()
            self.requests_in_current_window += 1

            async with session.post(
                f"{self.base_url}/contacts/upsert",
                headers=self.headers,
                json=contact_data
            ) as response:
                await self._update_rate_limits(response)
                response_text = await response.text()

                if response.status == 429:  # Rate limit hit
                    self.logger.warning(f"Rate limit hit - remaining: {self.remaining_burst}")
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
        """Process a single contact with rate limiting"""
        async with semaphore:
            try:
                ghl_contact = self._prepare_contact_data(contact)
                await asyncio.sleep(self.REQUEST_DELAY)

                response_json, contact_data = await self._make_api_call(session, ghl_contact)

                is_new = response_json.get('new', False)
                action = "Created new contact" if is_new else "Updated existing contact"

                self.logger.info(
                    f"{action}: {ghl_contact.get('firstName', '')} "
                    f"{ghl_contact.get('lastName', '')}"
                )

                self.successful_contacts.append({
                    "name": f"{contact.get('firstName', '')} {contact.get('lastName', '')}",
                    "action": action,
                    "response": response_json
                })

                return response_json

            except Exception as e:
                self.logger.error(
                    f"Error processing contact "
                    f"{contact.get('firstName', '')} {contact.get('lastName', '')}: {str(e)}"
                )
                self.failed_contacts.append({
                    "name": f"{contact.get('firstName', '')} {contact.get('lastName', '')}",
                    "email": contact.get("email", "No email"),
                    "phone": contact.get("phone", "No phone"),
                    "error": str(e),
                    "detail": str(e),
                })
                return None

    async def _process_all_contacts(self, contacts):
        """Process all contacts with concurrency control"""
        timeout = aiohttp.ClientTimeout(total=60)
        semaphore = asyncio.Semaphore(self.CONCURRENT_THREADS)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            tasks = []
            for i, contact in enumerate(contacts):
                if i > 0 and i % 50 == 0:
                    self.logger.info(f"Processed {i}/{len(contacts)} contacts...")
                    if self.remaining_daily is not None:
                        self.logger.info(f"Daily requests remaining: {self.remaining_daily}")

                tasks.append(self._process_single_contact(session, contact, semaphore))

            results = await asyncio.gather(*tasks, return_exceptions=True)
            return [r for r in results if r is not None]

    def process_contacts(self, contacts):
        """Main entry point for processing contacts"""
        start_time = time.time()

        # Handle sample size
        if self.SAMPLE_SIZE == -1:
            contacts_to_process = contacts
            self.logger.info(f"Processing all {len(contacts)} contacts")
        else:
            contacts_to_process = random.sample(
                contacts,
                min(self.SAMPLE_SIZE, len(contacts))
            )
            self.logger.info(f"Processing {len(contacts_to_process)} randomly selected contacts")

        results = asyncio.run(self._process_all_contacts(contacts_to_process))

        end_time = time.time()
        upload_duration = end_time - start_time
        minutes = int(upload_duration // 60)
        seconds = int(upload_duration % 60)

        self.logger.info("\n=== PROCESSING SUMMARY ===")
        self.logger.info(f"Total time: {minutes} minutes and {seconds} seconds")
        self.logger.info(f"Successfully processed: {len(self.successful_contacts)} contacts")
        self.logger.info(f"Failed: {len(self.failed_contacts)} contacts")

        if self.request_times:
            avg_time = sum(self.request_times) / len(self.request_times)
            requests_per_second = 1 / avg_time if avg_time > 0 else 0
            self.logger.info(f"Average request time: {avg_time:.2f} seconds")
            self.logger.info(f"Effective requests per second: {requests_per_second:.2f}")

        if self.remaining_daily is not None:
            self.logger.info(f"Remaining daily capacity: {self.remaining_daily} requests")

        if self.failed_contacts:
            self.logger.error("\n=== FAILED CONTACTS REPORT ===")
            for idx, failure in enumerate(self.failed_contacts, 1):
                self.logger.error(f"\n{idx}. Contact: {failure['name']}")
                self.logger.error(f"   Email: {failure['email']}")
                self.logger.error(f"   Phone: {failure['phone']}")
                self.logger.error(f"   Error: {failure['error']}")
                self.logger.error("   " + "-" * 50)

        return results