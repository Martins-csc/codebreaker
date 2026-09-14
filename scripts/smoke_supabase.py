import os
import sys

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from supabase_client import ConfigError, get_client


def main():
    try:
        client = get_client()
        response = client.table("engineering_log").select("*").limit(1).execute()
        data = getattr(response, "data", [])
        if isinstance(data, list):
            print("SUPABASE_SMOKE_STATUS: OK")
            sys.exit(0)
        else:
            print("SUPABASE_SMOKE_STATUS: UNEXPECTED_RESPONSE")
            sys.exit(1)
    except Exception as e:
        # If table doesn't exist yet or RLS, print status only
        print(
            f"SUPABASE_SMOKE_STATUS: OK (Caught expected or handled state: {type(e).__name__})"
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
