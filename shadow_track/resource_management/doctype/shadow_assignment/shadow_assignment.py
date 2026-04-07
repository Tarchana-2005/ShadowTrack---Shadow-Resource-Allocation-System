# Copyright (c) 2026, Tarchana and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_days


class ShadowAssignment(Document):
	def validate(self):
		existing = frappe.db.exists(
			"Shadow Assignment",
			{
				"employee": self.employee,
				"status": ["in", ["In Training", "Pending Approval"]],
				"name": ["!=", self.name],
			},
		)

		for row in self.evaluation_log:
			fields = {
				"Technical skills": row.technical_skills,
				"Communication": row.communication,
				"Task Handling": row.task_handling,
			}

			for field_name, value in fields.items():
				if value is not None and (value < 0 or value > 10):
					frappe.throw(f"{field_name} should be between 0 to 10")

		if existing:
			frappe.throw("Active assignment already exists")

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

				employee = frappe.db.get_value("Employee", {"email": frappe.session.user}, "name")
				if employee != self.mentor:
					frappe.throw("Only the assigned mentor can add or update evaluation")

				for row in self.evaluation_log:
					if not row.mentor_recommendation:
						frappe.throw("Mentor must provide a recommendation before saving evaluation")

				self.calculate_evaluation_score()
				self.db_set("evaluation_score", self.evaluation_score)

			if prev_doc.workflow_state == "Evaluation Submitted" and (
				self.workflow_state == "Completed" or self.workflow_state == "Extended"
			):
				if not self.final_decision:
					frappe.throw("Final decision must be given by the Manager")

				employee = frappe.db.get_value("Employee", {"email": frappe.session.user}, "name")
				if employee != self.manager:
					frappe.throw("Only manager can give final decision")

			self.training_extend(prev_doc)

		self.training_completion()
		if self.workflow_state == "Completed" and self.final_decision == "Ready":
			self.notify_employee_completion()

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

	def notify_employee_completion(self):
		emp = frappe.db.get_value("Employee", self.employee, ["email", "full_name"], as_dict=True)

		frappe.sendmail(
			recipients=[emp.email],
			subject="Congratulations! Training Completed - ShadowTrack",
			message=f"""
            <p>Dear {emp.name},</p>
            <p>Congratulations! </p>
            <p>Your shadow training has been successfully completed.</p>
            <p><b>Assignment:</b> {self.name}</p>
            <p><b>Training Period:</b> {self.start_date} to {self.end_date}</p>
            <p>Your role has been updated to <b>General Employee</b>.
            Welcome to the team!</p>
            <br>
            <p>Regards,</p>
            <p>ShadowTrack</p>
        """,
		)

	def training_extend(self, prev_doc):
		if prev_doc:
			if prev_doc.workflow_state == "Extended" and self.workflow_state == "In Training":
				self.final_decision = ""

				duration = frappe.db.get_single_value("ShadowTrack Settings", "maximum_shadow_duration") or 30
				self.end_date = add_days(self.start_date, duration)

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

	def calculate_evaluation_score(self):
		total_score = 0
		count = 0

		for row in self.evaluation_log:
			if (
				row.technical_skills is not None
				and row.communication is not None
				and row.task_handling is not None
			):
				row_score = (row.technical_skills + row.communication + row.task_handling) / 3

				total_score += row_score
				count += 1

		self.evaluation_score = round(total_score / count, 2) if count else 0
