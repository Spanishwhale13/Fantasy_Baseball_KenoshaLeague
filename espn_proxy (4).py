"""
ESPN Fantasy Baseball Proxy
----------------------------
Uses the full cookie string copied from your browser's Network tab.

Setup (one time):
  pip install flask flask-cors requests

Run:
  python espn_proxy.py

Debug: http://localhost:5001/api/debug/2026
"""

import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from urllib.parse import unquote

app = Flask(__name__)
CORS(app)

# ── Config ────────────────────────────────────────────────────────
LEAGUE_ID = "152693"
SEASON    = "2026"
API_BASE  = "https://lm-api-reads.fantasy.espn.com/apis/v3/games/flb"

# Full cookie string pasted directly from Chrome DevTools Network tab
# (Request Headers → Cookie)
RAW_COOKIE = 'device_bbe9c9a0=482aff8a-80cd-4e36-b98a-9a90a3e367b7; SWID={1CA18452-C9DD-49DD-89DB-1F5D6812CB59}; espn_s2=AECelYq%2Be4k1vMzgFUdAtfMCdiSmMahiwoUVXHZ3k2oSzpGRTqygaZ1hNjI0NEeYK%2FaoFXrvoor0fZQSUXdQILl2ZtVBwgAKI38lrQFjfRmbB1Iiy9kuVQtNRNATySOgtlECJKRyQvkkwaQYdwrxsApZZV3ReYwZzvfR8iZx6u%2FjJxtI3CXcf5H1w44oAYEjeV9Fm41KDEH7nize5PkzZYP14CCgCyE0yRt6Jjd42xXBGbfj9DKGyPqzgN00Sh1OkGmHbayCje5gCbg7xXvXDco2Z7%2FUeCFEm7YI5xtWUuap2N%2FcPoUhrVk8TO96HcB%2FrE8%3D; ESPN-ONESITE.WEB-PROD.token=5=eyJhY2Nlc3NfdG9rZW4iOiJleUpyYVdRaU9pSm5kV1Z6ZEdOdmJuUnliMnhzWlhJdExURTJNakF4T1RNMU5EUWlMQ0poYkdjaU9pSkZVekkxTmlKOS5leUpxZEdraU9pSnVXRFZDT0VkU2JVbE9UbEpNZEY5dFdXUjFkSE4zSWl3aWFYTnpJam9pYUhSMGNITTZMeTloZFhSb0xuSmxaMmx6ZEdWeVpHbHpibVY1TG1kdkxtTnZiU0lzSW5NMVlpSTZJbnN4UTBFNU9ERTNNaTFCT0RSQ0xUUTFNMFV0T0RSRlFpMHhSak5FTmpnd01qSkRPVGM5SWl3aWFXRjBJam94TnpjMU16TXhOekE1TENKdVltWWlPakUzTmpjeU1qRTRPVEVzSW1WNGNDSTZNVGMzTlRReE9URXdPU3dpWTJ4cFpXNTBYMmxrSWpvaVJWTlFUaTFQVGtWVFNWUkZMbGRGUWkxUVVrOUVJaXdpWTJGMElqb2laM1ZsYzNRaUxDSnBaR1Z1ZEdsMGVWOXBaQ0k2SWpkallXTXpaV1ptTFRrMU1UZ3ROR1JsT1MxaFkySWhMVEF3T0dSak5EWTFaREUyTlNKOS5JMGVQblVEcXFrNDJVaTRCSDdXZjBKZk1VX2laWnltb2VZTzRXVFExNG5URmszYktzRVpPa3o5N3dJRGRNSzU5WDdrYWh6c0t2bW01WlJobUNoUW9FdyIsInJlZnJlc2hfdG9rZW4iOiJleUpyYVdRaU9pSm5kV1Z6ZEdOdmJuUnliMnhzWlhJdExURTJNakF4T1RNMU5EUWlMQ0poYkdjaU9pSkZVekkxTmlKOS5leUpxZEdraU9pSnRRMjQ1VEVGemMwSTNSR0oxYVVFNVJESklTM0ozSWl3aWMzVmlJam9pZXpGRFFURTROREV5TFVNNVJFUXRORGxFUkMwNE9VUkNMVEZHTlVRMk9ERXlRMEkxT1gwaUxDSnBjM01pT2lKb2RIUndjem92TDJGMWRHZ3VjbVZuYVhOMFpYSmthWE51WlhrdVoyOHVZMjl0SWl3aVlYVmtJam9pZFhKdU9tUnBjMjVsZVRwdmJtVnBaRHB3Y205a0lpd2lhV0YwSWpveE56YzFNak16TnpBNUxDSnVZbVlpT2pFM056UXhPVE16TURZc0ltVjRjQ0k2TVRjNU1EZzRNek13T1N3aVkyeHBaVzUwWDJsa0lqb2lSVk5RVGkxUFRrVlRTVlJGTGxkRlFpMVFVazlFSWl3aVkyRjBJam9pY21WbWNtVnphQ0lzSW14cFpDSTZJalZpWXpjMk5qUmxMV0UyWWpJdE5EQmlNUzFpT1RrMUxUWTRZamRoTUdGa09EWTRNU0lzSW1sa1pXNTBhWFI1WDJsa0lqb2lOMk5pWVROd1lXUXRPVFV4T0MwMFpHVTVMV0ZqWW1FdE1EQTRaR00wTmpWa01UWTFJbjAueXltMnViSE12TEpITWxMZUxFczFVWjRFRmVSZEtBUEpaVW11U1VxaFZvOUUtVmlQaGJFU0VGU2g2QkZCSHV6V2xBV0Z5TXduTFJBeXVYaU1EZzhIMmciLCJzd2lkIjoiezFDQTE4NDUyLUM5REQtNDlERC04OURCLTFGNUQ2ODEyQ0I1OX0iLCJ0dGwiOjg2Mzk5LCJyZWZyZXNoX3R0bCI6MTU1NTE5OTksImhpZ2hfdHJ1c3RfZXhwaXJlc19pbiI6MCwiaW5pdGlhbF9ncmFudF9pbl9jaGFpbl90aW1lIjoxNzc0MTkzMzA2MDAwLCJpYXQiOjE3NzUzMzE3MDkwMDAsImV4cCI6MTc3NTQxODEwOTAwMCwicmVmcmVzaF9leHAiOjE3OTA4ODM3MDkwMDAsImhpZ2hfdHJ1c3RfZXhwIjoxNzc0MTk1MTA2MDAwLCJzc28iOm51bGwsImF1dGhlbnRpY2F0b3IiOm51bGwsImxvZ2luVmFsdWUiOm51bGwsImNsaWNrYmFja1R5cGUiOm51bGwsInNlc3Npb25UcmFuc2ZlcktleSI6ImJVdjB0U1RrYV9YSWpuT0FVTXA0bHJTWC1kWEpuTjgxeHRuTE9LbEQxVUxUTFFhemFWdHlRWXE3T2llWG1KZXpTcG92Q0YtVG0zQjlKZHpQcTc2cl9fSU52VDNXWVFfRmNXakJfVl9lMzFDR01oOEdZM3MiLCJjcmVhdGVkIjoiMjAyNi0wNC0wNFQxOTo0MTo0OC45MTBaIiwibGFzdENoZWNrZWQiOiIyMDI2LTA0LTA0VDE5OjQxOjQ4LjkxMFoiLCJleHBpcmVzIjoiMjAyNi0wNC0wNVQxOTo0MTo0OS4wMDBaIiwicmVmcmVzaF9leHBpcmVzIjoiMjAyNi0xMC0wMVQxOTo0MTo0OS4wMDBaIn0=|eyJraWQiOiJndWVzdGNvbnRyb2xsZXItLTE2MjAxOTM1NDQiLCJhbGciOiJFUzI1NiJ9.eyJqdGkiOiJWamRSTF9lWEJnY3RNZ1I3XzdibEJnIiwiaXNzIjoiaHR0cHM6Ly9hdXRoLnJlZ2lzdGVyZGlzbmV5LmdvLmNvbSIsImF1ZCI6IkVTUE4tT05FU0lURS5XRUItUFJPRCIsInN1YiI6InsxQ0ExODQ1Mi1DOURELTQ5REQtODlEQi0xRjVENjgxMkNCNTl9IiwiaWF0IjoxNzc1MzMxNzA5LCJuYmYiOjE3NzQxOTMzMDYsImV4cCI6MTc3NTQxODEwOSwiY2F0IjoiaWR0b2tlbiIsImVtYWlsIjoia2ZwZXRlcnNvbkB1d2FsdW1uaS5jb20iLCJpZGVudGl0eV9pZCI6IjdjYmEzZWZmLTk1MTgtNGRlOS1hY2JhLTAwOGRjNDY1ZDE2NSJ9.sbw2JbkSrzVazXCGB_cHqKADR5cpeHk7Xx3U1061ukdvFhgT6TqvN9Ebr-IsGBK7QMcCGioiODKhfDRdRiIMGw; espnAuth={"swid":"{1CA18452-C9DD-49DD-89DB-1F5D6812CB59}"}'

# ─────────────────────────────────────────────────────────────────

# Parse the raw cookie string into a dict for requests
def parse_cookies(raw):
    jar = {}
    for part in raw.split(';'):
        part = part.strip()
        if '=' in part:
            k, v = part.split('=', 1)
            jar[k.strip()] = unquote(v.strip())
    return jar

COOKIES = parse_cookies(RAW_COOKIE)

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    "Accept":             "application/json, text/plain, */*",
    "Accept-Language":    "en-US,en;q=0.9",
    "Referer":            "https://fantasy.espn.com/",
    "Origin":             "https://fantasy.espn.com",
    "x-fantasy-source":   "kona",
    "x-fantasy-platform": "kona-PROD-m.fantasy.espn.com",
})
SESSION.cookies.update(COOKIES)


def fetch_espn(path, params=None):
    url = f"{API_BASE}/{path}"
    print(f"\n→ GET {url}")
    resp = SESSION.get(url, params=params, timeout=15)
    print(f"  Status: {resp.status_code}")
    print(f"  Preview: {resp.text[:200]}")
    resp.raise_for_status()
    return resp.json()


@app.route("/api/league/<season>", methods=["GET"])
def league(season):
    path   = f"seasons/{season}/segments/0/leagues/{LEAGUE_ID}"
    params = request.args.to_dict(flat=False)
    # flatten multi-value params for requests
    flat   = []
    for k, vs in params.items():
        for v in vs:
            flat.append((k, v))
    try:
        resp = SESSION.get(f"{API_BASE}/{path}", params=flat, timeout=15)
        print(f"\n→ GET {resp.url}")
        print(f"  Status: {resp.status_code}")
        print(f"  Preview: {resp.text[:200]}")
        resp.raise_for_status()
        return jsonify(resp.json()), 200
    except requests.HTTPError as e:
        return jsonify({"error": str(e), "body": resp.text[:500]}), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 502


@app.route("/api/debug/<season>", methods=["GET"])
def debug(season):
    """Visit http://localhost:5001/api/debug/2026"""
    path   = f"seasons/{season}/segments/0/leagues/{LEAGUE_ID}"
    params = [
        ("view", "mMatchup"), ("view", "mMatchupScore"),
        ("view", "mTeam"),    ("view", "mSettings"),
        ("view", "mStatus"),
    ]
    try:
        resp = SESSION.get(f"{API_BASE}/{path}", params=params, timeout=15)
        print(f"\n→ DEBUG {resp.url}")
        print(f"  Status: {resp.status_code}")
        print(f"  Preview: {resp.text[:300]}")
        resp.raise_for_status()
        data     = resp.json()
        schedule = data.get("schedule", [])
        teams    = data.get("teams", [])
        return jsonify({
            "top_level_keys": list(data.keys()),
            "messages":  data.get("messages"),
            "details":   data.get("details"),
            "status":    data.get("status", {}),
            "teams_count": len(teams),
            "team_names": [(t.get("id"), (t.get("location","") + " " + t.get("nickname","")).strip()) for t in teams],
            "settings_name": data.get("settings", {}).get("name"),
            "schedule_count": len(schedule),
            "schedule_sample": schedule[:2],
            "matchup_period_ids_found": sorted(set(m.get("matchupPeriodId") for m in schedule)),
            "scoring_period_ids_found": sorted(set(m.get("scoringPeriodId")  for m in schedule)),
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 502


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "league_id": LEAGUE_ID, "season": SEASON,
                    "cookies_loaded": list(COOKIES.keys())[:5]})


if __name__ == "__main__":
    print("\n⚾  ESPN Fantasy Proxy")
    print(f"   Running at : http://localhost:5001")
    print(f"   League ID  : {LEAGUE_ID}")
    print(f"   Cookies    : {list(COOKIES.keys())[:6]}")
    print("   Debug      : http://localhost:5001/api/debug/2026\n")
    import os
app.run(port=int(os.environ.get("PORT", 5001)))
