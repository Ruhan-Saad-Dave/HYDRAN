import os
from fastapi import APIRouter, Response
from twilio.twiml.messaging_response import MessagingResponse
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

from .models import SmsReply
from .service import parse_sms, format_pharmacy_results

# Load environment variables from .env file
load_dotenv()

# --- Initialize Supabase Client ---
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# --- Define the IST Timezone Manually ---
ist_tz = timezone(timedelta(hours=5, minutes=30))

# Create the FastAPI application
stock_router = APIRouter(
    tags=["stock_checker"]
)


@stock_router.post("/sms")
async def sms_reply(sms_data: SmsReply):
    """Main webhook with logic to handle stateful conversations."""
    response = MessagingResponse()
    user_phone = sms_data.From
    user_message = sms_data.Body.strip()

    if user_message.isdigit():
        try:
            state_res = supabase.table("conversation_state").select("*").eq("user_phone", user_phone).single().execute()
            state = state_res.data

            expires_at_str = state['expires_at'].replace(' ', 'T')
            expiry_from_db_in_ist = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00')).astimezone(ist_tz)
            current_ist_time = datetime.now(ist_tz)

            if expiry_from_db_in_ist < current_ist_time:
                response.message("Your session has expired. Please start a new search.")
                supabase.table("conversation_state").delete().eq("user_phone", user_phone).execute()
                return Response(content=str(response), media_type="application/xml")

            selected_strength = state['options_map'].get(user_message)
            if not selected_strength:
                response.message("Invalid selection. Please reply with one of the numbers from the list.")
            else:
                medicine_name = state['context']['medicine']
                pincode = state['context']['pincode']

                pharmacies_res = supabase.rpc('get_nearby_pharmacies_sms', {
                    'medicine_name_input': medicine_name,
                    'strength_input': selected_strength,
                    'patient_pincode_input': pincode
                }).execute()

                if pharmacies_res.data:
                    response.message(format_pharmacy_results(pharmacies_res.data))
                else:
                    response.message(f"No pharmacies found with '{medicine_name} {selected_strength}' near {pincode}.")

                supabase.table("conversation_state").delete().eq("user_phone", user_phone).execute()
        except Exception as e:
            print(f"An error occurred: {e}")
            response.message("Sorry, something went wrong or your session expired. Please start a new search.")
        return Response(content=str(response), media_type="application/xml")

    medicine_name, pincode = parse_sms(user_message)
    if not medicine_name or not pincode:
        response.message("Sorry, I couldn't understand. Please send in the format: 'Medicine Name Pincode', e.g., 'Paracetamol 411001'")
        return Response(content=str(response), media_type="application/xml")

    try:
        med_variations = supabase.table("medicines").select("strength, brand_name").or_(f"brand_name.ilike.%{medicine_name}%,generic_name.ilike.%{medicine_name}%").execute()
        if not med_variations.data:
            response.message(f"Sorry, no medicine found matching '{medicine_name}'.")
            return Response(content=str(response), media_type="application/xml")

        unique_strengths = sorted(list(set([v['strength'] for v in med_variations.data if v['strength']])))
        if len(unique_strengths) > 1:
            options_map = {str(i + 1): strength for i, strength in enumerate(unique_strengths)}
            menu_text = f"Please select a strength for {med_variations.data[0]['brand_name']}:\n"
            for num, strength in options_map.items(): menu_text += f"{num}. {strength}\n"
            response.message(menu_text.strip())

            expiration_time = datetime.now(ist_tz) + timedelta(minutes=5)
            state_data = {
                "user_phone": user_phone, "context": {"medicine": medicine_name, "pincode": pincode},
                "options_map": options_map, "expires_at": expiration_time.isoformat()
            }
            # --- THIS LINE IS NOW FIXED ---
            # Added on_conflict to correctly update existing sessions
            supabase.table("conversation_state").upsert(state_data, on_conflict="user_phone").execute()
        else:
            strength = unique_strengths[0] if unique_strengths else '%'
            pharmacies_res = supabase.rpc('get_nearby_pharmacies_sms', {
                'medicine_name_input': medicine_name,
                'strength_input': strength,
                'patient_pincode_input': pincode
            }).execute()

            if pharmacies_res.data:
                response.message(format_pharmacy_results(pharmacies_res.data))
            else:
                response.message(f"No pharmacies found with '{medicine_name}' near {pincode}.")
    except Exception as e:
        print(f"An error occurred: {e}")
        response.message("Sorry, an error occurred on our end. Please try again later.")
    return Response(content=str(response), media_type="application/xml")

@stock_router.get("/")
def read_root():
    return {"status": "API is running"}