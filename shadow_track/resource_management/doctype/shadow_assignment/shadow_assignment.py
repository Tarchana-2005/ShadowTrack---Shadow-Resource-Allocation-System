# Copyright (c) 2026, Tarchana and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ShadowAssignment(Document):
	def validate(self):
		if self.start_date and self.end_date:
			if self.end_date < self.start_date:
				frappe.throw("End date cannot be before start date")

		self.validate_logs()

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

	def on_update_after_submit(self):
		prev_doc = self.get_doc_before_save()

		if prev_doc:
			if prev_doc.workflow_state == "In Training" and self.workflow_state == "Evaluation Submitted":
				if not self.learning_log:
					frappe.throw("Learning log must be provided before submitting evaluation")

				if not self.evaluation_log:
					frappe.throw("Evaluation must be completed before submitting")

				for row in self.evaluation_log:
					employee = frappe.db.get_value("Employee", {"email": frappe.session.user}, "name")
					if employee != self.mentor:
						frappe.throw("Only the assigned mentor can add or update evaluation")

					if not row.mentor_recommendation:
						frappe.throw("Mentor must provide a recommendation before saving evaluation")

		if self.final_decision:
			employee = frappe.db.get_value("Employee", {"email": frappe.session.user}, "name")
			if employee != self.manager:
				frappe.throw("Only manager can give final decision")

		if prev_doc:
			if prev_doc.workflow_state == "Evaluation Submitted" and (
				self.workflow_state == "Completed" or self.workflow_state == "Extended"
			):
				if not self.final_decision:
					frappe.throw("Final decision must be given by the Manager")
