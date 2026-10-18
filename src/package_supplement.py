"""Build a portable, hash-verified publication supplement from current sources."""
from pathlib import Path
import zipfile,hashlib,json
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'publication'
files={}
for name in ['src/churn_study.py','src/validate_results.py','src/analyze_publication.py','src/fetch_data.py','src/build_documents.py','src/package_supplement.py','tests/test_study.py','requirements-lock.txt','requirements.txt','config/study.json','PROTOCOL.md']:
 files[name]=(ROOT/name).read_bytes()
files['README.md']=(P/'SUPPLEMENT_README.md').read_bytes()
# Preserve the same file so the package can rebuild itself after extraction.
for name in ['SUPPLEMENT_README.md','EXTENSION_PROTOCOL.md','LITERATURE_REVIEW.md','Manuscript.md']:
 files['publication/'+name]=(P/name).read_bytes()
for base in [ROOT/'results',P/'figures',P/'tables']:
 for f in sorted(base.rglob('*')):
  if f.is_file() and f.suffix in {'.csv','.json','.npz','.png','.eps'}:
   files[str(f.relative_to(ROOT))]=f.read_bytes()
files['PACKAGE_SHA256.json']=json.dumps({n:hashlib.sha256(b).hexdigest() for n,b in files.items()},indent=2).encode()
with zipfile.ZipFile(P/'Reproducibility_Supplement.zip','w',zipfile.ZIP_DEFLATED) as z:
 for n,b in files.items():z.writestr(n,b)
with zipfile.ZipFile(P/'Reproducibility_Supplement.zip') as z:
 assert z.testzip() is None
 checks=json.loads(z.read('PACKAGE_SHA256.json'))
 assert all(hashlib.sha256(z.read(n)).hexdigest()==h for n,h in checks.items())
print('Verified archive',len(files),'files;',round((P/'Reproducibility_Supplement.zip').stat().st_size/1e6,2),'MB')
