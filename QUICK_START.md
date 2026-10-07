# Quick Start Guide - Tally Integration for ERPNext

This is a quick reference guide to get Tally Integration up and running quickly.

## Architecture Overview

```
┌─────────────┐         ┌──────────────────┐         ┌──────────┐
│  ERPNext    │  HTTP   │  Tally Receiver  │  HTTP   │  Tally   │
│  (Ubuntu)   │ ──────> │  (Windows PC)    │ ──────> │  Prime   │
└─────────────┘  Port   │  Port 8000       │  Port   │  Port    │
                 8000    └──────────────────┘  9000    └──────────┘
```

## Part 1: ERPNext Setup (Ubuntu/WSL)

### 1. Copy the App to Your Bench

```bash
# From Windows
wsl bash -c "cp -r /mnt/d/HC/tally_integration ~/frappe-dev/frappe-bench/apps/"

# Or from within WSL
cd ~/frappe-dev/frappe-bench/apps
cp -r /mnt/d/HC/tally_integration .
```

### 2. Install Dependencies

```bash
cd ~/frappe-dev/frappe-bench
source env/bin/activate
pip install -r apps/tally_integration/requirements.txt
```

### 3. Build and Restart

```bash
bench build
bench restart
```

### 4. Install on Your Site

```bash
# Replace with your actual site name
bench --site [your-site-name] install-app tally_integration
```

### 5. Configure in ERPNext

1. Login to ERPNext as Administrator
2. Go to **Tally Integration** > **Tally Configuration**
3. Fill in:
   - **Tally URL**: `http://[TALLY-PC-IP]` (e.g., `http://192.168.1.100`)
   - **Tally Port**: `8000` (receiver script port)
   - **Tally Company Name**: Exact company name from Tally
   - **Customer Ledger Parent**: `Sundry Debtors`
   - **Supplier Ledger Parent**: `Sundry Creditors`
4. Check **Enabled**
5. Click **Test Connection**

## Part 2: Tally PC Setup (Windows)

### 1. Enable Tally HTTP Integration

1. Open Tally
2. Go to **Gateway of Tally** > **F12: Configure**
3. Navigate to **Local Configuration** > **Odbc/Ie Integration**
4. Enable **Enable ODBC** and **Enable Browser Services**
5. Set **Port** to `9000`
6. Save and restart Tally

### 2. Setup Receiver Script

1. Copy `tally_receiver.py` from the app folder to your Tally PC
2. Edit the configuration section:
   ```python
   RECEIVER_HOST = "0.0.0.0"
   RECEIVER_PORT = 8000
   TALLY_URL = "http://127.0.0.1:9000"
   TALLY_COMPANY = "Your Company Name"  # Change this!
   ```
3. Run the script:
   ```bash
   python tally_receiver.py
   ```

### 3. Configure Windows Firewall

Allow Python through Windows Firewall or create a rule for port 8000:
```powershell
New-NetFirewallRule -DisplayName "Tally Receiver" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

### 4. Test the Receiver

Open a browser on another computer:
```
http://[TALLY-PC-IP]:8000/
```

You should see a JSON response with status "running".

## Usage

### Send Customer to Tally

1. Create a Customer in ERPNext
2. Submit it
3. Click **Create in Tally** button in Actions menu

### Send Supplier to Tally

1. Create a Supplier in ERPNext
2. Submit it
3. Click **Create in Tally** button in Actions menu

### Send Sales Invoice to Tally

1. Create and submit a Sales Invoice
2. Click **Create in Tally** button in Actions menu

### Send Purchase Invoice to Tally

1. Create and submit a Purchase Invoice
2. Click **Create in Tally** button in Actions menu

## Common Issues

### Connection Failed

- Check if receiver script is running on Tally PC
- Verify IP address is correct
- Check Windows Firewall settings
- Ensure both systems are on the same network

### Company Name Not Found

- Company name must match exactly in Tally
- Check for extra spaces or spelling differences

### Port Already in Use

- Change RECEIVER_PORT in the script (e.g., to 8001)
- Update the port in ERPNext Tally Configuration

## Files Reference

- `README.md` - Full documentation
- `INSTALLATION_GUIDE.md` - Detailed installation steps
- `TALLY_PC_SETUP.md` - Tally PC setup details
- `tally_receiver.py` - Receiver script for Tally PC

## Support

For detailed troubleshooting, refer to the full documentation files included in the app.
