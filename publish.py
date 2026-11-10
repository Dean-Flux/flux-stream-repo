"""Publish a built Flux Stream ZIP into this static Kodi repository."""

import argparse
import hashlib
from pathlib import Path, PurePosixPath
import re
import shutil
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parent
PLUGIN_ID = "plugin.video.personalstream"
REPO_ID = "repository.fluxstream"


def version(addon):
    value = addon.get("version", "")
    if not re.fullmatch(r"\d+\.\d+\.\d+", value):
        raise ValueError("Expected a three-part numeric add-on version")
    return tuple(int(part) for part in value.split("."))


def publish(package):
    package = Path(package).resolve()
    with ZipFile(package) as archive:
        manifest = ET.fromstring(archive.read(PLUGIN_ID + "/addon.xml"))
        if manifest.get("id") != PLUGIN_ID:
            raise ValueError("Expected the Flux Stream add-on ID")
        version(manifest)
        if archive.testzip() is not None:
            raise ValueError("Package failed its CRC integrity check")
        if any(not name.startswith(PLUGIN_ID + "/") for name in archive.namelist()):
            raise ValueError("Package has an unexpected top-level folder")
        folder = ROOT / PLUGIN_ID
        target = folder / "{}-{}.zip".format(PLUGIN_ID, manifest.get("version"))
        if target.exists() and target.read_bytes() != package.read_bytes():
            raise ValueError("Bump the version instead of replacing a published package")
        # Validate advertised artwork before writing files outside the package.
        artwork = []
        for asset in manifest.findall("./extension[@point='xbmc.addon.metadata']/assets/*"):
            name = asset.text or ""
            path = PurePosixPath(name)
            if not name or path.is_absolute() or ".." in path.parts or "\\" in name or ":" in name:
                raise ValueError("Unsafe artwork path")
            artwork.append((name, archive.read(PLUGIN_ID + "/" + name)))
        folder.mkdir(exist_ok=True)
        if package != target:
            shutil.copyfile(package, target)
        for name, data in artwork:
            output = folder / name
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(data)

    repo_folder = ROOT / REPO_ID
    repo_manifest = ET.parse(repo_folder / "addon.xml").getroot()
    version(repo_manifest)
    repo_zip = ROOT / "{}-{}.zip".format(REPO_ID, repo_manifest.get("version"))
    with ZipFile(repo_zip, "w", ZIP_DEFLATED) as archive:
        archive.write(repo_folder / "addon.xml", REPO_ID + "/addon.xml")
        archive.write(ROOT / "LICENSE", REPO_ID + "/LICENSE")
    shutil.copyfile(repo_zip, repo_folder / repo_zip.name)

    catalog = ET.Element("addons")
    catalog.append(repo_manifest)
    packages = list(folder.glob(PLUGIN_ID + "-*.zip"))
    manifests = []
    for item in packages:
        with ZipFile(item) as archive:
            manifests.append(ET.fromstring(archive.read(PLUGIN_ID + "/addon.xml")))
    catalog.append(max(manifests, key=version))
    data = ET.tostring(catalog, encoding="utf-8", xml_declaration=True)
    (ROOT / "addons.xml").write_bytes(data)
    (ROOT / "addons.xml.md5").write_text(hashlib.md5(data).hexdigest(), encoding="ascii")
    (ROOT / "index.html").write_text(
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>Flux Stream Repository</title></head><body>'
        '<h1>Flux Stream Repository</h1><p>Kodi 21 or newer.</p>'
        '<p><a href="' + repo_zip.name + '">' + repo_zip.name + '</a></p>'
        # Kodi caches HTTP listings; unlisted catalog files can be treated as missing.
        '<p><a href="addons.xml">addons.xml</a> '
        '<a href="addons.xml.md5">addons.xml.md5</a> '
        '<a href="plugin.video.personalstream/">plugin.video.personalstream/</a> '
        '<a href="repository.fluxstream/">repository.fluxstream/</a></p>'
        '<p>Install this repository ZIP, then choose Install from repository &gt; '
        'Flux Stream Repository &gt; Video add-ons &gt; Flux Stream.</p>'
        '<p>Enable Auto-update for Flux Stream. CocoScrapers must be installed separately. '
        'Trakt authorization currently supports only the app owner and invited testers.</p>'
        '<p><a href="https://github.com/Dean-Flux/flux-stream-repo">Source and instructions</a></p>'
        '</body></html>\n', encoding="utf-8")
    print("Published", target.name, "and", repo_zip.name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    publish(parser.parse_args().package)
