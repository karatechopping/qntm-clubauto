import os


def test_env_vars():
    required_vars = ["CLIENT_SECRET", "SMTP_USERNAME", "SMTP_PASSWORD"]

    print("\nChecking environment variables:")
    all_present = True
    for var in required_vars:
        exists = var in os.environ
        print(f"{var}: {'✓ SET' if exists else '✗ NOT SET'}")
        if not exists:
            all_present = False

    if all_present:
        print("\nAll required environment variables are set")
    else:
        print("\nWARNING: Some required variables are missing")


if __name__ == "__main__":
    test_env_vars()
