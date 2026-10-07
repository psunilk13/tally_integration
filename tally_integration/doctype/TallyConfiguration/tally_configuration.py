import frappe
from frappe import _
import requests
from requests.exceptions import RequestException


def test_connection(doc):
    """Test connection to Tally server"""
    try:
        tally_url = f"{doc.tally_url}:{doc.tally_port}"
        frappe.msgprint(_("Testing connection to {0}...").format(tally_url))

        # Simple test request to Tally
        test_xml = """<?xml version="1.0" encoding="UTF-8"?>
<ENVELOPE>
    <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Data</TYPE>
        <ID>All Masters</ID>
    </HEADER>
    <BODY>
        <DESC>
            <STATICVARIABLES>
                <SVCURRENTCOMPANY>{0}</SVCURRENTCOMPANY>
            </STATICVARIABLES>
        </DESC>
    </BODY>
</ENVELOPE>""".format(doc.tally_company)

        response = requests.post(
            tally_url,
            data=test_xml.encode('utf-8'),
            headers={
                'Content-Type': 'text/xml; charset=utf-8',
                'Content-Length': str(len(test_xml.encode('utf-8')))
            },
            timeout=10
        )

        if response.status_code == 200:
            frappe.msgprint(_("Connection successful! Tally is responding."))
            return True
        else:
            frappe.msgprint(_("Connection failed. Status code: {0}").format(response.status_code))
            return False

    except RequestException as e:
        frappe.msgprint(_("Connection error: {0}").format(str(e)))
        return False
    except Exception as e:
        frappe.msgprint(_("Error: {0}").format(str(e)))
        return False


@frappe.whitelist()
def get_tally_config():
    """Get Tally configuration"""
    doc = frappe.get_single("Tally Configuration")
    return {
        "tally_url": doc.tally_url,
        "tally_port": doc.tally_port,
        "tally_company": doc.tally_company,
        "enabled": doc.enabled,
        "customer_ledger_parent": doc.customer_ledger_parent,
        "supplier_ledger_parent": doc.supplier_ledger_parent
    }
