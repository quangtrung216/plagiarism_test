#!/usr/bin/env python3
"""
Debug subject validation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from services.subject_service import validate_subject_exists, get_subject_by_id, get_all_subjects

def debug_subject():
    """Debug subject validation"""
    
    load_dotenv()
    
    print("🔍 DEBUG SUBJECT VALIDATION")
    print("=" * 40)
    
    # Test 1: List all subjects
    print("\n📋 All subjects:")
    all_subjects = get_all_subjects()
    for subject in all_subjects:
        print(f"   - {subject['subject_id']}: {subject['subject_name']}")
    
    # Test 2: Check specific subject
    test_subject = "machine_learning"
    print(f"\n🔍 Testing subject: '{test_subject}'")
    
    # Check if exists
    exists = validate_subject_exists(test_subject)
    print(f"   validate_subject_exists(): {exists}")
    
    # Get subject details
    subject = get_subject_by_id(test_subject)
    if subject:
        print(f"   get_subject_by_id(): {subject}")
    else:
        print(f"   get_subject_by_id(): None")
    
    # Test 3: Check case sensitivity
    print(f"\n🔍 Testing case sensitivity:")
    test_cases = ["machine_learning", "Machine_Learning", "MACHINE_LEARNING"]
    for case in test_cases:
        exists_case = validate_subject_exists(case)
        print(f"   '{case}': {exists_case}")

if __name__ == "__main__":
    debug_subject()
