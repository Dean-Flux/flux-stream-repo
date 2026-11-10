# Flux Stream Repository

Kodi source URL: **https://dean-flux.github.io/flux-stream-repo/**

## Install once

1. In Kodi, open Settings > File manager > Add source.
2. Enter the source URL above and name it Flux Stream.
3. Under Settings > System > Add-ons, enable Unknown sources if needed.
4. Open Add-ons > Install from zip file > Flux Stream and choose `repository.fluxstream-1.0.0.zip`.
5. Choose Install from repository > Flux Stream Repository > Video add-ons > Flux Stream.
6. If Flux Stream is already installed manually, open its information screen and choose Update or Versions, then select the Flux Stream Repository version once.
7. Leave Auto-update enabled for Flux Stream and set Kodi's Updates preference to Install updates automatically if automatic installation is wanted.

The same add-on ID (`plugin.video.personalstream`) preserves the existing account settings and progress. Restart Kodi after upgrading this initial build. CocoScrapers must be installed separately from its developer's repository. Kodi's ordinary dependency resolver handles requests and routing from the official Kodi repository.

This is a development build targeting Kodi 21. TorBox cached playback has been confirmed by the owner. Full Trakt QR login and progress tracking still need live device confirmation. Trakt's application is registered in Development mode for its owner and invited testers; public downloads do not grant other users Trakt application access.

## Publish a future update

Bump the Flux Stream version, run its `package.py`, then run this from this checkout:

```powershell
python publish.py 'C:/path/to/plugin.video.personalstream-0.2.5.zip'
git diff --stat
git add --all
git commit -m 'Publish Flux Stream 0.2.5'
git push origin main
```

The publisher regenerates the repository installer, catalog, checksum, and download page. GitHub Pages serves the main branch root. Kodi sees a new version after Pages deploys and its next repository check. Never replace different contents under an existing published version.

The add-on's complete packaged Python source, build instructions, upstream notices, and license are included in its ZIP. GitHub's Source code ZIP for this distribution repository is not a Kodi installer. Development history is maintained separately in a private repository.

## Licensing and attribution

The repository installer and publisher use the MIT license in this repository's LICENSE. Flux Stream is derived from Jacktook by Sam-Max, snapshot `cb3bd2d2dc08dd35a98aabc668f319e31137fff9`. Its original notices and LICENSE remain in the add-on package. Upstream has inconsistent GPL metadata (the included LICENSE says GPL version 3; the manifest says GPL-2.0-only); this has not been independently resolved. Inherited artwork remains a development placeholder. This repository does not claim ownership of upstream code or artwork.

## Included metadata

Flux Stream 0.2.7 and newer includes the owner-approved TMDB application key. Family members do not need a TMDB account or a developer key; leave the Expert key override blank. Settings > Metadata > About / TMDB credits provides attribution. Each person connects their own TorBox and Trakt account, and CocoScrapers is installed separately.

## Trakt notice and privacy

Flux Stream uses Trakt but is not endorsed or certified by Trakt.

[Privacy policy](https://dean-flux.github.io/flux-stream-repo/privacy.html) | [App details and credits](https://dean-flux.github.io/flux-stream-repo/about.html)

Trakt Production access is being requested for device-code sign-in and read/write tracking features. No production approval or production Client ID is claimed. The existing Development app continues to apply until access is granted and the Client ID is updated in a subsequent release.
