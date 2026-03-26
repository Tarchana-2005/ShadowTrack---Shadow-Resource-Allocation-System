# Copyright (c) 2026, Tarchana and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Employee(Document):
	def after_insert(self):
		self.create_login_user()

	def create_login_user(self):
		if self.role not in ["HR", "Manager", "Mentor", "Shadow Employee"]:
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

		self.db_set("user", self.email)
