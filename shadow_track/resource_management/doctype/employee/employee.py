# Copyright (c) 2026, Tarchana and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today


class Employee(Document):
	def after_insert(self):
		self.create_login_user()

	def create_login_user(self):
		if self.role not in ["HR", "Manager", "Mentor", "Shadow Employee", "General Employee"]:
			return

		if frappe.db.exists("User", self.email):
			frappe.throw("User email already exists")

		user = frappe.get_doc(
			{
				"doctype": "User",
				"email": self.email,
				"first_name": self.full_name,
				"enabled": 1,
				"send_welcome_email": 1,
				"roles": [{"role": self.role}],
			}
		)

		user.insert(ignore_permissions=True)

	def validate(self):
		self.calculate_experience()

	def calculate_experience(self):
		if not self.date_of_joining:
			self.experience_in_months = 0
			self.experience_in_years = 0
			return
		joining_date = getdate(self.date_of_joining)
		current_date = getdate(today())

		months = (current_date.year - joining_date.year) * 12 + (current_date.month - joining_date.month)

		if months < 0:
			months = 0

		self.experience_in_months = months
		self.experience_in_years = round(months / 12, 1)
