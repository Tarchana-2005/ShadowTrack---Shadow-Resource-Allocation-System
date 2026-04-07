// Copyright (c) 2026, Tarchana and contributors
// For license information, please see license.txt

frappe.query_reports["Resource Readiness Report"] = {
	filters: [
		{
			fieldname: "project",
			label: "Project",
			fieldtype: "Link",
			options: "Project",
		},
	],
};
