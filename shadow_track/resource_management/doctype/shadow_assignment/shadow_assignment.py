# Copyright (c) 2026, Tarchana and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ShadowAssignment(Document):
	def validate(self):
		self.validate_roles()

		if self.start_date and self.end_date:
			if self.end_date < self.start_date:
				frappe.throw("End date cannot be before start date")

		self.validate_logs()
		self.validate_evaluation_logs()

	def validate_roles(self):
		if self.employee == self.mentor:
			frappe.throw("Employee and Mentor cannot be same")

		if self.employee == self.manager:
			frappe.throw("Employee and Manager cannot be same")

		if self.mentor == self.manager:
			frappe.throw("Mentor and Manager cannot be same")

	def validate_logs(self):
		if self.learning_log:
			if self.workflow_state != "In Training":
				if not self.is_new():
					frappe.throw("Learning Logs can only be added during In Training stage")

		if self.workflow_state == "Completed":
			if not self.evaluation_log:
				frappe.throw("Evaluation must be completed before marking as Completed")

			if not self.final_decision:
				frappe.throw("Manager must provide final decision before completion")

		if self.workflow_state == "In Training":
			if not self.evaluation_log:
				frappe.throw("Evaluation must be completed before Submitting")

			if not self.learning_log:
				frappe.throw("Learning log must be provided before Submitting")

	def on_update_after_submit(self):
		for row in self.evaluation_log:
			frappe.msgprint("HI")
			employee = frappe.db.get_value("Employee", {"email": frappe.session.user}, "name")
			if employee != self.mentor:
				frappe.throw("Only the assigned mentor can add or update evaluation")

			if not row.mentor_recommendation:
				frappe.throw("Mentor must provide a recommendation before saving evaluation")
