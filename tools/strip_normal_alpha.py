"""Remove an unused opaque BC3 alpha channel while preserving decoded RGB in every mip.

Usage: python tools/strip_normal_alpha.py input_normal.dds output_normal.dds
Requires Pillow. Intentional height data is rejected rather than discarded.
"""
import argparse
import io
from pathlib import Path
import struct

from PIL import Image, ImageChops


def mip_images(data):
    if data[:4] != b"DDS " or len(data) < 128:
        raise ValueError("Expected a complete DDS header")
    block_size = {b"DXT1": 8, b"DXT5": 16}.get(data[84:88])
    if block_size is None:
        raise ValueError("Only BC1/DXT1 and BC3/DXT5 are supported")
    width, height = struct.unpack_from("<I", data, 16)[0], struct.unpack_from("<I", data, 12)[0]
    count = struct.unpack_from("<I", data, 28)[0] or 1
    if not width or not height or count > max(width, height).bit_length():
        raise ValueError("Invalid texture dimensions or mip count")
    offset = 128
    for _ in range(count):
        size = max(1, (width + 3) // 4) * max(1, (height + 3) // 4) * block_size
        if offset + size > len(data):
            raise ValueError("Truncated mip data")
        header = bytearray(data[:128])
        struct.pack_into("<I", header, 12, height)
        struct.pack_into("<I", header, 16, width)
        struct.pack_into("<I", header, 20, size)
        struct.pack_into("<I", header, 28, 1)
        with Image.open(io.BytesIO(header + data[offset:offset + size])) as image:
            yield image.convert("RGBA")
        offset += size
        width, height = max(1, width // 2), max(1, height // 2)
    if offset != len(data):
        raise ValueError("Unexpected DDS payload length")


def remove_opaque_alpha(data):
    if data[84:88] != b"DXT5":
        raise ValueError("Source must be BC3/DXT5")
    originals = list(mip_images(data))
    if any(image.getchannel("A").getextrema() != (255, 255) for image in originals):
        raise ValueError("Normal map contains non-opaque alpha; preserve its intentional height data")
    header = bytearray(data[:128])
    header[84:88] = b"DXT1"
    struct.pack_into("<I", header, 80, 4)  # DDPF_FOURCC, no alpha flag
    struct.pack_into("<I", header, 20, struct.unpack_from("<I", header, 20)[0] // 2)
    output = bytearray(header)
    for offset in range(128, len(data), 16):
        color0, color1, indices = struct.unpack_from("<HHI", data, offset + 8)
        if color0 < color1:
            color0, color1 = color1, color0
            indices ^= 0x55555555  # swap selectors 0/1 and 2/3 to retain four-colour interpolation
        elif color0 == color1:
            indices = 0  # all BC3 colours were equal; avoid BC1's transparent selector
        output.extend(struct.pack("<HHI", color0, color1, indices))
    result = bytes(output)
    converted = list(mip_images(result))
    if len(originals) != len(converted):
        raise ValueError("Mip count changed")
    for level, (before, after) in enumerate(zip(originals, converted)):
        if ImageChops.difference(before.convert("RGB"), after.convert("RGB")).getbbox() is not None:
            raise ValueError(f"Decoded normal-map RGB changed in mip {level}")
        if after.getchannel("A").getextrema() != (255, 255):
            raise ValueError(f"Unexpected transparency in mip {level}")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    data = args.source.read_bytes()
    converted = remove_opaque_alpha(data)
    args.destination.write_bytes(converted)
    print(f"{args.destination}: BC1, {len(converted)} bytes; all decoded RGB pixels/mips preserved")


if __name__ == "__main__":
    main()
