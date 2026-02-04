"""
[CUSTOM] Native EPUB Extractor using ebooklib.

Provides local EPUB extraction without pypandoc/pandoc dependency.
Uses ebooklib + BeautifulSoup for pure Python extraction.
"""

import logging

from bs4 import BeautifulSoup
from ebooklib import ITEM_DOCUMENT, epub

from core.rag.extractor.extractor_base import BaseExtractor
from core.rag.models.document import Document

logger = logging.getLogger(__name__)


class NativeEpubExtractor(BaseExtractor):
    """
    Native EPUB extractor using ebooklib + BeautifulSoup.

    Features:
    - Pure Python implementation (no pypandoc/pandoc required)
    - Extracts text from all document items
    - Removes script and style elements
    - Groups content by chapter for better organization
    """

    def __init__(self, file_path: str):
        """
        Initialize the extractor.

        Args:
            file_path: Path to the EPUB file to extract.
        """
        self._file_path = file_path

    def extract(self) -> list[Document]:
        """
        Extract text content from EPUB file.

        Returns:
            List of Document objects, one per chapter with content.
        """
        try:
            book = epub.read_epub(self._file_path, options={"ignore_ncx": True})
            documents = []

            for item in book.get_items():
                if item.get_type() == ITEM_DOCUMENT:
                    content = self._extract_item_content(item)
                    if content.strip():
                        documents.append(
                            Document(
                                page_content=content.strip(),
                                metadata={
                                    "source": self._file_path,
                                    "chapter": item.get_name(),
                                },
                            )
                        )

            # If no documents were extracted, try to get all text as a single document
            if not documents:
                all_text = self._extract_all_text(book)
                if all_text.strip():
                    documents.append(
                        Document(
                            page_content=all_text.strip(),
                            metadata={"source": self._file_path},
                        )
                    )

            return documents

        except Exception as e:
            logger.exception("Failed to extract text from EPUB: %s", self._file_path)
            raise ValueError(f"Failed to extract text from EPUB: {e!s}") from e

    def _extract_item_content(self, item) -> str:
        """
        Extract text content from an EPUB item.

        Args:
            item: An item from the EPUB book.

        Returns:
            Extracted text content.
        """
        try:
            content = item.get_content()
            return self._html_to_text(content)
        except Exception as e:
            logger.warning("Failed to extract content from item %s: %s", item.get_name(), e)
            return ""

    def _html_to_text(self, html_content: bytes) -> str:
        """
        Convert HTML content to plain text.

        Args:
            html_content: Raw HTML content as bytes.

        Returns:
            Plain text extracted from HTML.
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # Remove script and style elements
            for element in soup(["script", "style", "meta", "link", "head"]):
                element.decompose()

            # Get text with proper spacing
            text = soup.get_text(separator="\n", strip=True)

            # Clean up excessive whitespace while preserving paragraph structure
            lines = []
            for line in text.split("\n"):
                line = line.strip()
                if line:
                    lines.append(line)

            return "\n".join(lines)

        except Exception as e:
            logger.warning("Failed to parse HTML content: %s", e)
            # Fallback: try to decode as plain text
            try:
                return html_content.decode("utf-8", errors="ignore")
            except Exception:
                return ""

    def _extract_all_text(self, book: epub.EpubBook) -> str:
        """
        Extract all text from the EPUB book as a single string.

        Args:
            book: An EpubBook object from ebooklib.

        Returns:
            All text content concatenated.
        """
        all_text: list[str] = []

        for item in book.get_items():
            if item.get_type() == ITEM_DOCUMENT:
                content = self._extract_item_content(item)
                if content.strip():
                    all_text.append(content.strip())

        return "\n\n".join(all_text)
