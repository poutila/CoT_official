# Encoding Error Prevention Guidelines

## For AI Assistants

### File Creation Rules

1. **Always use UTF-8 encoding** when creating or editing files
2. **Avoid non-ASCII characters** in critical positions:
   - First 10 bytes of any file
   - File headers and titles
   - Code comments in the first line

3. **Safe character usage**:
   ```
   ❌ AVOID: Special Unicode symbols in titles (➤, ➜, ⟶, etc.)
   ✅ PREFER: ASCII characters or well-supported emoji (📖, 🚀, ✅)
   ```

4. **When using emoji or special characters**:
   - Place them after position 10 in the file
   - Always include a space before and after
   - Test with a simple read operation after creation

5. **Validation after file creation**:
   ```bash
   # Always validate encoding after creating files
   file <filename>  # Should show "UTF-8 Unicode text"
   head -1 <filename> | od -c  # Should not show octal codes > 177
   ```

### Common Encoding Pitfalls

1. **Copy-paste from external sources**: May introduce invisible characters
2. **Smart quotes and dashes**: Often problematic from word processors
3. **Zero-width characters**: Invisible but break parsing
4. **BOM (Byte Order Mark)**: Avoid UTF-8 BOM in text files

### Safe File Creation Template

```python
# When creating files programmatically
content = """# Title Here

Content starts here...
"""

# Ensure clean ASCII for headers
with open(filename, 'w', encoding='utf-8') as f:
    f.write(content)
```

### Detection Commands

Add these to your workflow:

```bash
# Find files with encoding issues
find . -name "*.md" -type f -exec file {} \; | grep -v "UTF-8"

# Check for non-ASCII in first line
find . -name "*.md" -type f -exec head -1 {} \; -print | grep -P "[\x80-\xFF]"
```

## For Humans

### IDE Configuration

1. **VS Code settings.json**:
   ```json
   {
     "files.encoding": "utf8",
     "files.autoGuessEncoding": false,
     "editor.renderControlCharacters": true
   }
   ```

2. **Git configuration**:
   ```bash
   git config core.quotepath false
   git config core.precomposeunicode true
   ```

3. **Pre-commit hook** for encoding validation:
   ```yaml
   - repo: local
     hooks:
       - id: check-encoding
         name: Check file encoding
         entry: file
         language: system
         files: \.(md|py|js|ts)$
         pass_filenames: true
   ```

### CLAUDE.md Addition

Add this section to CLAUDE.md:

```markdown
### 🔤 Character Encoding Requirements

- **MUST use UTF-8 encoding** for all text files
- **MUST validate encoding** after file creation using `file <filename>`
- **AVOID non-ASCII characters** in:
  - First line of any file
  - File headers and titles  
  - First 10 bytes of files
- **PREFER ASCII** for critical metadata and headers
- **TEST encoding** immediately after file operations
- **FORBIDDEN**: UTF-8 BOM, UTF-16, Latin-1, or other encodings

**Validation Required**:
```bash
file myfile.md  # Must show "UTF-8 Unicode text"
```
```

This will help prevent encoding issues in the future!