import frappe


def execute(filters=None):
	columns = get_columns()

	project = filters.get("project") if filters else None

	employee_filters = {}
	if project:
		employee_filters["assigned_project"] = project

	shadow_count = frappe.db.count("Employee", {"current_status": "Shadow", **employee_filters})
	active_count = frappe.db.count("Employee", {"current_status": "Active", **employee_filters})
	total = shadow_count + active_count

	low = 0
	medium = 0
	high = 0

	employees = frappe.get_all(
		"Employee", filters=employee_filters, fields=["skill_ratings", "current_status"]
	)

	for emp in employees:
		score = emp.skill_ratings
		if score is None:
			continue
		score = float(score)
		if score <= 4:
			low += 1
		elif score <= 7:
			medium += 1
		else:
			high += 1

	data = [
		{"resource": "Total Employees", "count": total},
		{"resource": "Shadow Employees", "count": shadow_count},
		{"resource": "Active Employees", "count": active_count},
		{"resource": "Low Skill (0-4)", "count": low},
		{"resource": "Medium Skill (5-7)", "count": medium},
		{"resource": "High Skill (8-10)", "count": high},
	]

	chart = {
		"data": {
			"labels": ["Shadow", "Active"],
			"datasets": [{"name": "Employees", "values": [shadow_count, active_count]}],
		},
		"type": "pie",
	}

	return columns, data, None, chart


def get_columns():
	return [
		{"label": "Resourcec", "fieldname": "resource", "fieldtype": "Data", "width": 250},
		{"label": "Count", "fieldname": "count", "fieldtype": "Int", "width": 150},
	]
