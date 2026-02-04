"""
[CUSTOM] Native PPT Extractor wrapper.

Uses unstructured.partition.ppt for local PPT extraction.
Requires LibreOffice to be installed on the system.
"""

import logging

from core.rag.extractor.extractor_base import BaseExtractor
from core.rag.models.document import Document

logger = logging.getLogger(__name__)


class NativePPTExtractor(BaseExtractor):
    """
    PPT extractor using unstructured.partition.ppt with LibreOffice.

    This extractor uses the unstructured library's local partition_ppt function
    which requires LibreOffice to convert PPT files to PPTX before processing.

    If LibreOffice is not available, provides a clear error message guiding
    the user to either install LibreOffice or configure UNSTRUCTURED_API_URL.
    """

    def __init__(self, file_path: str):
        """
        Initialize the extractor.

        Args:
            file_path: Path to the PPT file to extract.
        """
        self._file_path = file_path

    def extract(self) -> list[Document]:
        """
        Extract text content from PPT file.

        Returns:
            List of Document objects with extracted content.

        Raises:
            ValueError: If LibreOffice is not available.
        """
        try:
            from unstructured.partition.ppt import partition_ppt

            elements = partition_ppt(filename=self._file_path)

            # Group content by page/slide if available
            text_by_page: dict[int, list[str]] = {}
            unassigned_text: list[str] = []

            for element in elements:
                text = getattr(element, "text", "")
                if not text or not text.strip():
                    continue

                page = getattr(getattr(element, "metadata", None), "page_number", None)
                if page is not None:
                    if page not in text_by_page:
                        text_by_page[page] = []
                    text_by_page[page].append(text.strip())
                else:
                    unassigned_text.append(text.strip())

            documents = []

            # Create documents for each page/slide
            for page, texts in sorted(text_by_page.items()):
                content = "\n".join(texts)
                if content.strip():
                    documents.append(
                        Document(
                            page_content=content.strip(),
                            metadata={
                                "source": self._file_path,
                                "slide": page,
                            },
                        )
                    )

            # Create a document for unassigned text
            if unassigned_text:
                content = "\n".join(unassigned_text)
                if content.strip():
                    if documents:
                        # Append to the last document or create a new one
                        documents[-1].page_content += "\n\n" + content.strip()
                    else:
                        documents.append(
                            Document(
                                page_content=content.strip(),
                                metadata={"source": self._file_path},
                            )
                        )

            # Fallback: if no pages were detected, create a single document
            if not documents:
                all_text = "\n".join([getattr(el, "text", "") for el in elements if getattr(el, "text", "")])
                if all_text.strip():
                    documents.append(
                        Document(
                            page_content=all_text.strip(),
                            metadata={"source": self._file_path},
                        )
                    )

            return documents

        except ImportError:
            logger.exception("Failed to import unstructured.partition.ppt")
            raise ValueError(
                "PPT extraction requires the 'unstructured' library with PPT support. "
                "Please ensure 'unstructured[ppt]' is installed."
            )

        except Exception as e:
            error_msg = str(e).lower()

            # Check for LibreOffice-related errors
            if "libreoffice" in error_msg or "soffice" in error_msg or "libre" in error_msg:
                logger.warning("LibreOffice not available for PPT extraction: %s", e)
                raise ValueError(
                    "PPT extraction requires LibreOffice to be installed.\n"
                    "Please either:\n"
                    "1. Install LibreOffice in your environment (apt-get install libreoffice-impress-nogui), or\n"
                    "2. Use the custom API Docker image with LibreOffice pre-installed, or\n"
                    "3. Configure UNSTRUCTURED_API_URL and set ETL_TYPE=Unstructured"
                ) from e

            logger.exception("Failed to extract text from PPT: %s", self._file_path)
            raise ValueError(f"Failed to extract text from PPT: {e!s}") from e
