from odoo import http
from odoo.http import request
import requests

class KhaltiController(http.Controller):
    @http.route("/payment/khalti/return", type="http", auth="public", methods=["GET"], csrf=False)
    def khalti_return(self, **query):
        tx = request.env["payment.transaction"].sudo()._get_tx_from_notification_data("khalti", query)
        if not tx:
            return request.redirect("/payment/status?error=tx_not_found")

        provider = tx.provider_id
        base = provider._khalti_base_url()
        secret = provider.khalti_live_secret_key if provider.state == "enabled" else provider.khalti_test_secret_key
        headers = {"Authorization": f"Key {secret}", "Content-Type": "application/json"}

        r = requests.post(f"{base}/epayment/lookup/", json={"pidx": tx.provider_reference}, headers=headers, timeout=30)
        data = r.json() if r.ok else {"status": "error"}

        tx._handle_notification_data("khalti", {"status": data.get("status")})
        return request.redirect("/payment/status")
