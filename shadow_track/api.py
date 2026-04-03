import frappe
from frappe.model.workflow import apply_workflow
from frappe.utils import add_days, getdate, nowdate


def send_training_reminder():
	today = getdate(nowdate())

	reminder_days = frappe.db.get_single_value("ShadowTrack Settings", "reminder_days_before")

	if not reminder_days:
		return

	target_date = add_days(today, reminder_days)

	assignments = frappe.get_all(
		"Shadow Assignment",
		filters={"workflow_state": "In Training", "reminder_sent": 0, "end_date": target_date},
		fields=["name", "mentor", "employee", "end_date"],
	)

	if not assignments:
		return

	for a in assignments:
		if not a.mentor:
			continue

		mentor_email = frappe.db.get_value("Employee", a.mentor, "email")

		if not mentor_email:
			continue

		frappe.sendmail(
			recipients=[mentor_email],
			subject="Training Ending Soon",
			message=f"""
                Hello,

                Training for employee {a.employee} is nearing completion.

                End Date: {a.end_date}

                Please complete evaluation.

                Assignment: {a.name}
            """,
		)

		frappe.db.set_value("Shadow Assignment", a.name, "reminder_sent", 1)


def update_evaluation_pending_status():
	today = getdate(nowdate())
	escalation_date = add_days(today, -1)

	assignments = frappe.get_all(
		"Shadow Assignment",
		filters={"workflow_state": "In Training", "escalation_sent": 0, "end_date": escalation_date},
		fields=["name", "employee", "employee_name", "end_date", "mentor"],
	)

	if not assignments:
		return

	for a in assignments:
		try:
			mentor_email = frappe.db.get_value("Employee", a.mentor, "email")

			doc = frappe.get_doc("Shadow Assignment", a.name)

			apply_workflow(doc, "End Training")
			frappe.db.commit()

			# Send escalation email
			frappe.sendmail(
				recipients=[mentor_email],
				subject=f"Escalation: Evaluation Pending - {a.employee_name}",
				message=f"""
                    <p>Dear Mentor,</p>
                    <p>The training period for <b>{a.employee_name}</b>
                    ended on <b>{a.end_date}</b>.</p>
                    <p>The evaluation is still <b>pending</b>.
                    Please complete it at the earliest.</p>
                    <br>
                    <p>Thank you</p>
                """,
			)

			frappe.db.set_value("Shadow Assignment", a.name, "escalation_sent", 1)

		except frappe.ValidationError:
			frappe.log_error(title=f"Workflow Failed: {a.name}", message=frappe.get_traceback())

		except Exception:
			frappe.log_error(title=f"Unexpected Error: {a.name}", message=frappe.get_traceback())
