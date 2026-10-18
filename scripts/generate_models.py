"""Bundle existing JSON Schemas locally and generate deterministic Pydantic models."""
import copy
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
BASE='https://yuanhang.example/contracts/'


def bundle():
    defs={}
    for p in sorted((ROOT/'contracts').glob('*.schema.json')):
        name=p.name.removesuffix('.schema.json')
        data=json.loads(p.read_text(encoding='utf-8'))
        data.pop('$id',None);data.pop('$schema',None)
        data['title']=''.join(x.capitalize() for x in name.split('-'))
        defs[name]=data
    def localize(value):
        if isinstance(value,dict):
            if '$ref' in value and value['$ref'].startswith(BASE):
                ref=value['$ref'][len(BASE):]
                file,_,fragment=ref.partition('#')
                value['$ref']='#/$defs/'+file.removesuffix('.schema.json')+fragment
            for child in value.values():localize(child)
        elif isinstance(value,list):
            for child in value:localize(child)
    result={'$schema':'https://json-schema.org/draft/2020-12/schema','title':'DomainContracts','type':'object',
            'properties':{k:{'$ref':'#/$defs/'+k} for k in defs if k!='common'},'additionalProperties':False,'$defs':defs}
    localize(result)
    return result


def main():
    temp=ROOT/'.local/contracts.bundle.json';temp.parent.mkdir(exist_ok=True)
    temp.write_text(json.dumps(bundle(),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    target=ROOT/'backend/app/generated/domain.py';target.parent.mkdir(parents=True,exist_ok=True)
    subprocess.run([sys.executable,'-m','datamodel_code_generator','--input',str(temp),'--input-file-type','jsonschema',
                    '--output',str(target),'--output-model-type','pydantic_v2.BaseModel','--target-python-version','3.11',
                    '--use-standard-collections','--use-union-operator','--use-title-as-name','--disable-timestamp','--extra-fields','forbid',
                    '--use-double-quotes','--strict-refs','--formatters','black','isort'],check=True,cwd=ROOT)
    # Remove machine-local paths from generated headers; source stays in the tracked schema files.
    lines=target.read_text(encoding='utf-8').splitlines()
    target.write_text('\n'.join('#   filename: contracts/*.schema.json (local bundle)' if line.startswith('#   filename:') else line for line in lines)+'\n',encoding='utf-8')
    print('Generated backend/app/generated/domain.py from current JSON Schemas.')


if __name__=='__main__':main()
