# Publishing

This folder is the repository root. Upload its contents to a GitHub repository,
including the `.github` directory.
The development dependencies and tests use relative paths and work independently
of the game installation.

1. Run `python -m pip install -r requirements-dev.txt`.
2. Run `python tests/test_lifecycle.py`.
3. Perform the final in-game smoke test described in VALIDATION.md.
4. Run `python package.py`.
5. Create a GitHub release for version 0.1.3 (tag `v0.1.3`) and attach the generated mod ZIP and
   `.zip.sha256` file from `dist/`. Use RELEASE_NOTES.md as the release description.
   The third-person portrait fix has been confirmed in-game; other validation
   limits remain documented in VALIDATION.md.

The optional GitHub-source ZIP is for importing the repository contents; it is
not the mod users should install. Distribution builds use an explicit file list
and do not collect files from the installed game or diagnostic probe.

GitHub Actions runs tests and builds an artifact on pushes and pull requests.
It does not publish releases automatically. Dist archives, logs and Python caches
are ignored by Git. The project's own code and documentation are dedicated under
CC0 1.0 Universal; the full text is in LICENSE.
