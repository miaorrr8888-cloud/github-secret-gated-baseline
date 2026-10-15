from pathlib import Path
import importlib.util, unittest, tempfile, subprocess, sys, json, zipfile, io, struct, os
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

class ScanPrecision(unittest.TestCase):
    def test_python_annotation_is_not_a_yaml_credential_exception(self):
        m=load('gate',ROOT/'scripts/gate_scan.py')
        self.assertFalse(m.scan_text('api_key: str','models.py'))
        self.assertIn('credential_assignment',m.scan_text('password: str','config.yaml'))
    def test_scan_status_is_not_a_credential_but_weak_password_is(self):
        m=load('gate',ROOT/'scripts/gate_scan.py')
        self.assertFalse(m.scan_text('SECRET_SCAN=PASS'))
        self.assertIn('credential_assignment',m.scan_text("password = 'PASS'"))
    def test_real_literal_is_not_ignored_for_containing_sample_word(self):
        m=load('gate',ROOT/'scripts/gate_scan.py')
        self.assertIn('credential_assignment',m.scan_text("password = 'actual_sample_pass_93!'"))
    def test_short_literal_is_not_ignored(self):
        m=load('gate',ROOT/'scripts/gate_scan.py')
        self.assertIn('credential_assignment',m.scan_text("password = 'abc'"))
    def test_freeze_skips_sensitive_inputs_and_absolute_root(self):
        m=load('freeze',ROOT/'scripts/freeze_manifest.py')
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); (p/'source.py').write_text('print(1)'); (p/'.env.production').write_text('fixture only'); (p/'browser_profile').mkdir(); (p/'browser_profile/Cookies').write_text('fixture')
            m.ROOT=d; m.OUT=str(p/'FREEZE_MANIFEST.json'); self.assertEqual(m.main(),0)
            result=json.loads((p/'FREEZE_MANIFEST.json').read_text()); self.assertEqual(result['root'],'.'); self.assertEqual([x['path'] for x in result['files']],['source.py'])
    def test_staged_secret_cannot_hide_behind_clean_worktree(self):
        import shutil
        git=shutil.which('git')
        if not git: self.skipTest('Git executable unavailable')
        with tempfile.TemporaryDirectory() as d:
            subprocess.run([git,'init',d],capture_output=True,check=True)
            p=Path(d)/'settings.py'; value='nvapi-'+'A9bcD8efG7hiJ6klM5noP4qrS3tuV2wx'; p.write_text('value="'+value+'"\n')
            subprocess.run([git,'-C',d,'add','settings.py'],check=True,capture_output=True)
            p.write_text('value=""\n')
            r=subprocess.run([sys.executable,str(ROOT/'scripts/gate_scan.py'),'--staged'],cwd=d,capture_output=True)
            self.assertEqual(r.returncode,1); self.assertNotIn(value.encode(),r.stdout)

if __name__=="__main__": unittest.main()
