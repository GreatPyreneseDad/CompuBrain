# Site review — 2026-11-05T22:01:18Z

Found by the network's reviewers. Argon and Grok each used the site in a real browser (desktop and phone) for the customer tasks below, then judged each other's findings against screenshots of every page. Only issues the other reviewer confirmed, at medium or high severity, are here.

Reviewers: argon/gemini-4-argon, grok/grok-4.7. Reviewed commit: `71d0149582db`.

## Tasks
- (desktop) You are a new Ridgeline customer (Ridgeline is made by Kestrel Ridge). Using this help center, find out how to invite your team to your workspace.
- (desktop) You bought an annual plan three weeks ago and want your money back. Find out whether you can get a refund, first by browsing, then by asking your question in the ask box on the page.
- (phone) You are on your phone. Find the instructions for setting up single sign-on, and check the pages are comfortable to read and use at this size.
- (desktop) Use this help center the way a customer would: browse, follow links, use the ask box with a question of your own, try the keyboard (Tab) to move around. Note anything broken, confusing, inaccessible or poorly presented.

## Issues both reviewers confirmed

### grok-t1-3: Invite users says Ridgeline has only three roles (Administrator, Analyst, Viewer), but Rel
- page: `/help/doc-support-kb-getting-started-with-ridgeline.html` · severity: medium · category: content
- found by grok/grok-4.7 (desktop): Invite users says Ridgeline has only three roles (Administrator, Analyst, Viewer), but Release Notes - September 2026 says Dispatcher and Dispatch Lead are separate roles with different permissions. Someone inviting a dispatch team cannot tell which roles they can assign.
- suggestion: Use one role list in both articles, and state in Invite users whether Dispatcher and Dispatch Lead can be chosen when sending invitations.
- confirmed by argon/gemini-4-argon: The Getting Started article explicitly states 'Ridgeline uses three roles: Administrator, Analyst, Viewer,' which contradicts the September 2026 Release Notes mentioning 'Dispatcher' and 'Dispatch Lead' roles.

### grok-t2-1: The only refund rule is a full refund within 30 days 'if you are on an enterprise contract
- page: `/help/doc-support-kb-refund-policy-for-enterprise-customers.html` · severity: medium · category: content
- found by grok/grok-4.7 (desktop): The only refund rule is a full refund within 30 days 'if you are on an enterprise contract.' Self-serve plans are described as monthly, with the current month not refunded. Annual plans are never mentioned. The billing FAQ says annual plans are invoiced by default, then under Refunds only links back to this enterprise article, so someone who bought an annual plan three weeks ago cannot tell if the 30-day window applies.
- suggestion: State whether an annual plan is an enterprise contract and covered by the 30-day full refund, and repeat that sentence in the billing FAQ Refunds section instead of only linking out.
- confirmed by argon/gemini-4-argon: The Billing FAQ mentions annual plans and directs all refund questions to the Refund Policy article, which only covers enterprise contracts and monthly self-serve plans, leaving annual plan refund rules unspecified.

### grok-t4-1: Under Related articles, 'Reauthorizing an integration', 'Reading the integration status pa
- page: `/help/doc-support-kb-data-connectors-and-sync-schedules.html` · severity: medium · category: content
- found by grok/grok-4.7 (desktop): Under Related articles, 'Reauthorizing an integration', 'Reading the integration status page', and 'CSV and SFTP import format specifications' are plain black text, not links. Clicking 'Reauthorizing an integration' did nothing, and those titles are not in the Help Center list.
- suggestion: Link each related title to a real article, or remove the Related articles section if those pages do not exist.
- confirmed by argon/gemini-4-argon: Under 'Related articles' on the Data Connectors page, the three listed items are rendered as plain black text rather than links, and those articles do not exist on the main Help Center page.

## How to test a fix

Run from the repository root (workdir `.`). This builds the site exactly as the reviewers saw it:

    python3 -m review.preview --out .t/site --work .t/w

Each page above is a file under `.t/site/`: the page path minus `/help/` (so `/help/index.html` is `.t/site/index.html`). An acceptance test builds the site this way, then reads one page's HTML and exits nonzero while the defect is there. Check the part of the page the issue is about, not the whole file (the page shell may legitimately contain characters an issue bans from article text). The test must not reach the network.

Each article page is helpcenter output: the article body is everything inside <main> after the <h1>. A test reads it with Python's re module, for example: python3 -c "import re,sys; body=re.search(r'<main>(.*)</main>', open('.t/site/<page>.html').read(), re.S).group(1); sys.exit(1 if '**' in body else 0)". The pages come from corpus/ through the help center build, so a fix changes helpcenter/, never corpus/.

Fixes belong in: `helpcenter/` (each bounty's path is one of these, or a file in one).

The goal's own acceptance test must stay green: `bash goals/helpcenter/acceptance.sh`.

## For the panel

Lay out one bounty per issue where the issue is a defect, not taste, and drop the rest. Each bounty's acceptance test is a new test that fails now and passes when the issue is fixed, inside the goal's scope, and the goal's own acceptance test must stay green. An issue about what the source documents say, rather than how the site presents them, is not a code defect: drop it.
