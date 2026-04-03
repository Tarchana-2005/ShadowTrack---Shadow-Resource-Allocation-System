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
			parent_start = frappe.get_value("Project", self.parent_project, "start_date")
			parent_end = frappe.get_value("Project", self.parent_project, "end_date")

			if parent_start and getdate(self.start_date) < getdate(parent_start):
				frappe.throw("Child project cannot start before parent project")

			if parent_end and getdate(self.end_date) > getdate(parent_end):
				frappe.throw("Child project cannot end after parent project")

		# parent project check
		if not self.is_group:
			if not self.parent_project:
				frappe.throw("Non-group project must have a parent project")
