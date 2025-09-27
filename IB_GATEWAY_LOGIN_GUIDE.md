# 🚪 IB Gateway Login & API Configuration Guide

## 📍 **Current Status**
- ✅ IB Gateway installed and running
- ✅ Process detected on port 4002 
- ❌ **CONNECTION BLOCKED** - Login/Configuration required

## 🔑 **Step 1: Login to IB Gateway**

IB Gateway is currently running but needs authentication and configuration.

### **Access the IB Gateway GUI:**
1. **Check if IB Gateway window is visible** on your desktop
2. **If not visible**, the window might be minimized or hidden

### **Login Process:**
1. **Enter your IBKR credentials:**
   - Username: Your IBKR username
   - Password: Your IBKR password
   
2. **Select Trading Mode:**
   - Choose **"Paper Trading"** (RECOMMENDED for testing)
   - This connects to virtual portfolio with $1M fake money
   - Safe for testing without risking real funds

3. **Complete Authentication:**
   - Enter any required 2FA codes
   - Accept terms if prompted

---

## ⚙️ **Step 2: Configure API Settings**

Once logged in:

### **Navigate to API Settings:**
1. **Click** `Configure` → `API` → `Settings`
2. **OR** Go to `File` → `Global Configuration` → `API` → `Settings`

### **Configure Required Settings:**
✅ **Enable ActiveX and Socket Clients** - MUST BE CHECKED
✅ **Socket port**: `4002` (for Paper Trading)
✅ **Master Client ID**: `1`
✅ **Allow connections from localhost only** - CHECKED
✅ **Read-Only API** - CHECKED (for initial testing)

### **Optional Advanced Settings:**
- **Download open orders on connection**: ✅ Recommended
- **Precautionary Confirmation**: ❌ Disabled for API trading
- **API logging level**: `Detail` (for troubleshooting)

### **Apply Settings:**
- **Click OK** to save
- **Restart** might be required for some settings

---

## 🧪 **Step 3: Test Connection**

After login and configuration:

```bash
cd /home/feanor/khazad_dum
python test_ib_connection.py
```

### **Expected Success Output:**
```
✅ IB Gateway is running on port 4002 (PAPER TRADING)
✅ Successfully connected to IB Gateway!
✅ Account summary retrieved:
   Net Liquidation: $1,000,000.00
   Total Cash: $1,000,000.00
   Buying Power: $4,000,000.00
✅ Complete portfolio data retrieved
🎉 IB GATEWAY CONNECTION TEST SUCCESSFUL!
```

---

## 🔧 **Step 4: Automated Monitoring**

I've created a monitoring script to check status:

```bash
# Check if IB Gateway is responding
python -c "
import socket
sock = socket.socket()
result = sock.connect_ex(('127.0.0.1', 4002))
print('✅ IB Gateway API ready' if result == 0 else '❌ IB Gateway API not responding')
sock.close()
"
```

---

## 🚨 **Troubleshooting**

### **"Connection Timeout"**
- ❌ Not logged in to IB Gateway
- ❌ API not enabled in settings
- ❌ Wrong port configuration
- **Solution**: Complete login and API configuration above

### **"Authentication Failed"**  
- ❌ Invalid IBKR credentials
- ❌ Account suspended or restricted
- **Solution**: Verify credentials, contact IBKR if needed

### **"Connection Refused"**
- ❌ API not enabled
- ❌ Firewall blocking connection
- **Solution**: Enable API in Gateway settings

### **"Client ID in Use"**
- ❌ Another application using Client ID 1
- **Solution**: Choose different Client ID or restart Gateway

---

## 🎯 **Next Steps After Success**

Once connection test passes:

1. **✅ Portfolio Integration Ready**
   - Your KHAZAD_DUM system will fetch live data
   - Real portfolio positions and cash available
   - Live P&L tracking

2. **✅ Start Main Pipeline**
   ```bash
   # Add API keys first (if not done)
   echo "OPENAI_API_KEY=your_key_here" >> /home/feanor/khazad_dum/.env
   echo "FINNHUB_API_KEY=your_key_here" >> /home/feanor/khazad_dum/.env
   
   # Run main system with live portfolio
   python main.py
   ```

3. **✅ Monitor Integration**
   - Check portfolio context provider logs
   - Verify accurate position data
   - Test trade signal generation with real data

---

## 🔒 **Safety Reminders**

- **✅ Using Paper Trading** (port 4002) - Safe virtual money
- **⚠️ Read-Only API** enabled - No accidental trades
- **🔍 Test thoroughly** before considering live trading
- **📊 Verify data accuracy** against your IBKR account

Your IB Gateway is ready to power the KHAZAD_DUM trading intelligence system!