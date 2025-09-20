import re

def parse_sms(sms_body: str):
    """Parses SMS for medicine name and pincode."""
    pincode_match = re.search(r'\b\d{6}\b', sms_body)
    if not pincode_match: return None, None
    pincode = pincode_match.group(0)
    medicine_name = sms_body[:pincode_match.start()].strip()
    return medicine_name, pincode


def format_pharmacy_results(pharmacies_data: list):
    """Formats the list of pharmacies into a readable string."""
    reply_text = "Available at:\n"
    for i, pharmacy in enumerate(pharmacies_data):
        reply_text += (
            f"\n{i + 1}. {pharmacy['pharmacy_name']}\n"
            f"   Addr: {pharmacy['pharmacy_address']}\n"
            f"   Med: {pharmacy['med_brand_name']} {pharmacy['med_strength']}\n"
            f"   Stock: {pharmacy['stock']}\n"
            f"   Ph: {pharmacy['pharmacy_phone']}\n"
        )
    return reply_text.strip()