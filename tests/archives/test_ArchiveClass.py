import pytest

from bsp_tool.archives import base
from bsp_tool.archives import bluepoint
from bsp_tool.archives import cdrom
from bsp_tool.archives import gearbox
from bsp_tool.archives import id_software
from bsp_tool.archives import infinity_ward
from bsp_tool.archives import mame
from bsp_tool.archives import nexon
from bsp_tool.archives import padus
from bsp_tool.archives import pi_studios
from bsp_tool.archives import pkware
from bsp_tool.archives import respawn
from bsp_tool.archives import sega
from bsp_tool.archives import utoplanet
from bsp_tool.archives import valve


archive_classes = [
    bluepoint.Bpk,
    cdrom.Iso,
    gearbox.Nightfire007,
    id_software.Pak,
    id_software.Pk3,
    infinity_ward.FastFile,
    infinity_ward.Iwd,
    mame.Chd,
    nexon.Hfs,
    nexon.Pkg,
    padus.Cdi,
    pi_studios.Bpk,
    pkware.Zip,
    respawn.RPak,
    respawn.Vpk,
    sega.GDRom,
    sega.Gdi,
    utoplanet.Apk,
    valve.Vpk]


def class_name(cls: object) -> str:
    short_module = cls.__module__.split(".")[-1]
    return ".".join([short_module, cls.__name__])


@pytest.mark.xfail
@pytest.mark.parametrize("archive_class", archive_classes, ids=map(class_name, archive_classes))
def test_in_spec(archive_class: object):
    assert issubclass(archive_class, base.Archive), "not a base.Archive subclass"
    assert hasattr(archive_class, "ext"), "ext not specified"
    assert isinstance(archive_class.ext, str), "ext must be of type str"
    assert archive_class.ext.startswith("*"), "ext must start with wildcard"
    # NOTE: expected formats are "*_dir.vpk" & "*.ext"
    # NOTE: if a subclass has namelist & read base.Archive can do the rest
    assert hasattr(archive_class, "namelist"), "no namelist method"
    assert hasattr(archive_class, "read"), "no read method"
    # TODO: .from_stream / .from_bytes / .from_file classmethods
