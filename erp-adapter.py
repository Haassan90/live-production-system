"""
ERPNext Adapter
----------------
Is file ka kaam:
- ERPNext se Work Orders lena
- ERPNext ko production progress bhejna

Abhi:
- Dummy / placeholder functions
- Scheduler safely call kar sakta hai
"""

import requests
from datetime import datetime

# ==============================
# ERP CONFIG (LATER REAL)
# ==============================
ERP_URL = "https://erp.example.com"
API_KEY = "API_KEY"
API_SECRET = "API_SECRET"


# ==============================
# PIPE SPEED (SOURCE OF TRUTH)
# ==============================
PIPE_SPEED = {
    20: 20,     # sec per meter
    32: 20,
    33: 22,
    110: 52
}


# ==============================
# AUTH HEADER (LATER USED)
# ==============================
def _headers():
    return {
        "Authorization": f"token {API_KEY}:{API_SECRET}",
        "Content-Type": "application/json"
    }


# ==============================
# FETCH WORK ORDERS (ERP → BACKEND)
# ==============================
def fetch_work_orders():
    """
    ERPNext se open Work Orders laayega
    Abhi dummy data return kar raha hai
    """

    # TODO: ERPNext API call
    # response = requests.get(
    #     f"{ERP_URL}/api/resource/Work Order",
    #     headers=_headers()
    # )

    # 🔴 TEMP DUMMY DATA
    return [
        {
            "work_order": "WO-1001",
            "pipe_size": 32,
            "quantity": 500,
            "priority": 1,
            "location": "Modan"
        },
        {
            "work_order": "WO-1002",
            "pipe_size": 110,
            "quantity": 300,
            "priority": 2,
            "location": "Baldeya"
        }
    ]


# ==============================
# UPDATE PROGRESS (BACKEND → ERP)
# ==============================
def update_work_order_progress(
    work_order: str,
    completed_qty: float,
    status: str
):
    """
    ERPNext ko live production update karega
    """

    payload = {
        "completed_qty": completed_qty,
        "status": status,
        "last_update": datetime.now().isoformat()
    }

    # TODO: ERPNext PATCH call
    # requests.put(
    #     f"{ERP_URL}/api/resource/Work Order/{work_order}",
    #     json=payload,
    #     headers=_headers()
    # )

    # TEMP LOG
    print(f"[ERP SYNC] {work_order} → {payload}")
