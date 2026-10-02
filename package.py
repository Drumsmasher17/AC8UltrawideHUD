"""Build an allowlisted release ZIP; never package the user's installed mod folder."""
from pathlib import Path
import hashlib
import re
import zipfile

ROOT = Path(__file__).resolve().parent
source = ROOT / 'mod/Scripts/main.lua'
version = re.search(r'AC8UltrawideHUD (\d+\.\d+\.\d+)', source.read_text()).group(1)
files = {
    'Scripts/main.lua': source,
    'enabled.txt': ROOT / 'mod/enabled.txt',
    **{name: ROOT / name for name in ['README.md', 'INSTALL.md', 'CHANGELOG.md', 'VALIDATION.md', 'LICENSE']},
    **{name: ROOT / name for name in ['AC8Ultrawide_ThirdPerson.png', 'AC8Ultrawide_Cockpit.png', 'AC8Ultrawide_HUDOnly.png']},
}
destination = ROOT / 'dist' / f'AC8UltrawideHUD-{version}.zip'
destination.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as archive:
    for name, path in files.items():
        archive.writestr(f'AC8UltrawideHUD/{name}', path.read_bytes())
digest = hashlib.sha256(destination.read_bytes()).hexdigest()
destination.with_suffix('.zip.sha256').write_text(f'{digest}  {destination.name}\n')
print(destination.name, digest)

# Keep the repository import bundle in sync with documentation and image updates.
source_files = [
    'README.md', 'INSTALL.md', 'CHANGELOG.md', 'VALIDATION.md', 'PUBLISHING.md',
    'LICENSE', '.gitignore', 'requirements-dev.txt', 'package.py',
    'tests/test_lifecycle.py', 'mod/Scripts/main.lua', 'mod/enabled.txt',
    '.github/workflows/test.yml', 'AC8Ultrawide_ThirdPerson.png',
    'AC8Ultrawide_Cockpit.png', 'AC8Ultrawide_HUDOnly.png',
]
source_destination = ROOT / 'dist' / f'AC8UltrawideHUD-{version}-GitHub-source.zip'
with zipfile.ZipFile(source_destination, 'w', zipfile.ZIP_DEFLATED) as archive:
    for name in source_files:
        archive.writestr(name, (ROOT / name).read_bytes())
print(source_destination.name)
