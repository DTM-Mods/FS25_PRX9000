"""Regression guard: concrete normals must have no alpha/parallax channel and a full mip chain."""
from pathlib import Path
import struct
import sys


def verify(path):
    data = path.read_bytes()
    assert data[:4] == b"DDS " and len(data) >= 128, "Invalid DDS header"
    assert data[84:88] == b"DXT1", "Concrete normal must use three-channel BC1, never BC3/RGBA parallax"
    assert struct.unpack_from("<I", data, 80)[0] == 4, "Unexpected alpha/pixel-format flags"
    width, height = struct.unpack_from("<I", data, 16)[0], struct.unpack_from("<I", data, 12)[0]
    mips = struct.unpack_from("<I", data, 28)[0]
    assert width > 0 and height > 0 and width & (width - 1) == 0 and height & (height - 1) == 0
    assert mips == max(width, height).bit_length(), "Incomplete mip chain"
    offset = 128
    for level in range(mips):
        blocks = max(1, (width + 3) // 4) * max(1, (height + 3) // 4)
        end = offset + blocks * 8
        assert end <= len(data), f"Truncated mip {level}"
        for color0, color1, indices in struct.iter_unpack("<HHI", data[offset:end]):
            if color0 <= color1:
                assert all(((indices >> shift) & 3) != 3 for shift in range(0, 32, 2)), "Transparent BC1 selector"
        offset = end
        width, height = max(1, width // 2), max(1, height // 2)
    assert offset == len(data), "Unexpected DDS payload length"
    print(f"PASS: {path.name}, BC1/no alpha, all {mips} mip levels complete, {len(data)} bytes")


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "textures/prx9000_concrete_normal.dds"
    verify(path)
