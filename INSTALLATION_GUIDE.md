# Installation Guide for Tally Integration App

This guide provides step-by-step instructions for installing the Tally Integration app in your ERPNext environment.

## Prerequisites

- ERPNext version 13 or higher
- Frappe Framework version 13 or higher
- Python 3.6 or higher
- Access to your Frappe bench directory

## Method 1: Installation via Bench (Recommended)

If you have the `bench` command available:

### Step 1: Copy the App to Your Bench

```bash
# Navigate to your bench directory
cd ~/frappe-bench

# Copy the tally_integration app to the apps directory
cp -r /path/to/tally_integration apps/
```

### Step 2: Install the App

```bash
# Install the app
bench install-app tally_integration

# Build the app
bench build

# Restart the bench
bench restart
```

### Step 3: Install on Your Site

```bash
# Replace [your-site-name] with your actual site name
bench --site [your-site-name] install-app tally_integration
```

## Method 2: Manual Installation

If you don't have the bench command available or prefer manual installation:

### Step 1: Copy the App

```bash
# Copy the app to your bench's apps directory
cp -r /path/to/tally_integration ~/frappe-bench/apps/
```

### Step 2: Install Dependencies

```bash
cd ~/frappe-bench
source env/bin/activate
pip install -r apps/tally_integration/requirements.txt
```

### Step 3: Run Bench Commands

```bash
# Build assets
bench build

# Restart services
bench restart
```

### Step 4: Install via ERPNext UI

1. Open your ERPNext site in a browser
2. Login as Administrator
3. Go to **Apps** > **Get Apps**
4. Search for "tally_integration"
5. Click **Install**
6. Or run from command line:
   ```bash
   bench --site [your-site-name] install-app tally_integration
   ```

## Method 3: Direct Database Installation (Advanced)

For advanced users who want to directly add the app to the database:

### Step 1: Copy the App

```bash
cp -r /path/to/tally_integration ~/frappe-bench/apps/
```

### Step 2: Add to sites/apps.txt

```bash
cd ~/frappe-bench
echo "tally_integration" >> sites/apps.txt
```

### Step 3: Run Bench Commands

```bash
bench build
bench restart
```

### Step 4: Migrate the App

```bash
bench --site [your-site-name] migrate
```

## Verification

After installation, verify the app is installed correctly:

1. Go to **Home** > **Tally Integration** in your ERPNext desk
2. You should see **Tally Configuration** in the menu
3. Open **Tally Configuration** and configure your Tally settings

## Troubleshooting

### App Not Showing in Menu

If the app doesn't appear in the menu:

1. Clear cache:
   ```bash
   bench --site [your-site-name] clear-cache
   ```

2. Restart bench:
   ```bash
   bench restart
   ```

3. Check if the app is installed:
   ```bash
   bench --site [your-site-name] list-apps
   ```

### Build Errors

If you encounter build errors:

1. Ensure Node.js and npm are installed
2. Run:
   ```bash
   bench build --app tally_integration
   ```

### Permission Errors

If you encounter permission errors:

```bash
# Fix permissions
cd ~/frappe-bench
sudo chown -R $USER:$USER apps/tally_integration
```

## Next Steps

After successful installation:

1. Configure the Tally Integration settings
2. Set up the Tally receiver script on your Tally PC (see TALLY_PC_SETUP.md)
3. Test the connection
4. Start using the integration

## Support

For issues or questions:
- Check the README.md for common issues
- Refer to TALLY_PC_SETUP.md for Tally PC setup
- Visit the Frappe/ERPNext community forums
