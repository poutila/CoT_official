"""Setup configuration for cot-semantic-enhancer package."""
from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
def read_requirements(filename):
    """Read requirements from file."""
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Base requirements
install_requires = [
    "numpy>=1.21.0",
    "pydantic>=2.0.0",
    "aiofiles>=23.0.0",
    "python-dotenv>=1.0.0",
    "tenacity>=8.0.0",
    "cachetools>=5.0.0",
]

# Optional requirements for different features
extras_require = {
    "sentence-transformers": ["sentence-transformers>=2.2.0", "torch>=2.0.0"],
    "openai": ["openai>=1.0.0"],
    "cohere": ["cohere>=4.0.0"],
    "faiss": ["faiss-cpu>=1.7.0"],
    "pinecone": ["pinecone-client>=2.0.0"],
    "weaviate": ["weaviate-client>=3.0.0"],
    "qdrant": ["qdrant-client>=1.0.0"],
    "chroma": ["chromadb>=0.4.0"],
    "nlp": ["nltk>=3.8.0", "spacy>=3.5.0"],
    "dev": [
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.0.0",
        "mypy>=1.0.0",
        "black>=23.0.0",
        "ruff>=0.1.0",
        "sphinx>=6.0.0",
        "sphinx-rtd-theme>=1.0.0",
    ],
    "all": [],  # Will be populated below
}

# Combine all optional dependencies
all_extras = []
for extra, deps in extras_require.items():
    if extra != "all":
        all_extras.extend(deps)
extras_require["all"] = list(set(all_extras))

setup(
    name="cot-semantic-enhancer",
    version="1.1.0",
    author="CoT Development Team",
    author_email="team@cot-semantic.dev",
    description="Advanced semantic similarity and document processing for Chain-of-Thought reasoning systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cot-team/cot-semantic-enhancer",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "cot-semantic=cot_semantic_enhancer.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "cot_semantic_enhancer": ["py.typed"],
    },
)