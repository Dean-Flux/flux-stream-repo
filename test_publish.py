"""Regression checks for Kodi's cached HTTP directory listing."""

import hashlib
from html.parser import HTMLParser
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import publish


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = set()

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.hrefs.add(dict(attrs).get("href"))


class RepositoryListingTests(unittest.TestCase):
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
