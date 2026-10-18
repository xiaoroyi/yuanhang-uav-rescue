"""Cross-platform G0 repository checks; never execute archived modeling code."""
import ast
from collections import Counter
import hashlib
from pathlib import Path
import re
import sys

from check_contracts import ROOT, ContractError, read_json, require
from render_task_board import render


def main():
    data = read_json(ROOT / 'docs/task-board.json')
    tasks = data['tasks']
    by_id = {t['id']: t for t in tasks}
    require(len(by_id) == len(tasks), 'duplicate task ID')
    require(set(data['team']) == {'A', 'B'}, 'team must contain exactly A and B')
    require({t['phase'] for t in tasks} == {f'G{i}' for i in range(7)}, 'missing phase')
    expected = {f'G0-{n:02}' for n in range(1,8)} | {f'A-{n:02}' for n in range(1,16)} | {f'B-{n:02}' for n in range(1,11)} | {f'C-{n:02}' for n in range(1,12)} | {f'X-{n:02}' for n in range(1,4)} | {'X-12'} | {f'Q-{n:02}' for n in range(1,6)} | {f'S-{n:02}' for n in range(1,5)}
    require(expected <= set(by_id), 'missing original task IDs: ' + ','.join(sorted(expected-set(by_id))))
    for task in tasks:
        require(task['owner'] in ('A', 'B', 'A+B'), 'invalid owner')
        require(not task['id'].startswith('C-') or task['owner'] == 'B', 'backend tasks must belong to B')
        require(task['status'] in ('todo','in_progress','blocked','done'), 'invalid task state')
        require(task['priority'] in ('P0','P1','P2'), 'invalid priority')
        for dep in task['dependencies']:
            require(dep in by_id, f'unknown dependency {dep}')
        for evidence in task['evidence']:
            require((ROOT / evidence).is_file(), f'missing task evidence {evidence}')
        if task['status'] == 'done':
            require(bool(task['evidence']), f'done without evidence: {task["id"]}')
    visiting, visited = set(), set()
    def visit(task_id):
        require(task_id not in visiting, f'cyclic task dependency at {task_id}')
        if task_id in visited:
            return
        visiting.add(task_id)
        for dep in by_id[task_id]['dependencies']:
            visit(dep)
        visiting.remove(task_id)
        visited.add(task_id)
    for task_id in by_id:
        visit(task_id)
    require((ROOT / 'docs/08-TASK-BOARD.md').read_text(encoding='utf-8') == render(data), 'task board stale: run scripts/render_task_board.py')
    source_manifest = read_json(ROOT / 'references/SOURCES.json')
    for item in source_manifest['files']:
        p = ROOT / item['path']
        require(p.is_file() and p.stat().st_size == item['bytes'], f'source file missing/size changed: {p}')
        require(hashlib.sha256(p.read_bytes()).hexdigest() == item['sha256'], f'source hash changed: {p}')
    legacy = list((ROOT / 'references/modeling/submitted-code').rglob('*.py'))
    require(len(legacy) == 18, 'unexpected submitted source inventory')
    for p in legacy:
        ast.parse(p.read_text(encoding='utf-8-sig'), filename=p.name)
    link_count = 0
    active = [ROOT / 'README.md', ROOT / 'AGENTS.md', ROOT / 'CONTRIBUTING.md']
    for folder in ['docs','prompts','templates','solver','backend','frontend','fixtures','submission']:
        active.extend((ROOT / folder).rglob('*.md'))
    for p in active:
        if any(part in {'node_modules','dist','test-results','playwright-report','.local'} for part in p.relative_to(ROOT).parts):
            continue
        text = p.read_text(encoding='utf-8')
        stale_rule = any(re.search(r'三人团队|三人协作|三位 Codex|三个 Codex|三方确认', line)
                         and not re.search(r'历史|原文|原始|旧版', line) for line in text.splitlines())
        require(not stale_rule, f'stale three-person rule: {p}')
        for match in re.finditer(r'(?<!!)\[[^\]]+\]\(([^)]+)\)',text):
            target = match.group(1).split('#')[0]
            if not target or re.match(r'^[a-z]+:',target):
                continue
            require((p.parent / target).exists(), f'broken Markdown link {p.relative_to(ROOT)} -> {target}')
            link_count += 1
    counts = Counter(t['status'] for t in tasks)
    print(f'PASS: {len(tasks)} tasks across G0–G6, dependency graph acyclic; states={dict(counts)}.')
    print(f'PASS: {len(source_manifest["files"])} source hashes, {len(legacy)} legacy Python ASTs, {link_count} local document links; no legacy code execution.')


if __name__ == '__main__':
    try:
        main()
    except (ContractError, ValueError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        raise SystemExit(1)
