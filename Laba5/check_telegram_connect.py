import os
import socket
import time
import requests
from dotenv import load_dotenv


def check_dns(host: str) -> bool:
    try:
        ip = socket.gethostbyname(host)
        print(f"[OK] DNS: {host} -> {ip}")
        return True
    except Exception as e:
        print(f"[FAIL] DNS: {host} ({e})")
        return False


def check_tcp(host: str, port: int = 443, timeout: float = 5.0) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    start = time.time()
    try:
        s.connect((host, port))
        elapsed = (time.time() - start) * 1000
        print(f"[OK] TCP: {host}:{port} ({elapsed:.1f} ms)")
        return True
    except Exception as e:
        print(f"[FAIL] TCP: {host}:{port} ({e})")
        return False
    finally:
        s.close()


def check_https(url: str, timeout: float = 10.0) -> bool:
    try:
        r = requests.get(url, timeout=timeout)
        print(f"[OK] HTTPS: {url} -> HTTP {r.status_code}")
        return True
    except Exception as e:
        print(f"[FAIL] HTTPS: {url} ({e})")
        return False


def check_bot_token(token: str, timeout: float = 10.0) -> bool:
    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        r = requests.get(url, timeout=timeout)
        data = r.json()
        if r.status_code == 200 and data.get("ok"):
            username = data.get("result", {}).get("username", "unknown")
            print(f"[OK] Bot token valid: @{username}")
            return True
        print(f"[FAIL] Bot token invalid: HTTP {r.status_code}, response={data}")
        return False
    except Exception as e:
        print(f"[FAIL] Bot API check ({e})")
        return False


def main() -> int:
    load_dotenv()
    token = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")

    host = "api.telegram.org"
    print("=== Telegram connectivity check ===")

    ok_dns = check_dns(host)
    ok_tcp = check_tcp(host, 443)
    ok_https = check_https(f"https://{host}")

    ok_token = True
    if token:
        ok_token = check_bot_token(token)
    else:
        print("[WARN] BOT_TOKEN/TELEGRAM_BOT_TOKEN not found in .env, skip getMe check")

    all_ok = ok_dns and ok_tcp and ok_https and ok_token
    print("\nRESULT:", "PASS" if all_ok else "FAIL")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())