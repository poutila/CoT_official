# Link analysis report

## Summary Statistics example
- **Total files scanned**: 45
- **Valid files**: 38 ✅
- **Files with issues**: 7 ❌
- **Total broken links**: 23 🔗
- **Processing errors**: 1 ⚠️


## `<file_path>`
### Links to external files from `<file_path>`
- Table must have this schema:
<!-- Links to external files table schema -->
| Links to external files | External file exists | 
|---|---|
<!-- End Links to external files table schema -->
Column description:
- Links to external files: Links found from <file_name>. Type: string.
- External file exists: If a file exists. Type: set[yes, no]

### Links to external file anchors from `<file_path>`
- Table must have this schema:
<!-- Links to external file anchors table schema -->
| Links to external file anchors  | External file anchor exists | 
|---|---|
<!-- End Links to external file anchors table schema -->
Column description:
- Links to external file anchors: Links to external file anchors found from <file_name>. Type: string.
- External file exists: If a file exists. Type: set[yes, no]

### Links that can not be parsed from `<file_path>`
- Table must have this schema:
<!-- Links that can not be parsed table schema -->
| Unparseable link text | Reason for parsing error | 
|---|---|
<!-- End Links that can not be parsed table schema -->
Column description:
- Unparseable link text: Text that could not be parsed as a link in <file_name>. Type: string.
- Reason for parsing error: error from try: except block

### Missing files
- Table must have this schema:
<!-- Missing file table schema -->
| Missing file | Link from file | Link in line number | Text in line |
|---|---|---|
<!-- End Missing file table schema -->
Column description:
- Missing file: File path that does not exist. Type: string.
- Link from file: File path that has the missing file link. Type: string
- Link in line number: Line number that contains the missing link in Link from file column. Type: Integer
- Text in line: Text that is in line that points to missing file: Type: string

