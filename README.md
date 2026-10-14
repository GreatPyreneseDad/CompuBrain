# Company Brain

A company knowledge store that knows who is asking. The asker's identity decides what the model may
see **before** it sees anything (the limit is a Snowflake row access policy, not a prompt), then
decides how the answer is rendered. Agents are held to the same gate as people. When documents
disagree, the brain reports the conflict instead of averaging it. Every question, refusal and
action is ledgered with the role that ran it.

Built for the Company Brain Hackathon, 12 October 2026. Scored third of ten finalists on the judges' sheet.

- **Ask.** One question, three askers, three answers cut by scope. A question about pay is refused for
  all of them because the database returns no rows.
- **Act.** A document pushed to `inbox/`, or emailed to the company inbox, becomes one GitHub issue per
  team with work to do, each written under that team's role, plus unblock emails to the departments
  it waits on and a forecast of where work will jam.
- **Grow.** A file the brain cannot read raises a tooling request, and
  [CERATA](https://github.com/GreatPyreneseDad/CERATA-Project) opens a pull request with the reader.
  A person merges it; the brain then processes the file. Issue #19 → PR #20 → issue #22 is one such run.

Stack: Snowflake (row access policy, `VECTOR` columns), Claude Haiku 5.5 (ingest) and Sonnet 5.5
(answers), GitHub Actions, CERATA, AgentMail. The company and its customers are fictional; the
stored data is real. Demo video and screenshots are on the
[DevPost page](https://company-brain-oct-2026.devpost.com/). The walkthrough is in `demo.md`.

## Quick start

Put `brain.env` and `brain_svc_key.p8` in this folder, then `./run.sh` and open http://localhost:8000.
`./run.sh demo` runs the four beats; `./run.sh gate` runs the gate test. The demo script is in `demo.md`.

## Run on Snowflake

Needs Enterprise Edition or higher: row access policies are not on Standard.

1. In Snowsight, as ACCOUNTADMIN, run `sf/00_setup.sql`. It creates the warehouse, the `BRAIN`
   database, five roles, and the key-pair service user `BRAIN_SVC`. Its last statement prints the
   account identifier.
2. Then, from this directory:

       pip install -r requirements.txt
       export SNOWFLAKE_ACCOUNT=<identifier from step 1>
       export SNOWFLAKE_PRIVATE_KEY_FILE=/path/to/brain_svc_key.p8
       export ANTHROPIC_API_KEY=...
       python -m sf.apply sf/01_schema.sql
       python -m ingest.run_sf corpus/
       python -m sf.test_gate

Trial accounts cannot call any Cortex AI function (embeddings or completion), so embeddings are
computed by `ingest/embed.py` and loaded into `VECTOR(FLOAT, 1024)` columns: set `VOYAGE_API_KEY`
or `OPENAI_API_KEY`, or it falls back to dev-only lexical vectors. On a paid account,
`BRAIN_SF_EMBED=cortex` computes them inside Snowflake instead. The last statement of
`01_schema.sql` is a Cortex smoke test and fails on a trial; everything before it applies.
Summaries and answers call the Anthropic API directly.

### How the gate works on Snowflake

One row access policy, `SCOPE_GATE`, is attached to `CHUNK`, `SUMMARY`, `DIGEST` and
`DOCUMENT_SCOPE`. It admits a row when the session's primary role is mapped to the row's scope in
`ROLE_SCOPE`. Per request the API runs `USE ROLE <asker's role>`, `USE SECONDARY ROLES NONE`, and
then plain SQL. A row access policy binds the table owner too, so nothing reads around it.

| Role | Holds |
| --- | --- |
| `BRAIN_SALES`, `BRAIN_EXEC`, `BRAIN_SUPPORT_AGENT` | Read knowledge through the gate; append to the ledger. |
| `BRAIN_ROUTER` | Resolve a token to a role; read scope and vector of every chunk (no content) for refusal routing. |
| `BRAIN_OWNER` | Owns the objects; ingest. Mapped to every scope. |

Cortex Search is deliberately not the retrieval path. A search service runs with its owner's
rights and takes its access filter from the caller, which puts the gate back in application code.
If its ranking is wanted, use it to propose chunk ids and re-select those ids from `CHUNK` under
the asker's role; rows the role may not see drop out.

Known gaps on Snowflake: there are no triggers, so the ledger is append-only by grants (asker roles
have INSERT only) and the owner role can still edit it. One service user holds every asker role;
giving each principal its own Snowflake user is the stricter form.

## Run on Postgres (fallback)

    pip install -r requirements.txt
    cp .env.example .env          # fill in, then: set -a; . ./.env; set +a
    psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/schema.sql
    python -m ingest.run corpus/
    psql "$DATABASE_URL" -f db/check_corpus.sql      # what each demo asker can reach

`db/test_gate.sql` asserts the gate on a scratch database (it expects empty tables and rolls back).

Untagged documents, such as a handout corpus, on either store:

    python -m ingest.run_sf handout/ --source handout --default-scope internal

## Flow: unblock emails and the choke-point forecast

Applied with `python -m sf.apply sf/02_flow.sql`.

- **Tasks.** Every plan the intake agent makes is stored task by task: owning department, due date, and the
  department it is waiting on, if any. `TASK` sits behind the same row access policy as knowledge.
- **Unblock emails.** For each department a plan waits on, the brain writes one email saying what is needed and
  by when, and stores it in `OUTBOX`. An email is written only from material the receiving department may see;
  when the sender drew on scopes the recipient lacks, the email says a briefing is needed and the row records
  which scopes were withheld. This filter runs in application code, not in a database policy, and the request
  line itself is redacted by the model, so it is weaker than the answer gate.
- **Sending.** With `AGENTMAIL_API_KEY` set, emails go from the brain's AgentMail inbox to a department's
  AgentMail inbox. Departments without a real inbox stay `queued`. Nothing is sent to the fictional
  `kestrelridge.example` addresses.
- **Forecast.** `GET /forecast` reads the tasks the asker may see and counts, per department and week, its own
  tasks plus the requests other departments have made of it, each deliverable once per (matter, department,
  due date). It compares that with `DEPARTMENT.capacity_per_week`, which is an illustrative number, and a model
  writes the choke points from the table. It is arithmetic over planned work, not a trained predictor.
- `python -m core.intake --record-only "<document title>"` plans and stores tasks and emails without touching
  any GitHub issue.

## The mail loop and tool requests

- **Mail in.** `.github/workflows/brain-mail.yml` polls the company inbox on AgentMail (every ten minutes, or
  on demand from the Actions tab). Each new email becomes a Markdown document in `inbox/`; attachments are
  saved beside it. The brain then plans the work exactly as for a file pushed by hand. Needs the
  `AGENTMAIL_API_KEY` secret. Email is outside data: the planner is told not to follow instructions in it.
- **A file it cannot read.** `ingest/chunk.py` lists the file types the brain has readers for. Anything else
  makes `core/tooling.py` open a `[tooling]` issue, write the `/cerata consume` command, and start the CERATA
  workflow with it. The candidate library comes from a short fixed list per file type.
- **A person merges.** CERATA opens a pull request following `.cerata/guide.md`. Nothing merges itself.
- **Going back.** A push that changes `ingest/` re-runs intake in catch-up mode: files in `inbox/` that are
  readable now but were never ingested are processed, and the tooling issue is closed.

## How scope is set

Every stored row, at all three grains, carries exactly one scope, and every read policy is the same
clause: `scope = any(scopes of the current principal)`.

1. A document's frontmatter gives the default scope.
2. A section can override it with `<!-- scope: people -->` under its heading.
3. Documents without frontmatter go through the classifier, which can only tighten: it moves a
   passage, or the whole document, into `people`, `finance`, `legal`, or `exec`.

Summaries are built per (document, scope) and digests per (topic, scope), each from that scope's
material only. A digest therefore cannot report a disagreement between documents in different
scopes; that has to be caught at answer time, from the chunks the asker is allowed to retrieve.

## Refusal routing

The router can name the scopes an asker lacks that hold near matches to a question. This fires on
ordinary questions too (a sales asker's refund question has near matches in finance and legal), so
it is a reason to refuse only when the asker's own retrieval comes back empty or weak. Otherwise
answer from what is visible and record the denied scopes in the ledger.

## Planted facts the demo depends on

| Fact | Document | Scope |
| --- | --- | --- |
| 30-day refund window | Employee Handbook, Sales Playbook, Support KB refund article | internal, sales, public |
| Exceptions approved by Priya Raman, VP of Sales Operations | Sales Playbook | sales |
| Window is 45 days on the March 2026 contract template | Legal Memo - Refund Terms | legal |
| Revenue deferred until the window lapses; 2 percent reserve | Finance Wiki - Revenue Recognition | finance |
| Two Q3 exceptions: Meridian Health Logistics, Castellan Freight | Board Minutes - Q3 2026 | exec |
| Salary bands | Compensation Bands 2026; one section of the Employee Handbook | people |
