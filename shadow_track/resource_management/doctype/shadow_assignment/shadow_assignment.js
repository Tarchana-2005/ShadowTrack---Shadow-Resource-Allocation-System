// Copyright (c) 2026, Tarchana and contributors
// For license information, please see license.txt
frappe.ui.form.on("Shadow Assignment", {
	setup: function (frm) {
		frm.set_query("employee", function () {
			return {
				filters: {
					current_status: "Shadow",
					assigned_project: "",
				},
			};
		}),
			frm.set_query("project", function () {
				return {
					filters: [
						["status", "=", "Active"],
						["is_group", "=", 0],
						["start_date", ">=", frappe.datetime.get_today()],
					],
				};
			}),
			frm.set_query("mentor", function () {
				return {
					filters: {
						current_status: "Active",
						is_mentor: 1,
						assigned_project: frm.doc.project,
					},
				};
			}),
			frm.set_query("manager", function () {
				return {
					filters: {
						current_status: "Active",
						is_manager: 1,
						assigned_project: frm.doc.project,
					},
				};
			});
	},
});
