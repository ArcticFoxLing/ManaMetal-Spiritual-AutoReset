from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parent
WORKSPACE = Path(os.environ.get('FOXFOX_WORKSPACE', ROOT.parent)).resolve()
BUILD = ROOT / 'build'
CLASSES = BUILD / 'classes'
DIST = ROOT / 'dist'
if CLASSES.exists():
    assert CLASSES.resolve().parent == BUILD.resolve()
    shutil.rmtree(CLASSES)
CLASSES.mkdir(parents=True)
DIST.mkdir(exist_ok=True)
forge = Path(os.environ.get('FORGE_SRG_JAR', str(WORKSPACE / 'FoxFoxAccessories/tools/forge-1.7.10-srg.jar')))
mana = Path(os.environ.get('MANAMETAL_JAR', str(WORKSPACE / 'fcwqmmmserver/mods/manametalmod-8.0.7.jar')))
muya = Path(os.environ.get('MUYA_JAR', str(WORKSPACE / '.minecraft/mods/[Muya]Muya_1.11.1.jar')))
for path in (forge, mana, muya):
    if not path.is_file():
        raise SystemExit(f'Missing compile dependency: {path}')
subprocess.run(['javac', '--release', '8', '-Xlint:-options', '-encoding', 'UTF-8', '-cp', os.pathsep.join(map(str, (forge, mana, muya))),
                '-d', str(CLASSES), *map(str, sorted((ROOT / 'src').rglob('*.java')))], check=True)
artifact = DIST / 'ManaMetal-Spiritual-AutoReset-1.7.10-1.1.0.jar'
with zipfile.ZipFile(artifact, 'w', zipfile.ZIP_DEFLATED) as jar:
    jar.write(ROOT / 'LICENSE', 'META-INF/LICENSE')
    jar.writestr('META-INF/MANIFEST.MF', 'Manifest-Version: 1.0\r\nImplementation-Title: ManaMetal Spiritual Auto Reset\r\nImplementation-Version: 1.1.0\r\n\r\n')
    for path in sorted(CLASSES.rglob('*.class')):
        assert int.from_bytes(path.read_bytes()[6:8], 'big') == 52
        jar.write(path, path.relative_to(CLASSES).as_posix())
    for path in sorted((ROOT / 'src').rglob('*')):
        if path.is_file() and path.suffix != '.java':
            jar.write(path, path.relative_to(ROOT / 'src').as_posix())
report = {'artifact': artifact.name, 'sha256': hashlib.sha256(artifact.read_bytes()).hexdigest(),
          'minecraft': '1.7.10', 'javaTarget': 8, 'clientOnly': True,
          'classCount': len(list(CLASSES.rglob('*.class')))}
(BUILD / 'build.json').write_text(json.dumps(report, indent=2), encoding='utf8')
print(json.dumps(report, indent=2))
