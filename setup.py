#!/usr/bin/env python3
"""
Setup configuration for CoT validation tools.

This provides CLI entry points for the Chain-of-Thought validation utilities.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="cot-validator",
    version="2.0.0",
    description="Chain-of-Thought (CoT) specification validator and bundle management tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="CoT Standards Committee",
    author_email="committee@cot-standard.org",
    url="https://github.com/cot-standard/chain-of-thought-spec",
    license="MIT",
    
    # Package configuration
    packages=find_packages(include=["cot_validator", "cot_validator.*"]),
    py_modules=["validate_bundle", "cot_version_check", "cot_validate_wrapper"],
    
    # CLI entry points - makes commands directly callable after installation
    entry_points={
        "console_scripts": [
            # Primary validation command: cot-validate
            "cot-validate=validate_bundle:main",
            # Alternative using wrapper module
            "cot-validate-wrapped=cot_validate_wrapper:main",
            # Alias for backward compatibility
            "cot-bundle-validator=validate_bundle:main",
            # Version checking command
            "cot-version-check=cot_version_check:main",
        ],
    },
    
    # Scripts (alternative method for CLI exposure)
    scripts=[],
    
    # Dependencies
    install_requires=[
        "jsonschema>=4.0.0",
        "pyyaml>=6.0",
        "click>=8.0.0",
    ],
    
    # Development dependencies
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "mypy>=1.0.0",
            "ruff>=0.0.200",
        ],
        "langchain": [
            "langchain>=0.1.0",
            "openai>=1.0.0",
        ],
    },
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Package data
    package_data={
        "cot_validator": [
            "schemas/*.json",
            "templates/*.md",
        ],
    },
    
    # Metadata
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
    ],
    
    keywords="chain-of-thought cot reasoning validation ai llm",
)