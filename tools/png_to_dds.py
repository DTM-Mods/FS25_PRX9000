"""Convert PNG to DDS with a full mip chain, preserving three-channel normal maps.

RGB *_normal.png -> BC1 (no accidental parallax); RGBA normals -> BC3 (height preserved).
Other texture types retain the previous BC3 conversion behavior.
Usage: python tools/png_to_dds.py input.png output.dds [--normal-rgb]
"""
import argparse
import io
from pathlib import Path
import struct

from PIL import Image
from strip_normal_alpha import remove_opaque_alpha


def convert(source, normal_rgb=False):
    with Image.open(source) as original:
        has_alpha = "A" in original.getbands() or "transparency" in original.info
        rgb_normal = normal_rgb or (source.stem.lower().endswith("_normal") and not has_alpha)
        image = original.convert("RGBA")
    if rgb_normal and image.getchannel("A").getextrema() != (255, 255):
        raise ValueError("--normal-rgb would remove non-opaque height data")
    levels = []
    size = image.size
    while True:
        level = image.resize(size, Image.Resampling.LANCZOS) if size != image.size else image
        buffer = io.BytesIO()
        level.save(buffer, "DDS", pixel_format="DXT5")
        levels.append(buffer.getvalue())
        if size == (1, 1):
            break
        size = max(1, size[0] // 2), max(1, size[1] // 2)
    header = bytearray(levels[0][:128])
    struct.pack_into("<I", header, 8, struct.unpack_from("<I", header, 8)[0] | 0x20000)
    struct.pack_into("<I", header, 28, len(levels))
    struct.pack_into("<I", header, 108, struct.unpack_from("<I", header, 108)[0] | 0x400008)
    data = bytes(header) + b"".join(level[128:] for level in levels)
    return remove_opaque_alpha(data) if rgb_normal else data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--normal-rgb", action="store_true", help="Remove an unused opaque alpha from a normal map")
    args = parser.parse_args()
    data = convert(args.source, normal_rgb=args.normal_rgb)
    args.destination.write_bytes(data)
    print(f"{args.destination}: {data[84:88].decode()}, {struct.unpack_from('<I', data, 28)[0]} mip levels")


if __name__ == "__main__":
    main()
