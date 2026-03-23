import os

# ------------------ AFRICA'S TALKING ------------------

# Sandbox username is ALWAYS "sandbox"
AFRICASTALKING_USERNAME = os.getenv(
    "AFRICASTALKING_USERNAME",
    "sandbox"
)

# ⚠️ Replace this later with a NEW key (security)
AFRICASTALKING_API_KEY = os.getenv(
    "AFRICASTALKING_API_KEY",
    "atsk_8b9e44e9d46946fc62502d484df394769b2528824ad48fb19a8e07896688e286fe7f5098"
)

# ✅ Correct product name for sandbox payments
AFRICASTALKING_PRODUCT_NAME = os.getenv(
    "AFRICASTALKING_PRODUCT_NAME",
    "Sandbox"
)


# ------------------ REDIS ------------------

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))


# ------------------ DATABASE ------------------

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:3698@localhost:5432/huduma_connect"
)