// Host half of dsh-ai-pm.
//
// Bridges the pm-scaffold PRD pipeline into DeepSeek Harness:
//   1. Model tools (agent-facing): ai_pm_init / status / entry / gate / reflow /
//      skill / artifact — thin wrappers over `src/scripts/pipeline.py` plus
//      SKILL.md / artifact readers, so the agent drafts PRD artifacts guided
//      by the 19-skill scaffold and runs machine gates through the same
//      command surface the scaffold itself uses.
//   2. HTTP API (GUI-facing): /api/ai-pm — the Web panel lists requirements,
//      runs gates, and performs the HUMAN review step (the only path that may
//      set `confirmed`). The review command is deliberately NOT exposed as a
//      model tool: `confirmed` can only be produced by a real human.
//
// Hard constraint inherited from pm-scaffold: machine checks never produce
// `confirmed`; `pipeline.py review --decision approve` with a real reviewer
// (name + id + role matched against 00-input/authorized-reviewers.json) is the
// only writer of that state.

import { spawn } from "node:child_process";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { existsSync, readFileSync, readdirSync } from "node:fs";
import { defineTool } from "@deepseek-ai/dsh-tools";

export const name = "dsh-ai-pm";
/** Hard dependencies: tool registry + HTTP carrier. */
export const inject = ["tools", "webServer"];

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const REGISTRY_PATH = join(ROOT, "src", "framework", "workflow-registry.json");
const REQUIREMENTS_DIR = join(ROOT, "requirements");
const REQ_ID_RE = /^[A-Za-z0-9][A-Za-z0-9_-]*$/;

// ── registry / skill / artifact index ───────────────────────────────────────

function loadRegistry() {
  try {
    return JSON.parse(readFileSync(REGISTRY_PATH, "utf8"));
  } catch {
    return null;
  }
}

/** skillId -> absolute directory holding SKILL.md (work items + capabilities). */
function skillIndex(registry) {
  const idx = new Map();
  const push = (id, skillPath) => {
    if (id && skillPath) idx.set(id, join(ROOT, skillPath));
  };
  for (const w of registry?.work_items || []) push(w.id, w.skill_path);
  for (const c of registry?.internal_capabilities || []) push(c.id, c.skill_path);
  for (const c of registry?.support_capabilities || []) push(c.id, c.skill_path);
  return idx;
}

/** artifact_dir/file for a work item (registry is the single source of truth). */
function artifactInfo(registry, workItemId) {
  const w = (registry?.work_items || []).find((x) => x.id === workItemId);
  if (!w) return null;
  return { dir: w.artifact_dir, file: w.artifact_file, name: w.name };
}

function workItemIds(registry) {
  return (registry?.work_items || []).map((w) => w.id);
}

// ── pipeline runner ─────────────────────────────────────────────────────────

function runPipeline(args, config, timeoutMs = 90000) {
  return new Promise((res) => {
    // Windows: `python` is often a Microsoft Store stub that exits silently
    // (9009); the `py` launcher resolves a real interpreter. macOS/Linux: python3.
    const py = config?.pythonCmd || (process.platform === "win32" ? "py" : "python3");
    const child = spawn(py, [join("src", "scripts", "pipeline.py"), ...args], {
      cwd: ROOT,
      env: { ...process.env, PYTHONIOENCODING: "utf-8", PYTHONUTF8: "1" },
      windowsHide: true,
    });
    let out = "";
    let err = "";
    const timer = setTimeout(() => {
      child.kill();
      res({ ok: false, error: `pipeline.py timed out after ${timeoutMs}ms`, stdout: out, stderr: err });
    }, timeoutMs);
    child.stdout.on("data", (d) => { out += d; });
    child.stderr.on("data", (d) => { err += d; });
    child.on("error", (e) => {
      clearTimeout(timer);
      res({ ok: false, error: `cannot run ${py}: ${String((e && e.message) || e)}`, stdout: out, stderr: err });
    });
    child.on("close", (code) => {
      clearTimeout(timer);
      if (code === 0) {
        let json = null;
        try { json = JSON.parse(out); } catch { /* non-JSON output is fine */ }
        res({ ok: true, code, stdout: out, json, stderr: err });
      } else {
        res({ ok: false, code, stdout: out, stderr: err, error: `pipeline.py exited ${code}` });
      }
    });
  });
}

/** Read a text file, tolerating absence. */
function readText(file) {
  try {
    return existsSync(file) ? readFileSync(file, "utf8") : null;
  } catch {
    return null;
  }
}

function readdirSafe(dir) {
  try {
    return readdirSync(dir);
  } catch {
    return [];
  }
}

// ── shared command plumbing ─────────────────────────────────────────────────

function reqDir(reqId) {
  if (!REQ_ID_RE.test(String(reqId || ""))) {
    throw new Error(`invalid requirement id: ${JSON.stringify(reqId)} (use REQ-NNN-topic, letters/digits/_- only)`);
  }
  return join(REQUIREMENTS_DIR, String(reqId));
}

function assertWorkItem(registry, workItem) {
  const ids = workItemIds(registry);
  if (!ids.includes(workItem)) {
    throw new Error(`unknown work item: ${JSON.stringify(workItem)}; expected one of: ${ids.join(", ")}`);
  }
}

/** Human-readable rendering of a pipeline result for the agent loop. */
function renderPipeline(result) {
  const lines = [];
  if (result.error) lines.push(`ERROR: ${result.error}`);
  if (result.stderr) lines.push(result.stderr.trim());
  if (result.stdout) lines.push(result.stdout.trim());
  return lines.filter(Boolean).join("\n") || "(no output)";
}

// ── model tools ─────────────────────────────────────────────────────────────

function registerTools(ctx, config) {
  const tools = [
    {
      name: "ai_pm_init",
      description:
        "Create a new PRD requirement skeleton in the ai-pm workspace (calls pm-scaffold pipeline.py init). " +
        "Returns the created directory layout. Follow up with ai_pm_status and the skill guides.",
      parameters: {
        reqId: { type: "string", required: true, description: "Requirement id, e.g. REQ-005-order-refund." },
      },
      async execute(args) {
        // init creates a directory under REQUIREMENTS_DIR; validate the id so a
        // crafted reqId cannot escape the workspace (spawn args are not a shell,
        // but a path-traversal name would still create files elsewhere).
        if (!REQ_ID_RE.test(String(args.reqId || ""))) {
          throw new Error(`invalid requirement id: ${JSON.stringify(args.reqId)} (use REQ-NNN-topic, letters/digits/_- only)`);
        }
        const r = await runPipeline(["init", String(args.reqId)], config);
        return renderPipeline(r);
      },
    },
    {
      name: "ai_pm_status",
      description:
        "Show the ai-pm workspace state: without reqId, list every requirement; " +
        "with reqId, show the full pipeline status (active work item, next step, per-artifact state, violation signals).",
      parameters: {
        reqId: { type: "string", description: "Optional requirement id (e.g. REQ-005-order-refund)." },
      },
      async execute(args) {
        if (!args.reqId) {
          const names = existsSync(REQUIREMENTS_DIR)
            ? readdirSafe(REQUIREMENTS_DIR).filter((d) => existsSync(join(REQUIREMENTS_DIR, d, "README.md")))
            : [];
          return names.length
            ? `ai-pm requirements in ${REQUIREMENTS_DIR}:\n${names.map((n) => `  - ${n}`).join("\n")}\n\nRun ai_pm_status with reqId for detail.`
            : `No requirements yet. Use ai_pm_init with reqId (e.g. REQ-001-topic) to create one.`;
        }
        const r = await runPipeline([reqDir(args.reqId), "status", "--json"], config);
        return renderPipeline(r);
      },
    },
    {
      name: "ai_pm_entry",
      description:
        "Entry maturity check (L0-L4) for a requirement: decides whether the raw materials are sufficient, " +
        "whether to run requirement-restate first, and what the next work item is.",
      parameters: {
        reqId: { type: "string", required: true, description: "Requirement id." },
      },
      async execute(args) {
        const r = await runPipeline([reqDir(args.reqId), "entry", "--json"], config);
        return renderPipeline(r);
      },
    },
    {
      name: "ai_pm_gate",
      description:
        "Run the machine gate (DoR/DoD/six-state annotation/B3 close-up/traceability validators) for one work item. " +
        "Read-only: it never changes state and never produces `confirmed`. " +
        "Fix the reported issues in the artifact, then re-run. Only after the gate passes may a HUMAN review (GUI) approve it.",
      parameters: {
        reqId: { type: "string", required: true, description: "Requirement id." },
        workItem: { type: "string", required: true, description: "Work item id (e.g. project-background-goal)." },
      },
      async execute(args) {
        const registry = loadRegistry();
        assertWorkItem(registry, args.workItem);
        const r = await runPipeline([reqDir(args.reqId), "gate", "--work-item", args.workItem, "--json"], config);
        return renderPipeline(r);
      },
    },
    {
      name: "ai_pm_reflow",
      description:
        "Change-reflow preview (dry-run by default) or --apply: cascade-invalidate downstream artifacts when an " +
        "upstream confirmed artifact changed. Use --apply only when the change is final.",
      parameters: {
        reqId: { type: "string", required: true, description: "Requirement id." },
        workItem: { type: "string", required: true, description: "Work item id that changed." },
        apply: { type: "boolean", description: "Apply the cascade (default false = dry-run)." },
      },
      async execute(args) {
        const registry = loadRegistry();
        assertWorkItem(registry, args.workItem);
        const cmd = [reqDir(args.reqId), "reflow", "--work-item", args.workItem];
        if (args.apply) cmd.push("--apply");
        const r = await runPipeline(cmd, config);
        return renderPipeline(r);
      },
    },
    {
      name: "ai_pm_skill",
      description:
        "Read the SKILL.md of a pm-scaffold skill (work item, sub-skill, or support capability) so you follow its " +
        "execution protocol, thinking prompts, anti-patterns and completion checklist when drafting the artifact.",
      parameters: {
        skillId: {
          type: "string",
          required: true,
          description: "Skill id, e.g. project-background-goal, product-ux, page-design, competitive-research, requirement-restate.",
        },
      },
      async execute(args) {
        const idx = skillIndex(loadRegistry());
        const dir = idx.get(String(args.skillId));
        if (!dir) {
          return `Unknown skill: ${args.skillId}. Available: ${[...idx.keys()].join(", ")}`;
        }
        const md = readText(join(dir, "SKILL.md"));
        return md !== null ? md : `SKILL.md not found under ${dir}`;
      },
    },
    {
      name: "ai_pm_artifact",
      description:
        "Read the current artifact file of a work item for a requirement, so you can continue drafting or review " +
        "what the machine gate found. Useful before/after ai_pm_gate.",
      parameters: {
        reqId: { type: "string", required: true, description: "Requirement id." },
        workItem: { type: "string", required: true, description: "Work item id." },
      },
      async execute(args) {
        const registry = loadRegistry();
        assertWorkItem(registry, args.workItem);
        const info = artifactInfo(registry, args.workItem);
        const artifactPath = join(reqDir(args.reqId), info.dir, info.file);
        const text = readText(artifactPath);
        return text !== null
          ? text
          : `Artifact not found: ${artifactPath} (work item ${args.workItem} may not be drafted yet).`;
      },
    },
  ];

  for (const t of tools) {
    ctx.tools.register(defineTool({
      name: t.name,
      description: t.description,
      parameters: t.parameters,
      output: { schema: { type: "string" }, render: (_a, v) => [{ type: "text", text: v }] },
      execute: t.execute,
    }));
  }
}

// ── HTTP API (GUI-facing, includes the human review gate) ───────────────────

function sameOrigin(req) {
  const origin = req.headers && req.headers.origin;
  const host = req.headers && req.headers.host;
  if (origin === undefined || host === undefined) return false;
  try {
    return new URL(origin).host === host;
  } catch {
    return false;
  }
}

function readBody(req) {
  return new Promise((resolveBody) => {
    let raw = "";
    req.on("data", (chunk) => { raw += chunk; });
    req.on("end", () => {
      try { resolveBody(JSON.parse(raw || "{}")); } catch { resolveBody({}); }
    });
    req.on("error", () => resolveBody({}));
  });
}

function sendJson(res, status, obj) {
  res.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store",
  });
  res.end(JSON.stringify(obj));
}

function registerHttpApi(ctx, config) {
  const webServer = ctx.get("webServer");
  if (webServer === undefined) return;

  webServer.register({
    kind: "exact",
    path: "/api/ai-pm",
    handler: async (req, res) => {
      try {
        const body = await readBody(req);
        const method = String(body.method || "");
        if (!sameOrigin(req)) {
          return sendJson(res, 403, { ok: false, error: "untrusted origin" });
        }

        // list every requirement with a lightweight status
        if (method === "list") {
          const names = existsSync(REQUIREMENTS_DIR)
            ? readdirSafe(REQUIREMENTS_DIR).filter((d) => existsSync(join(REQUIREMENTS_DIR, d, "README.md")))
            : [];
          const items = [];
          for (const n of names) {
            const r = await runPipeline([join(REQUIREMENTS_DIR, n), "status", "--json"], config);
            items.push({ reqId: n, ok: r.ok, error: r.error, status: r.json || null });
          }
          return sendJson(res, 200, { ok: true, requirements: items });
        }

        if (!body.reqId) return sendJson(res, 400, { ok: false, error: "reqId required" });
        let rd;
        try {
          rd = reqDir(body.reqId);
        } catch (e) {
          return sendJson(res, 400, { ok: false, error: String((e && e.message) || e) });
        }

        if (method === "init") {
          const r = await runPipeline(["init", String(body.reqId)], config);
          return sendJson(res, 200, { ok: r.ok, error: r.error, output: r.stdout || r.stderr });
        }

        const registry = loadRegistry();
        const passthrough = async (args, extra = {}) => {
          const r = await runPipeline(args, config);
          return sendJson(res, 200, { ok: r.ok, error: r.error, json: r.json, output: r.stdout || r.stderr, ...extra });
        };

        if (method === "status") return passthrough([rd, "status", "--json"]);
        if (method === "entry") return passthrough([rd, "entry", "--json"]);

        if (method === "reflow") {
          if (!body.workItem) return sendJson(res, 400, { ok: false, error: "workItem required" });
          const args = [rd, "reflow", "--work-item", String(body.workItem)];
          if (body.apply) args.push("--apply");
          return passthrough(args);
        }

        if (method === "gate") {
          if (!body.workItem) return sendJson(res, 400, { ok: false, error: "workItem required" });
          try { assertWorkItem(registry, body.workItem); } catch (e) {
            return sendJson(res, 400, { ok: false, error: String((e && e.message) || e) });
          }
          return passthrough([rd, "gate", "--work-item", String(body.workItem), "--json"]);
        }

        // human review gate — the ONLY writer of `confirmed`
        if (method === "review") {
          const { workItem, decision, reviewer, reviewerId, reviewerRole } = body;
          if (!workItem || !decision || !reviewer || !reviewerId || !reviewerRole) {
            return sendJson(res, 400, {
              ok: false,
              error: "review requires workItem, decision (approve|changes), reviewer, reviewerId, reviewerRole",
            });
          }
          if (!["approve", "changes"].includes(decision)) {
            return sendJson(res, 400, { ok: false, error: "decision must be approve or changes" });
          }
          try { assertWorkItem(registry, workItem); } catch (e) {
            return sendJson(res, 400, { ok: false, error: String((e && e.message) || e) });
          }
          const args = [
            rd, "review",
            "--work-item", String(workItem),
            "--decision", String(decision),
            "--reviewer", String(reviewer),
            "--reviewer-id", String(reviewerId),
            "--reviewer-role", String(reviewerRole),
            "--json",
          ];
          if (body.comments) args.push("--comments", String(body.comments));
          if (body.reason) args.push("--reason", String(body.reason));
          const r = await runPipeline(args, config, 120000);
          return sendJson(res, 200, { ok: r.ok, error: r.error, json: r.json, output: r.stdout || r.stderr });
        }

        return sendJson(res, 404, { ok: false, error: "unknown method " + method });
      } catch (e) {
        return sendJson(res, 500, { ok: false, error: String((e && e.message) || e) });
      }
    },
  });
}

export function apply(ctx, config) {
  registerTools(ctx, config);
  registerHttpApi(ctx, config);
}
