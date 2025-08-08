"""Document enrichment implementations."""
from .context_fixed import ContextFixedEnricher
from .enhanced_with_examples import ExampleEnhancedEnricher
from .full_enhanced import FullEnhancedEnricher
from .minimal_enhanced import MinimalEnhancedEnricher
from .markdown_validator import MarkdownDocEnricher

# Backward compatibility
import sys
sys.modules['context_fixed_enricher'] = sys.modules['enrichers.context_fixed']
sys.modules['enhanced_enricher_with_examples'] = sys.modules['enrichers.enhanced_with_examples']
sys.modules['full_enhanced_enricher'] = sys.modules['enrichers.full_enhanced']
sys.modules['minimal_enhanced_enricher'] = sys.modules['enrichers.minimal_enhanced']
sys.modules['markdown_validator_enricher'] = sys.modules['enrichers.markdown_validator']