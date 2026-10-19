"""Copy selected mathematical helpers without executing archived entry points."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[2]
DEST = Path(__file__).parent
EVIDENCE = ROOT / 'evidence/contest-baselines-v1'

def main():
    archive = ROOT / 'references/modeling/submitted-code'
    choices = {
        'legacy_routes.py': ('问题2/src/routes.py', [('import env\nfrom env import OUT,PROJECT\n', 'from support import OUT, PROJECT\n')]),
        'legacy_radio.py': ('问题3/src/communication.py', [('from setup_q3 import *', 'from support import *'), ('from routes import Physics', 'from legacy_routes import Physics')]),
        'legacy_terrain.py': ('问题1/src/terrain.py', [('import bootstrap\n', '')]),
        'legacy_sites.py': ('问题3/src/sites.py', [('from communication import Radio,phases,profile_bad_intervals', 'from legacy_radio import Radio,phases,profile_bad_intervals'), ('from setup_q3 import *', 'from support import *'), ('from terrain import route_points,supercover_segment', 'from legacy_terrain import route_points,supercover_segment')]),
        'legacy_atoms.py': ('问题3/src/atoms.py', [('from communication import *', 'from legacy_radio import *'), ('from setup_q3 import *', 'from support import *'), ('from routes import Physics', 'from legacy_routes import Physics')]),
        'legacy_master.py': ('问题2/src/master.py', [('import env\n', '')]),
        'legacy_joint.py': ('问题3/src/joint_batch.py', [('from setup_q3 import *', 'from support import *'), ('from routes import Physics,charge', 'from legacy_routes import Physics,charge'), ('from master import ceil_tick', 'from legacy_master import ceil_tick'), ("seedrows=json.loads((PROJECT/'问题2/results/solution.json').read_text(encoding='utf-8'))", 'seedrows=[] # No historical solution is supplied to any baseline.')]),
        'legacy_validate.py': ('问题2/src/validate.py', [('import env\nfrom env import OUT\nfrom prepare import load\nfrom data_io import dump,table', 'from support import OUT, inputs as load, dump, table')]),
        'legacy_validate_q3.py': ('问题3/src/validate_q3.py', [('from setup_q3 import *', 'from support import *'), ('from communication import Radio,phases', 'from legacy_radio import Radio,phases'), ('from routes import Physics', 'from legacy_routes import Physics'), ('from validate import check,peak', 'from legacy_validate import check,peak'), ('from sites import relay_metrics', 'from legacy_sites import relay_metrics')]),
    }
    manifest = []
    for dest, (src, replacements) in choices.items():
        p = archive / src
        source = p.read_text(encoding='utf-8')
        for old, new in replacements:
            assert old in source, (src, old)
            source = source.replace(old, new)
        source = source.split("if __name__=='__main__':")[0]
        (DEST / dest).write_text(source, encoding='utf-8')
        manifest.append(dict(destination=str((DEST/dest).relative_to(ROOT)), source=str(p.relative_to(ROOT)), source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(), adaptations='isolated imports; archived CLI removed; mathematical definitions unchanged'))
    with zipfile.ZipFile(ROOT/'references/modeling/verified-release-code-and-results.zip') as z:
        d = EVIDENCE/'inputs'
        d.mkdir(exist_ok=True, parents=True)
        for name in ['normalized_inputs.json', 'terrain_evidence_all.json']:
            member = 'review_runs/20260925_server_search/inputs/' + name
            raw = z.read(member)
            (d/name).write_bytes(raw)
            manifest.append(dict(destination=str((d/name).relative_to(ROOT)), archive='references/modeling/verified-release-code-and-results.zip', member=member, sha256=hashlib.sha256(raw).hexdigest()))
    (EVIDENCE/'source_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')

if __name__ == '__main__':
    main()
