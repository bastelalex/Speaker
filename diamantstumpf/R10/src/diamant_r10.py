"""Build the offline SOLANAL viewer from the signed-off R09 model."""
import base64
import gzip
from io import BytesIO
import json
from pathlib import Path
import re
import sys
import zipfile

HERE=Path(__file__).resolve().parent
OUT=HERE.parent/"outputs"
ROOT=HERE.parent.parent
for rev in ("R08","R07","R09"):
    src=ROOT/rev/"src"
    if src.is_dir():
        sys.path.insert(0,str(src))

import diamant_r09 as r9


def input_file(suffix):
    name="Diamantstumpf_R09_"+suffix
    local=OUT/name
    return local if local.is_file() else ROOT/"R09"/name


def main():
    page=input_file("Signature.html").read_text(encoding="utf-8")
    match=re.search(r'<script id="model-data" type="application/octet-stream">([A-Za-z0-9+/=]+)</script>',page)
    if not match:
        raise ValueError("Keine R09-Modelldaten im HTML gefunden")
    data=json.loads(gzip.decompress(base64.b64decode(match[1])))
    with zipfile.ZipFile(input_file("Geometrien_STL.zip")) as archive:
        base=r9.r.tm.load_mesh(BytesIO(archive.read("S3_Horn.stl")),file_type="stl")
    assert base.is_watertight and base.is_winding_consistent and base.area_faces.min()>0
    # The deformed region ends in front of the nearest side-port tube wall.
    assert r9.PORT_D-r9.PORT_R-3>130
    src=data["signature"]["S3"]
    data["signature"]={"SL":dict(src,name="SOLANAL",
                               description="Anatomisch inspirierte Kontur als Holzrelief im vorderen Hornverlauf. Vier Seiteneintritte und ein zentraler Hochtonhals.",
                               mesh=r9.r.data_mesh(base)),**data["signature"]}
    payload=base64.b64encode(gzip.compress(json.dumps(data,ensure_ascii=False,separators=(",",":")).encode(),
                                          mtime=0,compresslevel=6)).decode()
    previous=(r9.r7.HERE/"diamant_r07.html").read_text(encoding="utf-8")
    studio=previous[previous.index("function studioEnvironment("):previous.index("function mount(){")]
    template=(HERE/"diamant_r10.html").read_text(encoding="utf-8")
    library=(r9.r7.HERE/"three-face.min.js").read_text(encoding="utf-8")
    custom=(HERE/"solanal.js").read_text(encoding="utf-8")
    OUT.mkdir(exist_ok=True)
    (OUT/"Diamantstumpf_R10_SOLANAL.html").write_text(
        template.replace("/*THREE*/",library).replace("/*STUDIO*/",studio)
        .replace("/*SOLANAL*/",custom).replace("/*DATA*/",payload),encoding="utf-8")


if __name__=="__main__":
    main()
