"""Hash a local source snapshot; skip credentials, browser data, dependencies and symlinks."""
import datetime,hashlib,json,os,sys
from pathlib import Path

ROOT=os.path.abspath(os.getcwd())
OUT=os.path.join(ROOT,'FREEZE_MANIFEST.json')
SKIP_DIRS={'.git','__pycache__','.venv','venv','.pytest_cache','node_modules'}
SENSITIVE={'credentials','id_rsa','id_ed25519','.netrc','auth.json','cookies','login data','local state'}

def main():
    root=Path(ROOT); items=[]; errors=[]
    if Path(OUT).is_symlink(): print('FREEZE_ERROR symlink output'); return 2
    for dp,dn,fn in os.walk(root,followlinks=False):
        dn[:]=[d for d in dn if d not in SKIP_DIRS and 'profile' not in d.lower() and not (Path(dp)/d).is_symlink()]
        for name in sorted(fn):
            p=Path(dp)/name; low=name.lower()
            if name=='FREEZE_MANIFEST.json' or p.is_symlink(): continue
            if (low.startswith('.env') and low!='.env.example') or low in SENSITIVE or p.suffix.lower() in {'.key','.pem','.p12','.pfx','.jks'}: continue
            try:
                sha=hashlib.sha256()
                with p.open('rb') as f:
                    for chunk in iter(lambda:f.read(65536),b''): sha.update(chunk)
                items.append({'path':p.relative_to(root).as_posix(),'sha256':sha.hexdigest(),'size':p.stat().st_size})
            except OSError: errors.append(p.relative_to(root).as_posix())
    doc={'frozen_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'root':'.','file_count':len(items),'files':items,'errors':errors}
    Path(OUT).write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf-8')
    print('FREEZE_'+('PARTIAL' if errors else 'OK')+' files='+str(len(items))); return 2 if errors else 0

if __name__=='__main__': raise SystemExit(main())
