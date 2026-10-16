"use strict";

const { normalizeWritePolicy } = require("./write-control");

const DECISION_WEIGHT = {
  allow: 1,
  sandbox: 2,
  review: 3,
  block: 4,
};

const RISK_SIGNALS = {
  secrets: ["api key", "secret", "password", ".env", "token", "credential"],
  production: ["production", "prod", "deploy", "release", "terraform", "kubernetes"],
  destructive: ["delete database", "drop table", "remove all", "reset --hard", "wipe", "purge", "rm -rf"],
  broadScope: ["refactor entire", "rewrite whole", "all files", "entire codebase", "everything"],
};

function evaluateMissionPolicy(spec, opts = {}) {
  const text = missionText(spec);
  const policies = [];
  const policy = spec.policy && typeof spec.policy === "object" ? spec.policy : {};
  const codex = spec.codex || {};

  if (codex.sandbox === "danger-full-access") {
    policies.push(policyResult("block-danger-full-access", "block", "danger-full-access is blocked by default"));
  }

  for (const [riskType, terms] of Object.entries(RISK_SIGNALS)) {
    const matched = terms.find((term) => text.includes(term));
    if (matched) {
      policies.push(policyResult(`review-${riskType}`, "review", `Mission matched ${riskType} risk signal: ${matched}`));
    }
  }

  const deniedCommands = normalizeStringList(policy.commands && policy.commands.deny);
  const matchedCommand = deniedCommands.find((command) => text.includes(command.toLowerCase()));
  if (matchedCommand) {
    policies.push(policyResult("review-denied-command", "review", `Mission references denied command: ${matchedCommand}`));
  }

  const explicitDecision = policy.risk && policy.risk.decision;
  if (explicitDecision && explicitDecision !== "auto") {
    policies.push(policyResult("explicit-risk-decision", explicitDecision, `Mission policy requested decision: ${explicitDecision}`));
  }

  if (policies.length === 0) {
    policies.push(policyResult("default-allow", "allow", "Default low-risk mission policy"));
  }

  const reduced = reducePolicies(policies);
  const writePolicy = normalizeWritePolicy(policy.write || {});
  const controls = {
    sandbox: reduced.decision === "sandbox" ? "read-only" : codex.sandbox || "workspace-write",
    approval: codex.approval || "on-request",
    stagedExecution: opts.stagedExecution !== false,
    applyOnSuccessOnly: true,
    ...(reduced.controls || {}),
  };

  return {
    decision: reduced.decision,
    riskLevel: riskLevelForDecision(reduced.decision),
    reasons: reduced.reasons,
    controls,
    writePolicy,
  };
}

function policyResult(id, decision, reason, controls = {}) {
  return { id, decision, reason, controls };
}

function reducePolicies(policies) {
  let decision = "allow";
  const reasons = [];
  const controls = {};

  for (const policy of policies) {
    reasons.push(policy.reason);
    Object.assign(controls, policy.controls || {});
    if (DECISION_WEIGHT[policy.decision] > DECISION_WEIGHT[decision]) {
      decision = policy.decision;
    }
  }

  return { decision, reasons, controls };
}

function riskLevelForDecision(decision) {
  if (decision === "block") return "high";
  if (decision === "review") return "medium";
  if (decision === "sandbox") return "medium";
  return "low";
}

function missionText(spec) {
  return [
    spec.mission && spec.mission.id,
    spec.mission && spec.mission.title,
    spec.mission && spec.mission.objective,
    spec.target && spec.target.context,
    spec.target && spec.target.files,
    spec.instructions && spec.instructions.context,
    spec.instructions && spec.instructions.requirements,
    spec.instructions && spec.instructions.constraints,
    spec.instructions && (spec.instructions.nonGoals || spec.instructions.non_goals),
    spec.instructions && spec.instructions.notes,
    spec.acceptance && spec.acceptance.criteria,
    spec.acceptance && (spec.acceptance.validation || spec.acceptance.tests),
  ]
    .flat(Infinity)
    .filter(Boolean)
    .map((value) => String(value).toLowerCase())
    .join("\n");
}

function normalizeStringList(value) {
  if (Array.isArray(value)) return value.filter(Boolean).map(String);
  if (typeof value === "string" && value.trim()) return [value.trim()];
  return [];
}

module.exports = {
  RISK_SIGNALS,
  evaluateMissionPolicy,
};
