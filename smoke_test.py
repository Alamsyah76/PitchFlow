"""Simple smoke test for backend health and Supabase connectivity.

Run from project root after activating backend venv:

  .\backend\venv_py311\Scripts\Activate.ps1
  python smoke_test.py

Exit codes:
  0 = all checks passed
  1 = health check failed
  2 = supabase check failed (or env missing)
"""
import os
import sys
import requests
from dotenv import load_dotenv


def check_health(url: str) -> bool:
    try:
        r = requests.get(url, timeout=5)
        print(f"Health: {r.status_code} - {r.text}")
        return r.status_code == 200
    except Exception as e:
        print(f"Health check error: {e}")
        return False


def check_supabase(supabase_url: str, service_key: str) -> bool:
    # Uses the REST endpoint to query a small row from `contents` table
    try:
        headers = {"apikey": service_key, "Authorization": f"Bearer {service_key}"}
        url = supabase_url.rstrip("/") + "/rest/v1/contents?select=id&limit=1"
        r = requests.get(url, headers=headers, timeout=8)
        print(f"Supabase REST: {r.status_code}")
        return r.status_code == 200
    except Exception as e:
        print(f"Supabase check error: {e}")
        return False


def main():
    load_dotenv()

    health_url = os.getenv("BACKEND_HEALTH_URL", "http://127.0.0.1:8000/health")
    ok = check_health(health_url)
    if not ok:
        print("Backend health check failed")
        sys.exit(1)

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not supabase_service_key:
        print("Supabase ENV not configured — skipping Supabase connectivity check")
        sys.exit(0)

    ok2 = check_supabase(supabase_url, supabase_service_key)
    if not ok2:
        print("Supabase connectivity check failed")
        sys.exit(2)

    print("All smoke checks passed")
    sys.exit(0)


if __name__ == "__main__":
    main()
