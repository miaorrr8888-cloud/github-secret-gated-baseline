from pathlib import Path
import importlib.util,unittest,tempfile,json,sys,subprocess,os
ROOT=Path(__file__).resolve().parents[1]
def load(path):
    sys.path.insert(0,str(ROOT/'scripts'))
    spec=importlib.util.spec_from_file_location('extension',ROOT/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

class HistoryAudit(unittest.TestCase):
    def test_deleted_sensitive_file_found_without_value_output(self):
        with tempfile.TemporaryDirectory() as d:
            def git(*args):return subprocess.run(['git',*args],cwd=d,capture_output=True,check=True)
            git('init');git('config','user.email','demo@example.com');git('config','user.name','Demo')
            p=Path(d)/'.env';p.write_text('DEMO_CONFIGURATION=placeholder\n');git('add','.env');git('commit','-m','demo fixture');git('rm','.env');git('commit','-m','delete demo')
            r=load('scripts/scan_history.py').scan(d);self.assertEqual(r['status'],'FINDINGS');self.assertEqual(r['hits'][0]['path'],'.env');self.assertNotIn('DEMO_CONFIGURATION',json.dumps(r))
            limited=load('scripts/scan_history.py').scan(d,limit=1);self.assertTrue(limited['commit_limit_reached']);self.assertFalse(limited['complete_audit'])
