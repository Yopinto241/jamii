import requests
from app.config import (
    AFRICASTALKING_USERNAME,
    AFRICASTALKING_API_KEY,
    AFRICASTALKING_PRODUCT_NAME
)

class AfricasTalkingClient:
    def __init__(self):
        self.username = AFRICASTALKING_USERNAME
        self.api_key = AFRICASTALKING_API_KEY
        self.product_name = AFRICASTALKING_PRODUCT_NAME

        # ✅ Correct base URL
        self.base_url = "https://api.sandbox.africastalking.com"

    # ------------------ PAYMENT ------------------
    def initiate_mobile_checkout(self, phone_number, amount, currency="TZS"):
        """
        Initiate mobile money payment
        """
        url = f"{self.base_url}/mobile/checkout/request"

        headers = {
            "apiKey": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        payload = {
            "username": self.username,
            "productName": self.product_name,
            "phoneNumber": phone_number,
            "amount": int(amount),  # ✅ ensure integer
            "currencyCode": currency
        }

        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=30  # ✅ prevent hanging
            )

            print("STATUS CODE:", response.status_code)
            print("RAW RESPONSE:", response.text)

            # ✅ safer JSON parsing
            try:
                result = response.json()
            except:
                return {
                    "success": False,
                    "error": "Invalid JSON response from server"
                }

            if response.status_code in [200, 201]:
                return {
                    "success": True,
                    "transaction_id": result.get("transactionId"),
                    "status": result.get("status", "Pending")
                }
            else:
                return {
                    "success": False,
                    "error": result.get("description", response.text)
                }

        except requests.exceptions.SSLError as e:
            print("SSL ERROR:", e)
            return {
                "success": False,
                "error": "SSL Error - Check internet or sandbox support"
            }

        except requests.exceptions.RequestException as e:
            print("REQUEST ERROR:", e)
            return {
                "success": False,
                "error": str(e)
            }

    # ------------------ SMS ------------------
    def send_sms(self, phone_number, message):
        """
        Send SMS
        """
        url = f"{self.base_url}/version1/messaging"

        headers = {
            "apiKey": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded"
        }

        payload = {
            "username": self.username,
            "to": phone_number,
            "message": message
        }

        try:
            response = requests.post(
                url,
                data=payload,   # ✅ IMPORTANT: NOT json
                headers=headers,
                timeout=30
            )

            print("SMS STATUS:", response.status_code)
            print("SMS RESPONSE:", response.text)

            if response.status_code == 201:
                return {"success": True}
            else:
                return {"success": False, "error": response.text}

        except Exception as e:
            print("SMS ERROR:", e)
            return {"success": False, "error": str(e)}


# ✅ Global instance
client = AfricasTalkingClient()