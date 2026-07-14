"""
Seed RBAC data into database.
Run: python backend/scripts/seed_rbac.py
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.hse_models import (
    SecurityUser, SecurityRole, SecurityPermission,
    SecurityRolePermission, SecurityUserRole
)
from app.utils.security import hash_password

# Password untuk semua user: Welcome123!
DEMO_PASSWORD_HASH = hash_password("Welcome123!")

def seed_roles(db: Session):
    """Seed roles."""
    roles = [
        ("super_admin", "Super Admin", "Full system access with all permissions", True),
        ("hse_director", "HSE Director", "HSE Director with access to all HSE modules", True),
        ("site_manager", "Site Manager", "Site Manager with access to assigned sites", True),
        ("hse_manager", "HSE Manager", "HSE Manager with full HSE module access", True),
        ("hse_officer", "HSE Officer", "HSE Officer with input and monitoring access", True),
        ("supervisor", "Supervisor", "Supervisor with PTW, inspection, and HIRA access", True),
        ("ict_admin", "ICT Admin", "ICT Administrator with infrastructure access", True),
        ("auditor", "Auditor", "Auditor with read-only access and evidence management", True),
        ("contractor", "Contractor", "Contractor with access to own data only", True),
    ]

    for role_name, display_name, description, is_system in roles:
        existing = db.query(SecurityRole).filter(SecurityRole.role_name == role_name).first()
        if not existing:
            role = SecurityRole(
                role_name=role_name,
                role_display_name=display_name,
                role_description=description,
                is_system_role=is_system,
            )
            db.add(role)
            print(f"  ✓ Created role: {role_name}")
        else:
            print(f"  - Role exists: {role_name}")

    db.commit()


def seed_permissions(db: Session):
    """Seed permissions."""
    permissions = [
        # Dashboard
        ("dashboard:view", "View Dashboard", "dashboard", "view"),
        ("dashboard:export", "Export Dashboard", "dashboard", "export"),
        # Incident
        ("incident:view", "View Incidents", "incident", "view"),
        ("incident:create", "Create Incident", "incident", "create"),
        ("incident:edit", "Edit Incident", "incident", "edit"),
        ("incident:delete", "Delete Incident", "incident", "delete"),
        ("incident:investigate", "Investigate Incident", "incident", "investigate"),
        ("incident:close", "Close Incident", "incident", "close"),
        # PTW
        ("ptw:view", "View PTW", "ptw", "view"),
        ("ptw:create", "Create PTW", "ptw", "create"),
        ("ptw:edit", "Edit PTW", "ptw", "edit"),
        ("ptw:approve", "Approve PTW", "ptw", "approve"),
        ("ptw:close", "Close PTW", "ptw", "close"),
        ("ptw:violate", "Report Violation", "ptw", "violate"),
        # Training
        ("training:view", "View Training", "training", "view"),
        ("training:create", "Create Training", "training", "create"),
        ("training:edit", "Edit Training", "training", "edit"),
        ("training:delete", "Delete Training", "training", "delete"),
        ("training:certify", "Certify Training", "training", "certify"),
        # Environmental
        ("environmental:view", "View Environmental", "environmental", "view"),
        ("environmental:input", "Input Environmental", "environmental", "input"),
        ("environmental:edit", "Edit Environmental", "environmental", "edit"),
        ("environmental:export", "Export Environmental", "environmental", "export"),
        # Equipment
        ("equipment:view", "View Equipment", "equipment", "view"),
        ("equipment:create", "Create Equipment", "equipment", "create"),
        ("equipment:edit", "Edit Equipment", "equipment", "edit"),
        ("equipment:inspect", "Inspect Equipment", "equipment", "inspect"),
        ("equipment:certify", "Certify Equipment", "equipment", "certify"),
        # Audit
        ("audit:view", "View Audit", "audit", "view"),
        ("audit:create", "Create Audit", "audit", "create"),
        ("audit:edit", "Edit Audit", "audit", "edit"),
        ("audit:close", "Close Audit", "audit", "close"),
        ("audit:evidence", "Manage Evidence", "audit", "evidence"),
        # User Management
        ("user:view", "View Users", "user", "view"),
        ("user:create", "Create User", "user", "create"),
        ("user:edit", "Edit User", "user", "edit"),
        ("user:delete", "Delete User", "user", "delete"),
        ("user:assign_role", "Assign Role", "user", "assign_role"),
        # System
        ("system:config", "System Config", "system", "config"),
        ("system:monitor", "System Monitor", "system", "monitor"),
        ("system:backup", "System Backup", "system", "backup"),
    ]

    for perm_name, display_name, module, action in permissions:
        existing = db.query(SecurityPermission).filter(SecurityPermission.permission_name == perm_name).first()
        if not existing:
            perm = SecurityPermission(
                permission_name=perm_name,
                permission_display_name=display_name,
                module=module,
                action=action,
            )
            db.add(perm)
            print(f"  ✓ Created permission: {perm_name}")
        else:
            print(f"  - Permission exists: {perm_name}")

    db.commit()


def seed_role_permissions(db: Session):
    """Seed role-permission mappings."""
    # Clear existing
    db.query(SecurityRolePermission).delete()
    db.commit()

    mappings = {
        "super_admin": ["*"],
        "hse_director": ["dashboard:*", "incident:*", "ptw:*", "training:*", "environmental:*", "equipment:*", "audit:*"],
        "site_manager": [
            "dashboard:view", "dashboard:export",
            "incident:view", "incident:investigate", "incident:close",
            "ptw:view", "ptw:approve", "ptw:close",
            "training:view",
            "environmental:view", "environmental:export",
            "equipment:view",
            "audit:view", "audit:evidence",
        ],
        "hse_manager": [
            "dashboard:*",
            "incident:*",
            "ptw:*",
            "training:*",
            "environmental:*",
            "equipment:*",
            "audit:view", "audit:evidence", "audit:close",
        ],
        "hse_officer": [
            "dashboard:view",
            "incident:view", "incident:create", "incident:edit",
            "ptw:view", "ptw:create", "ptw:edit",
            "training:view",
            "environmental:view", "environmental:input",
            "equipment:view",
            "audit:view",
        ],
        "supervisor": [
            "dashboard:view",
            "ptw:view", "ptw:create",
            "incident:view",
            "equipment:view", "equipment:inspect",
            "audit:view",
        ],
        "ict_admin": [
            "system:monitor",
            "user:view",
            "dashboard:view",
        ],
        "auditor": [
            "dashboard:view",
            "incident:view",
            "ptw:view",
            "training:view",
            "environmental:view",
            "equipment:view",
            "audit:view", "audit:evidence",
        ],
        "contractor": [
            "dashboard:view",
            "incident:view",
            "ptw:view", "ptw:create",
            "training:view",
        ],
    }

    for role_name, perms in mappings.items():
        role = db.query(SecurityRole).filter(SecurityRole.role_name == role_name).first()
        if not role:
            continue

        for perm_name in perms:
            if perm_name == "*":
                # Grant all permissions
                all_perms = db.query(SecurityPermission).all()
                for perm in all_perms:
                    rp = SecurityRolePermission(role_id=role.role_id, permission_id=perm.permission_id, granted_by="system")
                    db.add(rp)
                continue

            perm = db.query(SecurityPermission).filter(SecurityPermission.permission_name == perm_name).first()
            if perm:
                rp = SecurityRolePermission(role_id=role.role_id, permission_id=perm.permission_id, granted_by="system")
                db.add(rp)

        print(f"  ✓ Mapped permissions for: {role_name}")

    db.commit()


def seed_users(db: Session):
    """Seed demo users."""
    users = [
        ("super.admin@company.com", "superadmin", "Super Admin", "super_admin", "ALL"),
        ("hse.director@company.com", "hsedirector", "HSE Director", "hse_director", "ALL"),
        ("site.manager.alpha@company.com", "sitemgr-alpha", "Site Manager Alpha", "site_manager", "SITE-A,SITE-A-C,SITE-A-O"),
        ("hse.manager@company.com", "hsemgr", "HSE Manager", "hse_manager", "ALL"),
        ("hse.officer.alpha@company.com", "hseoff-alpha", "HSE Officer Alpha", "hse_officer", "SITE-A,SITE-A-C"),
        ("supervisor.alpha@company.com", "sup-alpha", "Supervisor Alpha", "supervisor", "SITE-A"),
        ("ict.admin@company.com", "ictadmin", "ICT Administrator", "ict_admin", "ALL"),
        ("auditor.external@company.com", "auditor-ext", "External Auditor", "auditor", "ALL"),
        ("contractor.alpha@company.com", "ctr-alpha", "Contractor Alpha", "contractor", "SITE-A"),
    ]

    for email, username, full_name, role_name, site_access in users:
        existing = db.query(SecurityUser).filter(SecurityUser.email == email).first()
        if not existing:
            user = SecurityUser(
                email=email,
                username=username,
                full_name=full_name,
                password_hash=DEMO_PASSWORD_HASH,
                is_active=True,
                must_change_password=True,
            )
            db.add(user)
            db.flush()

            # Assign role
            role = db.query(SecurityRole).filter(SecurityRole.role_name == role_name).first()
            if role:
                user_role = SecurityUserRole(
                    user_id=user.user_id,
                    role_id=role.role_id,
                    site_access=site_access,
                    assigned_by="system",
                )
                db.add(user_role)

            print(f"  ✓ Created user: {email} ({role_name})")
        else:
            print(f"  - User exists: {email}")

    db.commit()


def main():
    """Run RBAC seed."""
    print("=" * 60)
    print("Seeding RBAC Data")
    print("=" * 60)

    db = SessionLocal()
    try:
        print("\n1. Seeding roles...")
        seed_roles(db)

        print("\n2. Seeding permissions...")
        seed_permissions(db)

        print("\n3. Seeding role-permission mappings...")
        seed_role_permissions(db)

        print("\n4. Seeding users...")
        seed_users(db)

        print("\n" + "=" * 60)
        print("✓ RBAC seeding complete")
        print("=" * 60)
        print("\nDefault password for all users: Welcome123!")
        print("Users must change password on first login.")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
