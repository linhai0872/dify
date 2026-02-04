"""
[CUSTOM] Native document extractors for DOC/PPT/PPTX/EPUB formats.

This module provides native extraction capabilities without requiring
external Unstructured API for common office document formats.

Extractors:
- NativePPTXExtractor: Uses python-pptx (pure Python)
- NativeEpubExtractor: Uses ebooklib + BeautifulSoup (pure Python)
- NativeDocExtractor: Uses unstructured.partition.doc (requires LibreOffice)
- NativePPTExtractor: Uses unstructured.partition.ppt (requires LibreOffice)
"""

from custom.extractors.doc_extractor import NativeDocExtractor
from custom.extractors.epub_extractor import NativeEpubExtractor
from custom.extractors.ppt_extractor import NativePPTExtractor
from custom.extractors.pptx_extractor import NativePPTXExtractor

__all__ = [
    "NativeDocExtractor",
    "NativeEpubExtractor",
    "NativePPTExtractor",
    "NativePPTXExtractor",
]
