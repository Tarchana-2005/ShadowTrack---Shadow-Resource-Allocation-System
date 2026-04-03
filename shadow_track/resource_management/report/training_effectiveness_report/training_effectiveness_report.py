# Copyright (c) 2026, Tarchana and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import date_diff


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"label": "Project", "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 150},
		{"label": "Mentor", "fieldname": "mentor", "fieldtype": "Link", "options": "Employee", "width": 150},
		{"label": "Total Assignments", "fieldname": "total", "fieldtype": "Int", "width": 150},
		{"label": "Completed", "fieldname": "completed", "fieldtype": "Int", "width": 120},
		{"label": "Successful", "fieldname": "success", "fieldtype": "Int", "width": 120},
		{
			"label": "Success Rate (% of Completed)",
			"fieldname": "success_rate",
			"fieldtype": "Float",
			"width": 180,
		},
		{"label": "Avg Duration (Days)", "fieldname": "avg_duration", "fieldtype": "Float", "width": 180},
	]


def get_data(filters):
	conditions = "WHERE docstatus = 1"

	if filters.get("project"):
		conditions += " AND project = %(project)s"

	if filters.get("mentor"):
		conditions += " AND mentor = %(mentor)s"

	if filters.get("from_date"):
		conditions += " AND start_date >= %(from_date)s"

	if filters.get("to_date"):
		conditions += " AND end_date <= %(to_date)s"

	records = frappe.db.sql(
		f"""
        SELECT
            project,
            mentor,
            start_date,
            end_date,
            workflow_state,
            final_decision
        FROM `tabShadow Assignment`
        {conditions}
    """,
		filters,
		as_dict=True,
	)

	report_map = {}

	for r in records:
		key = (r.project, r.mentor)

		if key not in report_map:
			report_map[key] = {"total": 0, "completed": 0, "success": 0, "duration": 0}

		report_map[key]["total"] += 1

		if r.end_date and r.workflow_state == "Completed":
			report_map[key]["completed"] += 1

			days = date_diff(r.end_date, r.start_date)
			report_map[key]["duration"] += days

			if r.final_decision == "Ready":
				report_map[key]["success"] += 1

	data = []

	for (project, mentor), val in report_map.items():
		completed = val["completed"]

		avg_duration = val["duration"] / completed if completed else 0

		success_rate = (val["success"] / completed) * 100 if completed else 0

		data.append(
			{
				"project": project,
				"mentor": mentor,
				"total": val["total"],
				"completed": completed,
				"success": val["success"],
				"success_rate": round(success_rate, 2),
				"avg_duration": round(avg_duration, 2),
			}
		)

	return data
