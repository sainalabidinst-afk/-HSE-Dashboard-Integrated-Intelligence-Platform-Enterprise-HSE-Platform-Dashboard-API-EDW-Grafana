# STEP 4 — Authentication & RBAC
## Enterprise HSE Platform: Security & Access Control

**Version:** 1.0  
**Date:** 2026-07-14  
**Status:** Completed

---

## 🎯 Objectives

- Implement enterprise-grade authentication and authorization
- Role-Based Access Control (RBAC) with granular permissions
- Site-level security (automatic data filtering)
- Session management with idle timeout
- Account lockout and password policy
- Audit trail for login history
- Dynamic menu based on permissions

---

## 🏗️ Architecture

```
┌──────────────────────────────┐
│        Browser Dashboard      │
└──────────────┬───────────────┘
               │ JWT
               ▼
┌──────────────────────────────┐
│        FastAPI Auth           │
├──────────────────────────────┤
│ Login                         │
│ Refresh Token                 │
│ Logout                        │
│ Current User                  │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│        RBAC Middleware        │
├──────────────────────────────┤
│ Permission Check              │
│ Site Restriction              │
│ Department Restriction        │
└──────────────┬───────────────┘
               │
               ▼
           Dashboard API
```

---

## 👥 Role Hierarchy

| Role | Hak Akses |
|---|---|
| Super Admin | Semua site & konfigurasi |
| HSE Director | Semua dashboard & analytics |
| Site Manager | Semua data site masing-masing |
| HSE Manager | Semua modul HSE |
| HSE Officer | Input & monitoring |
| Supervisor | PTW, inspeksi, HIRA |
| ICT Admin | Infrastruktur & monitoring sistem |
| Auditor | Read-only + evidence |
| Contractor | Data milik kontraktor sendiri |

---

## 🔐 Permission Matrix

| Modul | Admin | Director | Manager | Officer | Auditor |
|---|---|---|---|---|---|
| Executive Summary | ✅ | ✅ | ✅ | ✅ | ✅ |
| Incident | ✅ | ✅ | ✅ | ✅ | 👁️ |
| PTW | ✅ | ✅ | ✅ | ✅ | 👁️ |
| Training | ✅ | ✅ | ✅ | ✅ | 👁️ |
| Environmental | ✅ | ✅ | ✅ | ✅ | 👁️ |
| Equipment | ✅ | ✅ | ✅ | ✅ | 👁️ |
| Audit | ✅ | ✅ | ✅ | 👁️ | 👁️ |
| User Management | ✅ | ❌ | ❌ | ❌ | ❌ |

---

## 📊 Database Schema

### Security Tables

```sql
-- Users
security_users
  - user_id (PK)
  - email (unique)
  - username
  - full_name
  - password_hash
  - is_active
  - is_locked
  - failed_login_attempts
  - locked_until
  - last_login_at
  - password_changed_at
  - password_expires_at

-- Roles
security_roles
  - role_id (PK)
  - role_name (unique)
  - role_display_name
  - parent_role_id (hierarchy)
  - is_system_role

-- Permissions
security_permissions
  - permission_id (PK)
  - permission_name (unique)
  - module
  - action
  - description

-- Role-Permission Mapping
security_role_permission
  - role_id (FK)
  - permission_id (FK)

-- User-Role Mapping (with site scope)
security_user_role
  - user_role_id (PK)
  - user_id (FK)
  - role_id (FK)
  - site_access
  - department_access
  - contractor_access
  - expires_at

-- Sessions
security_sessions
  - session_id (PK)
  - user_id (FK)
  - ip_address
  - user_agent
  - expires_at
  - is_active

-- Login History (Audit Trail)
security_login_history
  - login_id (PK)
  - user_id (FK)
  - email
  - login_type
  - ip_address
  - login_status
  - failure_reason
  - created_at
```

---

## 🔑 Security Features

### 1. Password Policy
- Minimum 12 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- At least 1 symbol
- Expires every 90 days
- Must change on first login

### 2. Account Lockout
- Max 5 failed login attempts
- Lock account for 15 minutes
- Audit trail of all login attempts

### 3. Session Management
- Access token: 60 minutes
- Refresh token: 7 days
- Idle timeout: 30 minutes
- Absolute timeout: 12 hours
- Session invalidation on logout

### 4. Audit Trail
- All login attempts (success/failed/locked)
- IP address logging
- User agent logging
- Timestamp for all actions

---

## 🚀 API Endpoints

### Authentication
- `POST /api/auth/login` - Login with email/password
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout current session
- `POST /api/auth/logout-all` - Logout all sessions
- `GET /api/auth/me` - Get current user info
- `GET /api/auth/permissions` - Get user permissions
- `GET /api/auth/menu` - Get dynamic menu

### Dashboard (Protected)
- `GET /api/dashboard/summary` - Executive summary
- `GET /api/dashboard/incidents` - Incident analysis
- `GET /api/dashboard/ptw` - PTW summary
- `GET /api/dashboard/training` - Training compliance
- `GET /api/dashboard/environmental` - Environmental data
- `GET /api/dashboard/equipment` - Equipment status
- `GET /api/dashboard/contractor` - Contractor performance
- `GET /api/dashboard/alerts` - Active alerts

---

## 🎨 Dashboard Integration

### Dynamic Menu

The dashboard fetches menu from `/api/auth/menu` and renders based on permissions:

```javascript
// Fetch menu
const menuData = await Auth.fetchMenu();
Auth.renderMenu(menuData);
```

### Permission-Based UI

```javascript
// Check permission before showing action
if (Auth.hasPermission('incident:create')) {
  showCreateButton();
}
```

### Auto Logout on Token Expiry

```javascript
// API client automatically refreshes token
// If refresh fails, dispatches auth:logout event
window.addEventListener('auth:logout', () => {
  window.location.href = '/login';
});
```

---

## 🧪 Testing

### Test Users

| Email | Password | Role | Site Access |
|---|---|---|---|
| super.admin@company.com | Welcome123! | Super Admin | ALL |
| hse.director@company.com | Welcome123! | HSE Director | ALL |
| site.manager.alpha@company.com | Welcome123! | Site Manager | SITE-A, SITE-A-C, SITE-A-O |
| hse.manager@company.com | Welcome123! | HSE Manager | ALL |
| hse.officer.alpha@company.com | Welcome123! | HSE Officer | SITE-A, SITE-A-C |
| supervisor.alpha@company.com | Welcome123! | Supervisor | SITE-A |
| ict.admin@company.com | Welcome123! | ICT Admin | ALL |
| auditor.external@company.com | Welcome123! | Auditor | ALL |
| contractor.alpha@company.com | Welcome123! | Contractor | SITE-A |

### Test Scenarios

1. **Login Success**
   ```bash
   curl -X POST "http://localhost:8000/api/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin@hse.local&password=password"
   ```

2. **Login Failed (invalid password)**
   ```bash
   curl -X POST "http://localhost:8000/api/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin@hse.local&password=wrong"
   ```

3. **Access Protected Endpoint**
   ```bash
   curl "http://localhost:8000/api/dashboard/summary" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

4. **Get Dynamic Menu**
   ```bash
   curl "http://localhost:8000/api/auth/menu" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

---

## 🔧 Configuration

### Environment Variables

```env
# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Password Policy
PASSWORD_MIN_LENGTH=12
PASSWORD_REQUIRE_UPPERCASE=true
PASSWORD_REQUIRE_LOWERCASE=true
PASSWORD_REQUIRE_NUMBER=true
PASSWORD_REQUIRE_SYMBOL=true
PASSWORD_EXPIRE_DAYS=90

# Account Lockout
MAX_FAILED_LOGIN_ATTEMPTS=5
ACCOUNT_LOCKOUT_MINUTES=15

# Session
SESSION_IDLE_TIMEOUT_MINUTES=30
SESSION_ABSOLUTE_TIMEOUT_HOURS=12
```

---

## 📝 Implementation Details

### Permission Decorator

```python
from app.utils.rbac import require_permission, get_current_user

@router.get("/incidents")
async def get_incidents(
    current_user: Dict = Depends(require_permission("incident:view"))
):
    # Only users with incident:view permission can access
    return {"incidents": [...]}
```

### Site Restriction

```python
from app.utils.rbac import require_site_access

@router.get("/incidents")
async def get_incidents(
    site_id: str,
    current_user: Dict = Depends(require_site_access("SITE-A"))
):
    # Only users with access to SITE-A can access
    return {"incidents": [...]}
```

### Auto Site Filtering

```python
# Automatically filter by user's site access
user_site_access = current_user["site_access"]
if "ALL" not in user_site_access:
    query = query.filter(FactHSE.site_key.in_(user_site_access))
```

---

## 🚨 Security Hardening

### Rate Limiting

```python
# Already implemented in main.py
# Max 100 requests per minute per IP
```

### CORS

```python
# Configured in main.py
# Only allow trusted origins
CORS_ORIGINS = [
    "http://localhost:8080",
    "http://localhost:3000",
]
```

### Password Hashing

```python
from app.utils.security import hash_password, verify_password

# Hash password
password_hash = hash_password("Welcome123!")

# Verify password
is_valid = verify_password("Welcome123!", password_hash)
```

---

## 📋 Migration from Old System

### Before
```javascript
// Old security_user_role table
security_user_role
  - user_email (PK)
  - role_name
  - site_access
```

### After
```javascript
// New RBAC system
security_users          // User accounts
security_roles          // Role definitions
security_permissions    // Granular permissions
security_role_permission // Role-permission mapping
security_user_role      // User assignments
security_sessions       // Active sessions
security_login_history  // Audit trail
```

---

## 🔄 Next Steps

After STEP 4 completion:

1. ✅ Enterprise RBAC implemented
2. ✅ Permission-based access control
3. ✅ Site-level security
4. ✅ Session management
5. ✅ Audit trail
6. 🔄 Dynamic menu in dashboard
7. 🔄 Frontend permission-based UI
8. STEP 5: Audit Trail & Evidence Management

---

## 📚 References

- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [OWASP RBAC Guide](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)

---

*End of STEP 4 — Authentication & RBAC*
