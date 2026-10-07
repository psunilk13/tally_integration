from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from xml.sax.saxutils import escape
import json
import re
import traceback


# ============================================================
# CONFIGURATION
# ============================================================

# The port this receiver will listen on
RECEIVER_HOST = "0.0.0.0"  # Listen on all interfaces
RECEIVER_PORT = 8000

# Tally endpoint (Tally listens on port 9000 by default)
TALLY_URL = "http://127.0.0.1:9000"

# Tally company name (must match exactly in Tally)
TALLY_COMPANY = "Your Company Name"

# Path where ERPNext will send data
WEBHOOK_PATH = "/tally-receiver"


# ============================================================
# HELPERS
# ============================================================

def clean_text(value):
    if value is None:
        return ""
    return str(value).strip()


def xml_escape(value):
    return escape(clean_text(value))


# ============================================================
# ANALYZE TALLY RESPONSE
# ============================================================

def analyze_tally_response(response_text):
    """
    Tally normally returns an ENVELOPE containing import counts.
    Extract the important counters when present.
    """
    text = response_text or ""

    def get_tag(tag):
        match = re.search(
            rf"<{tag}>\s*(.*?)\s*</{tag}>",
            text,
            re.IGNORECASE | re.DOTALL
        )
        if match:
            return clean_text(match.group(1))
        return None

    created = get_tag("CREATED")
    altered = get_tag("ALTERED")
    errors = get_tag("ERRORS")
    cancelled = get_tag("CANCELLED")
    ignored = get_tag("IGNORED")
    exceptions = get_tag("EXCEPTIONS")

    return {
        "created": created,
        "altered": altered,
        "errors": errors,
        "cancelled": cancelled,
        "ignored": ignored,
        "exceptions": exceptions,
    }


# ============================================================
# SEND XML TO TALLY
# ============================================================

def send_to_tally(xml_data):
    print()
    print("=" * 70)
    print("SENDING DATA TO TALLY")
    print("=" * 70)
    print("Endpoint:", TALLY_URL)

    request_data = xml_data.encode("utf-8")

    request = Request(
        TALLY_URL,
        data=request_data,
        method="POST",
        headers={
            "Content-Type": "text/xml; charset=utf-8",
            "Content-Length": str(len(request_data)),
        },
    )

    try:
        with urlopen(request, timeout=15) as response:
            response_bytes = response.read()
            response_text = response_bytes.decode("utf-8", errors="replace")

            tally_status = analyze_tally_response(response_text)

            print()
            print("Tally HTTP status:", response.status)
            print("Tally import result:", json.dumps(tally_status, indent=4))
            print("Raw Tally response:", response_text)

            return {
                "transport_success": True,
                "http_status": response.status,
                "response": response_text,
                "import_result": tally_status,
            }

    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        print()
        print("TALLY HTTP ERROR")
        print(error.code)
        print(body)

        return {
            "transport_success": False,
            "http_status": error.code,
            "response": body,
            "import_result": {},
            "error": str(error),
        }

    except URLError as error:
        print()
        print("TALLY CONNECTION ERROR")
        print(error)

        return {
            "transport_success": False,
            "http_status": None,
            "response": "",
            "import_result": {},
            "error": str(error),
        }

    except Exception as error:
        print()
        print("UNEXPECTED TALLY ERROR")
        print(error)
        traceback.print_exc()

        return {
            "transport_success": False,
            "http_status": None,
            "response": "",
            "import_result": {},
            "error": str(error),
        }


# ============================================================
# HTTP RECEIVER
# ============================================================

class TallyReceiver(BaseHTTPRequestHandler):

    def send_json(self, status_code, payload):
        response = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def do_POST(self):
        path = urlparse(self.path).path
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)

        print()
        print("=" * 70)
        print("INCOMING REQUEST")
        print("=" * 70)
        print("Path:", path)
        print("Content-Type:", self.headers.get("Content-Type", ""))

        if path == WEBHOOK_PATH:
            try:
                # Try to parse as JSON first
                try:
                    payload = json.loads(raw_body.decode("utf-8"))
                    xml_data = payload.get("xml_data")
                except:
                    # If not JSON, treat raw body as XML directly
                    xml_data = raw_body.decode("utf-8")

                if not xml_data:
                    self.send_json(400, {"status": "error", "message": "No XML data provided"})
                    return

                print("XML data received:", xml_data[:500] + "..." if len(xml_data) > 500 else xml_data)

                print()
                print("=" * 70)
                print("SENDING TO TALLY")
                print("=" * 70)

                result = send_to_tally(xml_data)

                if not result["transport_success"]:
                    print()
                    print("FAILED TO SEND TO TALLY")
                    self.send_json(502, {
                        "status": "error",
                        "message": "Could not communicate with Tally",
                        "tally_http_status": result["http_status"],
                        "error": result.get("error"),
                    })
                    return

                print()
                print("SUCCESSFULLY SENT TO TALLY")

                self.send_json(200, {
                    "status": "success",
                    "message": "Data sent to Tally successfully",
                    "tally_http_status": result["http_status"],
                    "tally_import_result": result["import_result"],
                })
                return

        # Unknown endpoint
        self.send_json(404, {
            "status": "error",
            "message": "Unknown endpoint",
            "path": path,
        })

    def do_GET(self):
        if self.path == "/":
            self.send_json(200, {
                "status": "running",
                "service": "ERPNext → Tally Bridge",
                "receiver": f"{RECEIVER_HOST}:{RECEIVER_PORT}",
                "tally": TALLY_URL,
                "company": TALLY_COMPANY,
            })
            return

        self.send_json(404, {"status": "error", "message": "Not found"})

    def log_message(self, format_string, *args):
        print(f"{self.address_string()} - - [{self.log_date_time_string()}] {format_string % args}")


# ============================================================
# START
# ============================================================

def main():
    server = HTTPServer((RECEIVER_HOST, RECEIVER_PORT), TallyReceiver)

    print()
    print("=" * 70)
    print("ERPNext → Tally RECEIVER")
    print("=" * 70)
    print()
    print("Receiver: http://{}:{}".format(RECEIVER_HOST, RECEIVER_PORT))
    print("Tally:", TALLY_URL)
    print("Company:", TALLY_COMPANY)
    print("Webhook endpoint: http://{}:{}{}".format(RECEIVER_HOST, RECEIVER_PORT, WEBHOOK_PATH))
    print()
    print("RECEIVER READY. Waiting for ERPNext requests...")
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
        print("Stopping receiver...")
        server.server_close()


if __name__ == "__main__":
    main()
