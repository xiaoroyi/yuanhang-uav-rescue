"""Render the human board from docs/task-board.json; do not edit two status copies."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def render(data):
    lines = ['# 全量任务板', '', '由 `docs/task-board.json` 生成。两人：A 算法兼项目负责人，B 同一人负责前端、后端与集成。C-* 只是后端任务编号。', '',
             '阶段表示依赖，不按日期排期。P0/P1/P2 全部保留；done 需要真实验收证据。当前用户已授权单人全栈实现分支，契约仍待团队复核；详见 SOLO_EXECUTION。', '']
    for phase, gate in data['gate_status'].items():
        lines += [f'## {phase}', '', f'阶段状态：`{gate}`。', '', '| ID | 优先级 | Owner | 依赖 | 任务与验收 | 状态 | 分支/PR/证据 |', '|---|---|---|---|---|---|---|']
        for t in data['tasks']:
            if t['phase'] != phase:
                continue
            evidence = [*([t['branch']] if t['branch'] else []), *([t['pr']] if t['pr'] else []), *t['evidence']]
            cells = [t['id'], t['priority'], t['owner'], ', '.join(t['dependencies']) or '—', t['title'] + '；验收：' + t['acceptance'], t['status'], '; '.join(evidence) or '—']
            lines.append('| ' + ' | '.join(str(x).replace('|', '\\|').replace('\n', ' ') for x in cells) + ' |')
        lines += ['']
    entry = '- 当前 V2 入口为 evidence/redesign-v2/INDEX.md，分支 feat/mission-workspace-v2；旧发布证据只代表对应历史版本。' if any(t['id']=='R00' for t in data['tasks']) else '- 先读 IMPLEMENTATION_STATUS 与 SOLO_EXECUTION，沿用 feat/solo-fullstack-v0 的已验证结果。'
    lines += ['## 当前执行入口', '', entry,
              '- 优先完成当前 in_progress 任务的剩余验收，再推进下一项依赖。不同任务的部分实现不能自动算 done。',
              '- 两人接手前共同复核 RFC-001/RFC-002、现有运行接口、测试证据和 Git 差异；不伪造契约批准记录。', '']
    return '\n'.join(lines)


if __name__ == '__main__':
    data = json.loads((ROOT / 'docs/task-board.json').read_text(encoding='utf-8'))
    (ROOT / 'docs/08-TASK-BOARD.md').write_text(render(data), encoding='utf-8')
    print(f'Rendered {len(data["tasks"])} tasks.')
