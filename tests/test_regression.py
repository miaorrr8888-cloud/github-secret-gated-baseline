from pathlib import Path
import importlib.util, unittest, tempfile, subprocess, sys, json, zipfile, io, os
R=Path(__file__).resolve().parents[1]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module

class SecurityGate(unittest.TestCase):
    script=R/'scripts/gate_scan.py'
    def scan(self,root,*args): return subprocess.run([sys.executable,str(self.script),*args],cwd=root,capture_output=True,text=True)
    def test_clean_and_secret_exit_codes(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'config.py'; p.write_text('value = 123\n')
            self.assertEqual(self.scan(d).returncode,0)
            fake='nvapi-'+'Ab9Zx7Qw5Er3Ty1Ui2Op4As6Df8Gh0Jk'
            p.write_text('value = "'+fake+'"\n')
            result=self.scan(d); self.assertEqual(result.returncode,1); self.assertNotIn(fake,result.stdout)
    def test_tracked_not_git_fails(self):
        with tempfile.TemporaryDirectory() as d: self.assertNotEqual(self.scan(d,'--tracked').returncode,0)
    def test_empty_scope_is_error(self):
        with tempfile.TemporaryDirectory() as d: self.assertEqual(self.scan(d).returncode,2)
    def test_env_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d)/'.env').write_text('EMPTY='); self.assertEqual(self.scan(d).returncode,1)

class TestProfilePathRejectedWithoutOpeningContent(unittest.TestCase):
    def test_profile_path_rejected_without_opening_content(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder); (p/'browser_profile').mkdir(); (p/'browser_profile/Cookies').write_bytes(b'fixture')
            result=subprocess.run([sys.executable,str(R/'scripts/gate_scan.py')],cwd=p,capture_output=True)
            self.assertEqual(result.returncode,1); self.assertIn(b'sensitive_or_symlink_path',result.stdout)

if __name__=="__main__": unittest.main(verbosity=2)
