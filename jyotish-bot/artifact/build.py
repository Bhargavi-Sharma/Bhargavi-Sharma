"""Copy the artifact into dist/, escaping non-ASCII characters in the JS files as \\uXXXX so they
decode correctly whatever charset the host serves scripts with."""
from pathlib import Path

HERE = Path(__file__).parent
DIST = HERE / "dist"
DIST.mkdir(exist_ok=True)


def ascii_js(text: str) -> str:
    out = []
    for c in text:
        o = ord(c)
        if o < 128:
            out.append(c)
        elif o < 0x10000:
            out.append(f"\\u{o:04x}")
        else:  # surrogate pair
            o -= 0x10000
            out.append(f"\\u{0xD800 + (o >> 10):04x}\\u{0xDC00 + (o & 0x3FF):04x}")
    return "".join(out)


for name in ("astro.js", "engine-core.js", "engine-rules.js", "engine-time.js", "cities.js"):
    (DIST / name).write_text(ascii_js((HERE / name).read_text(encoding="utf-8")), encoding="ascii")
(DIST / "index.html").write_text((HERE / "index.html").read_text(encoding="utf-8"), encoding="utf-8")
print("built", sorted(p.name for p in DIST.iterdir()))
