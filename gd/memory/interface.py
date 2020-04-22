import ctypes
import sys

try:
    from .win import get_base_address, get_handle, get_pid_from_name, read_process_memory
except Exception:  # noqa
    pass

from .enums import Scene

from ..typing import Tuple
from ..utils.text_tools import make_repr

__all__ = ("Memory", "MemoryType", "get_memory")


class MemoryType:
    """Pure type for Memory objects to inherit from."""

    pass


class Result:
    """Type that allows to unwrap bytes that were read into different Python types."""

    def __init__(self, data: bytes) -> None:
        self.data = data

    def __repr__(self) -> str:
        info = {"data": repr(self.to_str())}
        return make_repr(self, info)

    def to_str(self) -> str:
        return " ".join(format(byte, "02x") for byte in self.data)

    def as_int(self, byte_order: str = "little") -> int:
        return int.from_bytes(self.data, byte_order)


class Memory(MemoryType):
    """Simple wrapper with platform check."""

    def __new__(cls, *args, **kwargs) -> MemoryType:
        if sys.platform == "win32":
            return WinMemory(*args, **kwargs)
        else:
            raise OSError("Only Windows is currently supported.")


class WinMemory(MemoryType):
    PTR_LEN = 4

    loaded = False
    process_handle = 0
    process_id = 0
    process_name = "undefined"
    base_address = 0

    def __init__(self, process_name: str, load: bool = False) -> None:
        self.process_name = process_name

        if load:
            self.load()

    def __repr__(self) -> str:
        info = {
            "name": repr(self.process_name),
            "pid": self.process_id,
            "base_addr": format(self.base_address, "x"),
            "handle": format(self.process_handle, "x"),
            "loaded": self.loaded,
        }
        return make_repr(self, info)

    def read_bytes(self, n: int = 0, address: int = 0, *offsets) -> Result:
        address = self.base_address + address
        final_buffer = ctypes.create_string_buffer(n)

        for offset in offsets:
            buffer = ctypes.create_string_buffer(self.PTR_LEN)
            read_process_memory(
                self.process_handle,
                ctypes.c_void_p(address),
                ctypes.byref(buffer),
                self.PTR_LEN,
                None,
            )
            address = int.from_bytes(buffer.raw, "little") + offset

        read_process_memory(
            self.process_handle, ctypes.c_void_p(address), ctypes.byref(final_buffer), n, None,
        )

        return Result(final_buffer.raw)

    def load(self) -> None:
        self.process_id = get_pid_from_name(self.process_name)
        self.process_handle = get_handle(self.process_id)
        self.base_address = get_base_address(self.process_id, self.process_name)
        self.loaded = True

    def is_loaded(self) -> bool:
        return self.loaded

    def reload(self) -> None:
        self.load()

    def get_scene_value(self) -> int:
        return self.read_bytes(4, 0x3222D0, 0x1DC).as_int()

    def get_scene(self) -> Scene:
        return Scene.from_value(self.get_scene_value())

    def get_resolution_value(self) -> int:
        return self.read_bytes(4, 0x3222D0, 0x2E0).as_int()

    def get_resolution(self) -> Tuple[int, int]:
        return resolution_from_value(self.get_resolution_value())

    def get_level_id(self) -> int:
        return self.read_bytes(4, 0x3222D0, 0x2A0).as_int()


def resolution_from_value(value: int) -> Tuple[int, int]:
    mapping = {
        1: (640, 480),
        2: (720, 480),
        3: (720, 576),
        4: (800, 600),
        5: (1024, 768),
        6: (1152, 864),
        7: (1176, 644),
        8: (1280, 720),
        9: (1280, 768),
        10: (1280, 800),
        11: (1280, 960),
        12: (1280, 1024),
        13: (1360, 768),
        14: (1366, 768),
        15: (1440, 900),
        16: (1600, 900),
        17: (1600, 1024),
        18: (1680, 1050),
        19: (1768, 992),
        20: (1920, 1080),
    }
    return mapping.get(value, (0, 0))


def get_memory(name: str = "GeometryDash.exe") -> MemoryType:
    return Memory(name, load=True)