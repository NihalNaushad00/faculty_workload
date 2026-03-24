#!/usr/bin/env python
"""
Admin Creation Script
Usage: python create_admin.py
"""

from app import app, db
from app.models import Faculty

def create_admin():
    """Create a new admin user"""
    with app.app_context():
        print("=" * 50)
        print("👤 CREATE NEW ADMIN USER")
        print("=" * 50)
        
        # Get input
        name = input("\n📝 Enter admin name: ").strip()
        if not name:
            print("❌ Name cannot be empty!")
            return
        
        email = input("📧 Enter admin email: ").strip()
        if not email:
            print("❌ Email cannot be empty!")
            return
        
        # Check if email already exists
        existing = Faculty.query.filter_by(email=email).first()
        if existing:
            print(f"❌ Email '{email}' already exists!")
            return
        
        password = input("🔐 Enter password (min 6 characters): ").strip()
        if len(password) < 6:
            print("❌ Password must be at least 6 characters!")
            return
        
        confirm_password = input("🔐 Confirm password: ").strip()
        if password != confirm_password:
            print("❌ Passwords do not match!")
            return
        
        department = input("🏢 Enter department (default: Computer Science): ").strip() or "Computer Science"
        designation = input("🎓 Enter designation (default: Professor): ").strip() or "Professor"
        
        max_workload = input("📊 Enter max workload hours/week (default: 20): ").strip()
        try:
            max_workload = int(max_workload) if max_workload else 20
        except ValueError:
            max_workload = 20
        
        # Create admin
        admin = Faculty(
            name=name,
            email=email,
            department=department,
            designation=designation,
            max_workload=max_workload,
            role="admin"
        )
        admin.set_password(password)
        
        try:
            db.session.add(admin)
            db.session.commit()
            print("\n✅ Admin user created successfully!")
            print(f"   Name: {name}")
            print(f"   Email: {email}")
            print(f"   Role: Admin")
            print(f"   Department: {department}")
            print(f"   Max Workload: {max_workload} hrs/week")
            print("\n🎉 You can now login with these credentials!")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error creating admin: {str(e)}")

if __name__ == '__main__':
    create_admin()
