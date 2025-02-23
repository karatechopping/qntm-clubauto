# src/test_ghl.py

from output_handlers.ghl_handler import GHLHandler


def test_main():
    try:
        ghl = GHLHandler()
        results = ghl.test_upsert()
        print("Test complete")
        print(f"Results: {results}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_main()
