frappe.pages["ecopan-bot"].on_page_load = function (wrapper) {
  frappe.ui.make_app_page({
    parent: wrapper,
    single_column: true,
  });
};

frappe.pages["ecopan-bot"].on_page_show = function (wrapper) {
  load_ecopanbot_ui(wrapper);
};

function load_ecopanbot_ui(wrapper) {
  let $parent = $(wrapper).find(".layout-main-section");
  $parent.empty();

  frappe.require("ecopanbot_ui.bundle.jsx").then(() => {
    new ecopanbot.ui.ecopanBotUI({
      wrapper: $parent,
      page: wrapper.page,
    });
  });
}
