"use strict";

const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");

const DEFAULT_DENY = [
  ".env",
  ".env.*",
  ".git/**",
  "node_modules/**",
  "secrets/**",
  "dist/**",
  "build/**",
];

const DEFAULT_ALLOW = ["**"];
const DEFAULT_EXCLUDE_DIRS = [".git", "node_modules", "dist", "build"];

function normalizeWritePolicy(policy = {}) {
  const write = policy && typeof policy === "object" ? policy : {};
  return {
    mode: write.mode || "permissive",
    allow: normalizeStringList(write.allow, DEFAULT_ALLOW),
    deny: normalizeStringList(write.deny, DEFAULT_DENY),
    maxFilesChanged: positiveInteger(write.maxFilesChanged || write.max_files_changed, 50),
    maxBytesChanged: positiveInteger(write.maxBytesChanged || write.max_bytes_changed, 1000000),
    allowDelete: Boolean(write.allowDelete || write.allow_delete),
    allowRename: Boolean(write.allowRename || write.allow_rename),
  };
}

function normalizeStringList(value, fallback = []) {
  if (Array.isArray(value)) return value.filter(Boolean).map(String);
  if (typeof value === "string" && value.trim()) return [value.trim()];
  return [...fallback];
}

function positiveInteger(value, fallback) {
  const parsed = Number.parseInt(value, 10);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : fallback;
}

function toPosixPath(filePath) {
  return filePath.split(path.sep).join("/").replace(/^\/+/, "");
}

function hasExcludedSegment(relativePath, excludeDirs = DEFAULT_EXCLUDE_DIRS) {
  const parts = toPosixPath(relativePath).split("/");
  return parts.some((part) => excludeDirs.includes(part));
}

function copyWorkspaceToStaging(sourceRoot, stagingRoot, excludeDirs = DEFAULT_EXCLUDE_DIRS) {
  fs.cpSync(sourceRoot, stagingRoot, {
    recursive: true,
    filter: (source) => {
      const relative = path.relative(sourceRoot, source);
      if (!relative) return true;
      return !hasExcludedSegment(relative, excludeDirs);
    },
  });
}

function scanWorkspaceDiff(originalRoot, stagingRoot, options = {}) {
  const excludeDirs = options.excludeDirs || DEFAULT_EXCLUDE_DIRS;
  const originalFiles = listFiles(originalRoot, originalRoot, excludeDirs);
  const stagingFiles = listFiles(stagingRoot, stagingRoot, excludeDirs);
  const paths = new Set([...originalFiles.keys(), ...stagingFiles.keys()]);
  const changes = [];

  for (const relativePath of [...paths].sort()) {
    const original = originalFiles.get(relativePath);
    const staged = stagingFiles.get(relativePath);

    if (!original && staged) {
      changes.push({
        path: relativePath,
        type: "add",
        bytesChanged: staged.size,
      });
    } else if (original && !staged) {
      changes.push({
        path: relativePath,
        type: "delete",
        bytesChanged: original.size,
      });
    } else if (original && staged && original.hash !== staged.hash) {
      changes.push({
        path: relativePath,
        type: "modify",
        bytesChanged: staged.size,
      });
    }
  }

  return changes;
}

function listFiles(root, current, excludeDirs) {
  const result = new Map();
  if (!fs.existsSync(current)) return result;

  for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
    const fullPath = path.join(current, entry.name);
    const relativePath = path.relative(root, fullPath);
    if (hasExcludedSegment(relativePath, excludeDirs)) continue;

    if (entry.isDirectory()) {
      for (const [key, value] of listFiles(root, fullPath, excludeDirs)) {
        result.set(key, value);
      }
    } else if (entry.isFile()) {
      const buffer = fs.readFileSync(fullPath);
      result.set(toPosixPath(relativePath), {
        size: buffer.length,
        hash: crypto.createHash("sha256").update(buffer).digest("hex"),
      });
    }
  }

  return result;
}

function evaluateWritePolicy(changes, policyInput = {}) {
  const policy = normalizeWritePolicy(policyInput);
  const violations = [];
  const totalBytesChanged = changes.reduce((sum, change) => sum + (change.bytesChanged || 0), 0);

  if (changes.length > policy.maxFilesChanged) {
    violations.push({
      type: "max-files-changed",
      path: null,
      message: `Changed ${changes.length} files, limit is ${policy.maxFilesChanged}`,
    });
  }

  if (totalBytesChanged > policy.maxBytesChanged) {
    violations.push({
      type: "max-bytes-changed",
      path: null,
      message: `Changed ${totalBytesChanged} bytes, limit is ${policy.maxBytesChanged}`,
    });
  }

  for (const change of changes) {
    const deniedBy = policy.deny.find((pattern) => matchesGlob(change.path, pattern));
    if (deniedBy) {
      violations.push({
        type: "denied-write",
        path: change.path,
        pattern: deniedBy,
        message: `Changed denied path: ${change.path}`,
      });
      continue;
    }

    if (policy.mode === "strict" && !policy.allow.some((pattern) => matchesGlob(change.path, pattern))) {
      violations.push({
        type: "outside-allow-list",
        path: change.path,
        message: `Changed path outside allow list: ${change.path}`,
      });
    }

    if (change.type === "delete" && !policy.allowDelete) {
      violations.push({
        type: "delete-not-allowed",
        path: change.path,
        message: `Deleted file but allowDelete is false: ${change.path}`,
      });
    }
  }

  return {
    decision: violations.length > 0 ? "block" : "allow",
    changes,
    violations,
    writePolicy: policy,
    stats: {
      filesChanged: changes.length,
      bytesChanged: totalBytesChanged,
    },
  };
}

function matchesGlob(relativePath, pattern) {
  const filePath = toPosixPath(relativePath);
  const normalizedPattern = toPosixPath(String(pattern || ""));
  if (!normalizedPattern) return false;
  if (normalizedPattern === "**" || normalizedPattern === "**/*") return true;
  if (normalizedPattern.endsWith("/**")) {
    const prefix = normalizedPattern.slice(0, -3);
    return filePath === prefix || filePath.startsWith(`${prefix}/`);
  }
  return globToRegExp(normalizedPattern).test(filePath);
}

function globToRegExp(pattern) {
  let source = "^";
  for (let i = 0; i < pattern.length; i += 1) {
    const char = pattern[i];
    const next = pattern[i + 1];
    if (char === "*" && next === "*") {
      source += ".*";
      i += 1;
    } else if (char === "*") {
      source += "[^/]*";
    } else if (char === "?") {
      source += "[^/]";
    } else {
      source += escapeRegExp(char);
    }
  }
  source += "$";
  return new RegExp(source);
}

function escapeRegExp(char) {
  return char.replace(/[|\\{}()[\]^$+*?.]/g, "\\$&");
}

function applyWorkspaceChanges(originalRoot, stagingRoot, changes) {
  for (const change of changes) {
    const targetPath = resolveInside(originalRoot, change.path);
    const stagedPath = resolveInside(stagingRoot, change.path);

    if (change.type === "delete") {
      if (fs.existsSync(targetPath)) fs.unlinkSync(targetPath);
      continue;
    }

    fs.mkdirSync(path.dirname(targetPath), { recursive: true });
    fs.copyFileSync(stagedPath, targetPath);
  }
}

function resolveInside(root, relativePath) {
  const resolvedRoot = path.resolve(root);
  const resolved = path.resolve(resolvedRoot, relativePath);
  if (resolved !== resolvedRoot && !resolved.startsWith(`${resolvedRoot}${path.sep}`)) {
    throw new Error(`Path escapes workspace: ${relativePath}`);
  }
  return resolved;
}

module.exports = {
  DEFAULT_DENY,
  DEFAULT_ALLOW,
  DEFAULT_EXCLUDE_DIRS,
  normalizeWritePolicy,
  copyWorkspaceToStaging,
  scanWorkspaceDiff,
  evaluateWritePolicy,
  applyWorkspaceChanges,
  matchesGlob,
};
