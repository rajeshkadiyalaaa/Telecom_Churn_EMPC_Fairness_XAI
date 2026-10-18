"""Retrieve the public benchmark and verify the recorded experiment input hash."""
from pathlib import Path
import hashlib,json,urllib.request
ROOT=Path(__file__).resolve().parents[1]
url='https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv'
expected=json.loads((ROOT/'results/manifest.json').read_text())['data_sha256']
path=ROOT/'01_Data/telco_churn_raw.csv'
if path.exists():
 assert hashlib.sha256(path.read_bytes()).hexdigest()==expected,'Existing file does not match; no overwrite performed'
 print('Existing input hash verified')
else:
 data=urllib.request.urlopen(url,timeout=60).read()
 assert hashlib.sha256(data).hexdigest()==expected,'Upstream content differs; stop and investigate'
 path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data);print('Downloaded and verified',path)
