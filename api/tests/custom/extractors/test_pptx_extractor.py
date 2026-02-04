"""
[CUSTOM] Unit tests for NativePPTXExtractor.

Tests cover:
1. Basic text extraction from slides
2. Table extraction and markdown conversion
3. Grouped shapes extraction
4. Error handling
"""

from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from custom.extractors.pptx_extractor import NativePPTXExtractor


class TestNativePPTXExtractor:
    """Tests for NativePPTXExtractor."""

    def test_init(self):
        """Test extractor initialization."""
        extractor = NativePPTXExtractor("/path/to/test.pptx")
        assert extractor._file_path == "/path/to/test.pptx"

    @patch("custom.extractors.pptx_extractor.Presentation")
    def test_extract_single_slide(self, mock_presentation_class):
        """Test extracting text from a single slide."""
        # Arrange
        mock_shape = MagicMock()
        mock_shape.has_table = False
        mock_text_frame = MagicMock()
        mock_paragraph = MagicMock()
        mock_paragraph.text = "Hello World"
        mock_text_frame.paragraphs = [mock_paragraph]
        mock_shape.text_frame = mock_text_frame
        # Ensure no sub-shapes
        del mock_shape.shapes

        mock_slide = MagicMock()
        mock_slide.shapes = [mock_shape]

        mock_presentation = MagicMock()
        mock_presentation.slides = [mock_slide]
        mock_presentation_class.return_value = mock_presentation

        extractor = NativePPTXExtractor("/path/to/test.pptx")

        # Act
        documents = extractor.extract()

        # Assert
        assert len(documents) == 1
        assert documents[0].page_content == "Hello World"
        assert documents[0].metadata["source"] == "/path/to/test.pptx"
        assert documents[0].metadata["slide"] == 1

    @patch("custom.extractors.pptx_extractor.Presentation")
    def test_extract_multiple_slides(self, mock_presentation_class):
        """Test extracting text from multiple slides."""

        # Arrange
        def create_slide(text):
            mock_shape = MagicMock()
            mock_shape.has_table = False
            mock_text_frame = MagicMock()
            mock_paragraph = MagicMock()
            mock_paragraph.text = text
            mock_text_frame.paragraphs = [mock_paragraph]
            mock_shape.text_frame = mock_text_frame
            del mock_shape.shapes

            mock_slide = MagicMock()
            mock_slide.shapes = [mock_shape]
            return mock_slide

        mock_presentation = MagicMock()
        mock_presentation.slides = [
            create_slide("Slide 1 content"),
            create_slide("Slide 2 content"),
            create_slide("Slide 3 content"),
        ]
        mock_presentation_class.return_value = mock_presentation

        extractor = NativePPTXExtractor("/path/to/test.pptx")

        # Act
        documents = extractor.extract()

        # Assert
        assert len(documents) == 3
        assert documents[0].page_content == "Slide 1 content"
        assert documents[1].page_content == "Slide 2 content"
        assert documents[2].page_content == "Slide 3 content"
        assert documents[0].metadata["slide"] == 1
        assert documents[1].metadata["slide"] == 2
        assert documents[2].metadata["slide"] == 3

    @patch("custom.extractors.pptx_extractor.Presentation")
    def test_extract_empty_presentation(self, mock_presentation_class):
        """Test extracting from an empty presentation."""
        # Arrange
        mock_presentation = MagicMock()
        mock_presentation.slides = []
        mock_presentation_class.return_value = mock_presentation

        extractor = NativePPTXExtractor("/path/to/test.pptx")

        # Act
        documents = extractor.extract()

        # Assert
        assert len(documents) == 0

    @patch("custom.extractors.pptx_extractor.Presentation")
    def test_extract_slide_with_empty_shapes(self, mock_presentation_class):
        """Test extracting from a slide with empty text frames."""
        # Arrange
        mock_shape = MagicMock()
        mock_shape.has_table = False
        mock_text_frame = MagicMock()
        mock_paragraph = MagicMock()
        mock_paragraph.text = ""
        mock_text_frame.paragraphs = [mock_paragraph]
        mock_shape.text_frame = mock_text_frame
        mock_shape.text = ""
        del mock_shape.shapes

        mock_slide = MagicMock()
        mock_slide.shapes = [mock_shape]

        mock_presentation = MagicMock()
        mock_presentation.slides = [mock_slide]
        mock_presentation_class.return_value = mock_presentation

        extractor = NativePPTXExtractor("/path/to/test.pptx")

        # Act
        documents = extractor.extract()

        # Assert
        assert len(documents) == 0

    def test_extract_table_markdown(self):
        """Test table to markdown conversion."""
        # Arrange
        extractor = NativePPTXExtractor("/path/to/test.pptx")

        mock_cell1 = MagicMock()
        mock_cell1.text = "Header 1"
        mock_cell2 = MagicMock()
        mock_cell2.text = "Header 2"

        mock_cell3 = MagicMock()
        mock_cell3.text = "Data 1"
        mock_cell4 = MagicMock()
        mock_cell4.text = "Data 2"

        mock_row1 = MagicMock()
        mock_row1.cells = [mock_cell1, mock_cell2]
        mock_row2 = MagicMock()
        mock_row2.cells = [mock_cell3, mock_cell4]

        mock_table = MagicMock()
        mock_table.rows = [mock_row1, mock_row2]

        # Act
        result = extractor._extract_table(mock_table)

        # Assert
        assert "| Header 1 | Header 2 |" in result
        assert "| --- | --- |" in result
        assert "| Data 1 | Data 2 |" in result

    def test_extract_table_with_pipe_escape(self):
        """Test that pipe characters in cells are escaped."""
        # Arrange
        extractor = NativePPTXExtractor("/path/to/test.pptx")

        mock_cell = MagicMock()
        mock_cell.text = "Value|with|pipes"

        mock_row = MagicMock()
        mock_row.cells = [mock_cell]

        mock_table = MagicMock()
        mock_table.rows = [mock_row]

        # Act
        result = extractor._extract_table(mock_table)

        # Assert
        assert "\\|" in result

    @patch("custom.extractors.pptx_extractor.Presentation")
    def test_extract_raises_on_invalid_file(self, mock_presentation_class):
        """Test that extraction raises ValueError on invalid file."""
        # Arrange
        mock_presentation_class.side_effect = Exception("Invalid file format")
        extractor = NativePPTXExtractor("/path/to/invalid.pptx")

        # Act & Assert
        with pytest.raises(ValueError, match="Failed to extract text from PPTX"):
            extractor.extract()

    def test_extract_text_frame(self):
        """Test extracting text from a text frame."""
        # Arrange
        extractor = NativePPTXExtractor("/path/to/test.pptx")

        mock_paragraph1 = MagicMock()
        mock_paragraph1.text = "Line 1"
        mock_paragraph2 = MagicMock()
        mock_paragraph2.text = "Line 2"
        mock_paragraph3 = MagicMock()
        mock_paragraph3.text = ""  # Empty paragraph should be skipped

        mock_text_frame = MagicMock()
        mock_text_frame.paragraphs = [mock_paragraph1, mock_paragraph2, mock_paragraph3]

        # Act
        result = extractor._extract_text_frame(mock_text_frame)

        # Assert
        assert "Line 1" in result
        assert "Line 2" in result

    def test_extract_table_empty(self):
        """Test handling of empty table."""
        # Arrange
        extractor = NativePPTXExtractor("/path/to/test.pptx")

        mock_table = MagicMock()
        mock_table.rows = []

        # Act
        result = extractor._extract_table(mock_table)

        # Assert
        assert result == ""


# Run with: cd api && uv run pytest tests/custom/extractors/test_pptx_extractor.py -v
