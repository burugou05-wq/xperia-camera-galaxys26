from pathlib import Path
from zipfile import ZipFile
import sys
root = Path(__file__).resolve().parents[1]
if len(sys.argv) > 1 and sys.argv[1] == 'classes':
    classes = root / 'build/helper/classes'
    with ZipFile(root / 'build/helper/classes.jar', 'w') as output:
        for path in classes.rglob('*.class'):
            output.write(path, path.relative_to(classes).as_posix())
    sys.exit(0)
with ZipFile(root / 'camera-2-9-a-0-24.apk') as original, ZipFile(root / 'build/helper/helper.apk', 'w') as output:
    output.writestr('AndroidManifest.xml', original.read('AndroidManifest.xml'))
    output.write(root / 'build/helper/dex/classes.dex', 'classes.dex')
