"""Core RAG pipeline components."""
from .adapters import *
from .models import *
from .pipeline import RAGPipeline

# Temporary backward compatibility
import sys
sys.modules['rag_adapters'] = sys.modules['core.adapters']
sys.modules['rag_models'] = sys.modules['core.models']
sys.modules['rag_pipeline'] = sys.modules['core.pipeline']