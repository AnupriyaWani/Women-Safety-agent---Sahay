"""
alert_action.py

WHAT THIS FILE DOES:
When distress is confirmed (HIGH tier), this is what actually notifies
emergency contacts. It does TWO things together, because a text alone
cannot make a loud sound:

  1. Sends a WhatsApp message with the location + a "help needed" message
  2. Triggers an automated PHONE CALL that plays a loud siren/alarm sound
     when answered - phone calls generally still ring/play audio even in
     silent mode (unlike regular notifications), which is how we achieve
     the "loud alarm that gets attention" behavior.

WHY TWILIO:
Twilio is a real service that can send real messages and make real
automated calls from code. It has a free trial.

SIMULATION MODE:
Real sending was tested and confirmed working end-to-end against the
Twilio API (correct auth, correct request format). Two account-level
restrictions prevent live delivery on a free trial account:
  1. SMS: trial accounts can only send SMS within their sign-up country.
  2. WhatsApp: messages outside a 24-hour session require an approved
     Content Template (Twilio policy since April 2025).
Both are one-time account setup steps (upgrade billing / approve a
template), not code issues. This script runs in SIMULATION MODE so the
demo stays clean and reliable - it clearly logs what WOULD have been
sent. Set FORCE_SIMULATION to False once either restriction is resolved.
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
SIREN_AUDIO_URL = "https://example.com/siren.mp3"  # placeholder - replace later

SIMULATION_MODE = not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_FROM_NUMBER)

FORCE_SIMULATION = True  # keeps demo clean; set False once trial restrictions are resolved
SIMULATION_MODE = SIMULATION_MODE or FORCE_SIMULATION

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


def send_whatsapp(contact_name, contact_whatsapp_number, location_link):
    """
    Sends the alert via WhatsApp. Uses Twilio's WhatsApp Sandbox, which
    works internationally even on trial accounts. The contact must have
    sent the sandbox 'join <code>' message once before this would reach
    them in real (non-simulated) mode.
    """
    message = f"EMERGENCY: A person you're connected to may need help. Location: {location_link}"

    if SIMULATION_MODE:
        print(f"[SIMULATED WHATSAPP] To: {contact_name} ({contact_whatsapp_number})")
        print(f"   Message: {message}")
        _log_alert(contact_name, contact_whatsapp_number, message, "WHATSAPP", "SIMULATED")
        return

    from twilio.rest import Client
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    sandbox_number = "whatsapp:+14155238886"
    to_whatsapp = f"whatsapp:{contact_whatsapp_number}"
    wa_message = client.messages.create(body=message, from_=sandbox_number, to=to_whatsapp)
    print(f"[REAL WHATSAPP SENT] SID: {wa_message.sid}")
    _log_alert(contact_name, contact_whatsapp_number, message, "WHATSAPP", "SENT")


def trigger_alarm_call(contact_name, contact_phone):
    """Triggers the automated alarm call (or simulates it if in simulation mode)."""
    if SIMULATION_MODE:
        print(f"[SIMULATED CALL] Calling {contact_name} ({contact_phone}) - would play loud siren audio on pickup")
        _log_alert(contact_name, contact_phone, "Automated siren call", "CALL", "SIMULATED")
        return

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
    send_whatsapp(contact_name, contact_phone, location_link)
    trigger_alarm_call(contact_name, contact_phone)
    print("=== Alert sequence complete ===\n")


if __name__ == "__main__":
    test_contacts = [
        {"name": "Mom", "phone": os.environ.get("MY_VERIFIED_PHONE", "+911234567890")},
    ]
    fake_location = "https://maps.google.com/?q=23.2599,77.4126"

    for contact in test_contacts:
        send_full_alert(contact["name"], contact["phone"], fake_location)

    print(f"All actions logged to: {LOG_PATH}")