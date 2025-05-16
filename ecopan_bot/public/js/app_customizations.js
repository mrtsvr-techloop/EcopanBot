frappe.ui.keys.add_shortcut({
  shortcut: "shift+ctrl+d",
  action: function () {
    // navigate to ask ecopan bot page
    frappe.set_route("ecopan-bot");
  },
  description: __("Ask ecopanBot"),
});
