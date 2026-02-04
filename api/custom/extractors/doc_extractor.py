"""
[CUSTOM] Native DOC Extractor wrapper.

Uses unstructured.partition.doc for local DOC extraction.
Requires LibreOffice to be installed on the system.
"""

import logging

from core.rag.extractor.extractor_base import BaseExtractor
from core.rag.models.document import Document

logger = logging.getLogger(__name__)


class NativeDocExtractor(BaseExtractor):
    """
    DOC extractor using unstructured.partition.doc with LibreOffice.

    This extractor uses the unstructured library's local partition_doc function
    which requires LibreOffice to convert DOC files to DOCX before processing.

    If LibreOffice is not available, provides a clear error message guiding
    the user to either install LibreOffice or configure UNSTRUCTURED_API_URL.
    """

    def __init__(self, file_path: str):
        """
        Initialize the extractor.

        Args:
            file_path: Path to the DOC file to extract.
        """
        self._file_path = file_path

    def extract(self) -> list[Document]:
        """
        Extract text content from DOC file.

        Returns:
            List of Document objects with extracted content.

        Raises:
            ValueError: If LibreOffice is not available.
        """
        try:
            from unstructured.partition.doc import partition_doc

            elements = partition_doc(filename=self._file_path)

            # Group content by page if available
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

            # Create documents for each page
            for page, texts in sorted(text_by_page.items()):
                content = "\n".join(texts)
                if content.strip():
                    documents.append(
                        Document(
                            page_content=content.strip(),
                            metadata={
                                "source": self._file_path,
                                "page": page,
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
            logger.exception("Failed to import unstructured.partition.doc")
            raise ValueError(
                "DOC extraction requires the 'unstructured' library with DOC support. "
                "Please ensure 'unstructured[doc]' is installed."
            )

        except Exception as e:
            error_msg = str(e).lower()

            # Check for LibreOffice-related errors
            if "libreoffice" in error_msg or "soffice" in error_msg or "libre" in error_msg:
                logger.warning("LibreOffice not available for DOC extraction: %s", e)
                raise ValueError(
                    "DOC extraction requires LibreOffice to be installed.\n"
                    "Please either:\n"
                    "1. Install LibreOffice in your environment (apt-get install libreoffice-writer-nogui), or\n"
                    "2. Use the custom API Docker image with LibreOffice pre-installed, or\n"
                    "3. Configure UNSTRUCTURED_API_URL and set ETL_TYPE=Unstructured"
                ) from e

            logger.exception("Failed to extract text from DOC: %s", self._file_path)
            raise ValueError(f"Failed to extract text from DOC: {e!s}") from e
