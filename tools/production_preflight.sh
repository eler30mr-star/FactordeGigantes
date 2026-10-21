#!/usr/bin/env bash
# Factor de Gigantes: proteger despliegues de Cloudflare desde main.
# No hace peticiones remotas, no modifica D1, no usa secretos.
set -euo pipefail
node --check src/worker.js
node --check src/research-control.mjs
node --check src/system-readiness.mjs
node --check public/app.js
node --check public/dossier-editor.js
node --test \
  tests/test_editorial_gate.mjs \
  tests/test_dossier_editor.mjs \
  tests/test_research_control.mjs \
  tests/test_system_readiness.mjs
python3 -m unittest discover -s tests -p 'test_editorial_audit.py' -v
python3 -m unittest discover -s tests -p 'test_edgar_discovery.py' -v
python3 -m unittest discover -s tests -p 'test_financial_facts.py' -v
python3 -m unittest discover -s tests -p 'test_editorial_package.py' -v
python3 -m unittest discover -s tests -p 'test_official_document_links.py' -v
python3 -m unittest discover -s tests -p 'test_primary_source_discovery.py' -v
python3 -m unittest discover -s tests -p 'test_blackberry_sources_pilot.py' -v
python3 -m unittest discover -s tests -p 'test_blackberry_script_quality.py' -v
python3 -m tools.blackberry_script_quality --out dist/blackberry-script
python3 -m unittest discover -s tests -p 'test_blackberry_edl.py' -v
python3 -m tools.blackberry_edl --out dist/blackberry-script
python3 -m unittest discover -s tests -p 'test_research_providers.py' -v
python3 -m unittest discover -s tests -p 'test_market_radar.py' -v
python3 -m unittest discover -s tests -p 'test_market_sources.py' -v
echo "Factor de Gigantes: pruebas previas al despliegue SUPERADAS"
