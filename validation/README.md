# Company Validation Scripts

Automated scripts for validating company information using Selenium WebDriver.

## Scripts

### 1. GST Validation (`gst.py`)

Fetches GST business details from gstsearch.in

### 2. MCA Validation (`mca.py`)

Fetches company details from zaubacorp.com using CIN (Corporate Identification Number)

## Setup

### Prerequisites

1. **Python 3.7+**
2. **Chrome Browser** (latest version)
3. **ChromeDriver** (matching your Chrome version)

### Installation

```bash
# Install required packages
pip install selenium beautifulsoup4

# Make sure ChromeDriver is in your system PATH
# Or set CHROMEDRIVER_PATH environment variable
```

### ChromeDriver Setup

**Option 1: Add to PATH (Recommended)**

- Download ChromeDriver from https://chromedriver.chromium.org/
- Add the directory containing chromedriver.exe to your system PATH

**Option 2: Set Environment Variable**

```bash
# Windows
set CHROMEDRIVER_PATH=C:\path\to\chromedriver.exe

# Linux/Mac
export CHROMEDRIVER_PATH=/path/to/chromedriver
```

## Usage

### GST Validation

```bash
# Basic usage
python gst.py 33AAACZ4322M1ZA

# Headless mode (no browser window)
python gst.py 33AAACZ4322M1ZA --headless

# With custom ChromeDriver path
set CHROMEDRIVER_PATH=C:\path\to\chromedriver.exe
python gst.py 33AAACZ4322M1ZA
```

**Output:**

```json
{
  "source": "gstsearch.in",
  "gstin": "33AAACZ4322M1ZA",
  "data": {
    "legal_name": "COMPANY NAME",
    "trade_name": "TRADE NAME",
    "gstin_status": "Active",
    ...
  }
}
```

### MCA Validation

```bash
# Basic usage
python mca.py U72900KA2018PTC123456

# Headless mode
python mca.py U72900KA2018PTC123456 --headless

# With custom ChromeDriver path
set CHROMEDRIVER_PATH=C:\path\to\chromedriver.exe
python mca.py U72900KA2018PTC123456
```

**Output:**

```json
{
  "source": "zaubacorp.com",
  "cin": "U72900KA2018PTC123456",
  "data": {
    "Company Name": "COMPANY NAME",
    "CIN": "U72900KA2018PTC123456",
    "Company Status": "Active",
    "ROC": "RoC-Karnataka",
    "Registration Number": "123456",
    "Company Category": "Company limited by Shares",
    "Company SubCategory": "Non-govt company",
    "Class of Company": "Private",
    "Date of Incorporation": "01-Jan-2018",
    "Age of Company": "6 years",
    "Activity": {
      "NIC Code": "72900",
      "NIC Description": "Other information technology service activities"
    },
    "Number of Members": "2",
    "Authorised Capital": "₹ 1,00,000",
    "Paid up capital": "₹ 1,00,000",
    "Email Id": "email@example.com",
    "Registered Address": "Full address here"
  }
}
```

## Features

### Common Features (Both Scripts)

✅ **Human-like Behavior**

- Random typing delays
- Realistic browser fingerprint
- Anti-bot detection measures

✅ **Robust Error Handling**

- Network errors
- Timeout handling
- Invalid input validation
- Detailed error messages

✅ **Flexible ChromeDriver**

- Uses system PATH by default
- Supports custom ChromeDriver path
- No dependency on webdriver-manager

✅ **JSON Output**

- Structured, parseable output
- Suitable for piping to other tools
- Easy integration with APIs

### GST Script Features

- Validates GSTIN format (15 characters)
- Extracts all available GST details
- Normalizes field names to snake_case

### MCA Script Features

- Validates CIN format (21 characters)
- Extracts comprehensive company details
- Handles nested data (NIC Code, Description)
- Parses financial information

## Validation Patterns

### GSTIN Format

```
Pattern: ^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$
Example: 33AAACZ4322M1ZA
Length: 15 characters
```

### CIN Format

```
Pattern: ^[LU]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}$
Example: U72900KA2018PTC123456
Length: 21 characters
```

## Error Handling

Both scripts return structured error responses:

```json
{
  "source": "gstsearch.in",
  "gstin": "INVALID123",
  "error": {
    "type": "INVALID_GSTIN",
    "message": "Invalid GSTIN format. Expected pattern: ..."
  }
}
```

**Error Types:**

- `INVALID_GSTIN` / `INVALID_CIN` - Invalid format
- `NOT_FOUND` - No record found
- `NETWORK_ERROR` - Connection issues
- `PARSE_ERROR` - Failed to extract data
- `TIMEOUT` - Request timeout

## Troubleshooting

### ChromeDriver Version Mismatch

**Error:** `This version of ChromeDriver only supports Chrome version X`

**Solution:**

1. Check your Chrome version: `chrome://version`
2. Download matching ChromeDriver from https://chromedriver.chromium.org/
3. Replace your existing ChromeDriver

### ChromeDriver Not Found

**Error:** `chromedriver.exe not found`

**Solution:**

```bash
# Option 1: Add to PATH
# Add ChromeDriver directory to system PATH

# Option 2: Set environment variable
set CHROMEDRIVER_PATH=C:\full\path\to\chromedriver.exe
```

### Timeout Errors

**Error:** `Results table did not load within timeout period`

**Solution:**

- Check your internet connection
- Try running without `--headless` flag
- Increase timeout in the code if needed

### No Data Extracted

**Error:** `No data extracted from table`

**Possible Causes:**

- Website structure changed
- Invalid GSTIN/CIN
- Network issues
- Bot detection

**Solution:**

- Verify the GSTIN/CIN is correct
- Try running without `--headless`
- Check if the website is accessible

## Integration with Backend

These scripts can be integrated into your backend API:

```python
import subprocess
import json

def validate_gst(gstin):
    result = subprocess.run(
        ['python', 'gst.py', gstin, '--headless'],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

def validate_cin(cin):
    result = subprocess.run(
        ['python', 'mca.py', cin, '--headless'],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)
```

## Performance

- **GST Validation:** ~5-10 seconds
- **MCA Validation:** ~5-10 seconds

Times may vary based on:

- Network speed
- Website response time
- Headless vs headed mode

## Notes

- Both scripts use Selenium for reliability
- Headless mode is faster but may be less reliable
- Scripts respect website rate limits
- Use responsibly and comply with website terms of service

## Support

For issues or questions:

1. Check ChromeDriver version matches Chrome
2. Verify input format (GSTIN/CIN)
3. Try without `--headless` flag
4. Check error messages in JSON output
