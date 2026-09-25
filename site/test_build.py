"""Small regression tests for publication boundaries and Markdown rendering."""
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('securebase_builder', HERE / 'build.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
ROOT = HERE.parent
CONFIG = json.loads((HERE / 'content.json').read_text())

class SiteTests(unittest.TestCase):
    def test_danish_github_anchors(self):
        self.assertEqual(builder.github_slug('Dokumentation / bevis'), 'dokumentation--bevis')
        self.assertEqual(builder.github_slug('Sikkerhedsmæssig begrundelse'), 'sikkerhedsmæssig-begrundelse')
        self.assertEqual(builder.github_slug('Event ID-oversigt'), 'event-id-oversigt')

    def test_output_prefixes(self):
        self.assertEqual(builder.root_prefix('index.html'), '')
        self.assertEqual(builder.root_prefix('moduler/01-vm-netvaerk.html'), '../')

    def test_evidence_index_is_complete(self):
        items = builder.evidence_items(ROOT, copy.deepcopy(CONFIG['modules']))
        self.assertEqual(len(items), len(list((ROOT / 'evidence').rglob('*.png'))))
        self.assertEqual(len(items), len(set(e['path'] for e in items)))

    def test_module_link_rewrite(self):
        mapping = builder.source_mapping(CONFIG['modules'])
        result = builder.rewrite_url('03-group-policy.md#resultat','docs/02-active-directory.md','moduler/02-active-directory.html',mapping,set())
        self.assertEqual(result,'03-group-policy.html#resultat')

    def test_evidence_link_rewrite(self):
        mapping = builder.source_mapping(CONFIG['modules'])
        result = builder.rewrite_url('../evidence/06-event-viewer/README.md','docs/06-event-viewer.md','moduler/06-event-viewer.html',mapping,set())
        self.assertEqual(result,'../beviser/index.html?modul=6')

    def test_unapproved_link_is_rejected(self):
        with self.assertRaises(ValueError):
            builder.rewrite_url('../.env','docs/06-event-viewer.md','moduler/06-event-viewer.html',{},set())
        with self.assertRaises(ValueError):
            builder.rewrite_url('javascript:alert(1)','docs/x.md','moduler/x.html',{},set())

    def test_path_escape_is_rejected(self):
        with self.assertRaises(ValueError): builder.safe_source(ROOT,'../outside.txt')

    def test_unknown_encoding_replacement_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'bad.md';path.write_text('\ufffd',encoding='utf-8')
            with self.assertRaises(ValueError): builder.read_utf8(path)

    def test_main_script_render_matches_original(self):
        from bs4 import BeautifulSoup
        original = builder.read_utf8(ROOT/'scripts/New-SecureBaseSupport.ps1').strip()
        # The script is rendered, not executed. Preserve its documented logic.
        html,_,_ = builder.render_markdown(ROOT,'scripts/README.md','kode/index.html',builder.source_mapping(CONFIG['modules']),{'scripts/New-SecureBaseSupport.ps1'})
        pres = [p.get_text().strip() for p in BeautifulSoup(html,'html.parser').find_all('pre')]
        self.assertIn(original,pres)

    def test_never_overwrite_source_directory(self):
        with self.assertRaises(ValueError): builder.build(ROOT,ROOT/'docs',CONFIG)
        with self.assertRaises(ValueError): builder.build(ROOT,ROOT,CONFIG)

    def test_refuse_unknown_output_folder(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory);(path/'keep.txt').write_text('keep')
            with self.assertRaises(ValueError): builder.build(ROOT,path,CONFIG)
            self.assertEqual((path/'keep.txt').read_text(),'keep')

if __name__ == '__main__': unittest.main()
