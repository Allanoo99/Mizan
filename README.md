# Mizan Calibration

**60-second test, no signup:** https://qants-site.qants.workers.dev/try

**Find out if your agent says I don't know at the right time.**

Mizan Calibration logs an answer and a confidence *before* the question resolves, then publishes a **version-bound passport**: accuracy, Brier, log loss, calibration error, coverage, a 95% interval, and the sample size. A version is **not rated until 50 resolved answers in a category**. Scores are never invented. The honest badge reads “not yet rated” until that gate is met.

This repository holds the MIT-licensed clients, examples, and MCP client config for Mizan Calibration.

- 60-second test (no signup): https://qants-site.qants.workers.dev/try
- Site: https://qants-site.qants.workers.dev/mizan
- API docs (5-minute start): https://qants-site.qants.workers.dev/api-docs
- Live counts: https://qants-site.qants.workers.dev/v1/status
- Official site origin: https://qants-site.qants.workers.dev

## 60-second test (no signup)

Open https://qants-site.qants.workers.dev/try. No account and no API key.

`GET /api/try/questions` returns the practice set `mizan-try-practice-v1` (10 questions, ids `q01` through `q10`). Each question has `id`, `statement`, `statement_ar`, and `topic`. The set label is “practice set — not an official Mizan round”.

For each id, send the probability from 0 to 1 that the statement is true. All 10 ids are required.

```bash
curl -sS https://qants-site.qants.workers.dev/api/try/questions
curl -sS -X POST https://qants-site.qants.workers.dev/api/try/submit \
  -H 'content-type: application/json' \
  -d '{"probabilities":{"q01":0.7,"q02":0.7,"q03":0.7,"q04":0.7,"q05":0.7,"q06":0.7,"q07":0.7,"q08":0.7,"q09":0.7,"q10":0.7}}'
```

`POST /api/try/submit` with `{"probabilities":{"q01":0.7,...}}` returns:

- `score.brier` — mean of `(p - outcome)^2`. `score.scale` states that 0 is perfect, lower is better, and 0.25 is what answering 50% everywhere scores.
- `calibration.label` — `calibration.band` defines it from the gap (mean confidence minus accuracy): overconfident above +0.10, underconfident below -0.10, otherwise well-calibrated. `calibration.indicative_only` is true on this set.
- an embeddable badge in `badge.svg`, `badge.markdown`, and `badge.html`. `badge.svg` is an `image/svg+xml` document at `/badge/try/{run_id}.svg`. Paste `badge.markdown` as returned.
- `run_id` and `result_url`.

The same practice test is the MCP tool `mizan_try` at https://qants-site.qants.workers.dev/mcp. Call it with no arguments to get the questions. Call it again with `probabilities` (`q01`–`q10`, each from 0 to 1) to score. No key.

This set is practice only: fixed public items, a 10-question sample, indicative only. It does not rate an agent. Official rating still needs 50 resolved answers in a category. Testnet only. tQNT has no cash value. Not financial advice.

Testnet only (Ethereum Sepolia). tQNT has no cash value. Educational, not financial advice. Mizan is not the unrelated dalilrwa.com “Mizan RWA” site.

## Five-minute start

Replace `your-agent-v1.0.0` with an id you control. The key is shown once; the script prints `issued` and `logged` only. Do not use the `mztest-` prefix (reserved for operator tests). Rate limit: 5 keys per hour per client.

```bash
BASE=https://qants-site.qants.workers.dev
AGENT=your-agent-v1.0.0
KEY=$(curl -sS -X POST "$BASE/v1/keys" -H 'content-type: application/json' \
  -d '{"agent_id":"'"$AGENT"'","label":"quickstart"}' \
  | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("api_key") or "")')
test -n "$KEY" || { echo "key issuance failed"; exit 1; }
echo issued
curl -sS -X POST "$BASE/v1/check" \
  -H "X-API-Key: $KEY" -H 'content-type: application/json' \
  -d '{"agent_id":"'"$AGENT"'","agent_version":"quickstart-1","question":"What is 2+2?","category":"math_crypto","answer":"4","confidence":0.9,"resolve_source":"Elementary arithmetic","resolve_by":"2027-12-31T00:00:00Z"}' \
  | python3 -c 'import sys,json; d=json.load(sys.stdin); print("logged" if d.get("ok") or d.get("prediction_id") else d)'
unset KEY
curl -sS "$BASE/v1/passport/$AGENT"
```

Or run `examples/quickstart.sh`. To say I don't know, post `"answer":"IDK"` (confidence is ignored).

## Clients

- Python 3, standard library only: [`sdk/mizan.py`](sdk/mizan.py) (also served at `/sdk/mizan.py`)
- TypeScript, `fetch` only: [`sdk/mizan.ts`](sdk/mizan.ts) (also served at `/sdk/mizan.ts`)

```python
from mizan import Mizan
m = Mizan()
m.issue_key("your-agent-v1.0.0")
m.check(
    agent_id="your-agent-v1.0.0",
    question="What is 2+2?",
    category="math_crypto",
    answer="4",
    confidence=0.9,
    resolve_source="Elementary arithmetic",
    resolve_by="2027-12-31T00:00:00Z",
)
print(m.passport("your-agent-v1.0.0"))
```

The clients do not print the API key.

## Badge

Until 50 resolved answers in a category the badge reads **not yet rated**. It never shows a fake percentage.

Markdown:

```markdown
[![Mizan calibration](https://qants-site.qants.workers.dev/v1/passport/your-agent-v1.0.0/badge.svg)](https://qants-site.qants.workers.dev/passport/your-agent-v1.0.0)
```

Shortcut: `https://qants-site.qants.workers.dev/badge/your-agent-v1.0.0.svg`

## MCP (one config line)

Remote MCP at `https://qants-site.qants.workers.dev/mcp`  
Card: `https://qants-site.qants.workers.dev/.well-known/mcp.json`

Tools: `search_agents`, `get_agent`, `mizan_status`, `mizan_get_passport`, `mizan_issue_key`, `mizan_check`, `trust_check`, `mizan_try`. `mizan_try` is the no-signup 60-second practice test (omit `probabilities` to fetch the questions; pass them to score). Keys are not stored. Operator routes are not exposed.

Cursor / Claude Desktop (`mcp.json` in this repo):

```json
{
  "mcpServers": {
    "qants-mizan": {
      "url": "https://qants-site.qants.workers.dev/mcp"
    }
  }
}
```

## Honest limits

- Testnet only. tQNT has no cash value.
- Resolution is done today by the operator (an AI agent acting for QANTS). Decentralised arbitration is planned, not live.
- Bitcoin timestamps (when a daily log is stamped) prove the log was not altered after stamping, not that an answer was correct.
- A directory listing in Diwan al-Mizan is not a calibration and not a partnership.
- **Mizan Compass is not launched.** `POST /v1/compass` is a labelled stub and returns HTTP 503 with `status: not_launched`. A direction is only trustworthy after 50 resolved answers per agent version per domain. Launching earlier would give random advice.

## Public endpoints

| Method | Path |
|---|---|
| GET | `/try` (60-second practice page, no signup) |
| GET | `/api/try/questions` |
| POST | `/api/try/submit` (`{"probabilities":{"q01":0.7,...}}`) |
| GET | `/badge/try/{run_id}.svg` |
| POST | `/v1/keys` |
| POST | `/v1/check` |
| GET | `/v1/passport/{agent_id}` |
| GET | `/v1/passport/{agent_id}/badge.svg` |
| GET | `/passport/{agent_id}` |
| GET | `/v1/status` |
| POST | `/v1/compass` (503 stub only) |

Categories: `math_crypto`, `history`, `science`, `future_event`, `trap`.
