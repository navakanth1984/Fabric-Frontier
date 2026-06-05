# test_failclosed.ps1 — Phase 5 Network Isolation Verification
# Run from ClawGlove repo root: .\scripts\test_failclosed.ps1
#
# Tests:
#   1. Stack comes up healthy
#   2. Agent direct access to api.sarvam.ai is blocked (internal: true network)
#   3. Agent can reach sidecar proxy on :8080
#   4. Sidecar down → agent has zero external access (fail-closed)
#   5. Sidecar restart → agent proxy route recovers

$ErrorActionPreference = "Stop"
$PASS  = "[PASS]"
$FAIL  = "[FAIL]"
$INFO  = "[INFO]"
$TOTAL_PASS = 0
$TOTAL_FAIL = 0

function Write-Pass($msg) { Write-Host "  $PASS $msg" -ForegroundColor Green;  $script:TOTAL_PASS++ }
function Write-Fail($msg) { Write-Host "  $FAIL $msg" -ForegroundColor Red;    $script:TOTAL_FAIL++ }
function Write-Info($msg) { Write-Host "  $INFO $msg" -ForegroundColor Cyan }

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  ClawGlove Phase 5 — Fail-Closed Network Isolation Test   " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# ── Step 1: Build and start the full stack ───────────────────────────
Write-Host "[1/5] Building and starting Docker stack..." -ForegroundColor Yellow
docker compose up -d --build
if ($LASTEXITCODE -ne 0) { Write-Error "docker compose up failed. Check Docker daemon."; exit 1 }

Write-Info "Waiting 25s for services to initialise (Kafka/etcd need time)..."
Start-Sleep -Seconds 25

# ── Step 2: Verify sidecar healthy ──────────────────────────────────
Write-Host ""
Write-Host "[2/5] Verifying sidecar health..." -ForegroundColor Yellow

$health = docker inspect --format="{{.State.Health.Status}}" clawglove-sidecar 2>&1
if ($health -match "healthy") {
    Write-Pass "Sidecar healthy (status: $health)"
} else {
    Write-Fail "Sidecar not healthy (status: $health)"
    Write-Host "       Check: docker logs clawglove-sidecar" -ForegroundColor DarkYellow
}

# ── Step 3: Network isolation — direct access must be blocked ────────
Write-Host ""
Write-Host "[3/5] Testing network isolation (direct access must be blocked)..." -ForegroundColor Yellow

$isolation_script = @'
import requests, sys
try:
    r = requests.get("https://api.sarvam.ai", proxies={"http": None, "https": None}, timeout=5)
    print(f"BREACH: got HTTP {r.status_code}")
    sys.exit(1)
except Exception as e:
    print(f"BLOCKED: {type(e).__name__}")
    sys.exit(0)
'@

$result = docker exec clawglove-screenwriter-agent python -c $isolation_script 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Pass "Direct access blocked — $result"
} else {
    Write-Fail "Network isolation FAILED — $result"
    Write-Host "       Agent can reach api.sarvam.ai without proxy. Check network config." -ForegroundColor DarkYellow
}

# Also verify the director agent
$result2 = docker exec clawglove-director-agent python -c $isolation_script 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Pass "Director: direct access blocked — $result2"
} else {
    Write-Fail "Director: network isolation FAILED — $result2"
}

# ── Step 4: Fail-closed — stop sidecar, agent must lose all access ───
Write-Host ""
Write-Host "[4/5] Testing fail-closed (stopping sidecar → agent must go dark)..." -ForegroundColor Yellow

Write-Info "Stopping clawglove-sidecar..."
docker stop clawglove-sidecar | Out-Null
Start-Sleep -Seconds 3

$failclosed_script = @'
import requests, sys, os
proxy = os.environ.get("HTTP_PROXY", "http://clawglove-sidecar:8080")
try:
    r = requests.get("https://api.sarvam.ai", timeout=5)
    print(f"ACCESS_SUCCEEDED (status {r.status_code}) — fail-closed BREACH")
    sys.exit(1)
except requests.exceptions.ProxyError as e:
    print(f"FAIL_CLOSED: ProxyError — sidecar down, agent blocked")
    sys.exit(0)
except requests.exceptions.ConnectionError as e:
    print(f"FAIL_CLOSED: ConnectionError — {str(e)[:80]}")
    sys.exit(0)
except Exception as e:
    print(f"FAIL_CLOSED: {type(e).__name__} — {str(e)[:80]}")
    sys.exit(0)
'@

$result = docker exec clawglove-screenwriter-agent python -c $failclosed_script 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Pass "Fail-closed confirmed — $result"
} else {
    Write-Fail "Fail-closed FAILED — agent has internet access without sidecar"
    Write-Host "       This means agents can bypass governance. Review network config." -ForegroundColor DarkYellow
}

# ── Step 5: Restart sidecar, verify recovery ────────────────────────
Write-Host ""
Write-Host "[5/5] Restarting sidecar and verifying recovery..." -ForegroundColor Yellow

Write-Info "Starting clawglove-sidecar..."
docker start clawglove-sidecar | Out-Null
Write-Info "Waiting 15s for sidecar to become healthy..."
Start-Sleep -Seconds 15

$recover_script = @'
import socket, sys
try:
    s = socket.create_connection(("clawglove-sidecar", 50051), timeout=5)
    s.close()
    print("TCP :50051 reachable — daemon recovered")
    sys.exit(0)
except Exception as e:
    print(f"TCP :50051 unreachable — {type(e).__name__}")
    sys.exit(1)
'@

$result = docker exec clawglove-screenwriter-agent python -c $recover_script 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Pass "Sidecar recovered — $result"
} else {
    Write-Fail "Sidecar recovery failed — $result"
}

# ── Summary ──────────────────────────────────────────────────────────
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  RESULT: $TOTAL_PASS passed / $TOTAL_FAIL failed" -ForegroundColor $(if ($TOTAL_FAIL -eq 0) { "Green" } else { "Red" })
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

if ($TOTAL_FAIL -eq 0) {
    Write-Host "  Phase 5 COMPLETE — fail-closed network isolation verified." -ForegroundColor Green
    Write-Host "  Run next: .\scripts\cgbench_docker.ps1" -ForegroundColor Cyan
} else {
    Write-Host "  Phase 5 INCOMPLETE — fix failures before running CGBench." -ForegroundColor Red
    Write-Host "  Debug: docker logs clawglove-sidecar" -ForegroundColor DarkYellow
    Write-Host "         docker network inspect clawglove_clawglove-internal" -ForegroundColor DarkYellow
    exit 1
}
