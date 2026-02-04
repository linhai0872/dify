"""
[CUSTOM] Unit tests for NativeEpubExtractor.

Tests cover:
1. Basic text extraction from EPUB items
2. HTML to text conversion
3. Chapter-based extraction
4. Error handling
"""

from unittest.mock import MagicMock, patch

import pytest
from ebooklib import ITEM_DOCUMENT

from custom.extractors.epub_extractor import NativeEpubExtractor


class TestNativeEpubExtractor:
    """Tests for NativeEpubExtractor."""

    def test_init(self):
        """Test extractor initialization."""
        extractor = NativeEpubExtractor("/path/to/test.epub")
        assert extractor._file_path == "/path/to/test.epub"

    @patch("custom.extractors.epub_extractor.epub.read_epub")
    def test_extract_single_chapter(self, mock_read_epub):
        """Test extracting text from a single chapter."""
        # Arrange
        mock_item = MagicMock()
        mock_item.get_type.return_value = ITEM_DOCUMENT
        mock_item.get_name.return_value = "chapter1.xhtml"
        mock_item.get_content.return_value = b"<html><body><p>Chapter 1 content</p></body></html>"

        mock_book = MagicMock()
        mock_book.get_items.return_value = [mock_item]
        mock_read_epub.return_value = mock_book

        extractor = NativeEpubExtractor("/path/to/test.epub")

        # Act
        documents = extractor.extract()

        # Assert
        assert len(documents) == 1
        assert "Chapter 1 content" in documents[0].page_content
        assert documents[0].metadata["source"] == "/path/to/test.epub"
        assert documents[0].metadata["chapter"] == "chapter1.xhtml"

    @patch("custom.extractors.epub_extractor.epub.read_epub")
    def test_extract_multiple_chapters(self, mock_read_epub):
        """Test extracting text from multiple chapters."""
        # Arrange
        def create_item(name, content):
            mock_item = MagicMock()
            mock_item.get_type.return_value = ITEM_DOCUMENT
            mock_item.get_name.return_value = name
            mock_item.get_content.return_value = content.encode("utf-8")
            return mock_item

        mock_book = MagicMock()
        mock_book.get_items.return_value = [
            create_item("chapter1.xhtml", "<html><body><p>Chapter 1</p></body></html>"),
            create_item("chapter2.xhtml", "<html><body><p>Chapter 2</p></body></html>"),
            create_item("chapter3.xhtml", "<html><body><p>Chapter 3</p></body></html>"),
        ]
        mock_read_epub.return_value = mock_book

        extractor = NativeEpubExtractor("/path/to/test.epub")

        # Act
        documents = extractor.extract()

        # Assert
        assert len(documents) == 3
        assert "Chapter 1" in documents[0].page_content
        assert "Chapter 2" in documents[1].page_content
        assert "Chapter 3" in documents[2].page_content

    @patch("custom.extractors.epub_extractor.epub.read_epub")
    def test_extract_skips_non_document_items(self, mock_read_epub):
        """Test that non-document items (images, styles) are skipped."""
        # Arrange
        mock_doc_item = MagicMock()
        mock_doc_item.get_type.return_value = ITEM_DOCUMENT
        mock_doc_item.get_name.return_value = "chapter1.xhtml"
        mock_doc_item.get_content.return_value = b"<html><body><p>Content</p></body></html>"

        mock_image_item = MagicMock()
        mock_image_item.get_type.return_value = 2  # ITEM_IMAGE

        mock_style_item = MagicMock()
        mock_style_item.get_type.return_value = 3  # ITEM_STYLE

        mock_book = MagicMock()
        mock_book.get_items.return_value = [mock_doc_item, mock_image_item, mock_style_item]
        mock_read_epub.return_value = mock_book

        extractor = NativeEpubExtractor("/path/to/test.epub")

        # Act
        documents = extractor.extract()

        # Assert
        assert len(documents) == 1
        assert "Content" in documents[0].page_content

    @patch("custom.extractors.epub_extractor.epub.read_epub")
    def test_extract_empty_epub(self, mock_read_epub):
        """Test extracting from an empty EPUB."""
        # Arrange
        mock_book = MagicMock()
        mock_book.get_items.return_value = []
        mock_read_epub.return_value = mock_book

        extractor = NativeEpubExtractor("/path/to/test.epub")

        # Act
        documents = extractor.extract()

        # Assert
        assert len(documents) == 0

    def test_html_to_text_removes_scripts(self):
        """Test that script tags are removed from HTML."""
        # Arrange
        extractor = NativeEpubExtractor("/path/to/test.epub")
        html_content = b"""
        <html>
        <head><script>alert('bad');</script></head>
        <body>
            <p>Safe content</p>
            <script>console.log('also bad');</script>
        </body>
        </html>
        """

        # Act
        result = extractor._html_to_text(html_content)

        # Assert
        assert "Safe content" in result
        assert "alert" not in result
        assert "console.log" not in result

    def test_html_to_text_removes_styles(self):
        """Test that style tags are removed from HTML."""
        # Arrange
        extractor = NativeEpubExtractor("/path/to/test.epub")
        html_content = b"""
        <html>
        <head><style>body { color: red; }</style></head>
        <body><p>Content</p></body>
        </html>
        """

        # Act
        result = extractor._html_to_text(html_content)

        # Assert
        assert "Content" in result
        assert "color: red" not in result

    def test_html_to_text_preserves_paragraphs(self):
        """Test that paragraph structure is preserved."""
        # Arrange
        extractor = NativeEpubExtractor("/path/to/test.epub")
        html_content = b"""
        <html><body>
            <p>Paragraph 1</p>
            <p>Paragraph 2</p>
            <p>Paragraph 3</p>
        </body></html>
        """

        # Act
        result = extractor._html_to_text(html_content)

        # Assert
        assert "Paragraph 1" in result
        assert "Paragraph 2" in result
        assert "Paragraph 3" in result

    def test_html_to_text_handles_malformed_html(self):
        """Test handling of malformed HTML."""
        # Arrange
        extractor = NativeEpubExtractor("/path/to/test.epub")
        html_content = b"<html><body><p>Unclosed tag<p>More content"

        # Act
        result = extractor._html_to_text(html_content)

        # Assert
        assert "Unclosed tag" in result
        assert "More content" in result

    @patch("custom.extractors.epub_extractor.epub.read_epub")
    def test_extract_raises_on_invalid_file(self, mock_read_epub):
        """Test that extraction raises ValueError on invalid file."""
        # Arrange
        mock_read_epub.side_effect = Exception("Invalid EPUB file")
        extractor = NativeEpubExtractor("/path/to/invalid.epub")

        # Act & Assert
        with pytest.raises(ValueError, match="Failed to extract text from EPUB"):
            extractor.extract()

    @patch("custom.extractors.epub_extractor.epub.read_epub")
    def test_extract_handles_encoding_issues(self, mock_read_epub):
        """Test handling of encoding issues in content."""
        # Arrange
        mock_item = MagicMock()
        mock_item.get_type.return_value = ITEM_DOCUMENT
        mock_item.get_name.return_value = "chapter1.xhtml"
        # Content with special characters
        mock_item.get_content.return_value = "<html><body><p>Café résumé</p></body></html>".encode("utf-8")

        mock_book = MagicMock()
        mock_book.get_items.return_value = [mock_item]
        mock_read_epub.return_value = mock_book

        extractor = NativeEpubExtractor("/path/to/test.epub")

        # Act
        documents = extractor.extract()

        # Assert
        assert len(documents) == 1
        assert "Café" in documents[0].page_content
        assert "résumé" in documents[0].page_content


# Run with: cd api && uv run pytest tests/custom/extractors/test_epub_extractor.py -v
