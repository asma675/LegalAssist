# Authorized local legal corpus

Place law-firm-owned, licensed, public-domain, or otherwise authorized `.txt` / `.md` materials here, then run:

```bash
docker compose run --rm backend python scripts/import_local_corpus.py
```

Do **not** bulk-copy CanLII content into this folder without permission. Rafi's supplied bulk loader uses the official Justice Canada XML repository for federal Acts and regulations instead.
