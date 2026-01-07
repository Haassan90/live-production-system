import requests
from config import ERP_URL, ERP_API_KEY, ERP_API_SECRET

def update_work_order(work_order_name, produced_qty):
    url = f"{ERP_URL}/api/resource/Work Order/{work_order_name}"

    headers = {
        "Authorization": f"token {ERP_API_KEY}:{ERP_API_SECRET}",
        "Content-Type": "application/json"
    }

    payload = {
        "status": "Completed",
        "produced_qty": produced_qty
    }

    try:
        requests.put(url, json=payload, headers=headers, timeout=5)
    except Exception as e:
        print("ERP update failed:", e)
