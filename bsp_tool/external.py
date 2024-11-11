from __future__ import annotations
import io


class File:
    """read-only streamed binary file wrapper"""
    filename: str
    archive: object  # ArchiveClass
    _stream: io.BytesIO  # cached file handle

    def __init__(self, filename: str, archive=None):
        self.archive = archive
        self.filename = filename
        self._stream = None

    def __repr__(self) -> str:
        if self.archive is not None:
            descriptor = f"'{self.filename}' in {repr(self.archive)}"
        else:
            descriptor = f"'{self.filename}'"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    @property
    def stream(self) -> io.BytesIO:
        """deferring opening the file until it's touched"""
        if self._stream is None:
            if self.archive is None:
                self._stream = open(self.filename, "rb")
            else:
                self._stream = io.BytesIO(self.archive.read(self.filename))
        return self._stream

    # exposed self.stream methods
    def read(self, length: int = -1) -> bytes:
        return self.stream.read(length)

    def seek(self, offset: int, whence: int = 0) -> int:
        return self.stream.seek(offset, whence)

    def tell(self) -> int:
        return self.stream.tell()

    @classmethod
    def from_archive(cls, filename: str, archive) -> File:
        return cls(filename, archive)

    @classmethod
    def from_bytes(cls, filename: str, raw_data: bytes) -> File:
        return cls.from_stream(io.BytesIO(raw_data))

    @classmethod
    def from_file(cls, filename: str) -> File:
        return cls(filename)

    @classmethod
    def from_stream(cls, filename: str, stream: io.BytesIO) -> File:
        out = cls(filename)
        out._stream = stream
        return out
