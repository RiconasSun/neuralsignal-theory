#!/usr/bin/env node
"use strict";

const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { spawn } = require("node:child_process");
const { evaluateMissionPolicy } = require("./risk-policy");
const {
  DEFAULT_EXCLUDE_DIRS,
  copyWorkspaceToStaging,
  scanWorkspaceDiff,
  evaluateWritePolicy,
  applyWorkspaceChanges,
} = require("./write-control");

const DEFAULT_CODEX_BIN = process.env.CODEX_BIN || "codex";
const DEFAULT_WORKDIR = process.cwd();

function printHelp() {
  console.log(`Codex Mission Wrapper

Usage:
  codex-code --mission mission.json
  codex-code --mission mission.json --dry-run
  codex-code "implement a health endpoint" --mission-out missions/health.json --spec-only
  codex-code --queue missions/queue.json --enqueue --mission mission.json
  codex-code --queue missions/queue.json --queue-list
  codex-code --queue missions/queue.json --queue-next
  codex-code --queue missions/queue.json --queue-run
  codex-code --stdin < mission.json
  codex-code "implement a health endpoint"

Options:
  --mission <file>          Read a JSON Mission Spec file
  --task <file>             Compatibility alias for --mission
  --mission-out <file>      Write the normalized Mission Spec JSON to a file
  --spec-only               Print/write the normalized Mission Spec and do not run Codex
  --queue <file>            Read/write a Queued Mission List JSON file
  --enqueue                 Add the current mission to --queue
  --queue-list              List queued missions
  --queue-next              Run the next pending mission from --queue
  --queue-run               Run pending missions from --queue
  --queue-limit <n>         Limit --queue-run to n missions
  --queue-json              Print queue list as JSON
  --stdin                   Read JSON Mission Spec or plain request from stdin
  --workdir, -C <dir>       Override Mission Spec target.workdir
  --model, -m <model>       Override Mission Spec codex.model
  --profile, -p <profile>   Override Mission Spec codex.profile
  --sandbox, -s <mode>      Override Mission Spec codex.sandbox
  --approval, -a <policy>   Override Mission Spec codex.approval
  --add-dir <dir>           Extra writable directory, repeatable
  --image, -i <file>        Attach image, repeatable
  --config, -c <key=value>  Codex config override, repeatable
  --search                  Enable Codex web search
  --json-events             Print Codex events as JSONL
  --skip-git-repo-check     Allow running outside a git repository
  --ephemeral               Do not persist Codex session files
  --openrouter              Ask OpenRouter to compile extra mission guidance before Codex
  --openrouter-spec         Ask OpenRouter to turn natural language into Mission Spec JSON
  --openrouter-model <id>   Override Mission Spec openrouter.model
  --openrouter-spec-model <id>
                            Override the OpenRouter model used for spec generation
  --openrouter-key-env <n>  Env var containing the OpenRouter API key
  --openrouter-base-url <u> Override the OpenRouter-compatible API base URL
  --policy <file>           Merge an external risk/write policy JSON file
  --allow-write <glob>      Append an allowed write glob, repeatable
  --deny-write <glob>       Append a denied write glob, repeatable
  --risk-report             Print risk/write policy decision without executing Codex
  --risk-allow-review       Allow review-risk missions to execute
  --no-staged-execution     Run Codex directly in target workdir (debug only)
  --codex-bin <command>     Codex executable (default: codex or CODEX_BIN)
  --dry-run                 Print generated prompt and command without running Codex
  --help, -h                Show this help

Mission Spec JSON:
  {
    "version": "1.0",
    "mission": { "id": "health-endpoint", "objective": "Add GET /health" },
    "target": { "workdir": ".", "files": ["src/server.ts"] },
    "instructions": {
      "requirements": ["Return {\"status\":\"ok\"}"],
      "constraints": ["Keep the change minimal"],
      "nonGoals": ["Do not add authentication"]
    },
    "acceptance": {
      "criteria": ["GET /health returns 200"],
      "validation": ["npm test"]
    },
    "codex": { "sandbox": "workspace-write", "approval": "on-request" },
    "openrouter": { "enabled": true, "model": "openai/gpt-5.2" }
  }
`);
}

function parseArgs(argv) {
  const opts = {
    addDirs: [],
    images: [],
    configs: [],
    allowWrites: [],
    denyWrites: [],
    positional: [],
    codexBin: DEFAULT_CODEX_BIN,
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];

    if (arg === "--help" || arg === "-h") opts.help = true;
    else if (arg === "--mission" || arg === "--task") opts.missionFile = requireValue(argv, ++i, arg);
    else if (arg === "--mission-out") opts.missionOut = requireValue(argv, ++i, arg);
    else if (arg === "--spec-only") opts.specOnly = true;
    else if (arg === "--queue") opts.queueFile = requireValue(argv, ++i, arg);
    else if (arg === "--enqueue" || arg === "--queue-add") opts.enqueue = true;
    else if (arg === "--queue-list") opts.queueList = true;
    else if (arg === "--queue-next") opts.queueNext = true;
    else if (arg === "--queue-run") opts.queueRun = true;
    else if (arg === "--queue-limit") opts.queueLimit = parsePositiveInt(requireValue(argv, ++i, arg), arg);
    else if (arg === "--queue-json") opts.queueJson = true;
    else if (arg === "--stdin") opts.stdin = true;
    else if (arg === "--workdir" || arg === "-C") opts.workdir = requireValue(argv, ++i, arg);
    else if (arg === "--model" || arg === "-m") opts.model = requireValue(argv, ++i, arg);
    else if (arg === "--profile" || arg === "-p") opts.profile = requireValue(argv, ++i, arg);
    else if (arg === "--sandbox" || arg === "-s") opts.sandbox = requireValue(argv, ++i, arg);
    else if (arg === "--approval" || arg === "-a") opts.approval = requireValue(argv, ++i, arg);
    else if (arg === "--add-dir") opts.addDirs.push(requireValue(argv, ++i, arg));
    else if (arg === "--image" || arg === "-i") opts.images.push(requireValue(argv, ++i, arg));
    else if (arg === "--config" || arg === "-c") opts.configs.push(requireValue(argv, ++i, arg));
    else if (arg === "--search") opts.search = true;
    else if (arg === "--json-events") opts.jsonEvents = true;
    else if (arg === "--skip-git-repo-check") opts.skipGitRepoCheck = true;
    else if (arg === "--ephemeral") opts.ephemeral = true;
    else if (arg === "--openrouter") opts.openrouter = true;
    else if (arg === "--openrouter-spec") opts.openrouterSpec = true;
    else if (arg === "--openrouter-model") opts.openrouterModel = requireValue(argv, ++i, arg);
    else if (arg === "--openrouter-spec-model") opts.openrouterSpecModel = requireValue(argv, ++i, arg);
    else if (arg === "--openrouter-key-env") opts.openrouterKeyEnv = requireValue(argv, ++i, arg);
    else if (arg === "--openrouter-base-url") opts.openrouterBaseURL = requireValue(argv, ++i, arg);
    else if (arg === "--policy") opts.policyFile = requireValue(argv, ++i, arg);
    else if (arg === "--allow-write") opts.allowWrites.push(requireValue(argv, ++i, arg));
    else if (arg === "--deny-write") opts.denyWrites.push(requireValue(argv, ++i, arg));
    else if (arg === "--risk-report") opts.riskReport = true;
    else if (arg === "--risk-allow-review") opts.riskAllowReview = true;
    else if (arg === "--no-staged-execution") opts.noStagedExecution = true;
    else if (arg === "--dry-run") opts.dryRun = true;
    else if (arg === "--codex-bin") opts.codexBin = requireValue(argv, ++i, arg);
    else if (arg.startsWith("--")) throw new Error(`Unknown option: ${arg}`);
    else opts.positional.push(arg);
  }

  return opts;
}

function parsePositiveInt(value, flag) {
  const parsed = Number.parseInt(value, 10);
  if (!Number.isInteger(parsed) || parsed < 1) {
    throw new Error(`${flag} requires a positive integer`);
  }
  return parsed;
}

function requireValue(argv, index, flag) {
  const value = argv[index];
  if (!value || value.startsWith("--")) {
    throw new Error(`${flag} requires a value`);
  }
  return value;
}

function readStdin() {
  if (process.stdin.isTTY) return "";
  return fs.readFileSync(0, "utf8").trim();
}

function readMissionFile(filePath) {
  const resolved = path.resolve(filePath);
  const raw = fs.readFileSync(resolved, "utf8");
  return parseMissionInput(raw, resolved);
}

function parseMissionInput(raw, source) {
  const text = raw.trim();
  if (!text) throw new Error(`Empty mission input${source ? `: ${source}` : ""}`);

  if (text.startsWith("{")) {
    try {
      return normalizeMissionSpec(JSON.parse(text), source);
    } catch (error) {
      throw new Error(`Invalid Mission Spec JSON${source ? ` in ${source}` : ""}: ${error.message}`);
    }
  }

  return missionFromText(text);
}

function missionFromText(text) {
  const spec = normalizeMissionSpec({
    version: "1.0",
    mission: {
      id: createMissionId(text),
      objective: text,
    },
    target: {
      workdir: DEFAULT_WORKDIR,
    },
  });
  spec.naturalLanguageInput = text;
  return spec;
}

function createMissionId(text) {
  const slug = text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 48);
  return slug || `mission-${new Date().toISOString().slice(0, 10)}`;
}

function normalizeMissionSpec(input, source) {
  if (!input || typeof input !== "object" || Array.isArray(input)) {
    throw new Error("Mission Spec must be a JSON object.");
  }

  const legacyObjective = input.objective || input.prompt || input.request || input.title;
  const mission = input.mission && typeof input.mission === "object"
    ? { ...input.mission }
    : {};

  if (!mission.objective && legacyObjective) mission.objective = legacyObjective;
  if (!mission.id && input.id) mission.id = input.id;
  if (!mission.title && input.title) mission.title = input.title;

  if (!mission.objective) {
    throw new Error("Mission Spec requires mission.objective.");
  }

  const target = input.target && typeof input.target === "object" ? { ...input.target } : {};
  if (!target.files && input.files) target.files = input.files;
  if (!target.workdir) target.workdir = input.workdir || DEFAULT_WORKDIR;

  const instructions = input.instructions && typeof input.instructions === "object"
    ? { ...input.instructions }
    : {};
  if (!instructions.requirements && input.requirements) instructions.requirements = input.requirements;
  if (!instructions.constraints && input.constraints) instructions.constraints = input.constraints;
  if (!instructions.context && input.context) instructions.context = input.context;
  if (!instructions.notes && input.notes) instructions.notes = input.notes;

  const acceptance = input.acceptance && typeof input.acceptance === "object"
    ? { ...input.acceptance }
    : {};
  if (!acceptance.criteria && (input.acceptanceCriteria || input.acceptance_criteria)) {
    acceptance.criteria = input.acceptanceCriteria || input.acceptance_criteria;
  }
  if (!acceptance.validation && input.tests) acceptance.validation = input.tests;

  const codex = input.codex && typeof input.codex === "object" ? { ...input.codex } : {};
  const policy = input.policy && typeof input.policy === "object" ? { ...input.policy } : {};

  return {
    version: String(input.version || "1.0"),
    source,
    mission,
    target,
    instructions,
    acceptance,
    codex,
    openrouter: input.openrouter && typeof input.openrouter === "object" ? input.openrouter : {},
    policy,
    metadata: input.metadata && typeof input.metadata === "object" ? input.metadata : {},
  };
}

function toMissionSpecJson(spec) {
  const output = {
    version: spec.version,
    mission: spec.mission,
    target: spec.target,
    instructions: spec.instructions,
    acceptance: spec.acceptance,
    codex: spec.codex,
  };

  if (spec.openrouter && Object.keys(spec.openrouter).length > 0) output.openrouter = spec.openrouter;
  if (spec.policy && Object.keys(spec.policy).length > 0) output.policy = spec.policy;
  if (spec.metadata && Object.keys(spec.metadata).length > 0) output.metadata = spec.metadata;

  return output;
}

function cloneJson(value) {
  return JSON.parse(JSON.stringify(value));
}

function applyMissionOverrides(opts, spec) {
  const next = {
    ...spec,
    mission: { ...spec.mission },
    target: { ...spec.target },
    instructions: { ...spec.instructions },
    acceptance: { ...spec.acceptance },
    codex: { ...spec.codex },
    openrouter: { ...spec.openrouter },
    policy: { ...spec.policy },
    metadata: { ...spec.metadata },
  };

  const externalPolicy = loadPolicyOverride(opts);
  if (externalPolicy) {
    next.policy = deepMerge(next.policy || {}, externalPolicy);
  }

  if (opts.workdir) next.target.workdir = opts.workdir;
  if (opts.model) next.codex.model = opts.model;
  if (opts.profile) next.codex.profile = opts.profile;
  if (opts.sandbox) next.codex.sandbox = opts.sandbox;
  if (opts.approval) next.codex.approval = opts.approval;
  if (opts.search) next.codex.search = true;
  if (opts.jsonEvents) next.codex.jsonEvents = true;
  if (opts.skipGitRepoCheck) next.codex.skipGitRepoCheck = true;
  if (opts.ephemeral) next.codex.ephemeral = true;
  if (opts.addDirs.length > 0) next.codex.addDirs = [...normalizeList(next.codex.addDirs || next.codex.add_dirs), ...opts.addDirs];
  if (opts.images.length > 0) next.codex.images = [...normalizeList(next.codex.images), ...opts.images];
  if (opts.configs.length > 0) next.codex.configs = [...normalizeList(next.codex.configs || next.codex.config), ...opts.configs];
  if (opts.openrouter) next.openrouter.enabled = true;
  if (opts.openrouterSpec) {
    next.openrouter.spec = {
      ...(next.openrouter.spec && typeof next.openrouter.spec === "object" ? next.openrouter.spec : {}),
      enabled: true,
    };
  }
  if (opts.openrouterModel) next.openrouter.model = opts.openrouterModel;
  if (opts.openrouterSpecModel) {
    next.openrouter.spec = {
      ...(next.openrouter.spec && typeof next.openrouter.spec === "object" ? next.openrouter.spec : {}),
      model: opts.openrouterSpecModel,
    };
  }
  if (opts.openrouterKeyEnv) next.openrouter.apiKeyEnv = opts.openrouterKeyEnv;
  if (opts.openrouterBaseURL) next.openrouter.baseURL = opts.openrouterBaseURL;
  if (opts.allowWrites.length > 0) {
    next.policy.write = {
      ...(next.policy.write && typeof next.policy.write === "object" ? next.policy.write : {}),
      allow: [
        ...normalizeList(next.policy.write && next.policy.write.allow),
        ...opts.allowWrites,
      ],
    };
  }
  if (opts.denyWrites.length > 0) {
    next.policy.write = {
      ...(next.policy.write && typeof next.policy.write === "object" ? next.policy.write : {}),
      deny: [
        ...normalizeList(next.policy.write && next.policy.write.deny),
        ...opts.denyWrites,
      ],
    };
  }

  return next;
}

function loadPolicyOverride(opts) {
  if (!opts.policyFile) return null;
  const policyPath = path.resolve(opts.policyFile);
  let parsed;
  try {
    parsed = JSON.parse(fs.readFileSync(policyPath, "utf8"));
  } catch (error) {
    throw new Error(`Invalid policy JSON in ${policyPath}: ${error.message}`);
  }
  return parsed.policy && typeof parsed.policy === "object" ? parsed.policy : parsed;
}

function deepMerge(base, override) {
  const output = { ...(base || {}) };
  for (const [key, value] of Object.entries(override || {})) {
    if (isPlainObject(value) && isPlainObject(output[key])) {
      output[key] = deepMerge(output[key], value);
    } else if (Array.isArray(value)) {
      output[key] = [...value];
    } else {
      output[key] = value;
    }
  }
  return output;
}

function isPlainObject(value) {
  return Boolean(value && typeof value === "object" && !Array.isArray(value));
}

function normalizeList(value) {
  if (!value) return [];
  if (Array.isArray(value)) return value.filter(Boolean).map(stringifyValue);
  return [stringifyValue(value)];
}

function stringifyValue(value) {
  if (typeof value === "string") return value;
  return JSON.stringify(value);
}

function formatList(title, values) {
  const list = normalizeList(values);
  if (list.length === 0) return "";
  return `\n## ${title}\n${list.map((item) => `- ${item}`).join("\n")}\n`;
}

function formatBlock(title, value) {
  if (!value) return "";
  return `\n## ${title}\n${stringifyValue(value).trim()}\n`;
}

function buildPrompt(spec) {
  const { mission, target, instructions, acceptance, metadata, openrouterGuidance } = spec;

  return [
    "You are Codex CLI running as a coding agent.",
    "Execute the following JSON Mission Spec against the target repository.",
    "Treat the Mission Spec JSON as the development task contract.",
    "Keep edits scoped, follow existing project style, and run relevant validation when practical.",
    "",
    "## Mission Spec JSON",
    "```json",
    JSON.stringify(toMissionSpecJson(spec), null, 2),
    "```",
    "",
    "## Mission",
    `- Version: ${spec.version}`,
    mission.id ? `- ID: ${mission.id}` : "",
    mission.title ? `- Title: ${mission.title}` : "",
    `- Objective: ${String(mission.objective).trim()}`,
    formatBlock("Context", instructions.context || target.context),
    formatList("Requirements", instructions.requirements),
    formatList("Target Files", target.files),
    formatList("Constraints", instructions.constraints),
    formatList("Non-Goals", instructions.nonGoals || instructions.non_goals),
    formatList("Acceptance Criteria", acceptance.criteria),
    formatList("Validation", acceptance.validation || acceptance.tests),
    formatBlock("OpenRouter Guidance", openrouterGuidance),
    formatBlock("Notes", instructions.notes),
    Object.keys(metadata).length > 0 ? formatBlock("Metadata", metadata) : "",
    "## Final Response",
    "Summarize changed files, validation performed, and any follow-up needed.",
  ]
    .filter(Boolean)
    .join("\n");
}

function mergeRuntimeOptions(opts, spec) {
  const codex = spec.codex || {};
  const openrouter = spec.openrouter || {};
  return {
    ...opts,
    workdir: opts.workdir || codex.workdir || spec.target.workdir || DEFAULT_WORKDIR,
    model: opts.model || codex.model,
    profile: opts.profile || codex.profile,
    sandbox: opts.sandbox || codex.sandbox,
    approval: opts.approval || codex.approval,
    search: opts.search || Boolean(codex.search),
    jsonEvents: opts.jsonEvents || Boolean(codex.jsonEvents || codex.json_events),
    skipGitRepoCheck: opts.skipGitRepoCheck || Boolean(codex.skipGitRepoCheck || codex.skip_git_repo_check),
    ephemeral: opts.ephemeral || Boolean(codex.ephemeral),
    addDirs: [...normalizeList(codex.addDirs || codex.add_dirs), ...opts.addDirs],
    images: [...normalizeList(codex.images), ...opts.images],
    configs: [...normalizeList(codex.configs || codex.config), ...opts.configs],
    openrouter: buildOpenRouterConfig(opts, openrouter),
  };
}

function buildOpenRouterConfig(opts, openrouter = {}) {
  const specConfig = openrouter.spec && typeof openrouter.spec === "object" ? openrouter.spec : {};
  const baseModel = opts.openrouterModel || openrouter.model || process.env.OPENROUTER_MODEL || "openai/gpt-5.2";
  return {
    enabled: Boolean(opts.openrouter || openrouter.enabled),
    model: baseModel,
    apiKeyEnv: opts.openrouterKeyEnv || openrouter.apiKeyEnv || openrouter.api_key_env || "OPENROUTER_API_KEY",
    baseURL: opts.openrouterBaseURL || openrouter.baseURL || openrouter.base_url || "https://openrouter.ai/api/v1",
    referer: openrouter.referer || openrouter.httpReferer || openrouter.http_referer,
    title: openrouter.title || openrouter.appTitle || openrouter.app_title || "Codex Mission Wrapper",
    temperature: typeof openrouter.temperature === "number" ? openrouter.temperature : 0.1,
    maxTokens: openrouter.maxTokens || openrouter.max_tokens || 1200,
    timeoutMs: openrouter.timeoutMs || openrouter.timeout_ms || 60000,
    systemPrompt: openrouter.systemPrompt || openrouter.system_prompt,
    spec: {
      enabled: Boolean(opts.openrouterSpec || specConfig.enabled),
      model: opts.openrouterSpecModel || specConfig.model || process.env.OPENROUTER_SPEC_MODEL || baseModel,
      temperature: typeof specConfig.temperature === "number" ? specConfig.temperature : 0,
      maxTokens: specConfig.maxTokens || specConfig.max_tokens || 2000,
      systemPrompt: specConfig.systemPrompt || specConfig.system_prompt,
    },
  };
}

function loadAxios() {
  try {
    return require("axios");
  } catch (error) {
    throw new Error("OpenRouter integration requires axios. Run npm install first.");
  }
}

async function callOpenRouterChat(config, body) {
  const apiKey = process.env[config.apiKeyEnv];
  if (!apiKey) {
    throw new Error(`OpenRouter is enabled but ${config.apiKeyEnv} is not set.`);
  }

  const axios = loadAxios();
  const endpoint = `${String(config.baseURL).replace(/\/$/, "")}/chat/completions`;
  const headers = {
    Authorization: `Bearer ${apiKey}`,
    "Content-Type": "application/json",
  };
  if (config.referer) headers["HTTP-Referer"] = config.referer;
  if (config.title) headers["X-OpenRouter-Title"] = config.title;

  const response = await axios.post(
    endpoint,
    body,
    {
      headers,
      timeout: config.timeoutMs,
      validateStatus: (status) => status >= 200 && status < 500,
    },
  );

  if (response.status < 200 || response.status >= 300) {
    const detail = typeof response.data === "string" ? response.data : JSON.stringify(response.data);
    throw new Error(`OpenRouter request failed with HTTP ${response.status}: ${detail}`);
  }

  const content = response.data && response.data.choices
    && response.data.choices[0]
    && response.data.choices[0].message
    && response.data.choices[0].message.content;

  if (!content) {
    throw new Error("OpenRouter response did not include choices[0].message.content.");
  }

  return String(content).trim();
}

function extractJsonObject(text) {
  const trimmed = text.trim();
  if (trimmed.startsWith("{") && trimmed.endsWith("}")) return trimmed;

  const fenced = trimmed.match(/```(?:json)?\s*([\s\S]*?)```/i);
  if (fenced) return fenced[1].trim();

  const start = trimmed.indexOf("{");
  const end = trimmed.lastIndexOf("}");
  if (start !== -1 && end !== -1 && end > start) {
    return trimmed.slice(start, end + 1);
  }

  throw new Error("OpenRouter did not return a JSON object for Mission Spec generation.");
}

async function generateMissionSpecWithOpenRouter(spec, opts) {
  if (!spec.naturalLanguageInput) return spec;

  const config = buildOpenRouterConfig(opts, spec.openrouter || {});
  if (!config.spec.enabled) return spec;

  const naturalLanguageInput = spec.naturalLanguageInput;
  const generated = await callOpenRouterChat(config, {
    model: config.spec.model,
    temperature: config.spec.temperature,
    max_tokens: config.spec.maxTokens,
    messages: [
      {
        role: "system",
        content: config.spec.systemPrompt || [
          "Convert a natural-language software development request into a JSON Mission Spec.",
          "Return only valid JSON. Do not wrap it in markdown.",
          "The JSON must contain version, mission, target, instructions, acceptance, codex, openrouter, and metadata when useful.",
          "The mission.objective field is required.",
          "Use concise requirements, constraints, nonGoals, acceptance criteria, and validation suggestions.",
          "Do not invent repository facts. Put uncertainty into instructions.notes.",
        ].join(" "),
      },
      {
        role: "user",
        content: JSON.stringify({
          naturalLanguageRequest: naturalLanguageInput,
          defaults: {
            version: spec.version,
            target: spec.target,
            codex: spec.codex,
            openrouter: spec.openrouter,
            policy: spec.policy,
            metadata: spec.metadata,
          },
        }, null, 2),
      },
    ],
  });

  let parsed;
  try {
    parsed = JSON.parse(extractJsonObject(generated));
  } catch (error) {
    throw new Error(`OpenRouter returned invalid Mission Spec JSON: ${error.message}`);
  }

  const normalized = normalizeMissionSpec(parsed);
  const merged = applyMissionOverrides(opts, normalized);
  merged.metadata = {
    ...merged.metadata,
    generatedFrom: "openrouter-natural-language",
  };
  return merged;
}

async function compileMissionWithOpenRouter(spec, runtime) {
  const config = runtime.openrouter;
  if (!config || !config.enabled) return spec;
  if (runtime.dryRun) {
    return {
      ...spec,
      openrouterGuidance: "OpenRouter guidance is enabled but was not requested during dry-run.",
    };
  }

  const content = await callOpenRouterChat(config, {
    model: config.model,
    temperature: config.temperature,
    max_tokens: config.maxTokens,
    messages: [
      {
        role: "system",
        content: config.systemPrompt || [
          "You compile coding Mission Specs into concise implementation guidance for Codex CLI.",
          "Do not write full files. Do not invent repository facts.",
          "Return actionable guidance, risks, likely files, and validation suggestions.",
        ].join(" "),
      },
      {
        role: "user",
        content: JSON.stringify({
          version: spec.version,
          mission: spec.mission,
          target: spec.target,
          instructions: spec.instructions,
          acceptance: spec.acceptance,
          metadata: spec.metadata,
        }, null, 2),
      },
    ],
  });

  return {
    ...spec,
    openrouterGuidance: content,
  };
}

function buildCodexArgs(runtime) {
  const args = [];
  if (runtime.approval) args.push("--ask-for-approval", runtime.approval);
  args.push("exec", "-");

  args.push("--cd", path.resolve(runtime.workdir || DEFAULT_WORKDIR));

  if (runtime.model) args.push("--model", runtime.model);
  if (runtime.profile) args.push("--profile", runtime.profile);
  if (runtime.sandbox) args.push("--sandbox", runtime.sandbox);
  if (runtime.search) args.push("--search");
  if (runtime.jsonEvents) args.push("--json");
  if (runtime.skipGitRepoCheck) args.push("--skip-git-repo-check");
  if (runtime.ephemeral) args.push("--ephemeral");

  for (const dir of runtime.addDirs) args.push("--add-dir", dir);
  for (const image of runtime.images) args.push("--image", image);
  for (const config of runtime.configs) args.push("--config", config);

  return args;
}

function collectMissionSpec(opts) {
  if (opts.missionFile) return readMissionFile(opts.missionFile);

  const parts = [];
  if (opts.positional.length > 0) parts.push(opts.positional.join(" "));
  if (opts.stdin || !process.stdin.isTTY) {
    const stdin = readStdin();
    if (stdin) parts.push(stdin);
  }

  const text = parts.join("\n\n").trim();
  if (!text) {
    throw new Error("No mission provided. Pass --mission <file>, JSON via --stdin, or a request string.");
  }
  return parseMissionInput(text);
}

function writeMissionSpec(opts, spec) {
  const json = `${JSON.stringify(toMissionSpecJson(spec), null, 2)}\n`;

  if (opts.missionOut) {
    const outputPath = path.resolve(opts.missionOut);
    fs.mkdirSync(path.dirname(outputPath), { recursive: true });
    fs.writeFileSync(outputPath, json, "utf8");
  }

  if (opts.specOnly) {
    if (opts.missionOut) {
      console.log(`Mission Spec written to ${path.resolve(opts.missionOut)}`);
    } else {
      process.stdout.write(json);
    }
  }
}

function hasQueueCommand(opts) {
  return Boolean(opts.queueFile && hasQueueAction(opts));
}

function hasQueueAction(opts) {
  return Boolean(
    opts.enqueue
    || opts.queueList
    || opts.queueNext
    || opts.queueRun
  );
}

function createEmptyQueue() {
  const now = new Date().toISOString();
  return {
    version: "1.0",
    createdAt: now,
    updatedAt: now,
    missions: [],
  };
}

function readQueue(filePath) {
  const resolved = path.resolve(filePath);
  if (!fs.existsSync(resolved)) return createEmptyQueue();

  let parsed;
  try {
    parsed = JSON.parse(fs.readFileSync(resolved, "utf8"));
  } catch (error) {
    throw new Error(`Invalid queue JSON in ${resolved}: ${error.message}`);
  }

  if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
    throw new Error("Queued Mission List must be a JSON object.");
  }

  const missions = Array.isArray(parsed.missions) ? parsed.missions : [];
  return {
    version: String(parsed.version || "1.0"),
    createdAt: parsed.createdAt || new Date().toISOString(),
    updatedAt: parsed.updatedAt || new Date().toISOString(),
    missions: missions.map(normalizeQueueItem),
  };
}

function normalizeQueueItem(item, index) {
  if (!item || typeof item !== "object" || Array.isArray(item)) {
    throw new Error(`Queue item at index ${index} must be an object.`);
  }

  const missionSpec = item.spec || item.missionSpec || item.mission;
  if (!missionSpec) {
    throw new Error(`Queue item at index ${index} must include spec, missionSpec, or mission.`);
  }

  const spec = normalizeMissionSpec(missionSpec);
  const missionId = spec.mission.id || createMissionId(spec.mission.objective);
  spec.mission.id = missionId;

  return {
    id: String(item.id || missionId),
    status: normalizeQueueStatus(item.status || "pending"),
    risk: item.risk || null,
    policyResult: item.policyResult || item.policy_result || null,
    attempts: Number.isInteger(item.attempts) ? item.attempts : 0,
    enqueuedAt: item.enqueuedAt || new Date().toISOString(),
    startedAt: item.startedAt || null,
    completedAt: item.completedAt || null,
    updatedAt: item.updatedAt || item.enqueuedAt || new Date().toISOString(),
    lastExitCode: Number.isInteger(item.lastExitCode) ? item.lastExitCode : null,
    lastError: item.lastError || null,
    spec: toMissionSpecJson(spec),
  };
}

function normalizeQueueStatus(status) {
  const allowed = new Set(["pending", "running", "completed", "failed"]);
  const normalized = String(status).toLowerCase();
  if (!allowed.has(normalized)) {
    throw new Error(`Invalid queue status: ${status}`);
  }
  return normalized;
}

function writeQueue(filePath, queue) {
  const resolved = path.resolve(filePath);
  fs.mkdirSync(path.dirname(resolved), { recursive: true });
  queue.updatedAt = new Date().toISOString();
  fs.writeFileSync(resolved, `${JSON.stringify(queue, null, 2)}\n`, "utf8");
}

async function enqueueMission(opts) {
  const initialSpec = applyMissionOverrides(opts, collectMissionSpec(opts));
  const spec = await generateMissionSpecWithOpenRouter(initialSpec, opts);
  const risk = evaluateMissionPolicy(spec, { stagedExecution: !opts.noStagedExecution });
  if (risk.decision === "block") {
    throw new Error(`Mission blocked by risk policy: ${risk.reasons.join("; ")}`);
  }
  const queue = readQueue(opts.queueFile);
  const missionJson = toMissionSpecJson(spec);
  const itemId = makeUniqueQueueId(queue, spec.mission.id || createMissionId(spec.mission.objective));
  const now = new Date().toISOString();

  queue.missions.push({
    id: itemId,
    status: "pending",
    risk,
    policyResult: null,
    attempts: 0,
    enqueuedAt: now,
    startedAt: null,
    completedAt: null,
    updatedAt: now,
    lastExitCode: null,
    lastError: null,
    spec: missionJson,
  });

  writeQueue(opts.queueFile, queue);
  console.log(`Enqueued mission ${itemId} -> ${path.resolve(opts.queueFile)}`);
  if (opts.missionOut || opts.specOnly) writeMissionSpec(opts, spec);
  return 0;
}

function makeUniqueQueueId(queue, baseId) {
  const base = createMissionId(baseId || "mission");
  const existing = new Set(queue.missions.map((item) => item.id));
  if (!existing.has(base)) return base;

  for (let i = 2; ; i += 1) {
    const candidate = `${base}-${i}`;
    if (!existing.has(candidate)) return candidate;
  }
}

function listQueue(opts) {
  const queue = readQueue(opts.queueFile);
  if (opts.queueJson) {
    console.log(JSON.stringify(queue, null, 2));
    return 0;
  }

  if (queue.missions.length === 0) {
    console.log("Queued Mission List is empty.");
    return 0;
  }

  for (const item of queue.missions) {
    const title = item.spec.mission.title ? ` (${item.spec.mission.title})` : "";
    const risk = item.risk && item.risk.decision ? ` risk=${item.risk.decision}` : "";
    console.log(`${item.status.padEnd(9)} ${item.id}${title}${risk}`);
    console.log(`  objective: ${item.spec.mission.objective}`);
    console.log(`  attempts: ${item.attempts}  updated: ${item.updatedAt}`);
    if (item.lastError) console.log(`  lastError: ${item.lastError}`);
  }
  return 0;
}

async function runQueue(opts) {
  const queue = readQueue(opts.queueFile);
  const pending = queue.missions.filter((item) => item.status === "pending");
  const selected = opts.queueNext ? pending.slice(0, 1) : pending.slice(0, opts.queueLimit || pending.length);

  if (selected.length === 0) {
    console.log("No pending missions in queue.");
    return 0;
  }

  let finalCode = 0;
  for (const item of selected) {
    const code = await runQueueItem(opts, queue, item);
    if (code !== 0) {
      finalCode = code;
      break;
    }
  }

  return finalCode;
}

async function runQueueItem(opts, queue, item) {
  const now = new Date().toISOString();
  const spec = applyMissionOverrides(opts, normalizeMissionSpec(cloneJson(item.spec)));
  const risk = evaluateMissionPolicy(spec, { stagedExecution: !opts.noStagedExecution });

  console.log(`Running queued mission ${item.id}: ${spec.mission.objective}`);

  item.risk = risk;
  item.updatedAt = now;

  if (opts.riskReport) {
    console.log(JSON.stringify(risk, null, 2));
    writeQueue(opts.queueFile, queue);
    return 0;
  }

  if (risk.decision === "block") {
    item.status = "failed";
    item.completedAt = now;
    item.updatedAt = now;
    item.lastExitCode = 1;
    item.lastError = `Mission blocked by risk policy: ${risk.reasons.join("; ")}`;
    item.policyResult = { decision: "block", risk };
    writeQueue(opts.queueFile, queue);
    console.error(item.lastError);
    return 1;
  }

  if (risk.decision === "review" && !opts.riskAllowReview) {
    writeQueue(opts.queueFile, queue);
    console.log(`Skipped queued mission ${item.id}: review required by risk policy.`);
    return 0;
  }

  if (!opts.dryRun) {
    item.status = "running";
    item.startedAt = now;
    item.completedAt = null;
    item.updatedAt = now;
    item.attempts += 1;
    item.lastExitCode = null;
    item.lastError = null;
    writeQueue(opts.queueFile, queue);
  }

  try {
    const result = await executeMission(opts, spec, { precomputedRisk: risk, printRiskReport: false });

    if (!opts.dryRun) {
      const done = new Date().toISOString();
      item.status = result.code === 0 ? "completed" : "failed";
      item.completedAt = done;
      item.updatedAt = done;
      item.lastExitCode = result.code;
      item.lastError = result.code === 0 ? null : (result.error || `Codex exited with code ${result.code}`);
      item.policyResult = result.policyResult || null;
      writeQueue(opts.queueFile, queue);
    }

    return result.code;
  } catch (error) {
    if (!opts.dryRun) {
      const failed = new Date().toISOString();
      item.status = "failed";
      item.completedAt = failed;
      item.updatedAt = failed;
      item.lastExitCode = 1;
      item.lastError = error.message;
      item.policyResult = item.policyResult || { decision: "block", error: error.message };
      writeQueue(opts.queueFile, queue);
    }
    throw error;
  }
}

async function handleQueueCommand(opts) {
  if (!opts.queueFile) throw new Error("Queue commands require --queue <file>.");
  const actions = [opts.enqueue, opts.queueList, opts.queueNext, opts.queueRun].filter(Boolean);
  if (actions.length !== 1) {
    throw new Error("Use exactly one queue action: --enqueue, --queue-list, --queue-next, or --queue-run.");
  }

  if (opts.enqueue) return enqueueMission(opts);
  if (opts.queueList) return listQueue(opts);
  return runQueue(opts);
}

async function executeMission(opts, spec, options = {}) {
  const risk = options.precomputedRisk || evaluateMissionPolicy(spec, { stagedExecution: !opts.noStagedExecution });

  if (opts.riskReport && options.printRiskReport !== false) {
    console.log(JSON.stringify(risk, null, 2));
    return { code: 0, risk, policyResult: null };
  }

  if (risk.decision === "block") {
    throw new Error(`Mission blocked by risk policy: ${risk.reasons.join("; ")}`);
  }

  if (risk.decision === "review" && !opts.riskAllowReview) {
    throw new Error(`Mission requires review: ${risk.reasons.join("; ")}`);
  }

  const runtime = mergeRuntimeOptions(opts, spec);
  runtime.sandbox = risk.controls && risk.controls.sandbox ? risk.controls.sandbox : runtime.sandbox;
  runtime.approval = risk.controls && risk.controls.approval ? risk.controls.approval : runtime.approval;

  const compiledSpec = await compileMissionWithOpenRouter(spec, runtime);
  const prompt = buildPrompt(compiledSpec);

  if (runtime.dryRun) {
    const code = await runCodex(runtime, prompt);
    return { code, risk, policyResult: null };
  }

  if (opts.noStagedExecution) {
    return executeMissionDirect(runtime, prompt, risk);
  }

  return executeMissionStaged(runtime, prompt, risk);
}

async function executeMissionStaged(runtime, prompt, risk) {
  const originalRoot = path.resolve(runtime.workdir || DEFAULT_WORKDIR);
  const stagingRoot = fs.mkdtempSync(path.join(os.tmpdir(), "codex-mission-"));

  try {
    copyWorkspaceToStaging(originalRoot, stagingRoot, DEFAULT_EXCLUDE_DIRS);
    const stagedRuntime = { ...runtime, workdir: stagingRoot };
    const code = await runCodex(stagedRuntime, prompt);
    if (code !== 0) return { code, risk, policyResult: null };

    const changes = scanWorkspaceDiff(originalRoot, stagingRoot, { excludeDirs: DEFAULT_EXCLUDE_DIRS });
    const policyResult = evaluateWritePolicy(changes, risk.writePolicy);
    if (policyResult.decision !== "allow") {
      printPolicyViolations(policyResult);
      return {
        code: 1,
        risk,
        policyResult,
        error: "Write policy violation",
      };
    }

    applyWorkspaceChanges(originalRoot, stagingRoot, changes);
    return { code: 0, risk, policyResult };
  } finally {
    fs.rmSync(stagingRoot, { recursive: true, force: true });
  }
}

async function executeMissionDirect(runtime, prompt, risk) {
  const originalRoot = path.resolve(runtime.workdir || DEFAULT_WORKDIR);
  const baselineRoot = fs.mkdtempSync(path.join(os.tmpdir(), "codex-baseline-"));

  try {
    copyWorkspaceToStaging(originalRoot, baselineRoot, DEFAULT_EXCLUDE_DIRS);
    const code = await runCodex(runtime, prompt);
    if (code !== 0) return { code, risk, policyResult: null };

    const changes = scanWorkspaceDiff(baselineRoot, originalRoot, { excludeDirs: DEFAULT_EXCLUDE_DIRS });
    const policyResult = evaluateWritePolicy(changes, risk.writePolicy);
    if (policyResult.decision !== "allow") {
      const revertChanges = scanWorkspaceDiff(originalRoot, baselineRoot, { excludeDirs: DEFAULT_EXCLUDE_DIRS });
      applyWorkspaceChanges(originalRoot, baselineRoot, revertChanges);
      printPolicyViolations(policyResult);
      return {
        code: 1,
        risk,
        policyResult,
        error: "Write policy violation",
      };
    }

    return { code: 0, risk, policyResult };
  } finally {
    fs.rmSync(baselineRoot, { recursive: true, force: true });
  }
}

function printPolicyViolations(policyResult) {
  console.error("Write policy violation:");
  for (const violation of policyResult.violations) {
    const pathPart = violation.path ? ` ${violation.path}` : "";
    console.error(`- ${violation.type}${pathPart}: ${violation.message}`);
  }
}

function runCodex(runtime, prompt) {
  const args = buildCodexArgs(runtime);

  if (runtime.dryRun) {
    console.log("$", [runtime.codexBin, ...args].join(" "));
    console.log("\n--- mission prompt ---\n");
    console.log(prompt);
    return Promise.resolve(0);
  }

  return new Promise((resolve, reject) => {
    const child = spawn(runtime.codexBin, args, {
      cwd: path.resolve(runtime.workdir || DEFAULT_WORKDIR),
      stdio: ["pipe", "inherit", "inherit"],
      shell: process.platform === "win32",
    });

    child.on("error", (error) => {
      reject(new Error(`Failed to start ${runtime.codexBin}: ${error.message}`));
    });

    child.on("close", (code) => resolve(code || 0));
    child.stdin.end(prompt);
  });
}

async function main() {
  const opts = parseArgs(process.argv.slice(2));
  if (opts.help) {
    printHelp();
    return 0;
  }

  if (hasQueueAction(opts) || opts.queueFile) {
    return handleQueueCommand(opts);
  }

  const initialSpec = applyMissionOverrides(opts, collectMissionSpec(opts));
  const spec = await generateMissionSpecWithOpenRouter(initialSpec, opts);
  writeMissionSpec(opts, spec);
  if (opts.specOnly) return 0;

  const result = await executeMission(opts, spec);
  return result.code;
}

main()
  .then((code) => {
    process.exitCode = code;
  })
  .catch((error) => {
    console.error(`codex-code: ${error.message}`);
    process.exitCode = 1;
  });
