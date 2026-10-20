#!/usr/bin/env python3
"""Turn an unpacked VectorCraft web release into an offline-capable site (PWA).

usage: build_site.py <unzipped_dir> <out_dir> --tag <release tag>

<unzipped_dir> holds the folder from vectorcraft-web-<version>.zip. The upstream files
(index.html, the hashed .js and .wasm) are copied unchanged; only index.html gets three
extra lines: the manifest link, the home-screen icon and the service-worker registration.
"""
import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"

# Upstream files that are not part of the running app: left in the site (licences must stay),
# but not downloaded into the offline cache.
NOT_PRECACHED_NAMES = {"README.md", "HOSTING.md", "ASSETS.md", "NOTICE", "sw.js", ".nojekyll"}
NOT_PRECACHED_PREFIXES = ("LICENSE", "licenses/")
# Host-specific rule files that do nothing on GitHub Pages.
REMOVED = {"_headers", ".htaccess"}

HEAD_INSERT = """  <link rel="manifest" href="./manifest.webmanifest">
  <link rel="apple-touch-icon" href="./icons/icon-180.png">
  <script>
    // The web build has no Korean font, so a Korean interface shows empty boxes.
    // Report English to the app in that case; other languages are left alone.
    (function () {
      try {
        var first = (navigator.languages && navigator.languages[0]) || navigator.language || '';
        if (/^ko/i.test(first)) {
          var langs = ['en-US', 'en'];
          Object.defineProperty(navigator, 'languages', { get: function () { return langs; }, configurable: true });
          Object.defineProperty(navigator, 'language', { get: function () { return langs[0]; }, configurable: true });
        }
      } catch (e) {}
    })();
  </script>
  <script>
    // Offline use: cache the app after it has started, and ask the browser to keep it.
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', function () {
        navigator.serviceWorker.register('./sw.js').catch(function () {});
        try { if (navigator.storage && navigator.storage.persist) navigator.storage.persist(); } catch (e) {}
      });
    }
  </script>
"""


def find_site_root(unzipped: Path) -> Path:
    candidates = [p.parent for p in unzipped.rglob("index.html")]
    if len(candidates) != 1:
        sys.exit(f"expected exactly one index.html under {unzipped}, found {len(candidates)}")
    return candidates[0]


def precache_list(out: Path) -> list[str]:
    files = []
    for path in sorted(out.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(out).as_posix()
        if path.name in NOT_PRECACHED_NAMES or rel.startswith(NOT_PRECACHED_PREFIXES):
            continue
        files.append("./" + rel)
    return ["./"] + files


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("unzipped")
    parser.add_argument("out")
    parser.add_argument("--tag", required=True)
    args = parser.parse_args()

    src = find_site_root(Path(args.unzipped))
    out = Path(args.out)
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(src, out)
    for name in REMOVED:
        (out / name).unlink(missing_ok=True)

    index = out / "index.html"
    html = index.read_text(encoding="utf-8")
    if "</head>" not in html:
        sys.exit("index.html has no </head>; the upstream page layout changed, update build_site.py")
    if "manifest.webmanifest" in html:
        sys.exit("index.html is already patched")
    index.write_text(html.replace("</head>", HEAD_INSERT + "</head>", 1), encoding="utf-8")

    shutil.copy(TEMPLATES / "manifest.webmanifest", out / "manifest.webmanifest")
    shutil.copytree(TEMPLATES / "icons", out / "icons")
    (out / ".nojekyll").write_text("", encoding="utf-8")

    files = precache_list(out)
    # A fingerprint of every small file we serve (the big .js/.wasm names already carry a
    # hash). It goes into sw.js so that any change to index.html, the manifest or the icons
    # makes the browser install a new version.
    digest = hashlib.sha256()
    for f in files:
        path = out / f[2:]
        if f != "./" and path.stat().st_size < 1_000_000:
            digest.update(f.encode() + b"\0" + path.read_bytes() + b"\0")
        else:
            digest.update(f.encode() + b"\0")
    build_id = digest.hexdigest()[:12]
    sw = (TEMPLATES / "sw.template.js").read_text(encoding="utf-8")
    sw = (sw.replace("__TAG__", args.tag).replace("__BUILD__", build_id)
            .replace("__FILES__", json.dumps(files, indent=2)))
    (out / "sw.js").write_text(sw, encoding="utf-8")

    total = sum((out / f[2:]).stat().st_size for f in files if f != "./")
    print(f"release {args.tag} build {build_id}: {len(files)} cached entries, {total / 1e6:.1f} MB")
    for f in files:
        print("  ", f)


if __name__ == "__main__":
    main()
