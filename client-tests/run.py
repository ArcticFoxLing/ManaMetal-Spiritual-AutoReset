from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import zipfile

sys.stdout.reconfigure(encoding='utf8')
root = Path(__file__).resolve().parents[1]
workspace = Path(os.environ.get('FOXFOX_WORKSPACE', root.parent)).resolve()
version = sys.argv[1] if len(sys.argv) > 1 else '8.0.7'
assert version in ('8.0.5', '8.0.7')
fixture = root / ('build/client-test-1.1.0-' + version)
game = fixture / 'client'
mods = game / 'mods'
mods.mkdir(parents=True, exist_ok=True)
config = game / 'config'
config.mkdir(exist_ok=True)
(config / 'splash.properties').write_text('enabled=false\n', encoding='ascii')
(game / 'options.txt').write_text('fullscreen:false\nlang:zh_CN\nguiScale:2\noverrideWidth:1280\noverrideHeight:720\n', encoding='ascii')
# Mute the isolated test directory before starting any game client.
sound_options = ''.join('soundCategory_' + c + ':0.0\n' for c in
                        ('master', 'music', 'record', 'weather', 'block', 'hostile', 'neutral', 'player', 'ambient'))
with (game / 'options.txt').open('a', encoding='ascii') as options_file:
    options_file.write(sound_options)
for name in ('config', 'falsepattern'):
    source = workspace / 'FoxFoxAccessories/test-server' / name
    if source.exists():
        shutil.copytree(source, game / name, dirs_exist_ok=True)
patterns = ( '*Muya*.jar', 'lwjgl3ify-*.jar', '+unimixins-*.jar', 'gtnhlib-*.jar')
for pattern in patterns:
    matches = list((workspace / '.minecraft/mods').glob(pattern))
    assert len(matches) == 1, (pattern, matches)
    path = matches[0]
    shutil.copy2(path, mods / path.name.split(']', 1)[-1])
mana_source = workspace / 'fcwqmmmserver/mods/manametalmod-8.0.7.jar' if version == '8.0.7' else next(workspace.glob('*8.0.5.jar'))
shutil.copy2(mana_source, mods / ('manametalmod-' + version + '.jar'))
artifact = root / 'dist/ManaMetal-Spiritual-AutoReset-1.7.10-1.1.0.jar'
shutil.copy2(artifact, mods / artifact.name)
classes = fixture / 'probe-classes'
classes.mkdir(exist_ok=True)
deps = [workspace / 'FoxFoxAccessories/tools/forge-1.7.10-srg.jar', artifact, mods / ('manametalmod-' + version + '.jar'), *mods.glob('*Muya*.jar'),
        *sorted((workspace / '.minecraft/libraries').rglob('*.jar'))]
subprocess.run(['javac', '--release', '8', '-Xlint:-options', '-encoding', 'UTF-8', '-cp', os.pathsep.join(map(str, deps)),
                '-d', str(classes), str(root / 'client-tests/SpiritualRuntimeCheck.java')], check=True)
with zipfile.ZipFile(mods / 'spiritual-autoreset-test.jar', 'w', zipfile.ZIP_DEFLATED) as jar:
    for path in classes.rglob('*.class'):
        jar.write(path, path.relative_to(classes).as_posix())
profile_dir = workspace / 'fcwqmmmserver/deployment/java21'
profile = json.loads((profile_dir / 'prepared-client-version.json').read_text(encoding='utf-8-sig'))
cp = os.pathsep.join(json.loads((profile_dir / 'client-classpath.json').read_text(encoding='utf-8-sig')))
natives = game / 'natives'
natives.mkdir(exist_ok=True)
args = ['-Xms256m', '-Xmx2G', '-XX:+UseG1GC', '-Dspiritualautoreset.test.root=' + str(fixture)]
args += [a.replace('${classpath}', cp).replace('${natives_directory}', str(natives))
         for a in profile['arguments']['jvm'] if isinstance(a, str)]
args += [profile['mainClass'], '--username', 'SpiritualAutoTest', '--version', profile['id'],
         '--gameDir', str(game), '--assetsDir', str(workspace / '.minecraft/assets'), '--assetIndex', '1.7.10',
         '--uuid', '00000000000000000000000000000006', '--accessToken', '0', '--userProperties', '{}',
         '--userType', 'legacy', '--width', '1280', '--height', '720', '--tweakClass', 'cpw.mods.fml.common.launcher.FMLTweaker']
argfile = fixture / 'client.args'
argfile.write_text('\n'.join('"' + a.replace('\\', '\\\\').replace('"', '\\"') + '"' for a in args), encoding='utf8')
report = fixture / 'result.txt'
report.write_text('RUNNING\n', encoding='utf8')
with (fixture / 'console.log').open('w', encoding='utf8') as log:
    process = subprocess.Popen(['java', '@' + str(argfile)], cwd=game, stdout=log, stderr=subprocess.STDOUT,
                               creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    print('Isolated client PID', process.pid, flush=True)
    try:
        code = process.wait(timeout=240)
    except subprocess.TimeoutExpired:
        process.kill(); process.wait()
        raise SystemExit('Client timeout; inspect build/client-test/console.log')
result = report.read_text(encoding='utf8')
print(result)
if code != 0 or 'status=PASS' not in result:
    raise SystemExit('Client verification failed; inspect build/client-test/console.log')

import hashlib
(fixture / 'verification.json').write_text(json.dumps({'artifact_sha256': hashlib.sha256(artifact.read_bytes()).hexdigest(), 'manametal': version, 'status': 'PASS'}, indent=2), encoding='utf8')
