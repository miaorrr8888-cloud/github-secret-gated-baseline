"""Bounded historical blob scan. Emits locations/categories, never matched contents."""
import argparse,json,subprocess
from pathlib import Path
from gate_scan import scan_text

def scan(repo,limit=100,max_blob=2_000_000):
    if type(limit)!=int or not 1<=limit<=10000:raise ValueError('limit must be 1..10000')
    def git(*args):return subprocess.run(['git',*args],cwd=repo,check=True,capture_output=True).stdout
    commits=git('rev-list','--all','--max-count='+str(limit+1)).decode().splitlines()
    truncated=len(commits)>limit;hits=[];seen={};skipped=0
    for commit in commits[:limit]:
        for entry in git('ls-tree','-r','-z',commit).split(b'\0'):
            if not entry:continue
            meta,path=entry.split(b'\t',1);mode,kind,oid=meta.decode().split()
            if kind!='blob':continue
            name=path.decode('utf-8',errors='replace')
            if oid not in seen:
                size=int(git('cat-file','-s',oid))
                if size>max_blob:seen[oid]=None
                else:
                    raw=git('cat-file','blob',oid)
                    try:seen[oid]=raw.decode('utf-8') if b'\0' not in raw else None
                    except UnicodeDecodeError:seen[oid]=None
            body=seen[oid]
            if body is None:skipped+=1;continue
            categories=scan_text(body,name)
            if Path(name).name.lower().startswith('.env') and Path(name).name not in {'.env.example','.env.template'}:categories.add('sensitive_path')
            if categories:hits.append({'commit':commit,'path':name,'categories':sorted(categories)})
    return {'status':'FINDINGS' if hits else 'NO_FINDINGS_IN_SCANNED_TEXT','hits':hits,'commits_scanned':min(limit,len(commits)),
            'commit_limit_reached':truncated,'skipped_blob_occurrences':skipped,'complete_audit':False,
            'notice':'Heuristic bounded scan; binary/oversized data and unreachable commits are not audited. Rotate any real exposed credential.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('repo');p.add_argument('--limit',type=int,default=100);a=p.parse_args()
    try:r=scan(a.repo,a.limit)
    except (OSError,ValueError,subprocess.CalledProcessError):p.exit(2,'History scan failed; verify Git and repository access.\n')
    print(json.dumps(r,ensure_ascii=False,indent=2));return 1 if r['hits'] else 0
if __name__=='__main__':raise SystemExit(main())
