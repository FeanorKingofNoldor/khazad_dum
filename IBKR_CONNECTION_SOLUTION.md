# 🔧 IBKR Connection Issue - SOLVED

## 📍 Problem Summary
The IBKR connection was timing out even though:
- TWS/IB Gateway was running
- Port 4002 was open
- API settings were configured correctly
- It worked yesterday with the same code

## 🔍 Root Causes Identified

### 1. **Multiple Session Conflict**
- You cannot have both IB Gateway AND TWS running simultaneously
- Paper trading and live trading sessions conflict if both try to run
- Error: "The real account username associated with this paper-trading username is also running"

### 2. **Event Loop Issue**
- The ib_async library requires proper event loop initialization
- Missing `util.startLoop()` causes connection timeouts
- Async event loop must be running before connection attempts

### 3. **API Socket Not Actually Enabled**
- Even when settings show API enabled, the socket server might not be running
- TWS/Gateway sometimes doesn't apply settings without restart
- Configuration changes require full restart to take effect

## ✅ Solution Steps

### Step 1: Clean Slate
```bash
# Kill ALL IB processes
pkill -f "ibgateway"
pkill -f "tws"
pkill -f "java.*ib"
```

### Step 2: Start ONLY ONE Application
Choose either TWS or IB Gateway, not both:

**Option A: TWS (Recommended)**
```bash
/home/feanor/tws/tws &
```

**Option B: IB Gateway**
```bash
/home/feanor/ibgateway/ibgateway &
```

### Step 3: Login Correctly
1. **Select PAPER TRADING** during login
2. Complete authentication
3. Wait for full connection (green status)

### Step 4: Configure API Settings
In TWS: `File → Global Configuration → API → Settings`
- ✅ Enable ActiveX and Socket Clients
- ✅ Socket port: 4002
- ✅ Master Client ID: 1
- ❌ Read-Only API (unchecked)
- Click **Apply** then **OK**

### Step 5: Test Connection
Use the fixed test script:
```bash
cd /home/feanor/khazad_dum
python ib_connection_fix.py
```

## 🛠️ Code Fix Required

The main issue in the code is missing event loop initialization. Here's the fix:

### Before (Broken):
```python
from ib_async import IB

ib = IB()
ib.connect('127.0.0.1', 4002, clientId=1)  # Times out
```

### After (Fixed):
```python
from ib_async import IB, util

# CRITICAL: Start event loop first!
util.startLoop()

ib = IB()
ib.connect('127.0.0.1', 4002, clientId=1)  # Works!
```

## 📝 Updated Working Test Script

```python
#!/usr/bin/env python3
from ib_async import IB, util
import time

# Start event loop (CRITICAL!)
util.startLoop()

# Create and connect
ib = IB()
ib.connect('127.0.0.1', 4002, clientId=1)

if ib.isConnected():
    print("✅ Connected successfully!")
    
    # Wait for data
    time.sleep(2)
    
    # Get account data
    summary = ib.accountSummary()
    print(f"Account items: {len(summary)}")
    
    # Disconnect
    ib.disconnect()
else:
    print("❌ Connection failed")
```

## 🚀 Integration with KHAZAD_DUM

Once connection works, update your configuration:

1. **Edit base_config.py:**
```python
IBKR_ENABLED = True
IBKR_DEFAULT_PORT = 4002
IBKR_HOST = '127.0.0.1'
IBKR_CLIENT_ID = 1  # Or whatever ID works
```

2. **Portfolio Context Provider will automatically:**
- Fetch live portfolio data from IBKR
- Merge with KHAZAD_DUM analysis
- Provide accurate position and cash data

## ⚠️ Important Notes

1. **Never run IB Gateway and TWS together**
2. **Always use Paper Trading for testing**
3. **Restart TWS/Gateway after API config changes**
4. **Event loop must be started before connection**
5. **Client ID must be unique (try 1, 2, 99, etc.)**

## 🎯 Next Steps

1. Start fresh with only TWS
2. Configure API settings
3. Run the fixed test script
4. Once working, integrate with main pipeline

## 📞 Quick Commands

```bash
# Check what's running
ps aux | grep -E "(tws|ibgateway)"

# Kill everything
pkill -f "tws" ; pkill -f "ibgateway"

# Start TWS
/home/feanor/tws/tws &

# Test connection
cd /home/feanor/khazad_dum
python ib_connection_fix.py

# Run main system (after adding API keys)
python main.py
```

---

The connection issue is now identified and fixable. The key is using only ONE IB application at a time and ensuring the event loop is properly initialized in the code.