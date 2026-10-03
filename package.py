from pathlib import Path
import hashlib
import json
import zipfile

root = Path(__file__).resolve().parent
dist = root / 'dist'
artifact = dist / 'ManaMetal-Spiritual-AutoReset-1.7.10-1.1.0.jar'
digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
for version in ('8.0.5', '8.0.7'):
    fixture = root / ('build/client-test-1.1.0-' + version)
    assert 'status=PASS' in (fixture / 'result.txt').read_text(encoding='utf8')
    verification = json.loads((fixture / 'verification.json').read_text(encoding='utf8'))
    assert verification['artifact_sha256'] == digest, 'Tests must match the release JAR'

bundle = dist / 'ManaMetal-Spiritual-AutoReset-1.7.10-1.1.0-with-source.zip'
with zipfile.ZipFile(bundle, 'w', zipfile.ZIP_DEFLATED) as out:
    out.write(root / 'LICENSE', 'LICENSE')
    out.write(root / 'README.md', 'README.md')
    out.write(root / 'LICENSE', 'source/LICENSE')
    out.write(root / 'README.md', 'source/README.md')
    out.write(root / '.gitignore', 'source/.gitignore')
    out.write(root / '.gitattributes', 'source/.gitattributes')
    out.write(artifact, artifact.name)
    out.write(root / '使用说明.md', '使用说明.md')
    out.write(root / 'build/build.json', 'validation/build.json')
    for version in ('8.0.5', '8.0.7'):
        fixture = root / ('build/client-test-1.1.0-' + version)
        for name in ('result.txt', 'verification.json'):
            out.write(fixture / name, 'validation/' + version + '/' + name)
    for path in sorted((root / 'build/client-test-1.1.0-8.0.7/screenshots').glob('*.png')):
        out.write(path, 'screenshots/' + path.name)
    for folder in ('src', 'client-tests'):
        for path in sorted((root / folder).rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts:
                out.write(path, 'source/' + path.relative_to(root).as_posix())
    for name in ('build.py', 'build.ps1', 'package.py', '使用说明.md'):
        out.write(root / name, 'source/' + name)
(dist / 'SHA256SUMS.txt').write_text(''.join(
    hashlib.sha256(path.read_bytes()).hexdigest() + '  ' + path.name + '\n'
    for path in (artifact, bundle)), encoding='ascii')
print(bundle.name)
