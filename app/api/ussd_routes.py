from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
from app.services.ussd_logic import *
from app.database.redis_client import r

router = APIRouter()

async def handle_payment_callback(data):
    """Handle payment callback from Africa's Talking"""
    try:
        status = data.get("status", "")
        phone = data.get("source", "")
        transaction_id = data.get("transactionId", "")
        value = data.get("value", "")

        print(f"Payment callback: phone={phone}, status={status}, tx_id={transaction_id}, value={value}")

        if not phone:
            print("No phone number in payment callback")
            return

        # Get session data from Redis
        session_data = r.hgetall(phone)
        if not session_data:
            print(f"No session found for phone {phone}")
            return

        session_type = session_data.get("type")

        if status.lower() == "success":
            amount = float(session_data.get("amount", 0)) if session_data.get("amount") else 0
            save_payment_record(phone, session_type, amount, "success", transaction_id)

            if session_type == "search":
                await send_provider_contacts(phone, session_data)
            elif session_type == "provider_registration":
                await complete_provider_registration(phone, session_data)
            elif session_type == "product_search":
                await send_product_provider_contacts(phone, session_data)
            elif session_type == "ajira_register":
                await complete_job_seeker_registration(phone, session_data)
            elif session_type == "ajira_search":
                await send_job_seeker_contacts(phone, session_data)
            elif session_type == "agent_register":
                await complete_agent_registration(phone, session_data)

            r.delete(phone)

        else:
            amount = float(session_data.get("amount", 0)) if session_data.get("amount") else 0
            save_payment_record(phone, session_type, amount, "failed", transaction_id)
            print(f"Payment failed for {phone}: {status}")
            # Optional: send failure SMS
            send_sms(phone, "Malipo hayakufaulu. Jaribu tena.")

    except Exception as e:
        print(f"Error handling payment callback: {e}")
        import traceback
        traceback.print_exc()

async def send_provider_contacts(phone, session_data):
    """Send provider contacts to user"""
    try:
        service_id = session_data.get("service")
        ward_id = session_data.get("ward")
        limit = int(session_data.get("limit", 3))

        providers = get_providers_with_rotation(service_id, ward_id, limit)

        if providers:
            message = "Huduma zilizopatikana:\n"
            for i, provider in enumerate(providers, 1):
                message += f"{i}. {provider[1]} - {provider[2]}\n"

            send_sms(phone, message)
            print(f"Sent provider contacts to {phone}")
        else:
            send_sms(phone, "Samahani, hakuna huduma kwa sasa.")
    except Exception as e:
        print(f"Error sending provider contacts: {e}")

async def complete_provider_registration(phone, session_data):
    """Complete provider registration after payment"""
    try:
        # Save provider to database
        save_provider_full(session_data, phone)

        send_sms(phone, "Usajili wako umekamilika! Utapata wateja kupitia mfumo huu.")
        print(f"Completed provider registration for {phone}")
    except Exception as e:
        print(f"Error completing provider registration: {e}")

async def send_product_provider_contacts(phone, session_data):
    """Send product provider contacts to user"""
    try:
        product_id = session_data.get("product")
        ward_id = session_data.get("ward")
        limit = int(session_data.get("limit", 3))

        providers = get_product_providers_with_rotation(product_id, ward_id, limit)

        if providers:
            message = "Wauzaji walioapatikana:\n"
            for i, provider in enumerate(providers, 1):
                message += f"{i}. {provider[1]} - {provider[2]}\n"

            send_sms(phone, message)
            print(f"Sent product provider contacts to {phone}")
        else:
            send_sms(phone, "Samahani, hakuna wauzaji kwa sasa.")
    except Exception as e:
        print(f"Error sending product provider contacts: {e}")

async def send_job_seeker_contacts(phone, session_data):
    """Send job seeker contacts to employer"""
    try:
        category = session_data.get("category")
        ward = session_data.get("ward")

        workers = get_job_seekers(category, ward)

        if workers:
            message = "Wafanyakazi:\n"
            for w in workers:
                message += f"{w[0]} - {w[1]}\n"

            send_sms(phone, message)
            print(f"Sent job seeker contacts to {phone}")
        else:
            send_sms(phone, "Samahani, hakuna wafanyakazi kwa sasa.")
    except Exception as e:
        print(f"Error sending job seeker contacts: {e}")

async def complete_job_seeker_registration(phone, session_data):
    """Complete job seeker registration after payment"""
    try:
        save_job_seeker(session_data, phone)
        send_sms(phone, "Usajili wako wa ajira umekamilika!")
        print(f"Completed job seeker registration for {phone}")
    except Exception as e:
        print(f"Error completing job seeker registration: {e}")

async def complete_agent_registration(phone, session_data):
    """Complete agent registration after payment"""
    try:
        save_agent(session_data, phone)
        send_sms(phone, "Umefanikiwa kuwa wakala wa Jamii Connect. Tutawasiliana nawe.")
        print(f"Completed agent registration for {phone}")
    except Exception as e:
        print(f"Error completing agent registration: {e}")

@router.post("/event")
async def handle_event(request: Request):
    """Handle USSD events like payment callbacks, delivery reports, etc."""
    try:
        # Try JSON first (Africa's Talking uses JSON for events)
        data = await request.json()
        print("EVENT RECEIVED (JSON):", data)

        # Handle different event types
        category = data.get("category", "")
        event_type = data.get("eventType", "")
        
        if category == "MobileCheckout" and event_type in ["CheckoutSuccess", "CheckoutFailure"]:
            await handle_payment_callback(data)
        elif category == "SMS" and event_type == "MessageReceived":
            print("SMS delivery report received")
        elif category == "USSD":
            # USSD traffic events (status Incomplete/Failed) are monitoring events, not payments
            print(f"USSD event: status={data.get('status')} input={data.get('input')} sessionId={data.get('sessionId')}")

        return {"status": "received"}

    except Exception as e:
        # Fallback to form data if JSON fails
        try:
            form = await request.form()
            print("EVENT RECEIVED (FORM):", dict(form))

            return {"status": "received"}
        except Exception as e2:
            print("EVENT ERROR:", str(e), str(e2))
            return {"status": "error", "message": "Invalid event format"}

@router.post("/ussd")
async def ussd_callback(request: Request):
    """Handle USSD callback with error handling"""
    try:
        form = await request.form()
        text = form.get("text", "")
        phone = form.get("phoneNumber")

        print(f"USSD REQUEST: phone={phone}, text='{text}'")

        inputs = text.split("*")

        # =========================
        # MAIN MENU
        # =========================
        if text == "":
            response = "CON Karibu Jamii Connect\n"
            response += "1. Tafuta Huduma\n"
            response += "2. Tafuta Bidhaa\n"
            response += "3. Jisajili Mtoa Huduma\n"
            response += "4. Jisajili Mfanya Biashara\n"
            response += "5. Ajira\n"
            response += "6. Omba Kuwa Wakala\n"
            response += "7. Msaada"

    # =====================================================
    # 🔍 1. TAFUTA HUDUMA (WORKING)
    # =====================================================

        elif inputs[0] == "1" and len(inputs) == 1:
            response = "CON Chagua Category:\n"
            for cat in get_categories():
                response += f"{cat[0]}. {cat[1]}\n"

        elif inputs[0] == "1" and len(inputs) == 2:
            response = "CON Chagua Service:\n"
            for srv in get_services(inputs[1]):
                response += f"{srv[0]}. {srv[1]}\n"

        elif inputs[0] == "1" and len(inputs) == 3:
            response = "CON Chagua Region:\n"
            for reg in get_regions():
                response += f"{reg[0]}. {reg[1]}\n"

        elif inputs[0] == "1" and len(inputs) == 4:
            response = "CON Chagua District:\n"
            for dist in get_districts(inputs[3]):
                response += f"{dist[0]}. {dist[1]}\n"

        elif inputs[0] == "1" and len(inputs) == 5:
            response = "CON Chagua Ward:\n"
            for ward in get_wards(inputs[4]):
                response += f"{ward[0]}. {ward[1]}\n"

        elif inputs[0] == "1" and len(inputs) == 6:
            service_id = inputs[2]
            ward_id = inputs[5]

            total = count_providers(service_id, ward_id)

            if total == 0:
                response = "END Hakuna huduma kwa sasa"
            else:
                response = f"CON Huduma zimepatikana: {total}\nChagua kifurushi:\n"

                if total <= 3:
                    response += f"1. 500 Tsh (Namba {total})\n"
                elif total <= 6:
                    response += "1. 500 Tsh (Namba 3)\n"
                    response += f"2. 1000 Tsh (Namba {total})\n"
                else:
                    response += "1. 500 Tsh (Namba 3)\n"
                    response += "2. 1000 Tsh (Namba 6)\n"
                    response += "3. 2000 Tsh (Namba 10)\n"

        elif inputs[0] == "1" and len(inputs) == 7:
            service_id = inputs[2]
            ward_id = inputs[5]
            choice = inputs[6]

            total = count_providers(service_id, ward_id)

            # decide package
            if total <= 3:
                amount = 500
                limit = total
            elif total <= 6:
                if choice == "1":
                    amount = 500
                    limit = 3
                else:
                    amount = 1000
                    limit = total
            else:
                if choice == "1":
                    amount = 500
                    limit = 3
                elif choice == "2":
                    amount = 1000
                    limit = 6
                else:
                    amount = 2000
                    limit = 10

            session_data = {
                "type": "search",
                "service": service_id,
                "ward": ward_id,
                "limit": limit,
                "amount": amount
            }

            r.hset(phone, mapping=session_data)
            r.expire(phone, 3600)

            initiate_payment(phone, amount)

            response = "END Lipa ili kupata namba za huduma"

    # =====================================================
    # 🛒 2. TAFUTA BIDHAA (WORKING)
    # =====================================================

        elif inputs[0] == "2" and len(inputs) == 1:
            response = "CON Chagua Category:\n"
            for cat in get_product_categories():
                response += f"{cat[0]}. {cat[1]}\n"

        elif inputs[0] == "2" and len(inputs) == 2:
            response = "CON Chagua Bidhaa:\n"
            for prod in get_products(inputs[1]):
                response += f"{prod[0]}. {prod[1]}\n"

        elif inputs[0] == "2" and len(inputs) == 3:
            response = "CON Chagua Region:\n"
            for reg in get_regions():
                response += f"{reg[0]}. {reg[1]}\n"

        elif inputs[0] == "2" and len(inputs) == 4:
            response = "CON Chagua District:\n"
            for dist in get_districts(inputs[3]):
                response += f"{dist[0]}. {dist[1]}\n"

        elif inputs[0] == "2" and len(inputs) == 5:
            response = "CON Chagua Ward:\n"
            for ward in get_wards(inputs[4]):
                response += f"{ward[0]}. {ward[1]}\n"

        elif inputs[0] == "2" and len(inputs) == 6:
            product_id = inputs[2]
            ward_id = inputs[5]

            total = count_product_providers(product_id, ward_id)

            if total == 0:
                response = "END Hakuna wauzaji kwa sasa"
            else:
                response = f"CON Wauzaji {total}\nChagua kifurushi:\n"

                if total <= 3:
                    response += f"1. 500 Tsh ({total})\n"
                elif total <= 6:
                    response += "1. 500 Tsh (3)\n"
                    response += f"2. 1000 Tsh ({total})\n"
                else:
                    response += "1. 500 Tsh (3)\n"
                    response += "2. 1000 Tsh (6)\n"
                    response += "3. 2000 Tsh (10)\n"

        elif inputs[0] == "2" and len(inputs) == 7:
            product_id = inputs[2]
            ward_id = inputs[5]
            choice = inputs[6]

            total = count_product_providers(product_id, ward_id)

            if total <= 3:
                amount, limit = 500, total
            elif total <= 6:
                amount, limit = (500, 3) if choice == "1" else (1000, total)
            else:
                if choice == "1":
                    amount, limit = 500, 3
                elif choice == "2":
                    amount, limit = 1000, 6
                else:
                    amount, limit = 2000, 10

            session_data = {
                "type": "product_search",
                "product": product_id,
                "ward": ward_id,
                "limit": limit,
                "amount": amount
            }

            r.hset(phone, mapping=session_data)
            r.expire(phone, 3600)

            initiate_payment(phone, amount)

            response = "END Lipa kupata wauzaji"

    # =====================================================
    # 👤 3. JISAJILI MTOA HUDUMA (WORKING)
    # =====================================================

        elif inputs[0] == "3" and len(inputs) == 1:
            response = "CON Ingiza jina lako:"

        elif inputs[0] == "3" and len(inputs) == 2:
            response = "CON Chagua Category:\n"
            for cat in get_categories():
                response += f"{cat[0]}. {cat[1]}\n"

        elif inputs[0] == "3" and len(inputs) == 3:
            response = "CON Chagua Service:\n"
            for srv in get_services(inputs[2]):
                response += f"{srv[0]}. {srv[1]}\n"

        elif inputs[0] == "3" and len(inputs) == 4:
            response = "CON Chagua Region:\n"
            for reg in get_regions():
                response += f"{reg[0]}. {reg[1]}\n"

        elif inputs[0] == "3" and len(inputs) == 5:
            response = "CON Chagua District:\n"
            for dist in get_districts(inputs[4]):
                response += f"{dist[0]}. {dist[1]}\n"

        elif inputs[0] == "3" and len(inputs) == 6:
            response = "CON Chagua Ward:\n"
            for ward in get_wards(inputs[5]):
                response += f"{ward[0]}. {ward[1]}\n"

        elif inputs[0] == "3" and len(inputs) == 7:
            response = "CON Namba ya wakala (au 0 kama hakuna):"

        elif inputs[0] == "3" and len(inputs) == 8:
            response = "CON Chagua Plan:\n1. Normal 5000\n2. Premium 10000"

        elif inputs[0] == "3" and len(inputs) == 9:
            plan_choice = inputs[8]
            amount = 5000 if plan_choice == "1" else 10000

            session_data = {
                "type": "provider_registration",
                "name": inputs[1],
                "category": inputs[2],
                "service": inputs[3],
                "region": inputs[4],
                "district": inputs[5],
                "ward": inputs[6],
                "agent": inputs[7] if inputs[7] != "0" else None,
                "plan": plan_choice,
                "amount": amount
            }

            r.hset(phone, mapping=session_data)
            r.expire(phone, 3600)

            initiate_payment(phone, amount)

            response = "END Lipa ili ukamilishe usajili"

    # =====================================================
    # 🏪 4. JISAJILI MFANYA BIASHARA (WORKING)
    # =====================================================

        elif inputs[0] == "4" and len(inputs) == 1:
            response = "CON Ingiza jina lako:"

        elif inputs[0] == "4" and len(inputs) == 2:
            response = "CON Chagua Category:\n"
            for cat in get_product_categories():
                response += f"{cat[0]}. {cat[1]}\n"

        elif inputs[0] == "4" and len(inputs) == 3:
            response = "CON Chagua Bidhaa:\n"
            for prod in get_products(inputs[2]):
                response += f"{prod[0]}. {prod[1]}\n"

        elif inputs[0] == "4" and len(inputs) == 4:
            response = "CON Chagua Region:\n"
            for reg in get_regions():
                response += f"{reg[0]}. {reg[1]}\n"

        elif inputs[0] == "4" and len(inputs) == 5:
            response = "CON Chagua District:\n"
            for dist in get_districts(inputs[4]):
                response += f"{dist[0]}. {dist[1]}\n"

        elif inputs[0] == "4" and len(inputs) == 6:
            response = "CON Chagua Ward:\n"
            for ward in get_wards(inputs[5]):
                response += f"{ward[0]}. {ward[1]}\n"

        elif inputs[0] == "4" and len(inputs) == 7:
            response = "CON Namba ya wakala (au 0 kama hakuna):"

        elif inputs[0] == "4" and len(inputs) == 8:
            response = "END Usajili wa biashara umekamilika"

    # =====================================================
    # 👷 AJIRA SYSTEM
    # =====================================================

        elif inputs[0] == "5" and len(inputs) == 1:
            response = "CON Ajira\n"
            response += "1. Tafuta Mfanyakazi\n"
            response += "2. Jisajili Ajira"

    # -------- REGISTER JOB SEEKER --------

        elif inputs[0] == "5" and len(inputs) > 1 and inputs[1] == "2" and len(inputs) == 2:
            response = "CON Ingiza jina lako:"

        elif inputs[0] == "5" and len(inputs) > 1 and inputs[1] == "2" and len(inputs) == 3:
            response = "CON Chagua taaluma:\n"
            for c in get_ajira_categories():
                response += f"{c[0]}. {c[1]}\n"

        elif inputs[0] == "5" and len(inputs) > 1 and inputs[1] == "2" and len(inputs) == 4:
            response = "CON Chagua Region:\n"
            for r in get_regions():
                response += f"{r[0]}. {r[1]}\n"

        elif inputs[0] == "5" and inputs[1] == "2" and len(inputs) == 5:
            response = "CON Chagua District:\n"
            for d in get_districts(inputs[4]):
                response += f"{d[0]}. {d[1]}\n"

        elif inputs[0] == "5" and inputs[1] == "2" and len(inputs) == 6:
            response = "CON Chagua Ward:\n"
            for w in get_wards(inputs[5]):
                response += f"{w[0]}. {w[1]}\n"

        elif inputs[0] == "5" and inputs[1] == "2" and len(inputs) == 7:
            response = "CON Andika Kijiji:"

        elif inputs[0] == "5" and inputs[1] == "2" and len(inputs) == 8:
            response = "CON Andika Mtaa:"

        elif inputs[0] == "5" and inputs[1] == "2" and len(inputs) == 9:
            response = "CON Chagua Plan:\n"
            response += "1. Basic - 2000 Tsh\n"
            response += "2. Premium - 3000 Tsh"

        elif inputs[0] == "5" and inputs[1] == "2" and len(inputs) == 10:

            session_data = {
                "type": "ajira_register",
                "name": inputs[2],
                "category": inputs[3],
                "region": inputs[4],
                "district": inputs[5],
                "ward": inputs[6],
                "village": inputs[7],
                "street": inputs[8],
                "plan": inputs[9],
                "amount": amount
            }

            r.hset(phone, mapping=session_data)
            r.expire(phone, 300)

            amount = 2000 if inputs[9] == "1" else 3000
            initiate_payment(phone, amount)

            response = "END Lipa kukamilisha usajili"

    # -------- SEARCH JOB SEEKERS --------

        elif inputs[0] == "5" and inputs[1] == "1" and len(inputs) == 2:
            response = "CON Chagua taaluma:\n"
            for c in get_ajira_categories():
                response += f"{c[0]}. {c[1]}\n"

        elif inputs[0] == "5" and inputs[1] == "1" and len(inputs) == 3:
            response = "CON Chagua Region:\n"
            for r in get_regions():
                response += f"{r[0]}. {r[1]}\n"

        elif inputs[0] == "5" and inputs[1] == "1" and len(inputs) == 4:
            response = "CON Chagua District:\n"
            for d in get_districts(inputs[3]):
                response += f"{d[0]}. {d[1]}\n"

        elif inputs[0] == "5" and inputs[1] == "1" and len(inputs) == 5:
            response = "CON Chagua Ward:\n"
            for w in get_wards(inputs[4]):
                response += f"{w[0]}. {w[1]}\n"

        elif inputs[0] == "5" and inputs[1] == "1" and len(inputs) == 6:

            session_data = {
                "type": "ajira_search",
                "category": inputs[2],
                "region": inputs[3],
                "district": inputs[4],
                "ward": inputs[5],
                "amount": 500
            }

            r.hset(phone, mapping=session_data)
            r.expire(phone, 300)

            initiate_payment(phone, 500)

            response = "END Lipa kuona wafanyakazi"

    # =====================================================
    # �‍💼 WAKALA SYSTEM
    # =====================================================

        elif inputs[0] == "6" and len(inputs) == 1:
            response = "CON Wakala\n"
            response += "1. Jisajili Wakala\n"
            response += "2. Mwongozo wa Wakala"

        elif inputs[0] == "6" and len(inputs) > 1 and inputs[1] == "1" and len(inputs) == 2:
            response = "CON Ingiza jina lako kamili:"

        elif inputs[0] == "6" and len(inputs) > 1 and inputs[1] == "1" and len(inputs) == 3:
            response = "CON Ingiza namba yako ya simu:"

        elif inputs[0] == "6" and len(inputs) > 1 and inputs[1] == "1" and len(inputs) == 4:
            response = "CON Kazi yako ni nini? (mfano: fundi, mfanyabiashara):"

        elif inputs[0] == "6" and len(inputs) > 1 and inputs[1] == "1" and len(inputs) == 5:
            response = "CON Chagua Region:\n"
            for r in get_regions():
                response += f"{r[0]}. {r[1]}\n"

        elif inputs[0] == "6" and len(inputs) > 1 and inputs[1] == "1" and len(inputs) == 6:
            response = "CON Chagua District:\n"
            for d in get_districts(inputs[5]):
                response += f"{d[0]}. {d[1]}\n"

        elif inputs[0] == "6" and len(inputs) > 1 and inputs[1] == "1" and len(inputs) == 7:
            response = "CON Chagua Ward:\n"
            for w in get_wards(inputs[6]):
                response += f"{w[0]}. {w[1]}\n"

        elif inputs[0] == "6" and len(inputs) > 1 and inputs[1] == "1" and len(inputs) == 8:
            response = "CON Chagua Kiwango:\n"
            response += "1. Mtaa/Kata - 3000 Tsh\n"
            response += "2. Wilaya - 5000 Tsh\n"
            response += "3. Mkoa - 10000 Tsh"

        elif inputs[0] == "6" and len(inputs) > 1 and inputs[1] == "1" and len(inputs) == 9:

            level_choice = inputs[8]

            prices = {
                "1": 3000,
                "2": 5000,
                "3": 10000
            }

            session_data = {
                "type": "agent_register",
                "name": inputs[2],
                "alt_phone": inputs[3],
                "profession": inputs[4],
                "region": inputs[5],
                "district": inputs[6],
                "ward": inputs[7],
                "level": level_choice,
                "amount": amount
            }

            r.hset(phone, mapping=session_data)
            r.expire(phone, 300)

            amount = prices.get(level_choice, 3000)

            initiate_payment(phone, amount)

            response = "END Lipa kukamilisha usajili wa wakala"

        elif inputs[0] == "6" and len(inputs) > 1 and inputs[1] == "2":
            response = "END Mwongozo wa Wakala: chagua, jisajili, lipa, shiriki.\nPiga 0628621737 kwa msaada."

    # =====================================================
    # ℹ️ 7. MSAADA
    # =====================================================

        elif inputs[0] == "7":
            response = "END Jamii Connect hukusaidia kupata huduma na bidhaa karibu yako.\nPiga: 0628621737"

        else:
            response = "END Invalid input"

        return PlainTextResponse(response)

    except Exception as e:
        print(f"USSD ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return PlainTextResponse("END Samahani, kuna tatizo la kiufundi. Jaribu tena baadaye.")