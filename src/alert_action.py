"""
alert_action.py

WHAT THIS FILE DOES:
When distress is confirmed (HIGH tier), this is what actually notifies
emergency contacts. It does TWO things together, because SMS alone
cannot make a loud sound:

  1. Sends an SMS (text) with the location + a "help needed" message
  2. Triggers an automated PHONE CALL that plays a loud siren/alarm sound
     when answered - phone calls generally still ring/play audio even in
     silent mode (unlike regular notifications), which is how we achieve
     the "loud alarm that gets attention" behavior you described.

WHY TWILIO:
Twilio is a real service that can send real SMS and make real automated
calls from code. It has a free trial. To actually use it for real:
  1. Sign up at twilio.com (free trial gives you credit + a phone number)
  2. Get your Account SID and Auth Token from the Twilio dashboard
  3. Put them into the placeholders below (or as environment variables)

UNTIL you have those credentials, this script automatically runs in
SIMULATION MODE - it won't fail, it'll just clearly log what WOULD have
been sent, so we can test the rest of the pipeline today.
"""

import os
import csv
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()  # reads the .env file and loads its values

# --- Twilio credentials (leave as-is for simulation mode, fill in for real use) ---
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM_NUMBER = os.environ.get("TWILIO_FROM_NUMBER", "")

# URL of a hosted siren/alarm audio file Twilio will play during the call.
# Twilio needs a real public URL to an audio file (mp3/wav) - you'd host
# one (e.g. on GitHub) and put its raw link here.
SIREN_AUDIO_URL = "https://example.com/siren.mp3"  # placeholder - replace later

SIMULATION_MODE = not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_FROM_NUMBER)

LOG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "alerts_log.csv"
)


def _log_alert(contact_name, contact_phone, message, action_type, status):
    """Writes one row to alerts_log.csv - our audit trail."""
    file_exists = os.path.isfile(LOG_PATH)
    with open(LOG_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "contact_name", "contact_phone", "action_type", "message", "status"])
        writer.writerow([datetime.now().isoformat(), contact_name, contact_phone, action_type, message, status])


def send_sms(contact_name, contact_phone, location_link):
    """Sends the SMS alert (or simulates it if Twilio isn't configured)."""
    message = f"EMERGENCY: A person you're connected to may need help. Location: {location_link}"

    if SIMULATION_MODE:
        print(f"[SIMULATED SMS] To: {contact_name} ({contact_phone})")
        print(f"   Message: {message}")
        _log_alert(contact_name, contact_phone, message, "SMS", "SIMULATED")
        return

    # Real Twilio SMS sending (only runs once credentials are filled in)
    from twilio.rest import Client
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    sms = client.messages.create(body=message, from_=TWILIO_FROM_NUMBER, to=contact_phone)
    print(f"[REAL SMS SENT] SID: {sms.sid}")
    _log_alert(contact_name, contact_phone, message, "SMS", "SENT")


def trigger_alarm_call(contact_name, contact_phone):
    """Triggers the automated alarm call (or simulates it if Twilio isn't configured)."""
    if SIMULATION_MODE:
        print(f"[SIMULATED CALL] Calling {contact_name} ({contact_phone}) - would play loud siren audio on pickup")
        _log_alert(contact_name, contact_phone, "Automated siren call", "CALL", "SIMULATED")
        return

    # Real Twilio call, playing a hosted siren audio file when answered
    from twilio.rest import Client
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    call = client.calls.create(
        twiml=f'<Response><Play loop="3">{SIREN_AUDIO_URL}</Play></Response>',
        from_=TWILIO_FROM_NUMBER,
        to=contact_phone,
    )
    print(f"[REAL CALL TRIGGERED] SID: {call.sid}")
    _log_alert(contact_name, contact_phone, "Automated siren call", "CALL", "TRIGGERED")


def send_full_alert(contact_name, contact_phone, location_link):
    """Does both actions together - this is what gets called when tier == HIGH."""
    print(f"\n=== SENDING FULL ALERT to {contact_name} ===")
    send_sms(contact_name, contact_phone, location_link)
    trigger_alarm_call(contact_name, contact_phone)
    print("=== Alert sequence complete ===\n")


if __name__ == "__main__":
    # Test with example emergency contacts (replace with real numbers when ready)
    test_contacts = [
        {"name": "Mom", "phone": "+911234567890"},
        {"name": "Best Friend", "phone": "+919876543210"},
    ]
    fake_location = "https://maps.google.com/?q=23.2599,77.4126"  # example: Bhopal coordinates

    for contact in test_contacts:
        send_full_alert(contact["name"], contact["phone"], fake_location)

    print(f"All actions logged to: {LOG_PATH}")
