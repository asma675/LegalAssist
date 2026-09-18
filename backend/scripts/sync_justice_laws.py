"""Load the official Justice Canada XML corpus into Rafi.

Source: https://github.com/justicecanada/laws-lois-xml
Justice Canada's FAQ states that the XML repository contains all consolidated
federal Acts and regulations and that federal enactments may be reproduced
subject to due diligence and not being represented as an official version.

This script downloads the official GitHub repository ZIP, parses XML documents,
and imports them as searchable RAG sources. It refuses to silently claim a
1,000-document corpus: by default it exits non-zero if fewer than 1,000 legal
instruments are imported.
"""
from __future__ import annotations
import io, os, re, sys, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
import httpx

sys.path.append(str(Path(__file__).resolve().parents[1]))
from app.db import Base, engine, SessionLocal
from app.models import CorpusDocument

URL = os.getenv("JUSTICE_LAWS_ZIP", "https://github.com/justicecanada/laws-lois-xml/archive/refs/heads/main.zip")
MIN_DOCS = int(os.getenv("MIN_CORPUS_DOCS", "1000"))

def text_of(root):
    chunks=[]
    for el in root.iter():
        if el.text and el.text.strip(): chunks.append(el.text.strip())
    return re.sub(r"\s+", " ", " ".join(chunks))

def localname(tag): return tag.split('}')[-1]

def first_text(root, names):
    wanted=set(names)
    for el in root.iter():
        if localname(el.tag) in wanted and el.text and el.text.strip():
            return el.text.strip()
    return None

def main():
    print(f"Downloading official Justice Canada XML corpus from {URL}")
    r=httpx.get(URL, timeout=180, follow_redirects=True); r.raise_for_status()
    z=zipfile.ZipFile(io.BytesIO(r.content))
    xml_names=[n for n in z.namelist() if n.lower().endswith('.xml')]
    Base.metadata.create_all(bind=engine)
    db=SessionLocal(); imported=0; skipped=0
    try:
        # Idempotent for Justice Laws source.
        db.query(CorpusDocument).filter(CorpusDocument.source_type=="justice_laws_xml").delete(synchronize_session=False)
        db.commit()
        for name in xml_names:
            try:
                root=ET.fromstring(z.read(name))
                title=first_text(root,["ShortTitle","LongTitle","Title"]) or Path(name).stem
                current=first_text(root,["CurrentToDate","LastAmendedDate"])
                body=text_of(root)
                if len(body)<100: skipped+=1; continue
                db.add(CorpusDocument(
                    source_type="justice_laws_xml", title=title[:400], citation=None,
                    jurisdiction="Canada", source_url="https://laws-lois.justice.gc.ca/eng/",
                    current_to=current, text_content=body,
                    metadata_json={"repository_path":name,"official_source":"Justice Laws Website","not_official_reproduction":True}
                ))
                imported+=1
                if imported % 100 == 0:
                    db.commit(); print(f"Imported {imported} instruments...")
            except Exception as e:
                skipped+=1; print(f"skip {name}: {e}")
        db.commit()
        total=db.query(CorpusDocument).filter(CorpusDocument.source_type=="justice_laws_xml").count()
        print(f"Imported {total}; skipped {skipped}")
        if total < MIN_DOCS:
            raise SystemExit(f"Corpus validation failed: expected at least {MIN_DOCS} official instruments, got {total}.")
        print("Corpus validation passed.")
    finally:
        db.close()

if __name__ == "__main__": main()
