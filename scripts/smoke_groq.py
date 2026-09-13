import os
import sys

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_engine import BlueprintError, generate_blueprint


def main():
    groq_key = os.environ.get("GROQ_API_KEY")
    if not groq_key:
        print("SKIP: GROQ_API_KEY not found in environment. Skipping live smoke test.")
        return

    print("Running live smoke test against Groq AI Engine...")
    analysis = {
        "project_name": "SmokeTestApp",
        "problem": "Build a minimal command-line utility to greet users.",
        "target_audience": "Developers",
        "skill_level": "Beginner",
    }

    try:
        blueprint = generate_blueprint(analysis)
        print("Status: SUCCESS")
        print(f"Blueprint Keys: {list(blueprint.keys())}")
        print(f"Project Name returned: {blueprint.get('project_name')}")
    except BlueprintError as e:
        print(f"Status: FAILED (BlueprintError): {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Status: FAILED (Unexpected Exception): {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
