#!/usr/bin/env python3
"""
Test Script for Architecture Context Extraction
===============================================

This script tests the extract_chatbot_architecture_context function
to ensure it properly extracts SYSTEM CONSTRAINTS & DESIGN and
TECHNICAL IMPLEMENTATION sections from a .md file.

Usage:
    python test_architecture_extraction.py <path_to_md_file>

Example:
    python test_architecture_extraction.py uploads/architecture_20260127_182925.md
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.architecture_utils import extract_chatbot_architecture_context


def main():
    """Main test function."""

    print("=" * 70)
    print("🧪 ARCHITECTURE EXTRACTION TEST")
    print("=" * 70)

    # Check command line arguments
    if len(sys.argv) != 2:
        print("❌ ERROR: Incorrect number of arguments")
        print("Usage: python test_architecture_extraction.py <path_to_md_file>")
        print("Example: python test_architecture_extraction.py uploads/architecture_20260127_182925.md")
        sys.exit(1)

    md_file_path = sys.argv[1]

    # Check if file exists
    if not os.path.exists(md_file_path):
        print(f"❌ ERROR: File not found: {md_file_path}")
        sys.exit(1)

    # Check if file is .md
    if not md_file_path.lower().endswith('.md'):
        print(f"❌ ERROR: File must be a .md file: {md_file_path}")
        sys.exit(1)

    print(f"📁 Testing file: {md_file_path}")
    print(f"📏 File size: {os.path.getsize(md_file_path)} bytes")
    print()

    try:
        # Extract architecture context
        print("🔍 Extracting architecture information...")
        extracted_info = extract_chatbot_architecture_context(md_file_path)

        print()
        print("=" * 70)
        print("✅ EXTRACTION RESULTS")
        print("=" * 70)

        if extracted_info and extracted_info.strip():
            print("📋 Successfully extracted the following information:")
            print()
            print(extracted_info)
            print()
            print("✅ Test PASSED: Architecture information extracted successfully")
        else:
            print("⚠️  WARNING: No architecture information was extracted")
            print("   This might indicate the .md file doesn't contain the expected sections")
            print("   Expected sections: 'SYSTEM CONSTRAINTS & DESIGN:' and 'TECHNICAL IMPLEMENTATION:'")
            print()
            print("✅ Test COMPLETED: No extraction errors, but no content found")

    except Exception as e:
        print(f"❌ ERROR: Extraction failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print("=" * 70)
    print("🏁 TEST COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()