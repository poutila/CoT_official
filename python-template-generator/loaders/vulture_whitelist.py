"""
Vulture whitelist for legitimate unused code.

This file contains false positives from vulture that are actually part of the API
or data model design and should not be removed.
"""

# Pydantic model fields - these are part of the data structure
# and may be accessed by external code
_.subsection  # chunker/models.py:26
_.start_line  # chunker/models.py:38
_.end_line  # chunker/models.py:39
_.topics  # chunker/models.py:44
_.keywords  # chunker/models.py:45
_.created_at  # chunker/models.py:48
_.processing_version  # chunker/models.py:49
_.prev_chunk_id  # chunker/models.py:70
_.next_chunk_id  # chunker/models.py:71
_.parent_chunk_id  # chunker/models.py:72
_.preserve_code_blocks  # chunker/models.py:150
_.preserve_sections  # chunker/models.py:151
_.respect_sentence_boundaries  # chunker/models.py:156

# Pydantic model properties and methods - part of the public API
_.has_good_example  # chunker/models.py:88
_.has_bad_example  # chunker/models.py:93
_.to_embedding_text  # chunker/models.py:98
_.to_retrieval_text  # chunker/models.py:120

# Base class methods that may be used by subclasses
_.estimate_chunks  # chunker/base_chunker.py:245

# Chunk linking attributes used for navigation
_.prev_chunk_id  # chunker/base_chunker.py:126
_.next_chunk_id  # chunker/base_chunker.py:144