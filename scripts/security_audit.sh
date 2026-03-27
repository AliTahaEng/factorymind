#!/usr/bin/env bash
set -euo pipefail
SERVICES=(inference-service api-service frontend)
EXIT_CODE=0
echo "=== FactoryMind Security Audit === $(date -u)"
if command -v trivy &>/dev/null; then
  for svc in "${SERVICES[@]}"; do
    echo "Scanning factorymind/${svc}:latest..."
    trivy image --exit-code 1 --severity HIGH,CRITICAL --ignore-unfixed "factorymind/${svc}:latest" \
      && echo "[PASS] ${svc}" || { echo "[FAIL] ${svc}"; EXIT_CODE=1; }
  done
else
  echo "[WARN] Trivy not installed. Skipping container scans."
fi
echo "=== Done (exit: ${EXIT_CODE}) ==="; exit $EXIT_CODE
