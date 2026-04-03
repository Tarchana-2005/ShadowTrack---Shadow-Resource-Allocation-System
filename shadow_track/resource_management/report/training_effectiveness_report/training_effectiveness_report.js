// Copyright (c) 2026, Tarchana and contributors
// For license information, please see license.txt

frappe.query_reports["Training Effectiveness Report"] = {
	filters: [
		{
			fieldname: "project",
			label: "Project",
			fieldtype: "Link",
			options: "Project",
		},
		{
			fieldname: "mentor",
			label: "Mentor",
			fieldtype: "Link",
			options: "Employee",
			get_query: function () {
				return {
					filters: {
						is_mentor: 1,
					},
				};
			},
		},
		{
			fieldname: "from_date",
			label: "From Date",
			fieldtype: "Date",
		},
		{
			fieldname: "to_date",
			label: "To Date",
			fieldtype: "Date",
		},
	],
};
