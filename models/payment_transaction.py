from odoo import models, _
from odoo.exceptions import ValidationError
import requests
import jsons

class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    def _get_specific_rendering_values(self, processing_values):
        self.ensure_one()
        if self.provider_code != "khalti":
            return super()._get_specific_rendering_values(processing_values)

        provider = self.provider_id
        secret = provider.khalti_live_secret_key if provider.state == "enabled" else provider.khalti_test_secret_key
        base = provider._khalti_base_url()
        amount_paisa = int(round(self.amount * 100))  # Khalti requires paisa

        payload = josn.dumps({
            "return_url": self._get_processing_return_url(),
            "website_url": self.env["ir.config_parameter"].sudo().get_param("web.base.url"),
            "amount": amount_paisa,
            "purchase_order_id": self.reference,
            "purchase_order_name": self.reference,
            "customer_info": {
                "name": self.partner_name or self.partner_id.name or "Customer",
                "email": self.partner_email or self.partner_id.email or "",
                "phone": self.partner_phone or self.partner_id.phone or "",
            },
        })
        headers = {"Authorization": f"Key {secret}", "Content-Type": "application/json"}

        r = requests.post(f"{base}/epayment/initiate/", json=payload, headers=headers, timeout=30)
        if not r.ok:
            raise ValidationError(_("Khalti initiate failed: %s") % r.text)
        data = r.json()

        self.provider_reference = data.get("pidx")  # store pidx for lookup

        return {"redirect_url": data.get("payment_url"), "redirect_method": "GET"}

    @classmethod
    def _get_tx_from_notification_data(cls, provider_code, notification_data):
        if provider_code != "khalti":
            return super()._get_tx_from_notification_data(provider_code, notification_data)
        pidx = (notification_data or {}).get("pidx")
        return cls.search([("provider_code", "=", "khalti"),
                           ("provider_reference", "=", pidx)], limit=1)

    def _process_notification_data(self, notification_data):
        self.ensure_one()
        status = (notification_data or {}).get("status")
        if status == "Completed":
            self._set_done(_("Payment completed on Khalti"))
        elif status in {"User canceled", "Expired"}:
            self._set_canceled(_("Payment canceled/expired on Khalti"))
        elif status in {"Initiated", "Pending"}:
            self._set_pending(_("Payment pending on Khalti"))
        else:
            self._set_error(_("Unexpected Khalti status: %s") % status)
