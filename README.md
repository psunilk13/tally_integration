# Tally Integration for ERPNext

A Frappe custom app that integrates ERPNext with Tally accounting software. This app allows you to send Customers, Suppliers, Sales Invoices, and Purchase Invoices from ERPNext to Tally with a single click.

## Features

- **Customer Integration**: Send customer data to Tally as Sundry Debtors ledger
- **Supplier Integration**: Send supplier data to Tally as Sundry Creditors ledger
- **Sales Invoice Integration**: Send sales invoices to Tally
- **Purchase Invoice Integration**: Send purchase invoices to Tally
- **Easy Configuration**: Simple configuration for Tally URL, port, and company name
- **One-Click Sync**: "Create in Tally" button on Customer, Supplier, Sales Invoice, and Purchase Invoice forms

## Requirements

- ERPNext version 13+
- Frappe Framework version 13+
- Python 3.6+
- Tally Prime or Tally.ERP 9 installed on a network-accessible system
- Tally ODBC/HTTP integration enabled

## Installation

### Step 1: Copy the App to Your Bench

Copy the `tally_integration` folder to your Frappe bench's `apps` directory:

```bash
# Assuming your bench is at ~/frappe-bench
cp -r tally_integration ~/frappe-bench/apps/
```

### Step 2: Install the App

Navigate to your bench directory and install the app:

```bash
cd ~/frappe-bench
bench get-app tally_integration
# Or if already copied
bench install-app tally_integration
```

### Step 3: Build and Restart

```bash
bench build
bench restart
```

### Step 4: Install on Your Site

```bash
bench --site [your-site-name] install-app tally_integration
```

Replace `[your-site-name]` with your actual site name.

## Configuration

After installation:

1. Go to **Tally Integration** > **Tally Configuration** in your ERPNext desk
2. Fill in the following fields:
   - **Tally URL**: The IP address or hostname of the system where the Tally receiver script is running (e.g., `http://192.168.1.100`)
   - **Tally Port**: The port where the Tally receiver script is listening (default: `8000`)
   - **Tally Company Name**: The exact company name as it appears in Tally
   - **Customer Ledger Parent**: Parent ledger for customers (default: `Sundry Debtors`)
   - **Supplier Ledger Parent**: Parent ledger for suppliers (default: `Sundry Creditors`)
3. Check the **Enabled** checkbox to activate the integration
4. Click **Test Connection** to verify connectivity with the Tally receiver

## Usage

### Creating Customer in Tally

1. Create or open a Customer in ERPNext
2. Submit the customer (docstatus must be 1)
3. Click the **Create in Tally** button in the Actions menu
4. The customer will be sent to Tally as a ledger under the configured parent ledger

### Creating Supplier in Tally

1. Create or open a Supplier in ERPNext
2. Submit the supplier (docstatus must be 1)
3. Click the **Create in Tally** button in the Actions menu
4. The supplier will be sent to Tally as a ledger under the configured parent ledger

### Creating Sales Invoice in Tally

1. Create and submit a Sales Invoice in ERPNext
2. Click the **Create in Tally** button in the Actions menu
3. The invoice will be sent to Tally as a Sales voucher

### Creating Purchase Invoice in Tally

1. Create and submit a Purchase Invoice in ERPNext
2. Click the **Create in Tally** button in the Actions menu
3. The invoice will be sent to Tally as a Purchase voucher

## Tally PC Setup

On the system where Tally is installed, you need to set up a receiver script to accept data from ERPNext and forward it to Tally. The architecture works as follows:

```
ERPNext → Receiver Script (Port 8000) → Tally (Port 9000)
```

See the `TALLY_PC_SETUP.md` file for detailed instructions on setting up the receiver script.

**Important**: The Tally URL/Port in ERPNext Configuration should point to the receiver script (default port 8000), not directly to Tally (port 9000).

## Troubleshooting

### Connection Failed

- Ensure Tally is running on the target system
- Verify the Tally URL and port are correct
- Check firewall settings to allow the port
- Ensure Tally ODBC/HTTP integration is enabled in Tally configuration

### Company Name Not Found

- The company name in Tally Configuration must match exactly with the company name in Tally
- Check for extra spaces or spelling differences

### Ledger Already Exists

- If a ledger already exists in Tally, Tally will update it instead of creating a new one
- This is normal behavior

## API Endpoints

The app provides the following whitelisted API methods:

- `tally_integration.api.tally_api.create_customer_in_tally`
- `tally_integration.api.tally_api.create_supplier_in_tally`
- `tally_integration.api.tally_api.create_sales_invoice_in_tally`
- `tally_integration.api.tally_api.create_purchase_invoice_in_tally`
- `tally_integration.doctype.tally_configuration.tally_configuration.get_tally_config`

## License

MIT License

## Support

For issues and questions, please refer to the Frappe/ERPNext community forums.
