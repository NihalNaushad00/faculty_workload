#!/usr/bin/env python3
"""
Timetable Management Script
Generate or clear timetables for specific semesters and academic years
"""

from app import create_app, db
from app.utils import generate_timetable, clear_timetable
import sys

app = create_app()

def main():
    with app.app_context():
        print("=" * 70)
        print("📅 TIMETABLE MANAGEMENT")
        print("=" * 70)
        
        if len(sys.argv) < 2:
            print("\nUsage:")
            print("  python3 manage_timetable.py generate <semester> <academic_year>")
            print("  python3 manage_timetable.py clear <semester> <academic_year>")
            print("\nExamples:")
            print("  python3 manage_timetable.py generate 1 2025-26")
            print("  python3 manage_timetable.py generate 3 2025-26")
            print("  python3 manage_timetable.py clear 1 2025-26")
            return
        
        command = sys.argv[1].lower()
        
        if command == 'generate':
            if len(sys.argv) < 4:
                print("❌ Error: Missing arguments")
                print("Usage: python3 manage_timetable.py generate <semester> <academic_year>")
                return
            
            try:
                semester = int(sys.argv[2])
                academic_year = sys.argv[3]
                
                if semester < 1 or semester > 8:
                    print("❌ Error: Semester must be between 1 and 8")
                    return
                
                print(f"\n🔄 Generating timetable for Semester {semester}, Year {academic_year}...\n")
                
                result = generate_timetable(semester, academic_year)
                
                print("=" * 70)
                if result['success']:
                    print("✅ TIMETABLE GENERATION SUCCESSFUL!")
                    print("=" * 70)
                    print(f"\n📊 Results:")
                    print(f"   Total Entries Created: {result['timetables_created']}")
                    print(f"   Successful Assignments: {result['successful']}")
                    print(f"   Failed Assignments: {result['failed']}")
                    print(f"   Summary: {result['summary']}")
                    
                    if result['successful_assignments']:
                        print(f"\n✅ Successfully Scheduled ({len(result['successful_assignments'])} shown):")
                        for i, assignment in enumerate(result['successful_assignments'], 1):
                            print(f"   {i}. {assignment}")
                    
                    if result['failed_assignments']:
                        print(f"\n❌ Failed to Schedule ({len(result['failed_assignments'])} shown):")
                        for i, assignment in enumerate(result['failed_assignments'], 1):
                            print(f"   {i}. {assignment}")
                else:
                    print(f"❌ ERROR: {result['message']}")
                    if 'error' in result:
                        print(f"   Details: {result['error']}")
                
                print("\n" + "=" * 70)
            
            except ValueError:
                print("❌ Error: Semester must be an integer")
        
        elif command == 'clear':
            if len(sys.argv) < 4:
                print("❌ Error: Missing arguments")
                print("Usage: python3 manage_timetable.py clear <semester> <academic_year>")
                return
            
            try:
                semester = int(sys.argv[2])
                academic_year = sys.argv[3]
                
                if semester < 1 or semester > 8:
                    print("❌ Error: Semester must be between 1 and 8")
                    return
                
                # Confirm deletion
                print(f"\n⚠️  About to delete timetable for Semester {semester}, Year {academic_year}")
                confirm = input("Are you sure? (yes/no): ").lower()
                
                if confirm == 'yes':
                    count = clear_timetable(semester, academic_year)
                    print(f"\n✅ Deleted {count} timetable entries")
                else:
                    print("❌ Deletion cancelled")
            
            except ValueError:
                print("❌ Error: Semester must be an integer")
        
        else:
            print(f"❌ Unknown command: {command}")
            print("Valid commands: generate, clear")

if __name__ == '__main__':
    main()
