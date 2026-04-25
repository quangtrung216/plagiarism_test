#!/usr/bin/env python3
"""
Check subjects directly with SQL
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.postgres import get_conn, release_conn

def check_subjects_sql():
    """Check subjects table directly"""
    
    print("🔍 CHECK SUBJECTS TABLE")
    print("=" * 40)
    
    conn = get_conn()
    try:
        cur = conn.cursor()
        
        # Check if table exists
        cur.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'subjects'
        """)
        if not cur.fetchone():
            print("❌ 'subjects' table does not exist!")
            return
        
        print("✅ 'subjects' table exists")
        
        # Count subjects
        cur.execute("SELECT COUNT(*) FROM subjects")
        count = cur.fetchone()[0]
        print(f"📊 Total subjects: {count}")
        
        # List all subjects
        cur.execute("SELECT subject_id, subject_name FROM subjects ORDER BY subject_id")
        subjects = cur.fetchall()
        
        if subjects:
            print(f"📋 Subjects list:")
            for subject_id, subject_name in subjects:
                print(f"   - {subject_id}: {subject_name}")
        else:
            print("⚠️  No subjects found")
        
        # Check specific subject
        test_id = "machine_learning"
        cur.execute("SELECT * FROM subjects WHERE subject_id = %s", (test_id,))
        result = cur.fetchone()
        
        if result:
            print(f"✅ Found subject '{test_id}': {result}")
        else:
            print(f"❌ Subject '{test_id}' not found")
            
            # Check similar subjects
            cur.execute("SELECT subject_id FROM subjects WHERE subject_id ILIKE %s", (f"%{test_id}%",))
            similar = cur.fetchall()
            if similar:
                print(f"🔍 Similar subjects: {[s[0] for s in similar]}")
        
    finally:
        cur.close()
        release_conn(conn)

if __name__ == "__main__":
    check_subjects_sql()
