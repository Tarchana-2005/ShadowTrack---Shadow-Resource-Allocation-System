# Copyright (c) 2026, Tarchana and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_days


class ShadowAssignment(Document):
	def validate(self):
		if self.start_date and self.end_date:
			if self.end_date < self.start_date:
				frappe.throw("End date cannot be before start date")

		if self.workflow_state == "Draft":
			if not self.project:
				frappe.throw("Project must be assigned before sending for approval")

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

	def on_submit(self):
		if self.workflow_state == "In Training":
			self.send_assignment_email()

	def on_update_after_submit(self):
		prev_doc = self.get_doc_before_save()

		if prev_doc:
			if prev_doc.workflow_state == "In Training" and self.workflow_state == "Evaluation Pending":
				if not self.learning_log:
					frappe.throw("Learning log must be provided before submitting evaluation")

			if (
				prev_doc.workflow_state == "Evaluation Pending"
				and self.workflow_state == "Evaluation Submitted"
			):
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

		self.training_completion()
		self.training_extend()

	def training_completion(self):
		if self.workflow_state == "Completed" and self.final_decision == "Ready":
			frappe.db.set_value(
				"Employee",
				self.employee,
				{
					"current_status": "Active",
					"role": "General Employee",
				},
			)

			email = frappe.db.get_value("Employee", self.employee, "email")

			user_doc = frappe.get_doc("User", email)

			new_roles = []

			for r in user_doc.roles:
				if r.role != "Shadow Employee":
					new_roles.append(r)

			user_doc.roles = new_roles

			found = False

			for r in user_doc.roles:
				if r.role == "General Employee":
					found = True
					break

				if not found:
					user_doc.append("roles", {"role": "General Employee"})

			user_doc.save(ignore_permissions=True)

	def training_extend(self):
		prev_doc = self.get_doc_before_save()

		if prev_doc:
			if prev_doc.workflow_state == "Extended" and self.workflow_state == "In Training":
				self.start_date = self.end_date

				duration = frappe.db.get_single_value("ShadowTrack Settings", "maximum_shadow_duration")

				if duration:
					self.end_date = add_days(self.start_date, duration)

				self.training_remainder = 0

	def send_assignment_email(self):
		mentor_email = frappe.db.get_value("Employee", self.mentor, "email")

		if not mentor_email:
			return

		frappe.sendmail(
			recipients=[mentor_email],
			subject="New Shadow Assignment - Training Started",
			message=f"""
            Hello,

            You have been assigned as a mentor for training.

            Employee: {self.employee}
            Project: {self.project}
            Start Date: {self.start_date}
            End Date: {self.end_date}

            The training phase has now started. Please begin guidance.

            Regards,
            ShadowTrack
            """,
		)
