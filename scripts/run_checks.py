"""Run the available G0 checks and save their actual output, without claiming E2E."""
from datetime import datetime, timedelta, timezone
from importlib import metadata
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'evidence/governance'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    commands = [
        ('contracts', [sys.executable, 'scripts/check_contracts.py']),
        ('contract-tests', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests/contracts', '-v']),
        ('governance', [sys.executable, 'scripts/check_governance.py']),
        ('git-whitespace', ['git', 'diff', '--cached', '--check']),
    ]
    results = []
    for label, cmd in commands:
        proc = subprocess.run(cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              encoding='utf-8', errors='replace')
        path = OUT / (label + '.log')
        path.write_text(proc.stdout, encoding='utf-8')
        result = {'name':label, 'command':['python' if c == sys.executable else c for c in cmd],
                  'exit_code':proc.returncode, 'status':'PASS' if proc.returncode == 0 else 'FAIL',
                  'output':path.relative_to(ROOT).as_posix()}
        results.append(result)
        print(label, result['status'])
    base = subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip()
    record = {'run_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),
              'base_commit_before_governance_commit':base, 'scope':'G0 review artifacts; not business implementation',
              'python_version':sys.version.split()[0],
              'packages':{name:metadata.version(name) for name in ['jsonschema','attrs','jsonschema-specifications','referencing','rpds-py']},
              'checks':results,
              'not_run':['legacy Q1-Q4 solving','independent flight physics/DEM/radio validation','running FastAPI/Pydantic/OpenAPI generation','frontend build/typecheck','real E2E/offline demo','hosted GitHub Actions']}
    (OUT/'check-results.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return 0 if all(r['exit_code'] == 0 for r in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
