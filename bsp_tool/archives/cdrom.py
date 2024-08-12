"""ISO-9660 / ECMA-119 Disc Image Format"""
# https://wiki.osdev.org/ISO_9660

from __future__ import annotations
import datetime
import enum
import io
from typing import List

from . import base
from ..utils import binary


# NOTE: Logical Block Address -> Byte Address:
# -- LBA * LB_size = BA


def read_both_endian(stream: io.BytesIO, format_: str) -> int:
    """process one field at a time, don't try for multiple!"""
    little_endian = binary.read_struct(stream, f"<{format_}")
    big_endian = binary.read_struct(stream, f">{format_}")
    assert little_endian == big_endian
    return little_endian


strD = {
    *{chr(x) for x in range(ord("a"), ord("z") + 1)},
    *{chr(x) for x in range(ord("A"), ord("Z") + 1)},
    *{chr(x) for x in range(ord("0"), ord("9") + 1)},
    *"_ "}

strA = {
    *strD,
    *"!\"%&\'()*+,-./:;<=>?"}


def read_strA(stream: io.BytesIO, length: int) -> str:
    raw_str = binary.read_struct(stream, f"{length}s")
    out = raw_str.decode().rstrip(" ")
    assert len(set(out).difference(strA)) == 0
    return out


def read_strD(stream: io.BytesIO, length: int) -> str:
    raw_str = binary.read_struct(stream, f"{length}s")
    out = raw_str.decode().rstrip(" ")
    assert len(set(out).difference(strD)) == 0
    return out


class TimeStamp:
    year: int  # 1..9999
    month: int  # 1..12
    day: int  # 1..31
    hour: int  # 0..23
    minute: int  # 0..59
    second: int  # 0..59
    centisecond: int  # 0..99 (100ths of a second)
    timezone: int

    def __init__(self, year, month, day, hour, minute, second, centisecond, timezone):
        assert 1 <= year <= 9999, year
        self.year = year
        assert 1 <= month <= 12, month
        self.month = month
        assert 1 <= day <= 31, day
        self.day = day
        assert 0 <= hour <= 23, hour
        self.hour = hour
        assert 0 <= minute <= 59, minute
        self.minute = minute
        assert 0 <= second <= 59, second
        self.second = second
        assert 0 <= centisecond <= 99, centisecond
        self.centisecond = centisecond
        # assert 0 <= timezone <= 100, timezone  # !!! BREAKING !!!
        self.timezone = timezone
        # NOTE: timezone is 15 min increments from GMT
        # -- -48 (West) -> 52 (East)
        # -- GMT-12 -> GMT+13

    def __repr__(self) -> str:
        try:
            time_string = self.as_datetime().strftime("%Y/%m/%d (%a) %H:%M:%S.%f")
            return f"<{self.__class__.__name__} {time_string}>"
        except Exception:  # TODO: be more specific
            args = [
                self.year, self.month, self.day,
                self.hour, self.minute, self.second, self.centisecond,
                self.timezone]
            return f"{self.__class__.__name__}({', '.join(args)})"

    def as_datetime(self) -> datetime.datetime:
        # NOTE: year must be >= 1601
        # TODO: timezone
        return datetime.datetime(
            self.year, self.month, self.day,
            self.hour, self.minute, self.second, self.centisecond * 10000)

    @classmethod
    def from_stream_ascii(cls, stream: io.BytesIO) -> TimeStamp:
        """mostly ASCII for PVD (17 bytes)"""
        year = int(read_strD(stream, 4))
        month = int(read_strD(stream, 2))
        day = int(read_strD(stream, 2))
        hour = int(read_strD(stream, 2))
        minute = int(read_strD(stream, 2))
        second = int(read_strD(stream, 2))
        centisecond = int(read_strD(stream, 2))
        timezone = binary.read_struct(stream, "B")
        if {year, month, day, hour, minute, second, centisecond, timezone} == {0}:
            return None  # valid data, but not a timestamp
        return cls(year, month, day, hour, minute, second, centisecond, timezone)

    @classmethod
    def from_stream_bytes(cls, stream: io.BytesIO) -> TimeStamp:
        """compressed form for Directories & Path Table (7 bytes)"""
        year, month, day = binary.read_struct(stream, "3B")
        hour, minute, second = binary.read_struct(stream, "3B")
        centisecond = 0
        timezone = binary.read_struct(stream, "B")
        if {year, month, day, hour, minute, second, centisecond, timezone} == {0}:
            return None  # valid data, but not a timestamp
        return cls(year, month, day, hour, minute, second, centisecond, timezone)


class FileFlag(enum.IntFlag):
    HIDDEN = 1 << 0
    DIRECTORY = 1 << 1
    ASSOCIATED = 1 << 2  # is an "Associated File", whatever that means
    FORMAT_IN_EAR = 1 << 3  # Extended Attribute Record has info on format
    PERMISSIONS_IN_EAR = 1 << 4  # Owner & Group permissions are stored in the EAR
    # NOTE: bits 5 & 6 are reserved
    NOT_FINAL_DIR = 1 << 7


class Directory:
    data_lba: int  # LBA of data extent
    data_size: int  # size of data extent (in bytes)
    recorded: TimeStamp
    flags: FileFlag
    interleaved_unit_size: int  # "file unit size"; 0 if not interleaved
    interleaved_gap_size: int  # 0 if not interleaved
    volume_sequence_index: int  # volume this extent is recorded on
    name: str  # "" for ".", "\\1" for ".."
    index: int

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} "{self.name}" (self.index) @ 0x{id(self):016X}>'

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> Directory:
        out = cls()
        length, ear_length = binary.read_struct(stream, "2B")
        # "Extended Attribute Record"
        out.data_lba = read_both_endian(stream, "I")
        out.data_size = read_both_endian(stream, "I")
        out.recorded = TimeStamp.from_stream_bytes(stream)
        out.flags = FileFlag(binary.read_struct(stream, "B"))
        out.interleaved_unit_size = binary.read_struct(stream, "B")
        out.interleaved_gap_size = binary.read_struct(stream, "B")
        out.volume_sequence_index = read_both_endian(stream, "H")
        file_id_length = binary.read_struct(stream, "B")
        file_id = binary.read_struct(stream, f"{file_id_length}s")
        # NOTE: technically strD w/ a ";" split, but ";" isn't a valid strD char
        if b";" in file_id:
            out.name, out.index = file_id.decode().split(";")
            out.index = int(out.index)
        else:  # HACK: sweep it under the rug for now
            print("!!! SPECIAL DIRECTORY !!!")
            print(f"{file_id_length=}, {file_id=}")
            out.name, out.index = "", 0
        # optional 1 byte pad (next Directory will start on an even address)
        if file_id_length % 2 == 0:
            assert stream.read(1) == b"\x00"
        # TODO: ISO extensions if we haven't reached length
        assert length == 33 + file_id_length + (file_id_length + 1) % 2
        return out


class PrimaryVolumeDescriptor:
    system: str  # who can boot from the first 16 sectors of this disc
    name: str
    size_in_blocks: int  # size of volume in Logical Blocks
    num_discs: int  # in a set
    dics: int  # index of this disc in it's set
    block_size: int  # size of a Logical Block (typically 2048)
    path_table_size: int  # in bytes
    path_table_le_lba: int  # Logical Block Address of Little-Endian Path Table
    opt_path_table_le_lba: int  # Logical Block Address of Optional Little-Endian Path Table
    path_table_be_lba: int  # Logical Block Address of Big-Endian Path Table
    opt_path_table_be_lba: int  # Logical Block Address of Optional Big-Endian Path Table
    # NOTE: optinal path table addresses are 0 if absent
    root_dir: Directory
    set_name: str  # name of the set this dics belongs to
    publisher: str  # name of volume publisher (extended w/ "_" @ start)
    data_preparer: str  # who prepared data for this volume (extended w/ "_" @ start)
    application: str  # how data is recorded (extended w/ "_" @ start)
    copyright_file: str
    abstract_file: str
    bibliography_file: str
    volume_created: TimeStamp
    volume_modified: TimeStamp
    volume_expires: TimeStamp  # when obsolete; can be None
    volume_effective: TimeStamp  # release date; can be None
    application_bytes: bytes  # observed: either all ASCII whitespace or null bytes

    def __init__(self):
        self.system = "Win32"
        self.name = "Untitled"
        # TODO: more defaults

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} "{self.name}" @ 0x{id(self):016X}>'

    def __str__(self) -> str:
        # TODO: pretty printed table of various data
        raise NotImplementedError()

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> PrimaryVolumeDescriptor:
        out = cls()
        type_code = binary.read_struct(stream, "B")
        assert type_code == 0x01
        magic = binary.read_struct(stream, "5s")
        assert magic == b"CD001"
        version = binary.read_struct(stream, "H")  # technically uint8 + 1 char pad
        assert version == 0x0001
        out.system = read_strA(stream, 32)
        out.name = read_strD(stream, 32)
        assert stream.read(8) == b"\x00" * 8
        out.size_in_blocks = read_both_endian(stream, "I")
        assert stream.read(32) == b"\x00" * 32
        out.num_discs = read_both_endian(stream, "H")
        out.disc = read_both_endian(stream, "H")
        out.block_size = read_both_endian(stream, "H")
        out.path_table_size = read_both_endian(stream, "I")  # in bytes
        out.path_table_le_lba = binary.read_struct(stream, "<I")
        out.opt_path_table_le_lba = binary.read_struct(stream, "<I")
        out.path_table_be_lba = binary.read_struct(stream, ">I")
        out.opt_path_table_be_lba = binary.read_struct(stream, ">I")
        out.root_dir = Directory.from_stream(stream)
        # TODO: assert root_dir was 34 bytes long
        out.set_name = read_strD(stream, 128)
        out.publisher = read_strA(stream, 128)
        out.data_preparer = read_strA(stream, 128)
        out.application = read_strA(stream, 128)
        # filenames in root dir
        out.copyright_file = read_strD(stream, 37)
        out.abstract_file = read_strD(stream, 37)
        out.bibliography_file = read_strD(stream, 37)
        # timestamps
        out.volume_created = TimeStamp.from_stream_ascii(stream)
        out.volume_modified = TimeStamp.from_stream_ascii(stream)
        out.volume_expires = TimeStamp.from_stream_ascii(stream)  # when obsolete (can be zeroed?)
        out.volume_effective = TimeStamp.from_stream_ascii(stream)  # release date (can be zeroed?)
        file_structure_version = binary.read_struct(stream, "H")  # techically uint8_t + 1 char pad
        assert file_structure_version == 0x0001
        out.application_bytes = stream.read(512)  # empty ASCII whitespace
        reserved = stream.read(653)  # ISO reserved bytes (typically all NULL)
        assert reserved == b"\x00" * 653, "unexpected data in RESERVED section"
        # NOTE: start of next logical block
        terminator = stream.read(7)
        assert terminator == b"\xFFCD001\x01"
        return out


# TODO: class PathTable(endian="little")


class Iso(base.Archive):
    def __init__(self, filename: str):
        self._from_file(filename)

    def __repr__(self) -> str:
        # TODO: give some data from the PVD + a filecount
        return f'<Iso ... @ 0x{id(self):016X}>'

    def read(self, filename: str) -> bytes:
        raise NotImplementedError()

    def namelist(self) -> List[str]:
        raise NotImplementedError()

    def _from_bytes(self, raw_iso: bytes):
        assert b"\x01CD001" in raw_iso, "Primary Volume Descriptor not found"
        raise NotImplementedError()
        # load pvd
        # hook filesystem
        # we might want to target a specific PVD in future
        # -- should give an option to specify it's address / index

    def _from_file(self, filename: str):
        with open(filename, "rb") as iso_file:
            self._from_stream(iso_file)

    def _from_stream(self, stream: io.BytesIO):
        self._from_bytes(stream.read())
