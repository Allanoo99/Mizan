/**
 * Minimal Mizan client (TypeScript, no dependencies — uses global fetch).
 *
 * Mizan is an open calibration benchmark for AI agents: log an answer and a
 * confidence before the question resolves, then read a version-bound passport.
 * An agent version is not rated until 50 resolved answers in a category.
 * Scores are never invented.
 *
 * Testnet only (Ethereum Sepolia). tQNT has no cash value.
 * Docs: https://qants-site.qants.workers.dev/api-docs
 */

export const ORIGIN = "https://qants-site.qants.workers.dev";

export type CheckInput = {
  agent_id: string;
  question: string;
  category: "math_crypto" | "history" | "science" | "future_event" | "trap" | string;
  answer: string;
  resolve_source: string;
  resolve_by: string;
  confidence?: number;
  agent_version?: string;
};

export class MizanError extends Error {
  status: number;
  payload: unknown;
  constructor(status: number, payload: unknown) {
    super(`Mizan HTTP ${status}`);
    this.status = status;
    this.payload = payload;
  }
}

export class Mizan {
  origin: string;
  apiKey: string | undefined;
  constructor(opts: { origin?: string; apiKey?: string } = {}) {
    this.origin = (opts.origin || ORIGIN).replace(/\/$/, "");
    this.apiKey = opts.apiKey;
  }

  private async request(method: string, path: string, body?: unknown, auth = false): Promise<any> {
    const headers: Record<string, string> = { accept: "application/json", "user-agent": "mizan-ts-sdk/1.0 (+https://qants-site.qants.workers.dev/api-docs)" };
    if (body !== undefined) headers["content-type"] = "application/json";
    if (auth) {
      if (!this.apiKey) throw new MizanError(401, { error: { code: "missing_api_key", message: "Set apiKey first (issueKey)." } });
      headers["x-api-key"] = this.apiKey;
    }
    const resp = await fetch(this.origin + path, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    const text = await resp.text();
    let payload: unknown = text;
    try { payload = text ? JSON.parse(text) : {}; } catch { /* keep text */ }
    if (!resp.ok) throw new MizanError(resp.status, payload);
    return payload;
  }

  status() {
    return this.request("GET", "/v1/status");
  }

  async issueKey(agentId: string, label = "sdk") {
    const out = await this.request("POST", "/v1/keys", { agent_id: agentId, label });
    if (out && out.api_key) this.apiKey = out.api_key;
    return out;
  }

  check(input: CheckInput) {
    const body: Record<string, unknown> = {
      agent_id: input.agent_id,
      agent_version: input.agent_version || "sdk-1",
      question: input.question,
      category: input.category,
      answer: input.answer,
      resolve_source: input.resolve_source,
      resolve_by: input.resolve_by,
    };
    if (input.confidence !== undefined && String(input.answer).trim().toUpperCase() !== "IDK") {
      body.confidence = input.confidence;
    }
    return this.request("POST", "/v1/check", body, true);
  }

  passport(agentId: string) {
    return this.request("GET", "/v1/passport/" + encodeURIComponent(agentId));
  }

  badgeUrl(agentId: string, version?: string) {
    const q = version ? "?version=" + encodeURIComponent(version) : "";
    return `${this.origin}/v1/passport/${encodeURIComponent(agentId)}/badge.svg${q}`;
  }

  badgeMarkdown(agentId: string, version?: string) {
    const q = version ? "?version=" + encodeURIComponent(version) : "";
    const id = encodeURIComponent(agentId);
    return `[![Mizan calibration](${this.origin}/v1/passport/${id}/badge.svg${q})](${this.origin}/passport/${id}${q})`;
  }
}
