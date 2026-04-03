// Copyright (c) 2026, Tarchana and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Employee", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("Employee", {
	setup: function (frm) {
		frm.set_query("role", function () {
			return {
				filters: {
					name: [
						"in",
						["Mentor", "Manager", "HR", "Shadow Employee", "General Employee"],
					],
				},
			};
		});
	},
});
