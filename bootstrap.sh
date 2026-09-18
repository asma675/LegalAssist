#!/usr/bin/env sh
set -eu
[ -f backend/.env ] || cp backend/.env.example backend/.env
docker compose up -d --build
printf '\nRafi is starting at http://localhost:8080\n'
printf 'Demo login: admin@rafi.app / ChangeMe123!\n'
printf 'To add 1,000+ official Justice Canada instruments, run:\n  docker compose run --rm backend python scripts/sync_justice_laws.py\n'
