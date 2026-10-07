import frappe
from frappe import _
import requests
from requests.exceptions import RequestException
from xml.sax.saxutils import escape


def get_tally_config():
    """Get Tally configuration"""
    try:
        doc = frappe.get_single("Tally Configuration")
        if not doc.enabled:
            frappe.throw(_("Tally integration is not enabled. Please enable it in Tally Configuration."))
        return {
            "tally_url": doc.tally_url,
            "tally_port": doc.tally_port,
            "tally_company": doc.tally_company,
            "customer_ledger_parent": doc.customer_ledger_parent,
            "supplier_ledger_parent": doc.supplier_ledger_parent
        }
    except frappe.DoesNotExistError:
        frappe.throw(_("Tally Configuration not found. Please configure it first."))
    except Exception as e:
        frappe.throw(_("Error getting Tally configuration: {0}").format(str(e)))


def clean_text(value):
    """Clean and convert text to string"""
    if value is None:
        return ""
    return str(value).strip()


def xml_escape(value):
    """Escape XML special characters"""
    return escape(clean_text(value))


def send_to_tally(xml_data):
    """Send XML data to Tally receiver server"""
    config = get_tally_config()
    tally_url = f"{config['tally_url']}:{config['tally_port']}/tally-receiver"

    try:
        # Send as JSON with xml_data field
        payload = {
            "xml_data": xml_data
        }
        response = requests.post(
            tally_url,
            json=payload,
            headers={
                'Content-Type': 'application/json; charset=utf-8'
            },
            timeout=30
        )

        if response.status_code == 200:
            return {
                "success": True,
                "status_code": response.status_code,
                "response": response.text
            }
        else:
            return {
                "success": False,
                "status_code": response.status_code,
                "error": response.text
            }

    except RequestException as e:
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist()
def create_customer_in_tally(customer_name):
    """Create customer in Tally"""
    try:
        customer = frappe.get_doc("Customer", customer_name)
        config = get_tally_config()

        name = xml_escape(customer.customer_name or customer.name)
        company = xml_escape(config['tally_company'])
        parent = xml_escape(config['customer_ledger_parent'])

        # Build address information
        address_text = ""
        if customer.customer_primary_address:
            address = frappe.get_doc("Address", customer.customer_primary_address)
            address_text = f"""
                    <ADDRESS.LIST>
                        <ADDRESS>{xml_escape(address.address_line1)}</ADDRESS>
                        <CITY>{xml_escape(address.city)}</CITY>
                        <STATE>{xml_escape(address.state)}</STATE>
                        <PINCODE>{xml_escape(address.pincode)}</PINCODE>
                        <COUNTRY>{xml_escape(address.country)}</COUNTRY>
                    </ADDRESS.LIST>"""

        # Build GSTIN if available
        gstin = ""
        if customer.gstin:
            gstin = f"<GSTIN>{xml_escape(customer.gstin)}</GSTIN>"

        # Build PAN if available
        pan = ""
        if customer.pan:
            pan = f"<PAN>{xml_escape(customer.pan)}</PAN>"

        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<ENVELOPE>
    <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Import</TALLYREQUEST>
        <TYPE>Data</TYPE>
        <ID>All Masters</ID>
    </HEADER>
    <BODY>
        <DESC>
            <STATICVARIABLES>
                <SVCURRENTCOMPANY>{company}</SVCURRENTCOMPANY>
            </STATICVARIABLES>
        </DESC>
        <DATA>
            <TALLYMESSAGE xmlns:UDF="TallyUDF">
                <LEDGER NAME="{name}" ACTION="Create">
                    <NAME>{name}</NAME>
                    <PARENT>{parent}</PARENT>
                    <ISBILLWISEON>Yes</ISBILLWISEON>
                    <ISPARTY>Yes</ISPARTY>
                    {gstin}
                    {pan}
                    {address_text}
                </LEDGER>
            </TALLYMESSAGE>
        </DATA>
    </BODY>
</ENVELOPE>"""

        result = send_to_tally(xml)

        if result.get('success'):
            frappe.msgprint(_("Customer '{0}' sent to Tally successfully.").format(customer.customer_name))
            return {"success": True, "message": "Customer sent to Tally"}
        else:
            frappe.msgprint(_("Failed to send customer to Tally: {0}").format(result.get('error')))
            return {"success": False, "error": result.get('error')}

    except Exception as e:
        frappe.msgprint(_("Error creating customer in Tally: {0}").format(str(e)))
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def create_supplier_in_tally(supplier_name):
    """Create supplier in Tally"""
    try:
        supplier = frappe.get_doc("Supplier", supplier_name)
        config = get_tally_config()

        name = xml_escape(supplier.supplier_name or supplier.name)
        company = xml_escape(config['tally_company'])
        parent = xml_escape(config['supplier_ledger_parent'])

        # Build address information
        address_text = ""
        if supplier.supplier_primary_address:
            address = frappe.get_doc("Address", supplier.supplier_primary_address)
            address_text = f"""
                    <ADDRESS.LIST>
                        <ADDRESS>{xml_escape(address.address_line1)}</ADDRESS>
                        <CITY>{xml_escape(address.city)}</CITY>
                        <STATE>{xml_escape(address.state)}</STATE>
                        <PINCODE>{xml_escape(address.pincode)}</PINCODE>
                        <COUNTRY>{xml_escape(address.country)}</COUNTRY>
                    </ADDRESS.LIST>"""

        # Build GSTIN if available
        gstin = ""
        if supplier.gstin:
            gstin = f"<GSTIN>{xml_escape(supplier.gstin)}</GSTIN>"

        # Build PAN if available
        pan = ""
        if supplier.pan:
            pan = f"<PAN>{xml_escape(supplier.pan)}</PAN>"

        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<ENVELOPE>
    <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Import</TALLYREQUEST>
        <TYPE>Data</TYPE>
        <ID>All Masters</ID>
    </HEADER>
    <BODY>
        <DESC>
            <STATICVARIABLES>
                <SVCURRENTCOMPANY>{company}</SVCURRENTCOMPANY>
            </STATICVARIABLES>
        </DESC>
        <DATA>
            <TALLYMESSAGE xmlns:UDF="TallyUDF">
                <LEDGER NAME="{name}" ACTION="Create">
                    <NAME>{name}</NAME>
                    <PARENT>{parent}</PARENT>
                    <ISBILLWISEON>Yes</ISBILLWISEON>
                    <ISPARTY>Yes</ISPARTY>
                    {gstin}
                    {pan}
                    {address_text}
                </LEDGER>
            </TALLYMESSAGE>
        </DATA>
    </BODY>
</ENVELOPE>"""

        result = send_to_tally(xml)

        if result.get('success'):
            frappe.msgprint(_("Supplier '{0}' sent to Tally successfully.").format(supplier.supplier_name))
            return {"success": True, "message": "Supplier sent to Tally"}
        else:
            frappe.msgprint(_("Failed to send supplier to Tally: {0}").format(result.get('error')))
            return {"success": False, "error": result.get('error')}

    except Exception as e:
        frappe.msgprint(_("Error creating supplier in Tally: {0}").format(str(e)))
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def create_sales_invoice_in_tally(invoice_name):
    """Create sales invoice in Tally"""
    try:
        invoice = frappe.get_doc("Sales Invoice", invoice_name)
        config = get_tally_config()

        if invoice.docstatus != 1:
            frappe.throw(_("Only submitted invoices can be sent to Tally."))

        company = xml_escape(config['tally_company'])
        voucher_no = xml_escape(invoice.name)
        date = xml_escape(invoice.posting_date.strftime("%Y-%m-%d"))
        ledger_name = xml_escape(invoice.customer)

        # Build ledger entries
        ledger_entries = ""
        for item in invoice.items:
            if item.item_code:
                item_name = xml_escape(item.item_name or item.item_code)
                rate = clean_text(item.rate)
                quantity = clean_text(item.qty)
                amount = clean_text(item.amount)

                ledger_entries += f"""
                    <ALLINVENTORYLIST.LIST>
                        <STOCKITEMNAME>{item_name}</STOCKITEMNAME>
                        <RATE>{rate}</RATE>
                        <QUANTITY>{quantity}</QUANTITY>
                        <AMOUNT>{amount}</AMOUNT>
                    </ALLINVENTORYLIST.LIST>"""

        # Build accounting entries
        accounting_entries = f"""
            <ACCOUNTINGALLOCATIONS.LIST>
                <LEDGERNAME>{xml_escape(config['customer_ledger_parent'])}</LEDGERNAME>
                <AMOUNT>{clean_text(invoice.grand_total)}</AMOUNT>
            </ACCOUNTINGALLOCATIONS.LIST>"""

        # Build tax entries if available
        tax_entries = ""
        for tax in invoice.taxes:
            if tax.tax_amount:
                tax_ledger = xml_escape(tax.account_head)
                tax_amount = clean_text(tax.tax_amount)
                tax_entries += f"""
            <ACCOUNTINGALLOCATIONS.LIST>
                <LEDGERNAME>{tax_ledger}</LEDGERNAME>
                <AMOUNT>{tax_amount}</AMOUNT>
            </ACCOUNTINGALLOCATIONS.LIST>"""

        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<ENVELOPE>
    <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Import</TALLYREQUEST>
        <TYPE>Data</TYPE>
        <ID>Vouchers</ID>
    </HEADER>
    <BODY>
        <DESC>
            <STATICVARIABLES>
                <SVCURRENTCOMPANY>{company}</SVCURRENTCOMPANY>
            </STATICVARIABLES>
        </DESC>
        <DATA>
            <TALLYMESSAGE xmlns:UDF="TallyUDF">
                <VOUCHER ACTION="Create">
                    <VOUCHERTYPENAME>Sales</VOUCHERTYPENAME>
                    <DATE>{date}</DATE>
                    <VOUCHERNO>{voucher_no}</VOUCHERNO>
                    <PARTYLEDGERNAME>{ledger_name}</PARTYLEDGERNAME>
                    <EFFECTIVEDATE>{date}</EFFECTIVEDATE>
                    {ledger_entries}
                    <ALLLEDGERENTRIES.LIST>
                        {accounting_entries}
                        {tax_entries}
                    </ALLLEDGERENTRIES.LIST>
                </VOUCHER>
            </TALLYMESSAGE>
        </DATA>
    </BODY>
</ENVELOPE>"""

        result = send_to_tally(xml)

        if result.get('success'):
            frappe.msgprint(_("Sales Invoice '{0}' sent to Tally successfully.").format(invoice.name))
            return {"success": True, "message": "Sales Invoice sent to Tally"}
        else:
            frappe.msgprint(_("Failed to send Sales Invoice to Tally: {0}").format(result.get('error')))
            return {"success": False, "error": result.get('error')}

    except Exception as e:
        frappe.msgprint(_("Error creating Sales Invoice in Tally: {0}").format(str(e)))
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def create_purchase_invoice_in_tally(invoice_name):
    """Create purchase invoice in Tally"""
    try:
        invoice = frappe.get_doc("Purchase Invoice", invoice_name)
        config = get_tally_config()

        if invoice.docstatus != 1:
            frappe.throw(_("Only submitted invoices can be sent to Tally."))

        company = xml_escape(config['tally_company'])
        voucher_no = xml_escape(invoice.name)
        date = xml_escape(invoice.posting_date.strftime("%Y-%m-%d"))
        ledger_name = xml_escape(invoice.supplier)

        # Build ledger entries
        ledger_entries = ""
        for item in invoice.items:
            if item.item_code:
                item_name = xml_escape(item.item_name or item.item_code)
                rate = clean_text(item.rate)
                quantity = clean_text(item.qty)
                amount = clean_text(item.amount)

                ledger_entries += f"""
                    <ALLINVENTORYLIST.LIST>
                        <STOCKITEMNAME>{item_name}</STOCKITEMNAME>
                        <RATE>{rate}</RATE>
                        <QUANTITY>{quantity}</QUANTITY>
                        <AMOUNT>{amount}</AMOUNT>
                    </ALLINVENTORYLIST.LIST>"""

        # Build accounting entries
        accounting_entries = f"""
            <ACCOUNTINGALLOCATIONS.LIST>
                <LEDGERNAME>{xml_escape(config['supplier_ledger_parent'])}</LEDGERNAME>
                <AMOUNT>{clean_text(invoice.grand_total)}</AMOUNT>
            </ACCOUNTINGALLOCATIONS.LIST>"""

        # Build tax entries if available
        tax_entries = ""
        for tax in invoice.taxes:
            if tax.tax_amount:
                tax_ledger = xml_escape(tax.account_head)
                tax_amount = clean_text(tax.tax_amount)
                tax_entries += f"""
            <ACCOUNTINGALLOCATIONS.LIST>
                <LEDGERNAME>{tax_ledger}</LEDGERNAME>
                <AMOUNT>{tax_amount}</AMOUNT>
            </ACCOUNTINGALLOCATIONS.LIST>"""

        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<ENVELOPE>
    <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Import</TALLYREQUEST>
        <TYPE>Data</TYPE>
        <ID>Vouchers</ID>
    </HEADER>
    <BODY>
        <DESC>
            <STATICVARIABLES>
                <SVCURRENTCOMPANY>{company}</SVCURRENTCOMPANY>
            </STATICVARIABLES>
        </DESC>
        <DATA>
            <TALLYMESSAGE xmlns:UDF="TallyUDF">
                <VOUCHER ACTION="Create">
                    <VOUCHERTYPENAME>Purchase</VOUCHERTYPENAME>
                    <DATE>{date}</DATE>
                    <VOUCHERNO>{voucher_no}</VOUCHERNO>
                    <PARTYLEDGERNAME>{ledger_name}</PARTYLEDGERNAME>
                    <EFFECTIVEDATE>{date}</EFFECTIVEDATE>
                    {ledger_entries}
                    <ALLLEDGERENTRIES.LIST>
                        {accounting_entries}
                        {tax_entries}
                    </ALLLEDGERENTRIES.LIST>
                </VOUCHER>
            </TALLYMESSAGE>
        </DATA>
    </BODY>
</ENVELOPE>"""

        result = send_to_tally(xml)

        if result.get('success'):
            frappe.msgprint(_("Purchase Invoice '{0}' sent to Tally successfully.").format(invoice.name))
            return {"success": True, "message": "Purchase Invoice sent to Tally"}
        else:
            frappe.msgprint(_("Failed to send Purchase Invoice to Tally: {0}").format(result.get('error')))
            return {"success": False, "error": result.get('error')}

    except Exception as e:
        frappe.msgprint(_("Error creating Purchase Invoice in Tally: {0}").format(str(e)))
        return {"success": False, "error": str(e)}
