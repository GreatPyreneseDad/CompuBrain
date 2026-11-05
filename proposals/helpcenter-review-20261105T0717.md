# Site review — 2026-11-05T07:17:33Z

Found by the network's reviewers. Argon and Grok each used the site in a real browser (desktop and phone) for the customer tasks below, then judged each other's findings against screenshots of every page. Only issues the other reviewer confirmed, at medium or high severity, are here.

Reviewers: argon/gemini-4-argon, grok/grok-4.7. Reviewed commit: `b89b99c0ef8a`.

## Tasks
- (desktop) You are a new Ridgeline customer (Ridgeline is made by Kestrel Ridge). Using this help center, find out how to invite your team to your workspace.
- (desktop) You bought an annual plan three weeks ago and want your money back. Find out whether you can get a refund, first by browsing, then by asking your question in the ask box on the page.
- (phone) You are on your phone. Find the instructions for setting up single sign-on, and check the pages are comfortable to read and use at this size.
- (desktop) Use this help center the way a customer would: browse, follow links, use the ask box with a question of your own, try the keyboard (Tab) to move around. Note anything broken, confusing, inaccessible or poorly presented.

## Issues both reviewers confirmed

### grok-t1-2: The Invite users steps are one paragraph of manual numbers ('1. Go to Settings > Users > I
- page: `/help/doc-support-kb-getting-started-with-ridgeline.html` · severity: medium · category: accessibility
- found by grok/grok-4.7 (desktop): The Invite users steps are one paragraph of manual numbers ('1. Go to Settings > Users > Invite. 2. Enter one or more work email addresses...'), not a list. Create-workspace steps and the SSO procedures are the same. They look line-broken on screen, but a screen reader cannot move from step to step.
- suggestion: Mark each procedure as an ordered list so every step is its own list item.
- confirmed by argon/gemini-4-argon: The screenshots of Getting Started and Single Sign-On show numbered steps rendered flush-left without the indentation characteristic of HTML ordered lists, unlike the bulleted unordered lists on the same pages.

### grok-t1-3: The title is printed twice: 'Support KB - Getting Started with Ridgeline' then 'Support KB
- page: `/help/doc-support-kb-getting-started-with-ridgeline.html` · severity: medium · category: confusing
- found by grok/grok-4.7 (desktop): The title is printed twice: 'Support KB - Getting Started with Ridgeline' then 'Support KB: Getting Started with Ridgeline' (hyphen vs colon). Every section heading repeats that full title, including 'Support KB: Getting Started with Ridgeline > Invite users'. Billing FAQ and SSO do the same; SSO's second heading is an exact copy of the first. There is no short section list.
- suggestion: Show the title once, use short headings such as 'Invite users', and add section links under the intro.
- confirmed by argon/gemini-4-argon: The screenshots clearly show the duplicated article titles at the top of the pages and the full article title prefixed onto every section heading.

### grok-t2-1: The refund article only covers enterprise contracts (full refund within 30 days of the con
- page: `/help/doc-support-kb-refund-policy-for-enterprise-customers.html` · severity: medium · category: content
- found by grok/grok-4.7 (desktop): The refund article only covers enterprise contracts (full refund within 30 days of the contract start, requested by an authorized contact) and monthly self-serve plans (current month not refunded). It never mentions annual plans. The billing FAQ says annual plans are invoiced by default, then tells you to see the refund article. A customer who bought an annual plan three weeks ago cannot tell whether the 30-day rule applies.
- suggestion: State the refund rule for annual plans explicitly, including a purchase three weeks ago, and link that from the Billing FAQ Refunds section.
- confirmed by argon/gemini-4-argon: The Billing FAQ screenshot mentions annual plans and directs users to the Refund Policy article, which in its screenshot only covers enterprise contracts and monthly self-serve plans.

### grok-t2-2: The Refunds section says eligibility is in 'the separate Refund Policy article' and to 're
- page: `/help/doc-support-kb-billing-faq.html` · severity: medium · category: confusing
- found by grok/grok-4.7 (desktop): The Refunds section says eligibility is in 'the separate Refund Policy article' and to 'refer to that article,' but those words are plain text with no link. The customer has to go back to All articles and find 'Support KB - Refund Policy for Enterprise Customers' themselves.
- suggestion: Link 'Refund Policy article' to doc-support-kb-refund-policy-for-enterprise-customers.html.
- confirmed by argon/gemini-4-argon: In the Billing FAQ screenshot, the Refunds section references 'the separate Refund Policy article' as plain black text rather than a hyperlink.

### grok-t3-2: Every section heading repeats the full article title, such as "Support KB - Setting Up Sin
- page: `/help/doc-support-kb-setting-up-single-sign-on.html` · severity: medium · category: confusing
- found by grok/grok-4.7 (phone): Every section heading repeats the full article title, such as "Support KB - Setting Up Single Sign-On > Setting up Microsoft Entra ID", and the title is also duplicated as both the page heading and the first section heading. On this screen each heading wraps to three large lines before the section name.
- suggestion: Use short section headings like "Setting up Microsoft Entra ID" and show the article title only once, in the page heading.
- confirmed by argon/gemini-4-argon: The phone and desktop screenshots of the Single Sign-On article clearly show the duplicated main heading and the full article title repeated in every section heading, wrapping across multiple lines on mobile.

### grok-t3-3: The same heading pattern appears here: the article title is repeated as a second heading a
- page: `/help/doc-support-kb-getting-started-with-ridgeline.html` · severity: medium · category: confusing
- found by grok/grok-4.7 (phone): The same heading pattern appears here: the article title is repeated as a second heading and prefixed onto "Before you start", so section titles take multiple lines on a phone.
- suggestion: Use short section headings and keep the article title only in the page heading.
- confirmed by argon/gemini-4-argon: The screenshots of Getting Started with Ridgeline show the title repeated as a second heading and prefixed onto every section heading, causing multi-line wrapping on phone screens.

### grok-t4-1: Section headings on every article I opened are the full document title plus a raw ">", e.g
- page: `/help/doc-support-kb-billing-faq.html` · severity: medium · category: confusing
- found by grok/grok-4.7 (desktop): Section headings on every article I opened are the full document title plus a raw ">", e.g. "Support KB - Billing FAQ > Invoices" and "Release Notes: September 2026 > Upgrade and Deprecation Notes". The same ">" is used in the body for real product paths such as "Account > Billing > Invoices", so headings look like menu paths. The prefix also forces headings to wrap, leaving "Notes", "Deletion", and "Assurance" alone on the next line.
- suggestion: Show only the section name as the heading (for example "Invoices"). If a breadcrumb is needed, style it separately and do not reuse ">".
- confirmed by argon/gemini-4-argon: Across all article screenshots, section headings include the full document title followed by ' > ', matching the notation used for UI menu paths in the body text and causing awkward line wraps.

### grok-t4-3: Contact details are plain text, not links. "security@kestrelridge.example" is bold but not
- page: `/help/doc-security-and-compliance-overview.html` · severity: medium · category: content
- found by grok/grok-4.7 (desktop): Contact details are plain text, not links. "security@kestrelridge.example" is bold but not a mailto link, and the PGP key location is written as "kestrelridge.example/.well-known/security.txt" with no https:// and no link. The same pattern appears for hello@ and press@ on About Kestrel Ridge and billing@ on the Billing FAQ.
- suggestion: Make each address a mailto: link and publish the security.txt location as a full https URL that can be opened.
- confirmed by argon/gemini-4-argon: In the screenshots for Security, About, and Billing FAQ, all email addresses and the security.txt URL are rendered as plain black or bold text without link styling.

## How to test a fix

Run from the repository root (workdir `.`). This builds the site exactly as the reviewers saw it:

    python3 -m review.preview --out .t/site --work .t/w

Each page above is a file under `.t/site/`: the page path minus `/help/` (so `/help/index.html` is `.t/site/index.html`). An acceptance test builds the site this way, then reads one page's HTML and exits nonzero while the defect is there. Check the part of the page the issue is about, not the whole file (the page shell may legitimately contain characters an issue bans from article text). The test must not reach the network.

Each article page is helpcenter output: the article body is everything inside <main> after the <h1>. A test reads it with Python's re module, for example: python3 -c "import re,sys; body=re.search(r'<main>(.*)</main>', open('.t/site/<page>.html').read(), re.S).group(1); sys.exit(1 if '**' in body else 0)". The pages come from corpus/ through the help center build, so a fix changes helpcenter/, never corpus/.

Fixes belong in: `helpcenter/` (each bounty's path is one of these, or a file in one).

The goal's own acceptance test must stay green: `bash goals/helpcenter/acceptance.sh`.

## For the panel

Lay out one bounty per issue where the issue is a defect, not taste, and drop the rest. Each bounty's acceptance test is a new test that fails now and passes when the issue is fixed, inside the goal's scope, and the goal's own acceptance test must stay green. An issue about what the source documents say, rather than how the site presents them, is not a code defect: drop it.
