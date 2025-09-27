# 🏗️ IB Gateway Setup for KHAZAD_DUM

## 📋 **Current Status**
- ✅ `ib_async` library installed and working
- ✅ KHAZAD_DUM IB integration code ready  
- ✅ Connection test script created
- ⚠️ **IB Gateway not running** (needs to be started)

---

## 🚀 **Step 1: Start IB Gateway**

You need to launch either TWS (Trader Workstation) or IB Gateway:

### **Option A: IB Gateway (Recommended)**
1. **Find IB Gateway executable:**
   ```bash
   # Usually installed at:
   ~/Jts/ibgateway/[version]/ibgateway
   # or
   ~/IBJts/ibgateway/[version]/ibgateway
   ```

2. **Launch IB Gateway:**
   ```bash
   # Navigate to IB Gateway directory and run
   ./ibgateway
   ```

### **Option B: TWS (Trader Workstation)**  
1. Launch TWS from your applications menu
2. Log in with your IBKR credentials

---

## ⚙️ **Step 2: Configure API Settings**

Once IB Gateway/TWS is running:

1. **Go to Configure → API → Settings**
2. **Enable the following:**
   - ✅ **Enable ActiveX and Socket Clients**
   - ✅ **Allow connections from localhost only**
   - ✅ **Read-Only API** (for safety during testing)

3. **Set Socket Port:**
   - **Paper Trading**: `4002` (RECOMMENDED for testing)
   - **Live Trading**: `4001` (use only after thorough testing)

4. **Master Client ID**: `1` (matches KHAZAD_DUM config)

5. **Click OK and Apply**

---

## 🧪 **Step 3: Test Connection**

Once IB Gateway is configured and running:

```bash
cd /home/feanor/khazad_dum
python test_ib_connection.py
```

### **Expected Output:**
```
🔍 Checking if IB Gateway is running...
✅ IB Gateway is running on port 4002 (PAPER TRADING)

🏔️ KHAZAD_DUM IB Gateway Connection Test
============================================================
IB Gateway Configuration:
  Host: 127.0.0.1
  Port: 4002 (PAPER TRADING)
  Client ID: 1
  Enabled: True

1. Testing IB library availability...
✅ ib_async library available

2. Testing connection to IB Gateway...
   Attempting connection to 127.0.0.1:4002...
✅ Successfully connected to IB Gateway!

3. Testing portfolio data retrieval...
✅ Account summary retrieved:
   Net Liquidation: $1,000,000.00
   Total Cash: $1,000,000.00
   Buying Power: $4,000,000.00
   Gross Position Value: $0.00

4. Testing position retrieval...
✅ Found 0 positions:
   No positions found (clean account or paper trading)

5. Testing complete portfolio retrieval...
✅ Complete portfolio data retrieved:
   Portfolio Value: $0.00
   Total Positions: 0
   Total Unrealized P&L: $0.00

✅ Successfully disconnected from IB Gateway

============================================================
🎉 IB GATEWAY CONNECTION TEST SUCCESSFUL!
✅ Your KHAZAD_DUM system can connect to IB Gateway
✅ Portfolio data retrieval is working
✅ Ready for live portfolio integration
```

---

## 🔧 **Step 4: Integration with KHAZAD_DUM**

Once the test passes, your system can fetch live portfolio data:

### **Portfolio Context Provider**
Your system will automatically use IB data when available:
- **Cash available** from IB account
- **Current positions** with real P&L
- **Portfolio value** and risk metrics
- **Live market data** for position tracking

### **Configuration**
In `config/settings/base_config.py`:
```python
IBKR_ENABLED = True           # Master switch
IBKR_DEFAULT_PORT = 4002      # Paper trading (safe)
IBKR_HOST = '127.0.0.1'       # Localhost
IBKR_CLIENT_ID = 1            # Must match IB Gateway
```

---

## 🚨 **Troubleshooting**

### **"No IB Gateway on port 4002"**
- IB Gateway is not running
- Wrong port configuration in IB Gateway
- API not enabled in IB Gateway settings

### **"Connection timeout"**  
- Check firewall settings
- Ensure "localhost" connections allowed
- Restart IB Gateway

### **"Authentication failed"**
- Check IB Gateway login status
- Verify account permissions
- Try restarting IB Gateway

### **"Market data subscription required"**
- Some data requires market data subscriptions
- Portfolio data should work without subscriptions
- Contact IBKR support for data permissions

---

## ⚡ **Quick Commands**

### **Check if IB Gateway is running:**
```bash
python -c "
import socket
sock = socket.socket()
result = sock.connect_ex(('127.0.0.1', 4002))
print('✅ IB Gateway running' if result == 0 else '❌ IB Gateway not running')
sock.close()
"
```

### **Test connection only:**
```bash
python test_ib_connection.py
```

### **Run main pipeline with IB integration:**
```bash
# After adding API keys to .env
python main.py
```

---

## 🎯 **Next Steps After Success**

1. **Add API keys** to `.env` file (OPENAI_API_KEY, FINNHUB_API_KEY)
2. **Test full pipeline** with live portfolio data
3. **Verify position tracking** accuracy  
4. **Switch to live port** (4001) only after thorough testing
5. **Enable order execution** when ready for live trading

---

## 🔒 **Safety Notes**

- **Start with paper trading** (port 4002)
- **Enable Read-Only API** initially  
- **Test thoroughly** before live trading
- **Monitor positions** closely during testing
- **Keep IB Gateway running** during trading hours

Your KHAZAD_DUM system is designed to work safely with IB Gateway for portfolio monitoring and eventual trade execution.