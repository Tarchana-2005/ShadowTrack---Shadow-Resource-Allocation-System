# Copyright (c) 2026, Tarchana and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ShadowAssignment(Document):
	def validate(self):
		if self.end_date < self.start_date:
			frappe.throw("End date cannot be before start date")
