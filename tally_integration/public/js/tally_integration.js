frappe.ui.form.on('Customer', {
	refresh: function(frm) {
		if (frm.doc.docstatus === 1) {
			frm.add_custom_button('Create in Tally', function() {
				frappe.call({
					method: 'tally_integration.api.tally_api.create_customer_in_tally',
					args: {
						customer_name: frm.doc.name
					},
					callback: function(r) {
						if (r.message && r.message.success) {
							frappe.msgprint(r.message.message);
						} else if (r.message && r.message.error) {
							frappe.msgprint(__('Error: ') + r.message.error);
						}
					}
				});
			}, __('Actions'));
		}
	}
});

frappe.ui.form.on('Supplier', {
	refresh: function(frm) {
		if (frm.doc.docstatus === 1) {
			frm.add_custom_button('Create in Tally', function() {
				frappe.call({
					method: 'tally_integration.api.tally_api.create_supplier_in_tally',
					args: {
						supplier_name: frm.doc.name
					},
					callback: function(r) {
						if (r.message && r.message.success) {
							frappe.msgprint(r.message.message);
						} else if (r.message && r.message.error) {
							frappe.msgprint(__('Error: ') + r.message.error);
						}
					}
				});
			}, __('Actions'));
		}
	}
});

frappe.ui.form.on('Sales Invoice', {
	refresh: function(frm) {
		if (frm.doc.docstatus === 1) {
			frm.add_custom_button('Create in Tally', function() {
				frappe.call({
					method: 'tally_integration.api.tally_api.create_sales_invoice_in_tally',
					args: {
						invoice_name: frm.doc.name
					},
					callback: function(r) {
						if (r.message && r.message.success) {
							frappe.msgprint(r.message.message);
						} else if (r.message && r.message.error) {
							frappe.msgprint(__('Error: ') + r.message.error);
						}
					}
				});
			}, __('Actions'));
		}
	}
});

frappe.ui.form.on('Purchase Invoice', {
	refresh: function(frm) {
		if (frm.doc.docstatus === 1) {
			frm.add_custom_button('Create in Tally', function() {
				frappe.call({
					method: 'tally_integration.api.tally_api.create_purchase_invoice_in_tally',
					args: {
						invoice_name: frm.doc.name
					},
					callback: function(r) {
						if (r.message && r.message.success) {
							frappe.msgprint(r.message.message);
						} else if (r.message && r.message.error) {
							frappe.msgprint(__('Error: ') + r.message.error);
						}
					}
				});
			}, __('Actions'));
		}
	}
});
