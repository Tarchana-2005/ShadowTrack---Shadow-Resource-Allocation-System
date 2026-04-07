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

	// refresh: function(frm) {
	//     set_evaluation_log_visibility(frm);
	// },

	// onload: function(frm) {
	//     set_evaluation_log_visibility(frm);
	// },

	// end_date: function(frm) {
	//     set_evaluation_log_visibility(frm);
	// }

	// onload: function(frm) {
	//     set_date(frm)
	// },

	// start_date: function(frm) {
	//     set_date(frm)
	// }
});

function set_date(frm) {
	if (!frm.doc.start_date) return;

	frappe.db.get_single_value("ShadowTrack Settings", "maximum_shadow_duration").then((d) => {
		frm.set_value("end_date", frappe.datetime.add_days(frm.doc.start_date, d));
	});
}

// function set_evaluation_log_visibility(frm) {
//     if (!frm.doc.end_date) {
//         frm.set_df_property("evaluation_log", "hidden", 1);
//         return;
//     }

//     let today = frappe.datetime.get_today();
//     let show_from = frappe.datetime.add_days(frm.doc.end_date, -1);

//     if (today >= show_from) {
//         frm.set_df_property("evaluation_log", "hidden", 0);
//     } else {
//         frm.set_df_property("evaluation_log", "hidden", 1);
//     }
// }
