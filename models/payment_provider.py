from odoo import fields, models

KHALTI = "khalti"

class PaymentProvider(models.Model):
    _inherit = "payment.provider"

    code = fields.Selection(selection_add=[(KHALTI, "Khalti")])

    khalti_test_secret_key = fields.Char("Khalti Test Secret")
    khalti_live_secret_key = fields.Char("Khalti Live Secret")

    def _khalti_base_url(self):
        # Odoo 18 provider.state: "disabled" | "test" | "enabled"
        return "https://dev.khalti.com/api/v2" if self.state == "test" else "https://khalti.com/api/v2"

    def _compute_feature_support_fields(self):
        super()._compute_feature_support_fields()
        for p in self.filtered(lambda r: r.code == KHALTI):
            p.support_refund = None
