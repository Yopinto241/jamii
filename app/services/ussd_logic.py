from app.integrations.africastalking_client import client
from app.database.db import get_connection   # ✅ FIXED IMPORT

# ------------------ HELPER ------------------

def fetch_all(query, params=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        print("DB ERROR:", e)
        return []


def execute_query(query, params=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("DB ERROR:", e)


# ------------------ FETCH DATA ------------------

def get_categories():
    return fetch_all("SELECT id, name FROM service_categories")


def get_services(category_id):
    return fetch_all(
        "SELECT id, name FROM services WHERE category_id = %s",
        (category_id,)
    )


def get_regions():
    return fetch_all("SELECT id, name FROM regions")


def get_districts(region_id):
    return fetch_all(
        "SELECT id, name FROM districts WHERE region_id = %s",
        (region_id,)
    )


def get_wards(district_id):
    return fetch_all(
        "SELECT id, name FROM wards WHERE district_id = %s",
        (district_id,)
    )


# ------------------ PROVIDERS ------------------

def count_providers(service_id, ward_id):
    result = fetch_all("""
        SELECT COUNT(*)
        FROM providers
        WHERE service_id = %s AND ward_id = %s
    """, (service_id, ward_id))

    return result[0][0] if result else 0


def get_providers(service_id, ward_id):
    return fetch_all("""
        SELECT full_name, phone
        FROM providers
        WHERE service_id = %s AND ward_id = %s
        LIMIT 3
    """, (service_id, ward_id))


def get_providers_with_rotation(service_id, ward_id, limit):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, full_name, phone, type, last_served_at
            FROM providers
            WHERE service_id = %s AND ward_id = %s
            ORDER BY last_served_at ASC
        """, (service_id, ward_id))

        providers = cur.fetchall()
        selected = providers[:limit]

        for p in selected:
            cur.execute("""
                UPDATE providers
                SET last_served_at = NOW()
                WHERE id = %s
            """, (p[0],))

        conn.commit()
        cur.close()
        conn.close()

        return selected

    except Exception as e:
        print("ROTATION ERROR:", e)
        return []


def save_provider_full(data, phone):
    try:
        is_premium = data["plan"] == "2"
        plan_type = "premium" if is_premium else "normal"

        execute_query("""
            INSERT INTO providers
            (full_name, phone, service_id, ward_id, type, is_premium)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data["name"],
            phone,
            data["service"],
            data["ward"],
            plan_type,
            is_premium
        ))

    except Exception as e:
        print("SAVE PROVIDER ERROR:", e)


# ------------------ PAYMENT ------------------

def initiate_payment(phone, amount):
    try:
        result = client.initiate_mobile_checkout(phone, amount)

        if result.get("success"):
            print("Payment started:", result.get("transaction_id"))
            return True

        print("Payment failed:", result.get("error"))
        return False

    except Exception as e:
        print("PAYMENT ERROR:", e)
        return False


def send_sms(phone, message):
    try:
        result = client.send_sms(phone, message)
        return result.get("success", False)
    except Exception as e:
        print("SMS ERROR:", e)
        return False


def give_commission(agent_phone, amount):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE agents
            SET available_balance = available_balance + %s
            WHERE phone = %s
        """, (amount, agent_phone))

        cur.execute("""
            INSERT INTO commissions (agent_phone, amount, type)
            VALUES (%s, %s, %s)
        """, (agent_phone, amount, "registration"))

        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        print("COMMISSION ERROR:", e)


def save_payment_record(phone, session_type, amount, status, transaction_id=None):
    try:
        execute_query("""
            INSERT INTO payments
            (phone, session_type, amount, status, transaction_id)
            VALUES (%s,%s,%s,%s,%s)
        """, (
            phone,
            session_type,
            amount or 0,
            status,
            transaction_id
        ))
    except Exception as e:
        print("SAVE PAYMENT RECORD ERROR:", e)


# ------------------ PRODUCTS ------------------

def get_product_categories():
    return fetch_all("SELECT id, name FROM product_categories")


def get_products(category_id):
    return fetch_all(
        "SELECT id, name FROM products WHERE category_id = %s",
        (category_id,)
    )


def get_product_providers(product_id, ward_id):
    return fetch_all("""
        SELECT name, phone
        FROM product_providers
        WHERE product_id = %s
        AND ward_id = %s
        AND payment_status = 'paid'
        LIMIT 3
    """, (product_id, ward_id))


def count_product_providers(product_id, ward_id):
    result = fetch_all("""
        SELECT COUNT(*)
        FROM product_providers
        WHERE product_id = %s
        AND ward_id = %s
        AND payment_status = 'paid'
        AND subscription_expiry > NOW()
    """, (product_id, ward_id))

    return result[0][0] if result else 0


def get_product_providers_with_rotation(product_id, ward_id, limit):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, name, phone, plan, last_served_at
            FROM product_providers
            WHERE product_id = %s
            AND ward_id = %s
            AND payment_status = 'paid'
            AND subscription_expiry > NOW()
            ORDER BY 
                CASE WHEN plan='premium' THEN 1 ELSE 2 END,
                last_served_at ASC
        """, (product_id, ward_id))

        providers = cur.fetchall()
        selected = providers[:limit]

        for p in selected:
            cur.execute("""
                UPDATE product_providers
                SET last_served_at = NOW()
                WHERE id = %s
            """, (p[0],))

        conn.commit()
        cur.close()
        conn.close()

        return selected

    except Exception as e:
        print("PRODUCT ROTATION ERROR:", e)
        return []


# ------------------ AJIRA ------------------

def get_ajira_categories():
    return fetch_all("SELECT id, name FROM ajira_categories")


def save_job_seeker(data, phone):
    try:
        execute_query("""
            INSERT INTO job_seekers
            (full_name, phone, category_id, region, district, ward, village, street, plan, payment_status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,'paid')
        """, (
            data["name"],
            phone,
            data["category"],
            data["region"],
            data["district"],
            data["ward"],
            data["village"],
            data["street"],
            data["plan"]
        ))

    except Exception as e:
        print("SAVE JOB SEEKER ERROR:", e)


def get_job_seekers(category, ward):
    return fetch_all("""
        SELECT full_name, phone
        FROM job_seekers
        WHERE category_id = %s
        AND ward = %s
        AND payment_status = 'paid'
        LIMIT 3
    """, (category, ward))


# ------------------ AGENTS ------------------

def save_agent(data, phone):
    try:
        levels = {
            "1": "mtaa",
            "2": "wilaya",
            "3": "mkoa"
        }

        execute_query("""
            INSERT INTO agents
            (full_name, phone, alt_phone, profession, region, district, ward, level, status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'active')
        """, (
            data.get("name"),
            phone,
            data.get("alt_phone"),
            data.get("profession"),
            data.get("region"),
            data.get("district"),
            data.get("ward"),
            levels.get(data.get("level"))
        ))

    except Exception as e:
        print("SAVE AGENT ERROR:", e)