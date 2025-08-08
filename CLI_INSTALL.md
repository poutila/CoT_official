# CLI Installation Guide

## Installation Methods

### Method 1: Install from Source (Development)

```bash
# Clone the repository
git clone https://github.com/cot-standard/chain-of-thought-spec.git
cd chain-of-thought-spec

# Install in development mode
pip install -e .

# Verify installation
cot-validate --version
```

### Method 2: Install from PyPI

```bash
# Install latest version
pip install cot-validator

# Install specific version
pip install cot-validator==2.0.0
```

### Method 3: Install via pipx (Recommended for CLI tools)

```bash
# Install pipx if not already installed
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Install cot-validator
pipx install cot-validator
```

## Available Commands

After installation, the following commands will be available:

### cot-validate

Primary validation command for CoT bundles.

```bash
# Validate a bundle
cot-validate chain_of_thought.bundle.json

# Generate file hashes
cot-validate chain_of_thought.bundle.json --generate-hashes

# Generate signed validation report
cot-validate chain_of_thought.bundle.json --generate-signed-report report.json --sign

# Check signature
cot-validate chain_of_thought.bundle.json --check-signature
```

### cot-version-check

Check for updates to the CoT specification.

```bash
# Check current version against latest
cot-version-check

# Check specific version
cot-version-check 6.0.0

# Use custom registry URL
COT_REGISTRY_URL=https://mirror.example.com/registry.json cot-version-check
```

## Verification

Verify the installation:

```bash
# Check installed commands
which cot-validate
which cot-version-check

# Run help
cot-validate --help
cot-version-check --help

# Test validation
echo '{"$schema": "test", "version": "1.0.0"}' > test.json
cot-validate test.json
```

## Troubleshooting

### Command not found

If commands are not found after installation:

1. Check PATH:
   ```bash
   echo $PATH
   # Ensure ~/.local/bin is in PATH for pip install --user
   ```

2. Reload shell:
   ```bash
   source ~/.bashrc  # or ~/.zshrc
   ```

3. Use full path:
   ```bash
   python3 -m cot_validator.validate_bundle
   ```

### Permission denied

If you get permission errors:

```bash
# Install for current user only
pip install --user cot-validator

# Or use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install cot-validator
```

### Version conflicts

If you have version conflicts:

```bash
# Uninstall existing version
pip uninstall cot-validator

# Install fresh
pip install --upgrade cot-validator
```

## Uninstallation

To remove the CLI tools:

```bash
# If installed with pip
pip uninstall cot-validator

# If installed with pipx
pipx uninstall cot-validator

# If installed in development mode
pip uninstall -e .
```