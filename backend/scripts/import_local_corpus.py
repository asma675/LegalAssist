"""Import law-firm licensed/public-domain TXT/MD files from /data/legal_corpus."""
from pathlib import Path
import os, sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from app.db import Base, engine, SessionLocal
from app.models import CorpusDocument

ROOT=Path(os.getenv("CORPUS_DIR","/data/legal_corpus"))
def main():
    Base.metadata.create_all(bind=engine); db=SessionLocal(); n=0
    try:
        for p in ROOT.rglob('*'):
            if p.suffix.lower() not in {'.txt','.md'}: continue
            text=p.read_text(errors='ignore')
            if len(text)<100: continue
            db.add(CorpusDocument(source_type="local_authorized",title=p.stem,jurisdiction="Canada",source_url=None,text_content=text,metadata_json={"path":str(p)})); n+=1
        db.commit(); print(f"Imported {n} local documents")
    finally: db.close()
if __name__=='__main__': main()
