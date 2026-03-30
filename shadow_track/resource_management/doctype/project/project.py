# Copyright (c) 2026, Tarchana and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate
from frappe.utils.nestedset import NestedSet


class Project(NestedSet):
	def validate(self):
		if self.start_date and self.end_date:
			if getdate(self.end_date) < getdate(self.start_date):
				frappe.throw("End date cannot be before start date")

		# parent child date check
		if self.parent_project:
			parent = frappe.get_doc("Project", self.parent_project)

			if parent.start_date and getdate(self.start_date) < getdate(parent.start_date):
				frappe.throw("Child project cannot start before parent project")

			if parent.end_date and getdate(self.end_date) > getdate(parent.end_date):
				frappe.throw("Child project cannot end after parent project")

		# parent project check
		if not self.is_group:
			if not self.parent_project:
				frappe.throw("Team must have a parent project")
