#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PASS=0
FAIL=0

run() {
  local label="$1"; shift
  if "$@" >/dev/null 2>&1; then
    printf 'PASS %s\n' "$label"; PASS=$((PASS + 1))
  else
    printf 'FAIL %s\n' "$label"; FAIL=$((FAIL + 1))
  fi
}

negative() {
  # Inverted check: *violation* fixtures must be REJECTED by the validator.
  local label="$1"; shift
  if "$@" >/dev/null 2>&1; then
    printf 'FAIL negative/%s (validator did not reject violation)\n' "$label"; FAIL=$((FAIL + 1))
  else
    printf 'PASS negative/%s\n' "$label"; PASS=$((PASS + 1))
  fi
}

# ---- Phase 0: registry contract (借鉴点三) — must pass BEFORE consistency, so template↔validator drift never reaches fixtures ----
run "registry/contract-schema+closure" python3 "$ROOT/src/scripts/registry_contract_check.py"

# ---- Phase 0b-1: fixtures 脱敏检查（E3）— 任一疑似未脱敏真实数据即 FAIL ----
run "desensitize/test-fixtures" python3 "$ROOT/src/scripts/desensitize_check.py"

# ---- Phase 0b-2: cross-document consistency (registry-vs-docs paths / skill contracts / E1/E3/E desensitization) ----
run "consistency/registry-vs-docs" python3 "$ROOT/src/scripts/consistency_check.py"

while IFS=$'\t' read -r skill path; do
  [ "$skill" = "sub-validator" ] && { run "sub-validator/${path#"$ROOT/src/"/}" python3 -c "compile(open('$ROOT/$path/validate_artifact.py').read(),'x','exec')"; continue; }
  validator="$ROOT/$path/scripts/validate_artifact.py"
  fixtures="$ROOT/test/skills/$skill/fixtures"
  [ -f "$validator" ] || { printf 'FAIL missing validator %s\n' "$skill"; FAIL=$((FAIL + 1)); continue; }
  [ -d "$fixtures" ] || { printf 'FAIL missing fixtures %s\n' "$skill"; FAIL=$((FAIL + 1)); continue; }
  for fixture in "$fixtures"/*.md; do
    [ -f "$fixture" ] || continue
    case "$(basename "$fixture")" in
      *violation*)
        negative "$skill/$(basename "$fixture")" python3 "$validator" "$fixture" --json
        continue ;;
    esac
    run "$skill/$(basename "$fixture")" python3 "$validator" "$fixture" --json
  done
done < <(python3 - "$ROOT/src/framework/workflow-registry.json" <<'PY'
import json,sys
r=json.load(open(sys.argv[1]))
for i in r['work_items']:
    print(f"{i['id']}\t{i['skill_path']}")
# sub-skills: only syntax-check validators (they validate parent artifact sections)
for i in r['work_items']:
    base = i['skill_path']
    subdir = f"{base}/skills"
    import os
    if os.path.isdir(subdir):
        for sub in sorted(os.listdir(subdir)):
            v = f"{subdir}/{sub}/scripts/validate_artifact.py"
            if os.path.isfile(v):
                print(f"sub-validator\t{subdir}/{sub}/scripts")
PY
)

# Syntax-check branch/support-skill validators (registry-driven: independent artifacts, no parent section)
while IFS=$'\t' read -r skill path; do
  v="$ROOT/$path/scripts/validate_artifact.py"
  [ -f "$v" ] || { printf 'FAIL missing branch validator %s\n' "$skill"; FAIL=$((FAIL + 1)); continue; }
  run "branch-validator/$skill" python3 -c "compile(open('$v').read(),'$v','exec')"
done < <(python3 - "$ROOT/src/framework/workflow-registry.json" <<'PY'
import json,sys
r=json.load(open(sys.argv[1]))
for c in r.get('support_capabilities', []):
    print(f"{c['id']}\t{c['skill_path']}")
PY
)

# Fixture-test sub-skill validators (now with fixture dirs)
for dir in "$ROOT"/src/stages/002-product-requirements/skills/product-ux/skills/*/ "$ROOT"/src/stages/002-product-requirements/skills/function-description/skills/*/; do
  skill=$(basename "$dir")
  validator="$dir/scripts/validate_artifact.py"
  fixtures="$ROOT/test/skills/$skill/fixtures"
  [ -f "$validator" ] || { printf 'FAIL missing sub-validator %s\n' "$skill"; FAIL=$((FAIL + 1)); continue; }
  [ -d "$fixtures" ] || { printf 'FAIL missing fixtures %s\n' "$skill"; FAIL=$((FAIL + 1)); continue; }
  for fixture in "$fixtures"/*.md; do
    [ -f "$fixture" ] || continue
    case "$(basename "$fixture")" in
      *violation*)
        negative "sub-skill/$skill/$(basename "$fixture")" python3 "$validator" "$fixture" --json
        continue ;;
    esac
    run "sub-skill/$skill/$(basename "$fixture")" python3 "$validator" "$fixture" --json
  done
done

# Fixture-test branch/support-skill validators (registry-driven)
while IFS=$'\t' read -r skill path; do
  validator="$ROOT/$path/scripts/validate_artifact.py"
  fixtures="$ROOT/test/skills/$skill/fixtures"
  [ -f "$validator" ] || { printf 'FAIL missing branch validator %s\n' "$skill"; FAIL=$((FAIL + 1)); continue; }
  [ -d "$fixtures" ] || { printf 'FAIL missing fixtures %s\n' "$skill"; FAIL=$((FAIL + 1)); continue; }
  for fixture in "$fixtures"/*.md; do
    [ -f "$fixture" ] || continue
    case "$(basename "$fixture")" in
      *violation*)
        negative "branch-skill/$skill/$(basename "$fixture")" python3 "$validator" "$fixture" --json
        continue ;;
    esac
    run "branch-skill/$skill/$(basename "$fixture")" python3 "$validator" "$fixture" --json
  done
done < <(python3 - "$ROOT/src/framework/workflow-registry.json" <<'PY'
import json,sys
r=json.load(open(sys.argv[1]))
for c in r.get('support_capabilities', []):
    print(f"{c['id']}\t{c['skill_path']}")
PY
)

while IFS= read -r test_file; do
  run "unit/${test_file#"$ROOT/test/"}" python3 "$test_file"
done < <(find "$ROOT/test" -name 'test_*.py' -type f | sort)

for req_dir in "$ROOT"/requirements/REQ-*; do
  [ -d "$req_dir" ] || continue
  req="$(basename "$req_dir")"
  run "status/$req" python3 "$ROOT/src/scripts/orchestrator.py" "$req_dir" --json
  run "records/$req" python3 "$ROOT/src/scripts/branch_validator.py" "$req_dir" --json
  if [ -f "$req_dir/003-prd-output/prd.md" ] && ! grep -q '^status: simulated' "$req_dir/003-prd-output/prd.md"; then
    run "trace/$req" python3 "$ROOT/src/scripts/traceability_check.py" "$req_dir" --json
  fi
done

printf '\nResult: %d passed / %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
