# Demo: four beats, under three minutes

Start: `./run.sh`, open http://localhost:8000. Warm it once before you present: click **Refund policy**.

**Open (15s).** "Every team here built retrieval. We built the asker. Same corpus, same question, three
identities, and the database decides what the model is allowed to read before it reads anything."

**Beats 1 to 3 (90s).** Click **Refund policy**. All three columns fill from one question.
- **Maya, sales, week 2.** Short and plain. The 30-day window, and the approver by name. Three sources.
- **Dana, CFO.** Same policy, plus what Maya cannot see: Legal says the contract template moved to
  45 days, so the playbook is wrong; Finance defers revenue until the window lapses; the board
  minutes name the two exceptions granted last quarter. The amber box is the brain refusing to
  pick a side: sources disagree, both cited.
- **svc-support-bot, an AI agent.** JSON it can relay to a customer. It says exceptions are routed
  internally and stops. The approver's name is not in its scope, so it is not in its answer.
- Point at the struck-through scope chips: that is each asker's gate.

**Beat 4 (30s).** Click **Comp bands**. Refused, for all three, the CFO included.
"The model was never shown the comp document, so there is nothing to talk it into. This is the
answer to 'why not put the role in the system prompt'."

**Ledger (20s).** Scroll down. Every question, the Snowflake role it ran as, the scopes that were
denied, what was cited. "Who asked what, and what did they see" is one table.

**Close (15s).** "On Snowflake the gate is one row access policy. Agents are principals like people.
Scope is data, set once at ingest, not a line in a prompt."

## Beat 5: the brain acts (GitHub)

Open github.com/GreatPyreneseDad/CompuBrain.

1. **Show PR #7.** "This morning the brain could not read a Word file. Someone commented
   `/cerata consume` on an issue. CERATA checked the licence, digested the code, wrote and ran nine
   tests, and opened this pull request. We reviewed it and merged."
2. **Drop a Word contract.** In `inbox/`: Add file → Upload files → drag
   `samples/ridgeback-cold-chain-order-form.docx` → Commit changes.
3. **Actions tab.** "Brain intake" runs for about a minute and a half.
4. **Issues tab.** One issue per team, each written under that team's role:
   - Sales: onboarding tasks with due dates worked out from the contract.
   - Leadership: what sales cannot see. The 22 percent discount is over the limit the regional
     director can approve. The customer was promised 99.99 percent uptime in writing. And the refund
     window on this contract is 45 days, not the playbook's 30.
   - Support: nothing, because that role cannot see this document.
   - A repeat disagreement is added as a comment on the existing "Sources disagree" issue, not reopened.
5. **Ask in place.** On any issue: `/brain ask as:maya What are the comp bands for an L4 engineer?`
   The refusal comes back as a reply.

Say: "It doesn't just answer. New data arrives, and each team gets its work, scoped to what that
team may know. And the people who hit the wall can extend it themselves."

The model words things differently on each run. Do not promise a specific issue list.

## If asked

- **Why not Cortex Search?** A search service runs with its owner's rights and takes its access
  filter from the caller. That puts the gate back in application code. Here the policy is on the
  table, and it binds the owner too.
- **How does a mixed document work?** Scope is per chunk. The handbook is `internal` except its
  compensation section, which is `people`. Maya reads the handbook and not that section.
- **What about untagged documents?** A classifier tags them at ingest and can only tighten. A false
  deny is a shrug; a false allow is the failure.
- **Is the retrieval semantic?** Not yet: this trial account blocks Cortex embeddings, so the vectors
  are lexical with model-side query expansion. One environment variable switches to real ones.

## Wiring a handout corpus (Round 1)

    ./run.sh ingest path/to/their/files --source handout --default-scope internal

Markdown and text files. Anything else needs converting first.
