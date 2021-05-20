"""exceptions.py"""


class DocumentNotFound(Exception):
    """Raised on document not found in db."""

    def __init__(self, path) -> None:
        self.path = path

    def __str__(self) -> str:
        return f"Docuemnt {self.path!r} not found"
