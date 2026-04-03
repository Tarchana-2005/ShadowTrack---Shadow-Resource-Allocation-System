# Copyright (c) 2026, Tarchana and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"label": "Mentor", "fieldname": "mentor", "fieldtype": "Link", "options": "Employee", "width": 180},
		{"label": "Total Trainees", "fieldname": "total", "fieldtype": "Int", "width": 140},
		{"label": "Completed", "fieldname": "completed", "fieldtype": "Int", "width": 120},
		{"label": "Successful", "fieldname": "successful", "fieldtype": "Int", "width": 120},
		{"label": "Success Rate (%)", "fieldname": "success_rate", "fieldtype": "Float", "width": 150},
		{"label": "Avg Technical Score", "fieldname": "avg_technical", "fieldtype": "Float", "width": 170},
		{
			"label": "Avg Communication Score",
			"fieldname": "avg_communication",
			"fieldtype": "Float",
			"width": 200,
		},
		{
			"label": "Avg Task Handling Score",
			"fieldname": "avg_task_handling",
			"fieldtype": "Float",
			"width": 200,
		},
		{"label": "Avg Evaluation Score", "fieldname": "avg_score", "fieldtype": "Float", "width": 170},
		{"label": "Evaluation (%)", "fieldname": "percentage_score", "fieldtype": "Percent", "width": 150},
		{"label": "Result", "fieldname": "result", "fieldtype": "Data", "width": 100},
	]


def get_data(filters):
	conditions = "WHERE sa.docstatus = 1"

	if filters.get("mentor"):
		conditions += " AND sa.mentor = %(mentor)s"

	if filters.get("from_date"):
		conditions += " AND sa.start_date >= %(from_date)s"

	if filters.get("to_date"):
		conditions += " AND sa.end_date <= %(to_date)s"

	assignments = frappe.db.sql(
		f"""
        SELECT
            sa.name,
            sa.mentor,
            sa.workflow_state,
            sa.final_decision
        FROM `tabShadow Assignment` sa
        {conditions}
    """,
		filters,
		as_dict=True,
	)

	if not assignments:
		return []

	assignment_names = [a.name for a in assignments]
	evaluation_logs = frappe.db.sql(
		"""
        SELECT
            parent,
            technical_skills,
            communication,
            task_handling
        FROM `tabEvaluation Log`
        WHERE parent IN %(parents)s
    """,
		{"parents": assignment_names},
		as_dict=True,
	)

	eval_map = {}
	for log in evaluation_logs:
		eval_map[log.parent] = log

	min_passing_score = frappe.db.get_single_value("ShadowTrack Settings", "minimum_passing_score") or 60

	mentor_map = {}

	for a in assignments:
		mentor = a.mentor

		if mentor not in mentor_map:
			mentor_map[mentor] = {
				"total": 0,
				"completed": 0,
				"successful": 0,
				"technical_scores": [],
				"communication_scores": [],
				"task_handling_scores": [],
			}

		mentor_map[mentor]["total"] += 1

		if a.workflow_state == "Completed":
			mentor_map[mentor]["completed"] += 1

			if a.final_decision == "Ready":
				mentor_map[mentor]["successful"] += 1

			log = eval_map.get(a.name)
			if log:
				if log.technical_skills:
					mentor_map[mentor]["technical_scores"].append(log.technical_skills)
				if log.communication:
					mentor_map[mentor]["communication_scores"].append(log.communication)
				if log.task_handling:
					mentor_map[mentor]["task_handling_scores"].append(log.task_handling)

	data = []

	for mentor, val in mentor_map.items():
		completed = val["completed"]

		success_rate = round((val["successful"] / completed) * 100 if completed else 0, 2)

		avg_technical = round(
			sum(val["technical_scores"]) / len(val["technical_scores"]) if val["technical_scores"] else 0, 2
		)

		avg_communication = round(
			sum(val["communication_scores"]) / len(val["communication_scores"])
			if val["communication_scores"]
			else 0,
			2,
		)

		avg_task_handling = round(
			sum(val["task_handling_scores"]) / len(val["task_handling_scores"])
			if val["task_handling_scores"]
			else 0,
			2,
		)

		all_scores = val["technical_scores"] + val["communication_scores"] + val["task_handling_scores"]
		avg_score = round(sum(all_scores) / len(all_scores) if all_scores else 0, 2)

		percentage_score = avg_score * 10
		result = "Pass" if percentage_score >= min_passing_score else "Fail"

		data.append(
			{
				"mentor": mentor,
				"total": val["total"],
				"completed": completed,
				"successful": val["successful"],
				"success_rate": success_rate,
				"avg_technical": avg_technical,
				"avg_communication": avg_communication,
				"avg_task_handling": avg_task_handling,
				"avg_score": avg_score,
				"percentage_score": percentage_score,
				"result": result,
			}
		)
		data.append

	return data
