"""Render the human board from docs/task-board.json; do not edit two status copies."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def render(data):
    lines = ['# 全量任务板', '', '由 `docs/task-board.json` 生成。两人：A 算法兼项目负责人，B 同一人负责前端、后端与集成。C-* 只是后端任务编号。', '',
             '阶段表示依赖，不按日期排期。P0/P1/P2 全部保留；done 需要真实验收证据。当前 G0 尚待共同评审，不自动进入业务开发。', '']
    for phase, gate in data['gate_status'].items():
        lines += [f'## {phase}', '', f'阶段状态：`{gate}`。', '', '| ID | 优先级 | Owner | 依赖 | 任务与验收 | 状态 | 分支/PR/证据 |', '|---|---|---|---|---|---|---|']
        for t in data['tasks']:
            if t['phase'] != phase:
                continue
            evidence = [*([t['branch']] if t['branch'] else []), *([t['pr']] if t['pr'] else []), *t['evidence']]
            cells = [t['id'], t['priority'], t['owner'], ', '.join(t['dependencies']) or '—', t['title'] + '；验收：' + t['acceptance'], t['status'], '; '.join(evidence) or '—']
            lines.append('| ' + ' | '.join(str(x).replace('|', '\\|').replace('\n', ' ') for x in cells) + ' |')
        lines += ['']
    lines += ['## 首张可执行任务卡', '',
              '- A：A-01，先完成来源、依赖、物理参数和无副作用适配核验；真实 API 开发依赖 G0-03 人工冻结。验收详见 LEGACY_BASELINE_AUDIT。',
              '- B：C-01/C-02 与 B-01 作为一个系统任务组，先对照草案设计字段映射与三页骨架；冻结后实现类型生成、导入/错误、快照、Mock/HTTP Provider。',
              '- 共同：对 RFC-001 六项决策留确认记录，B 提供 GitHub 用户名，A 审核合并规范分支。', '']
    return '\n'.join(lines)


if __name__ == '__main__':
    data = json.loads((ROOT / 'docs/task-board.json').read_text(encoding='utf-8'))
    (ROOT / 'docs/08-TASK-BOARD.md').write_text(render(data), encoding='utf-8')
    print(f'Rendered {len(data["tasks"])} tasks.')
