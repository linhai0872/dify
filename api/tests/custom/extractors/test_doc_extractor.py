"""
[CUSTOM] Unit tests for NativeDocExtractor.

Tests cover:
1. Successful extraction with LibreOffice available
2. Error handling when LibreOffice is not available
3. Error message clarity
"""

from unittest.mock import MagicMock, patch

import pytest

from custom.extractors.doc_extractor import NativeDocExtractor


class TestNativeDocExtractor:
    """Tests for NativeDocExtractor."""

    def test_init(self):
        """Test extractor initialization."""
        extractor = NativeDocExtractor("/path/to/test.doc")
        assert extractor._file_path == "/path/to/test.doc"

    @patch("unstructured.partition.doc.partition_doc")
    def test_extract_success(self, mock_partition_doc):
        """Test successful extraction when LibreOffice is available."""
        # Arrange
        mock_element1 = MagicMock()
        mock_element1.text = "Paragraph 1"
        mock_element1.metadata = None

        mock_element2 = MagicMock()
        mock_element2.text = "Paragraph 2"
        mock_element2.metadata = None

        mock_partition_doc.return_value = [mock_element1, mock_element2]

        extractor = NativeDocExtractor("/path/to/test.doc")

        # Act
        documents = extractor.extract()

        # Assert
        assert len(documents) == 1
        assert "Paragraph 1" in documents[0].page_content
        assert "Paragraph 2" in documents[0].page_content
        assert documents[0].metadata["source"] == "/path/to/test.doc"

    @patch("unstructured.partition.doc.partition_doc")
    def test_extract_empty_document(self, mock_partition_doc):
        """Test extracting from an empty document."""
        # Arrange
        mock_partition_doc.return_value = []

        extractor = NativeDocExtractor("/path/to/test.doc")

        # Act
        documents = extractor.extract()

        # Assert
        assert len(documents) == 0

    @patch("unstructured.partition.doc.partition_doc")
    def test_extract_filters_empty_elements(self, mock_partition_doc):
        """Test that elements with empty text are filtered."""
        # Arrange
        mock_element1 = MagicMock()
        mock_element1.text = "Content"
        mock_element1.metadata = None

        mock_element2 = MagicMock()
        mock_element2.text = ""
        mock_element2.metadata = None

        mock_element3 = MagicMock()
        mock_element3.text = "   "
        mock_element3.metadata = None

        mock_partition_doc.return_value = [mock_element1, mock_element2, mock_element3]

        extractor = NativeDocExtractor("/path/to/test.doc")

        # Act
        documents = extractor.extract()

        # Assert
        assert len(documents) == 1
        assert documents[0].page_content == "Content"

    @patch("unstructured.partition.doc.partition_doc")
    def test_extract_libreoffice_not_found(self, mock_partition_doc):
        """Test error handling when LibreOffice is not found."""
        # Arrange
        mock_partition_doc.side_effect = Exception("libreoffice command not found")

        extractor = NativeDocExtractor("/path/to/test.doc")

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            extractor.extract()

        assert "LibreOffice" in str(exc_info.value)

    @patch("unstructured.partition.doc.partition_doc")
    def test_extract_soffice_not_found(self, mock_partition_doc):
        """Test error handling when soffice is not found."""
        # Arrange
        mock_partition_doc.side_effect = Exception("soffice binary not found")

        extractor = NativeDocExtractor("/path/to/test.doc")

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            extractor.extract()

        assert "LibreOffice" in str(exc_info.value)

    @patch("unstructured.partition.doc.partition_doc")
    def test_extract_generic_error(self, mock_partition_doc):
        """Test error handling for generic errors."""
        # Arrange
        mock_partition_doc.side_effect = Exception("Some other error")

        extractor = NativeDocExtractor("/path/to/test.doc")

        # Act & Assert
        with pytest.raises(ValueError, match="Failed to extract text from DOC"):
            extractor.extract()

    @patch("unstructured.partition.doc.partition_doc")
    def test_extract_preserves_document_structure(self, mock_partition_doc):
        """Test that document structure is preserved with newlines."""
        # Arrange
        mock_elements = []
        for i in range(3):
            mock_element = MagicMock()
            mock_element.text = f"Paragraph {i + 1}"
            mock_element.metadata = None
            mock_elements.append(mock_element)

        mock_partition_doc.return_value = mock_elements

        extractor = NativeDocExtractor("/path/to/test.doc")

        # Act
        documents = extractor.extract()

        # Assert
        assert len(documents) == 1
        lines = documents[0].page_content.split("\n")
        assert len(lines) == 3

    @patch("unstructured.partition.doc.partition_doc")
    def test_extract_with_page_numbers(self, mock_partition_doc):
        """Test extraction with page numbers in metadata."""
        # Arrange
        mock_element1 = MagicMock()
        mock_element1.text = "Page 1 content"
        mock_metadata1 = MagicMock()
        mock_metadata1.page_number = 1
        mock_element1.metadata = mock_metadata1

        mock_element2 = MagicMock()
        mock_element2.text = "Page 2 content"
        mock_metadata2 = MagicMock()
        mock_metadata2.page_number = 2
        mock_element2.metadata = mock_metadata2

        mock_partition_doc.return_value = [mock_element1, mock_element2]

        extractor = NativeDocExtractor("/path/to/test.doc")

        # Act
        documents = extractor.extract()

        # Assert
        assert len(documents) == 2
        assert documents[0].metadata["page"] == 1
        assert documents[1].metadata["page"] == 2


# Run with: cd api && uv run pytest tests/custom/extractors/test_doc_extractor.py -v
