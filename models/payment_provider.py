from odoo import fields, models

KHALTI = "khalti"

class PaymentProvider(models.Model):
    _inherit = "payment.provider"

    # add selection item AND define ondelete behavior (v18 is strict)
    code = fields.Selection(
        selection_add=[(KHALTI, "Khalti")],
        ondelete={KHALTI: "set default"},
    )

    khalti_test_secret_key = fields.Char("Khalti Test Secret")
    khalti_live_secret_key = fields.Char("Khalti Live Secret")

    def _khalti_base_url(self):
        return "https://dev.khalti.com/api/v2" if self.state == "test" else "https://khalti.com/api/v2"

    def _compute_feature_support_fields(self):
        super()._compute_feature_support_fields()
        for p in self.filtered(lambda r: r.code == KHALTI):
            p.support_refund = None
