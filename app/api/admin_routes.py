from fastapi import APIRouter, HTTPException
from app.database.db import get_connection
from datetime import datetime, timedelta
import psycopg2

router = APIRouter(prefix="/admin")


def check_duplicate(query, params, conn):
    """Check if record already exists"""
    cur = conn.cursor()
    try:
        cur.execute(query, params)
        result = cur.fetchone()
        cur.close()
        return result is not None
    except:
        cur.close()
        return False


def close_connection(conn, cur):
    """Safely close connection and cursor"""
    try:
        cur.close()
    except:
        pass
    try:
        conn.close()
    except:
        pass


# =========================
# LOCATION DATA
# =========================
@router.get("/categories")
def get_categories():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM service_categories")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return {"categories": data}


@router.get("/services/{category_id}")
def get_services(category_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM services WHERE category_id = %s", (category_id,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return {"services": data}


@router.get("/product-categories")
def get_product_categories():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM product_categories")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return {"categories": data}


@router.get("/products/{category_id}")
def get_products(category_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM products WHERE category_id = %s", (category_id,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return {"products": data}


@router.get("/regions")
def get_regions():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM regions")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return {"regions": data}


@router.get("/districts/{region_id}")
def get_districts(region_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM districts WHERE region_id = %s", (region_id,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return {"districts": data}


@router.get("/wards/{district_id}")
def get_wards(district_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM wards WHERE district_id = %s", (district_id,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return {"wards": data}


# =========================
# ALL DATA ENDPOINTS
# =========================

@router.get("/all-service-categories")
def get_all_service_categories():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM service_categories ORDER BY id")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return {"data": data}


@router.get("/all-services")
def get_all_services():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT s.id, s.name, sc.name as category FROM services s JOIN service_categories sc ON s.category_id = sc.id ORDER BY s.id")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return {"data": data}


@router.get("/all-product-categories")
def get_all_product_categories():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM product_categories ORDER BY id")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return {"data": data}


@router.get("/all-products")
def get_all_products():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT p.id, p.name, pc.name as category FROM products p JOIN product_categories pc ON p.category_id = pc.id ORDER BY p.id")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return {"data": data}


@router.get("/all-regions")
def get_all_regions():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM regions ORDER BY id")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return {"data": data}


@router.get("/all-districts")
def get_all_districts():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT d.id, d.name, r.name as region FROM districts d JOIN regions r ON d.region_id = r.id ORDER BY d.id")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return {"data": data}


@router.get("/all-wards")
def get_all_wards():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT w.id, w.name, d.name as district FROM wards w JOIN districts d ON w.district_id = d.id ORDER BY w.id")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return {"data": data}


@router.get("/all-providers")
def get_all_providers():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id, p.full_name, p.phone, p.type, p.is_premium, p.last_served_at, p.created_at,
               s.name as service, w.name as ward, d.name as district, r.name as region
        FROM providers p
        LEFT JOIN services s ON p.service_id = s.id
        LEFT JOIN wards w ON p.ward_id = w.id
        LEFT JOIN districts d ON w.district_id = d.id
        LEFT JOIN regions r ON d.region_id = r.id
        ORDER BY p.id
    """)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return {"data": data}


@router.get("/all-product-providers")
def get_all_product_providers():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT pp.id, pp.name, pp.phone, pp.plan, pp.payment_status, pp.subscription_expiry, pp.last_served_at,
               p.name as product, w.name as ward, d.name as district, r.name as region
        FROM product_providers pp
        LEFT JOIN products p ON pp.product_id = p.id
        LEFT JOIN wards w ON pp.ward_id = w.id
        LEFT JOIN districts d ON w.district_id = d.id
        LEFT JOIN regions r ON d.region_id = r.id
        ORDER BY pp.id
    """)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return {"data": data}


@router.get("/all-agents")
def get_all_agents():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM agents ORDER BY id")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return {"data": data}


@router.get("/all-commissions")
def get_all_commissions():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT c.id, c.amount, c.type, c.created_at, a.name as agent_name FROM commissions c JOIN agents a ON c.agent_phone = a.phone ORDER BY c.id")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return {"data": data}


@router.get("/all-payments")
def get_all_payments():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM payments ORDER BY created_at DESC")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return {"data": data}


# =========================
# ADD DATA ENDPOINTS WITH VALIDATION & DUPLICATE CHECK
# =========================

@router.post("/add-service-category")
def add_service_category(data: dict):
    """Add new service category with duplicate check"""
    if not data.get("name") or not data["name"].strip():
        raise HTTPException(status_code=400, detail="Category name is required")
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Check for duplicates
        duplicate = check_duplicate(
            "SELECT id FROM service_categories WHERE LOWER(name) = LOWER(%s)",
            (data["name"],),
            conn
        )
        if duplicate:
            raise HTTPException(status_code=409, detail="Category already exists")
        
        # Insert new category
        cur.execute("INSERT INTO service_categories (name) VALUES (%s)", (data["name"],))
        conn.commit()
        return {"message": "Service category added successfully", "status": "success"}
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")
    finally:
        close_connection(conn, cur)


@router.post("/add-service")
def add_service(data: dict):
    """Add new service with validation"""
    if not data.get("name") or not data["name"].strip():
        raise HTTPException(status_code=400, detail="Service name is required")
    if not data.get("category_id"):
        raise HTTPException(status_code=400, detail="Category ID is required")
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Check if category exists
        cur.execute("SELECT id FROM service_categories WHERE id = %s", (data["category_id"],))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Category not found")
        
        # Check for duplicates
        duplicate = check_duplicate(
            "SELECT id FROM services WHERE LOWER(name) = LOWER(%s) AND category_id = %s",
            (data["name"], data["category_id"]),
            conn
        )
        if duplicate:
            raise HTTPException(status_code=409, detail="Service already exists in this category")
        
        # Insert new service
        cur.execute("INSERT INTO services (name, category_id) VALUES (%s, %s)", 
                   (data["name"], data["category_id"]))
        conn.commit()
        return {"message": "Service added successfully", "status": "success"}
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")
    finally:
        close_connection(conn, cur)


@router.post("/add-product-category")
def add_product_category(data: dict):
    """Add new product category with duplicate check"""
    if not data.get("name") or not data["name"].strip():
        raise HTTPException(status_code=400, detail="Category name is required")
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Check for duplicates
        duplicate = check_duplicate(
            "SELECT id FROM product_categories WHERE LOWER(name) = LOWER(%s)",
            (data["name"],),
            conn
        )
        if duplicate:
            raise HTTPException(status_code=409, detail="Category already exists")
        
        # Insert new category
        cur.execute("INSERT INTO product_categories (name) VALUES (%s)", (data["name"],))
        conn.commit()
        return {"message": "Product category added successfully", "status": "success"}
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")
    finally:
        close_connection(conn, cur)


@router.post("/add-product")
def add_product(data: dict):
    """Add new product with validation"""
    if not data.get("name") or not data["name"].strip():
        raise HTTPException(status_code=400, detail="Product name is required")
    if not data.get("category_id"):
        raise HTTPException(status_code=400, detail="Category ID is required")
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Check if category exists
        cur.execute("SELECT id FROM product_categories WHERE id = %s", (data["category_id"],))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Category not found")
        
        # Check for duplicates
        duplicate = check_duplicate(
            "SELECT id FROM products WHERE LOWER(name) = LOWER(%s) AND category_id = %s",
            (data["name"], data["category_id"]),
            conn
        )
        if duplicate:
            raise HTTPException(status_code=409, detail="Product already exists in this category")
        
        # Insert new product
        cur.execute("INSERT INTO products (name, category_id) VALUES (%s, %s)", 
                   (data["name"], data["category_id"]))
        conn.commit()
        return {"message": "Product added successfully", "status": "success"}
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")
    finally:
        close_connection(conn, cur)


@router.post("/add-region")
def add_region(data: dict):
    """Add new region with duplicate check"""
    if not data.get("name") or not data["name"].strip():
        raise HTTPException(status_code=400, detail="Region name is required")
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Check for duplicates
        duplicate = check_duplicate(
            "SELECT id FROM regions WHERE LOWER(name) = LOWER(%s)",
            (data["name"],),
            conn
        )
        if duplicate:
            raise HTTPException(status_code=409, detail="Region already exists")
        
        # Insert new region
        cur.execute("INSERT INTO regions (name) VALUES (%s)", (data["name"],))
        conn.commit()
        return {"message": "Region added successfully", "status": "success"}
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")
    finally:
        close_connection(conn, cur)


@router.post("/add-district")
def add_district(data: dict):
    """Add new district with validation"""
    if not data.get("name") or not data["name"].strip():
        raise HTTPException(status_code=400, detail="District name is required")
    if not data.get("region_id"):
        raise HTTPException(status_code=400, detail="Region ID is required")
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Check if region exists
        cur.execute("SELECT id FROM regions WHERE id = %s", (data["region_id"],))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Region not found")
        
        # Check for duplicates within the same region
        duplicate = check_duplicate(
            "SELECT id FROM districts WHERE LOWER(name) = LOWER(%s) AND region_id = %s",
            (data["name"], data["region_id"]),
            conn
        )
        if duplicate:
            raise HTTPException(status_code=409, detail="District already exists in this region")
        
        # Insert new district
        cur.execute("INSERT INTO districts (name, region_id) VALUES (%s, %s)", 
                   (data["name"], data["region_id"]))
        conn.commit()
        return {"message": "District added successfully", "status": "success"}
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")
    finally:
        close_connection(conn, cur)


@router.post("/add-ward")
def add_ward(data: dict):
    """Add new ward with validation"""
    if not data.get("name") or not data["name"].strip():
        raise HTTPException(status_code=400, detail="Ward name is required")
    if not data.get("district_id"):
        raise HTTPException(status_code=400, detail="District ID is required")
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Check if district exists
        cur.execute("SELECT id FROM districts WHERE id = %s", (data["district_id"],))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="District not found")
        
        # Check for duplicates within the same district
        duplicate = check_duplicate(
            "SELECT id FROM wards WHERE LOWER(name) = LOWER(%s) AND district_id = %s",
            (data["name"], data["district_id"]),
            conn
        )
        if duplicate:
            raise HTTPException(status_code=409, detail="Ward already exists in this district")
        
        # Insert new ward
        cur.execute("INSERT INTO wards (name, district_id) VALUES (%s, %s)", 
                   (data["name"], data["district_id"]))
        conn.commit()
        return {"message": "Ward added successfully", "status": "success"}
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")
    finally:
        close_connection(conn, cur)
    cur.execute("INSERT INTO districts (name, region_id) VALUES (%s, %s)", (data["name"], data["region_id"]))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "District added"}


@router.post("/add-ward")
def add_ward(data: dict):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO wards (name, district_id) VALUES (%s, %s)", (data["name"], data["district_id"]))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Ward added"}


# =========================
# 👤 ALL PROVIDERS
# =========================
@router.get("/providers")
def get_all_providers():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, phone, plan, subscription_expiry
        FROM providers
        ORDER BY created_at DESC
    """)

    data = cur.fetchall()

    cur.close()
    conn.close()

    return {"providers": data}


@router.post("/providers")
def add_provider(provider: dict):
    """Add new service provider with validation and duplicate phone check"""
    # Validate required fields
    required_fields = ["name", "phone", "service_id", "ward_id", "plan"]
    for field in required_fields:
        if field not in provider or not str(provider[field]).strip():
            raise HTTPException(status_code=400, detail=f"{field} is required")

    # Validate phone format (basic check)
    if not str(provider["phone"]).startswith("+") and len(str(provider["phone"])) < 7:
        raise HTTPException(status_code=400, detail="Invalid phone number")

    if provider["plan"] not in ["normal", "premium"]:
        raise HTTPException(status_code=400, detail="Plan must be 'normal' or 'premium'")

    conn = get_connection()
    cur = conn.cursor()

    try:
        # Check if service exists
        cur.execute("SELECT id FROM services WHERE id = %s", (provider["service_id"],))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Service not found")

        # Check if ward exists
        cur.execute("SELECT id FROM wards WHERE id = %s", (provider["ward_id"],))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Ward not found")

        # Check for duplicate phone number (providers can't have the same phone)
        duplicate = check_duplicate(
            "SELECT id FROM providers WHERE phone = %s",
            (provider["phone"],),
            conn
        )
        if duplicate:
            raise HTTPException(status_code=409, detail="Phone number already registered as provider")

        # Map plan to is_premium boolean
        is_premium = provider["plan"] == "premium"

        cur.execute("""
            INSERT INTO providers
            (full_name, phone, type, service_id, ward_id, is_premium)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            provider["name"],  # Maps to full_name
            provider["phone"],
            provider["plan"],  # Maps to type
            provider["service_id"],
            provider["ward_id"],
            is_premium  # Maps plan to is_premium boolean
        ))

        conn.commit()
        return {"message": "Provider added successfully", "status": "success"}
    except psycopg2.IntegrityError as e:
        conn.rollback()
        raise HTTPException(status_code=409, detail=f"Database constraint violation: {str(e)}")
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")
    finally:
        close_connection(conn, cur)


@router.delete("/providers/{provider_id}")
def delete_provider(provider_id: int):
    """Delete provider from database"""
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Check if provider exists first
        cur.execute("SELECT id, full_name, phone FROM providers WHERE id = %s", (provider_id,))
        provider = cur.fetchone()

        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")

        # Delete the provider
        cur.execute("DELETE FROM providers WHERE id = %s", (provider_id,))
        conn.commit()

        return {"message": f"Provider '{provider[1]}' deleted successfully", "status": "success"}
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")
    finally:
        close_connection(conn, cur)


@router.post("/product-providers")
def add_product_provider(provider: dict):
    """Add new product provider with validation and duplicate phone check"""
    # Validate required fields
    required_fields = ["name", "phone", "product_id", "ward_id", "plan"]
    for field in required_fields:
        if field not in provider or not str(provider[field]).strip():
            raise HTTPException(status_code=400, detail=f"{field} is required")
    
    # Validate phone format (basic check)
    if not str(provider["phone"]).startswith("+") and len(str(provider["phone"])) < 7:
        raise HTTPException(status_code=400, detail="Invalid phone number")
    
    if provider["plan"] not in ["normal", "premium"]:
        raise HTTPException(status_code=400, detail="Plan must be 'normal' or 'premium'")
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Check if product exists
        cur.execute("SELECT id FROM products WHERE id = %s", (provider["product_id"],))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Check if ward exists
        cur.execute("SELECT id FROM wards WHERE id = %s", (provider["ward_id"],))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Ward not found")
        
        # Check for duplicate phone number (product providers can't have the same phone)
        duplicate = check_duplicate(
            "SELECT id FROM product_providers WHERE phone = %s",
            (provider["phone"],),
            conn
        )
        if duplicate:
            raise HTTPException(status_code=409, detail="Phone number already registered as product provider")
        
        expiry = datetime.now() + timedelta(days=30)

        cur.execute("""
            INSERT INTO product_providers 
            (name, phone, product_id, ward_id, plan, payment_status, subscription_expiry)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            provider["name"],
            provider["phone"],
            provider["product_id"],
            provider["ward_id"],
            provider["plan"],
            "paid",
            expiry
        ))

        conn.commit()
        return {"message": "Product provider added successfully", "status": "success", "expiry": expiry.isoformat()}
    except psycopg2.IntegrityError as e:
        conn.rollback()
        raise HTTPException(status_code=409, detail=f"Database constraint violation: {str(e)}")
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")
    finally:
        close_connection(conn, cur)


@router.delete("/product-providers/{provider_id}")
def delete_product_provider(provider_id: int):
    """Delete product provider from database"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Check if product provider exists first
        cur.execute("SELECT id, name, phone FROM product_providers WHERE id = %s", (provider_id,))
        provider = cur.fetchone()
        
        if not provider:
            raise HTTPException(status_code=404, detail="Product provider not found")
        
        # Delete the product provider
        cur.execute("DELETE FROM product_providers WHERE id = %s", (provider_id,))
        conn.commit()

        return {"message": f"Product provider '{provider[1]}' deleted successfully", "status": "success"}
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")
    finally:
        close_connection(conn, cur)


# =========================
# 💰 PAYMENTS
# =========================
@router.get("/payments")
def get_payments():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT phone, amount, type, status, created_at
        FROM payments
        ORDER BY created_at DESC
    """)

    data = cur.fetchall()

    cur.close()
    conn.close()

    return {"payments": data}


# =========================
# 📊 STATS
# =========================
@router.get("/stats")
def get_stats():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM providers")
    providers = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM product_providers")
    sellers = cur.fetchone()[0]

    cur.execute("SELECT SUM(amount) FROM payments WHERE status='Success'")
    revenue = cur.fetchone()[0] or 0

    cur.close()
    conn.close()

    return {
        "providers": providers,
        "sellers": sellers,
        "revenue": revenue
    }