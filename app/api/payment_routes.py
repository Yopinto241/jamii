from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
from app.services.ussd_logic import *
from app.database.redis_client import r

router = APIRouter()

@router.post("/payment/callback")
async def payment_callback(request: Request):
    form = await request.form()
    phone = form.get("phoneNumber")
    status = form.get("status")

    session_data = r.hgetall(phone)
    if session_data:
        session_data = {k.decode(): v.decode() for k, v in session_data.items()}
        session_type = session_data.get("type")
        amount = float(session_data.get("amount", 0)) if session_data.get("amount" ) else 0

    if status == "Success":
        if session_data:
            save_payment_record(phone, session_type, amount, "success")

            if session_type == "search":
                providers = get_providers_with_rotation(
                    session_data["service"],
                    session_data["ward"],
                    int(session_data["limit"])
                )

                if providers:
                    message = "Huduma:\n"
                    for p in providers:
                        message += f"{p[1]} - {p[2]}\n"
                else:
                    message = "Hakuna huduma kwa sasa"

                send_sms(phone, message)

            elif session_type == "product_search":
                providers = get_product_providers_with_rotation(
                    session_data["product"],
                    session_data["ward"],
                    int(session_data["limit"])
                )

                if providers:
                    message = "Bidhaa:\n"
                    for p in providers:
                        message += f"{p[1]} - {p[2]}\n"
                else:
                    message = "Hakuna wauzaji"

                send_sms(phone, message)

            elif session_type == "provider_registration":
                save_provider_full(session_data, phone)

                agent = session_data.get("agent")
                if agent:
                    give_commission(agent, 1000)

                send_sms(phone, "Usajili umekamilika!")

            elif session_type == "ajira_register":
                save_job_seeker(session_data, phone)
                send_sms(phone, "Usajili wako wa ajira umekamilika!")

            elif session_type == "ajira_search":
                workers = get_job_seekers(session_data["category"], session_data["ward"])
                message = "Wafanyakazi:\n" if workers else "Samahani, hakuna wafanyakazi kwa sasa."
                for w in workers:
                    message += f"{w[0]} - {w[1]}\n"
                send_sms(phone, message)

            elif session_type == "agent_register":
                save_agent(session_data, phone)
                send_sms(phone, "Umefanikiwa kuwa wakala wa Jamii Connect. Tutawasiliana nawe.")

        r.delete(phone)

    return PlainTextResponse("OK")
