"""Resume only missing configurations; preserve interrupted artifacts and frozen search."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
import os
import subprocess
import sys
import time
from benchmark_v2 import load, digest
from pattern_v4 import V4
from support import PROJECT, dump, table

BASE = V4 / 'corrected_600s_seed42'

def main():
    protocol = load(BASE / 'protocol.json')
    for name, sha in protocol['source_sha256'].items():
        assert digest(Path(__file__).with_name(name)) == sha, name
    for name, sha in protocol['candidate_sha256'].items():
        assert digest(V4 / name) == sha, name
    records, paths, missing = [], {}, []
    for q in ['Q2', 'Q3']:
        for method in ['greedy', 'aco', 'alns', 'cp_sat']:
            label = f'{q}_energy_{method}'
            path = BASE / label / 'run.json'
            if path.exists():
                records.append(load(path)); paths[label] = label
            else:
                missing.append((q, method, label))
    assert len(records) == 5 and {m for q, m, _ in missing if q == 'Q3'} == {'aco', 'alns', 'cp_sat'}
    original_progress = load(BASE / 'progress.json')
    started = time.perf_counter()
    manifest = dict(started_at=datetime.now(timezone.utc).isoformat(), original_completed=5,
        original_progress=original_progress, missing=[label for _, _, label in missing],
        source_and_candidate_hashes_verified=True, discarded_interrupted_runs_preserved=True,
        policy='Fresh 600s reruns of only three incomplete configurations; unchanged algorithms and inputs; prior partial runs excluded.')
    dump(BASE / 'resume_manifest.json', manifest)
    def invoke(q, method, label):
        new_label = 'resumed_' + label
        assert not (BASE / new_label).exists()
        cmd = [sys.executable, '-u', str(Path(__file__).with_name('benchmark_v4.py')),
            '--question', q, '--method', method, '--seconds', '600', '--checkpoints', '180,600',
            '--name', BASE.name + '/' + new_label]
        print('START', label, flush=True)
        with (BASE / (new_label + '.txt')).open('w', encoding='utf-8') as log:
            result = subprocess.run(cmd, cwd=PROJECT, stdout=log, stderr=subprocess.STDOUT,
                timeout=780, env={**os.environ, 'PYTHONIOENCODING':'utf-8',
                    'OMP_NUM_THREADS':'1', 'MKL_NUM_THREADS':'1', 'OPENBLAS_NUM_THREADS':'1'})
        assert result.returncode == 0, (label, result.returncode)
        return label, new_label, load(BASE / new_label / 'run.json')
    errors = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(invoke, *item) for item in missing]
        for future in as_completed(futures):
            try:
                label, path, record = future.result()
                records.append(record); paths[label] = path
                print('COMPLETE', label, record['checkpoints'][-1]['metrics'], flush=True)
            except Exception as exc:
                errors.append(repr(exc)); print('ERROR', repr(exc), flush=True)
            dump(BASE / 'run_paths.json', paths)
            dump(BASE / 'results.json', sorted(records, key=lambda r:(r['question'],r['method'])))
            dump(BASE / 'resume_progress.json', dict(completed=len(records), total=8, errors=errors,
                resume_wall_s=time.perf_counter()-started))
    rows = [dict(question=r['question'], method=r['method'], checkpoint_s=c['checkpoint_s'],
        status=c['status'], search_wall_s=r['search_wall_s'], **c['metrics'])
        for r in records for c in r['checkpoints']]
    table(BASE / 'results.csv', rows)
    wall = time.perf_counter()-started
    dump(BASE / 'completion.json', dict(complete=len(records)==8 and not errors,
        completed_runs=len(records), errors=errors, resumed_runs=3, resume_wall_s=wall,
        experiment_wall_s=wall, timing_scope='Three resumed configurations only; original partial searches and pause excluded.',
        sum_search_wall_s=sum(r['search_wall_s'] for r in records),
        feasible_final_runs=sum(r['checkpoints'][-1]['metrics'] is not None for r in records)))
    assert not errors and len(records)==8

if __name__ == '__main__': main()
