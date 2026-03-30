// Copyright (c) 2026, Tarchana and contributors
// For license information, please see license.txt

frappe.ui.form.on("Project", {
	setup: function (frm) {
		(frm.fields_dict["team_members"].grid.get_field("employee").get_query = function (doc) {
			let selected = [];

			(doc.team_members || []).forEach(function (row) {
				if (row.employee) {
					selected.push(row.employee);
				}
			});

			return {
				filters: [
					["role", "in", ["Mentor", "Shadow Employee"]],
					["name", "not in", selected],
				],
			};
		}),
			frm.set_query("manager", function () {
				return {
					filters: {
						current_status: "Active",
						is_manager: 1,
					},
				};
			});
	},
});
