# VDR with Individual SQL Environment Variables

## 🎯 **Cleaner Configuration Like Your Other Project**

This version uses **individual SQL environment variables** instead of one long DATABASE_URL string, just like your other successful Railway project!

## ✅ **Advantages of Individual Variables:**

- **🔧 Easier to manage** - Each setting separate
- **🔒 More secure** - Can hide/show individual values
- **🚀 Consistent** - Same pattern as your other project
- **🛠️ Flexible** - Easy to change individual settings
- **📝 Readable** - Clear what each variable does

## 🔧 **Railway Environment Variables Setup:**

### **Required Variables (Same as Your Other Project):**

Add these **5 variables** in Railway Dashboard → Variables:

| Variable Name | Value | Description |
|---------------|-------|-------------|
| `SQL_SERVER` | `skapaserver.database.windows.net` | Azure SQL Server |
| `SQL_DATABASE` | `VDR` | Database name |
| `SQL_USER` | `CloudSA65310c01` | SQL username |
| `SQL_PASSWORD` | `SK2050885Ronde!` | Your SQL password |
| `SQL_PORT` | `1433` | SQL Server port |

## 🚀 **Railway Setup Steps:**

### **1. Upload Code to GitHub:**
```bash
git add .
git commit -m "VDR with individual SQL variables"
git push origin main
```

### **2. Remove Old DATABASE_URL:**
1. **Railway Dashboard** → your VDR project
2. **Variables tab**
3. **Delete** the old `DATABASE_URL` variable (if exists)

### **3. Add Individual Variables:**
**For each variable, click "New Variable":**

**Variable 1:**
- **Name:** `SQL_SERVER`
- **Value:** `skapaserver.database.windows.net`

**Variable 2:**
- **Name:** `SQL_DATABASE`  
- **Value:** `VDR`

**Variable 3:**
- **Name:** `SQL_USER`
- **Value:** `CloudSA65310c01`

**Variable 4:**
- **Name:** `SQL_PASSWORD`
- **Value:** `SK2050885Ronde!`

**Variable 5:**
- **Name:** `SQL_PORT`
- **Value:** `1433`

### **4. Save and Deploy:**
- **Save** all variables
- Railway will **automatically redeploy**
- **Check logs** for successful connection

## 🎯 **Expected Result:**

After setup, Railway logs will show:
```
✅ Flask app 'main'
✅ SQL Server connection established
✅ Database tables created
✅ Running on all addresses (0.0.0.0)
```

## 🔒 **Security Benefits:**

- **Individual control** - Hide/show specific variables
- **No long connection strings** - Cleaner and more secure
- **Easy password rotation** - Change only SQL_PASSWORD
- **Consistent pattern** - Same as your other project

## 🏆 **Code Logic:**

The VDR now checks for variables in this order:
1. **Individual SQL variables** (preferred)
2. **DATABASE_URL** (fallback)
3. **In-memory SQLite** (development)

```python
# Priority 1: Individual variables (like your other project)
server = os.environ.get('SQL_SERVER')
database = os.environ.get('SQL_DATABASE') 
username = os.environ.get('SQL_USER')
password = os.environ.get('SQL_PASSWORD')

# Build connection string
mssql+pymssql://username:password@server:port/database
```

## ✅ **Full Functionality:**

With individual SQL variables, your VDR gets:
- ✅ **Persistent Azure SQL storage**
- ✅ **File uploads enabled**
- ✅ **User accounts permanent**
- ✅ **Q&A system persistent**
- ✅ **Folder structure maintained**
- ✅ **No data loss on restart**

## 🎉 **Result:**

Your VDR will have the **same clean variable structure** as your other successful Railway project, with full Azure SQL functionality!

**This approach is proven to work - just like your other project!** 🚀

---

## 🔧 **Troubleshooting:**

**If connection fails:**
1. Verify all 5 variables are set correctly
2. Check Azure SQL firewall allows Railway
3. Test individual variable values
4. Check Railway logs for specific errors

**Variables should match exactly:**
- `SQL_SERVER`: skapaserver.database.windows.net
- `SQL_DATABASE`: VDR  
- `SQL_USER`: CloudSA65310c01
- `SQL_PASSWORD`: SK2050885Ronde!
- `SQL_PORT`: 1433

