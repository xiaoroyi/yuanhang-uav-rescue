"""CLI compatibility entry point for the shared schema and semantic validators."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from shared.contracts import *

if __name__ == '__main__':
    try:
        main()
    except (ContractError, ValueError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        raise SystemExit(1)