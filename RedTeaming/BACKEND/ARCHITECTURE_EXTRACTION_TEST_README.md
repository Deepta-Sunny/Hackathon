# Architecture Extraction Test

This test script verifies that the `extract_chatbot_architecture_context` function correctly extracts SYSTEM CONSTRAINTS & DESIGN and TECHNICAL IMPLEMENTATION sections from a .md file.

## Purpose

The test ensures that:
- Only relevant sections are extracted for red-teaming purposes
- The extraction handles file I/O correctly
- Error conditions are handled gracefully
- The extracted information is displayed clearly

## Usage

```bash
python test_architecture_extraction.py <path_to_md_file>
```

## Example

```bash
python test_architecture_extraction.py uploads/architecture_20260127_182925.md
```

## Expected Output

When successful, the script will:
1. Display file information
2. Extract and display the SYSTEM CONSTRAINTS & DESIGN section
3. Extract and display the TECHNICAL IMPLEMENTATION section
4. Show a success message

## Error Handling

The script handles:
- Missing command line arguments
- Non-existent files
- Non-.md files
- Extraction failures