import frappe


def shadow_assignment_permission(user):
	if not user:
		user = frappe.session.user

	roles = frappe.get_roles(user)

	employee = frappe.db.get_value("Employee", {"user": user}, "name")

	if any(role in roles for role in ["System Manager", "Administrator", "HR"]):
		return ""

	if "Mentor" in roles:
		return (
			f"`tabShadow Assignment`.mentor = {frappe.db.escape(employee)}"
			f" AND `tabShadow Assignment`.workflow_state IN ('In Training', 'Evaluation Pending')"
		)

	if "Shadow Employee" in roles:
		return (
			f"`tabShadow Assignment`.employee = {frappe.db.escape(employee)}"
			f" AND `tabShadow Assignment`.workflow_state = 'In Training'"
		)

	if "Manager" in roles:
		return (
			f"`tabShadow Assignment`.manager= {frappe.db.escape(employee)}"
			f" AND `tabShadow Assignment`.workflow_state != 'Draft'"
		)


def employee_permission(user):
	if not user:
		user = frappe.session.user

	roles = frappe.get_roles(user)

	employee = frappe.db.get_value("Employee", {"user": user}, "name")

	if any(role in roles for role in ["System Manager", "Administrator", "HR"]):
		return ""

	return f"`tabEmployee`.name = {(frappe.db.escape(employee))}"
