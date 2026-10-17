from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT.parent
sys.path.insert(0,str(PROJECT/'问题1/src'))
import bootstrap
sys.path.insert(0,str(ROOT/'deps311'))
OUT=ROOT/'results'
OUT.mkdir(exist_ok=True,parents=True)
