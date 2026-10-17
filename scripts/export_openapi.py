"""Export the actual application's OpenAPI without starting a server or writing a DB."""
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend.app.main import app

path=ROOT/'contracts/http/openapi.generated.json'
path.write_text(json.dumps(app.openapi(),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Exported actual OpenAPI:',len(app.openapi()['paths']),'paths.')
