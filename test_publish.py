"""Regression checks for Kodi's cached HTTP directory listing."""

import hashlib
from html.parser import HTMLParser
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import publish


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = set()

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.hrefs.add(dict(attrs).get("href"))


class RepositoryListingTests(unittest.TestCase):
    def test_retention_keeps_two_numeric_releases_and_unrelated_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            names = ["plugin.video.personalstream-1.9.0.zip", "plugin.video.personalstream-1.10.0.zip",
                     "plugin.video.personalstream-1.11.0.zip", "plugin.video.personalstream-notes.zip",
                     "skin.fluxstream-1.0.0.zip"]
            for name in names:
                (folder / name).write_bytes(b"test")
            publish.retain_latest_two(folder, "plugin.video.personalstream")
            self.assertEqual({p.name for p in folder.iterdir()}, set(names[1:]))

    def test_skin_and_helper_remain_in_catalog_after_plugin_publication(self):
        source = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(source / publish.REPO_ID, root / publish.REPO_ID)
            shutil.copyfile(source / "LICENSE", root / "LICENSE")
            with patch.object(publish, "ROOT", root):
                for addon_id in reversed(publish.ADDON_IDS):
                    package = root / (addon_id + ".zip")
                    with ZipFile(package, "w") as archive:
                        archive.writestr(addon_id + "/addon.xml", '<addon id="{}" version="1.0.0" />'.format(addon_id))
                    publish.publish(package)
            ids = {row.get("id") for row in ET.parse(root / "addons.xml").getroot()}
            self.assertEqual(ids, set(publish.ADDON_IDS) | {publish.REPO_ID})

    def test_catalog_and_checksum_remain_visible_to_kodi(self):
        source = Path(__file__).resolve().parent
        package = max((source / publish.PLUGIN_ID).glob("*.zip"))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(source / publish.REPO_ID, root / publish.REPO_ID)
            shutil.copyfile(source / "LICENSE", root / "LICENSE")
            with patch.object(publish, "ROOT", root):
                publish.publish(package)
            links = Links()
            links.feed((root / "index.html").read_text(encoding="utf-8"))
            self.assertTrue({"addons.xml", "addons.xml.md5",
                             publish.PLUGIN_ID + "/", publish.REPO_ID + "/",
                             "repository.fluxstream-1.0.0.zip", "about.html", "privacy.html"}.issubset(links.hrefs))
            self.assertEqual(
                hashlib.md5((root / "addons.xml").read_bytes()).hexdigest(),
                (root / "addons.xml.md5").read_text(encoding="ascii"))


if __name__ == "__main__":
    unittest.main()
