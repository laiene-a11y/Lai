from markitdown import MarkItDown, StreamInfo
from io import BytesIO
from pathlib import Path
from pydantic import Field

SUPPORTED_EXTENSIONS = ("pdf", "docx")


def binary_document_to_markdown(
    binary_data: bytes = Field(
        description="The raw bytes of the document to convert"
    ),
    file_type: str = Field(
        description="The file extension identifying the document format, "
        "without a leading dot (e.g. 'docx', 'pdf', 'pptx', 'xlsx', 'html')"
    ),
) -> str:
    """Convert a binary document to markdown-formatted text.

    Reads in-memory document bytes and uses MarkItDown to produce a markdown
    representation of the document's textual content, preserving structure such
    as headings, lists, and tables where the source format allows.

    When to use:
    - When you have document bytes (e.g. an uploaded or downloaded file) and
      need their text content as markdown for an LLM to read or summarize.
    - For office and web formats supported by MarkItDown such as DOCX, PDF,
      PPTX, XLSX, and HTML.

    When not to use:
    - For plain text or files that are already markdown; no conversion is needed.
    - For images or audio where no textual content can be extracted.

    Examples:
    >>> with open("report.docx", "rb") as f:
    ...     binary_document_to_markdown(f.read(), "docx")
    '# Quarterly Report\\n\\nRevenue grew...'
    """
    md = MarkItDown()
    file_obj = BytesIO(binary_data)
    stream_info = StreamInfo(extension=file_type)
    result = md.convert(file_obj, stream_info=stream_info)
    return result.text_content


def document_path_to_markdown(
    file_path: str = Field(
        description="Filesystem path to a PDF or DOCX document to convert"
    ),
) -> str:
    """Read a PDF or DOCX file from disk and convert it to markdown text.

    Resolves the given path, reads the document's bytes, infers the format from
    the file extension, and converts the content to a markdown representation
    using MarkItDown. This is a path-based convenience wrapper around
    binary_document_to_markdown.

    When to use:
    - When a PDF or DOCX file already exists on the local filesystem and you
      need its text content as markdown for an LLM to read or summarize.

    When not to use:
    - When you only have the document's bytes in memory (no path on disk);
      use binary_document_to_markdown instead.
    - For formats other than PDF and DOCX; this tool rejects them.

    Raises:
        FileNotFoundError: if no file exists at file_path.
        ValueError: if the file extension is not a supported format.

    Examples:
    >>> document_path_to_markdown("reports/q3.pdf")
    '# Quarterly Report\\n\\nRevenue grew...'
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"No file found at path: {file_path}")

    file_type = path.suffix.lstrip(".").lower()
    if file_type not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(SUPPORTED_EXTENSIONS)
        raise ValueError(
            f"Unsupported file type '{file_type}'. Supported formats: {supported}"
        )

    return binary_document_to_markdown(path.read_bytes(), file_type)
