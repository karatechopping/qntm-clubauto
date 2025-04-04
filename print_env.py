import os
from dotenv import load_dotenv

# 1. Load environment variables from .env file
#    override=True ensures that values from .env replace any existing
#    environment variables (including empty ones).
load_dotenv(override=True)

# 2. Get the value of the 'GHL_LOCATION' environment variable
ghl_location_value = os.getenv("GHL_LOCATION")

# 3. Print the value to the terminal
print(ghl_location_value)
