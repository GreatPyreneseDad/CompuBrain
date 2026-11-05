# Site review — 2026-11-05T19:57:12Z

Found by the network's reviewers. Argon and Grok each used the site in a real browser (desktop and phone) for the customer tasks below, then judged each other's findings against screenshots of every page. Only issues the other reviewer confirmed, at medium or high severity, are here.

Reviewers: argon/gemini-4-argon, grok/grok-4.7. Reviewed commit: `5300f0c5166d`.

## Tasks
- (desktop) You are a new Ridgeline customer (Ridgeline is made by Kestrel Ridge). Using this help center, find out how to invite your team to your workspace.
- (desktop) You bought an annual plan three weeks ago and want your money back. Find out whether you can get a refund, first by browsing, then by asking your question in the ask box on the page.
- (phone) You are on your phone. Find the instructions for setting up single sign-on, and check the pages are comfortable to read and use at this size.
- (desktop) Use this help center the way a customer would: browse, follow links, use the ask box with a question of your own, try the keyboard (Tab) to move around. Note anything broken, confusing, inaccessible or poorly presented.

## Issues both reviewers confirmed

### grok-t1-1: Getting Started says to allow pop-ups from app.ridgeline.kestrelridge.com, but Setting Up 
- page: `/help/doc-support-kb-getting-started-with-ridgeline.html` · severity: medium · category: content
- found by grok/grok-4.7 (desktop): Getting Started says to allow pop-ups from app.ridgeline.kestrelridge.com, but Setting Up Single Sign-On lists the app as https://app.kestrelridge.com/saml/acs and https://app.kestrelridge.com/saml/metadata.
- suggestion: Use one canonical app hostname in both articles so popup and SSO instructions match.
- confirmed by argon/gemini-4-argon: The Getting Started article instructs users to allow pop-ups from app.ridgeline.kestrelridge.com, while the Single Sign-On article uses app.kestrelridge.com for its SAML and login URLs.

### grok-t2-1: The article only grants a full refund within 30 days of an enterprise contract start, and 
- page: `/help/doc-support-kb-refund-policy-for-enterprise-customers.html` · severity: medium · category: content
- found by grok/grok-4.7 (desktop): The article only grants a full refund within 30 days of an enterprise contract start, and says self-serve plans are monthly with the current month not refunded. It never says whether an annual plan bought three weeks ago is refundable, and the title 'for Enterprise Customers' makes that easy to miss. It also says to send the request 'to support or to your account manager' with no email, form, or link.
- suggestion: Add an annual-plan section that states the window, whether unused time is prorated, and who qualifies, and put a working support email or refund-request link next to those instructions.
- confirmed by argon/gemini-4-argon: The Refund Policy article only addresses enterprise contracts and monthly self-serve plans without covering non-enterprise annual plans mentioned in the Billing FAQ, and provides no link or email address for support.

### grok-t2-2: The Refunds section says eligibility is 'described in the separate Refund Policy article' 
- page: `/help/doc-support-kb-billing-faq.html` · severity: medium · category: confusing
- found by grok/grok-4.7 (desktop): The Refunds section says eligibility is 'described in the separate Refund Policy article' but that phrase is plain text, not a link, so I had to go back to the article list to open it.
- suggestion: Link 'Refund Policy article' to doc-support-kb-refund-policy-for-enterprise-customers.html.
- confirmed by argon/gemini-4-argon: In the Refunds section of the Billing FAQ, 'the separate Refund Policy article' is rendered as plain text rather than a hyperlink.

### grok-t2-3: The billing contact is billing@kestrelridge.example, used twice as a mailto link. That add
- page: `/help/doc-support-kb-billing-faq.html` · severity: medium · category: broken
- found by grok/grok-4.7 (desktop): The billing contact is billing@kestrelridge.example, used twice as a mailto link. That address is not a deliverable mailbox, so the 'email Billing Support' path on this page does not work.
- suggestion: Replace it with a real billing support address.
- confirmed by argon/gemini-4-argon: The Billing FAQ uses the reserved placeholder domain billing@kestrelridge.example in three mailto links instead of a deliverable domain like the support@kestrelridge.com address used on other pages.

### grok-t4-1: Under “What to do when a sync fails,” the numbered steps restart after the error-code bull
- page: `/help/doc-support-kb-data-connectors-and-sync-schedules.html` · severity: medium · category: content
- found by grok/grok-4.7 (desktop): Under “What to do when a sync fails,” the numbered steps restart after the error-code bullets: Check and Match are 1 and 2, then Retry manually and Open a ticket are numbered 1 and 2 again.
- suggestion: Keep one ordered list so the steps continue as 3 and 4 (Retry manually, then Open a ticket).
- confirmed by argon/gemini-4-argon: Under 'What to do when a sync fails', the ordered list restarts at 1 and 2 for 'Retry manually' and 'Open a ticket' after the bulleted error codes instead of continuing at 3 and 4.

### grok-t4-2: Related articles (“Reauthorizing an integration,” “Reading the integration status page,” “
- page: `/help/doc-support-kb-data-connectors-and-sync-schedules.html` · severity: medium · category: broken
- found by grok/grok-4.7 (desktop): Related articles (“Reauthorizing an integration,” “Reading the integration status page,” “CSV and SFTP import format specifications”) are plain text, not links, and those titles are not in the help index.
- suggestion: Link each title to a real article, or remove titles that do not exist.
- confirmed by argon/gemini-4-argon: The three items under 'Related articles' on the Data Connectors page are plain text bullets rather than links, and none of those articles exist on the Help Center index page.

## How to test a fix

Run from the repository root (workdir `.`). This builds the site exactly as the reviewers saw it:

    python3 -m review.preview --out .t/site --work .t/w

Each page above is a file under `.t/site/`: the page path minus `/help/` (so `/help/index.html` is `.t/site/index.html`). An acceptance test builds the site this way, then reads one page's HTML and exits nonzero while the defect is there. Check the part of the page the issue is about, not the whole file (the page shell may legitimately contain characters an issue bans from article text). The test must not reach the network.

Each article page is helpcenter output: the article body is everything inside <main> after the <h1>. A test reads it with Python's re module, for example: python3 -c "import re,sys; body=re.search(r'<main>(.*)</main>', open('.t/site/<page>.html').read(), re.S).group(1); sys.exit(1 if '**' in body else 0)". The pages come from corpus/ through the help center build, so a fix changes helpcenter/, never corpus/.

Fixes belong in: `helpcenter/` (each bounty's path is one of these, or a file in one).

The goal's own acceptance test must stay green: `bash goals/helpcenter/acceptance.sh`.

## For the panel

Lay out one bounty per issue where the issue is a defect, not taste, and drop the rest. Each bounty's acceptance test is a new test that fails now and passes when the issue is fixed, inside the goal's scope, and the goal's own acceptance test must stay green. An issue about what the source documents say, rather than how the site presents them, is not a code defect: drop it.
