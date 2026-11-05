# Site review — 2026-11-05T03:47:00Z

Found by the network's reviewers. Argon and Grok each used the site in a real browser (desktop and phone) for the customer tasks below, then judged each other's findings against screenshots of every page. Only issues the other reviewer confirmed, at medium or high severity, are here.

Reviewers: argon/gemini-4-argon, grok/grok-4.7. Reviewed commit: `fffbf2098829`.

## Tasks
- (desktop) You are a new Ridgeline customer (Ridgeline is made by Kestrel Ridge). Using this help center, find out how to invite your team to your workspace.
- (desktop) You bought an annual plan three weeks ago and want your money back. Find out whether you can get a refund, first by browsing, then by asking your question in the ask box on the page.
- (phone) You are on your phone. Find the instructions for setting up single sign-on, and check the pages are comfortable to read and use at this size.
- (desktop) Use this help center the way a customer would: browse, follow links, use the ask box with a question of your own, try the keyboard (Tab) to move around. Note anything broken, confusing, inaccessible or poorly presented.

## Issues both reviewers confirmed

### grok-t1-1: Article bodies are unrendered markup. On Getting Started, section titles show as literal t
- page: `/help/doc-support-kb-getting-started-with-ridgeline.html` · severity: medium · category: broken
- found by grok/grok-4.7 (desktop): Article bodies are unrendered markup. On Getting Started, section titles show as literal text like "[Support KB: Getting Started with Ridgeline > Invite users]", labels keep asterisks ("**Settings > Users > Invite**"), and the role list and steps are dash lines inside one paragraph rather than headings and lists. The same raw markup appears on Billing FAQ, Release Notes, About, and SSO, where the IdP values are a pipe table ("| Setting | Value |" and "|---|---|") instead of a table.
- suggestion: Render article markdown to HTML: real headings, bold, lists, and tables, so steps and the SSO settings can be scanned.
- confirmed by argon/gemini-4-argon: The screenshots clearly show raw, unrendered markdown across the articles, including literal bracketed section paths, double asterisks, dash lists, and pipe tables.

### grok-t1-3: Billing FAQ tells customers to email billing@kestrelridge.example for uncovered billing qu
- page: `/help/doc-support-kb-billing-faq.html` · severity: medium · category: content
- found by grok/grok-4.7 (desktop): Billing FAQ tells customers to email billing@kestrelridge.example for uncovered billing questions and for tax-exemption certificates. That uses the reserved .example domain, so mail cannot be delivered, and the address is plain text, not a link.
- suggestion: Replace it with a real billing address or contact form and make it a mailto link.
- confirmed by argon/gemini-4-argon: The Billing FAQ screenshot shows 'billing@kestrelridge.example' as plain unlinked text using a reserved .example domain.

### grok-t2-1: Article text is unrendered source. Section titles show as bracket labels such as "[Refund 
- page: `/help/doc-support-kb-refund-policy-for-enterprise-customers.html` · severity: medium · category: visual
- found by grok/grok-4.7 (desktop): Article text is unrendered source. Section titles show as bracket labels such as "[Refund Policy for Enterprise Customers > The policy]" instead of headings, and markup is literal (**bold**, "- " lists). The same raw markup appears on Billing FAQ (including a pipe table), Data Connectors, and About Kestrel Ridge.
- suggestion: Render article bodies as HTML: real h2/h3 headings, lists, bold, and tables, so sections can be scanned and skipped to.
- confirmed by argon/gemini-4-argon: The screenshots confirm that Refund Policy and the other mentioned articles render raw markdown syntax and bracketed section labels as plain text.

### grok-t2-2: The policy gives a full refund within 30 days only for "an enterprise contract," and says 
- page: `/help/doc-support-kb-refund-policy-for-enterprise-customers.html` · severity: medium · category: content
- found by grok/grok-4.7 (desktop): The policy gives a full refund within 30 days only for "an enterprise contract," and says self-serve plans are monthly with the current month not refunded. Nothing says whether an annual plan is an enterprise contract or how the 30-day window applies. Billing FAQ only says annual plans are invoiced by default.
- suggestion: State whether an annual plan bought within 30 days is refundable, and link that sentence from the Billing FAQ Refunds section.
- confirmed by argon/gemini-4-argon: Comparing the Refund Policy and Billing FAQ screenshots confirms that annual plans are mentioned in Billing FAQ, while Refund Policy only covers enterprise contracts and monthly self-serve plans.

### grok-t2-3: The Refunds section says to "Refer to that article" for the refund policy, but those words
- page: `/help/doc-support-kb-billing-faq.html` · severity: medium · category: confusing
- found by grok/grok-4.7 (desktop): The Refunds section says to "Refer to that article" for the refund policy, but those words are not a link and no article title or URL is given.
- suggestion: Link "Refund Policy article" to /help/doc-support-kb-refund-policy-for-enterprise-customers.html.
- confirmed by argon/gemini-4-argon: In the Billing FAQ screenshot under Refunds, 'Refer to that article' and 'Refund Policy article' appear as plain text rather than hyperlinks.

### grok-t2-4: The policy says to send a refund request "to support or to your account manager," but this
- page: `/help/doc-support-kb-refund-policy-for-enterprise-customers.html` · severity: medium · category: confusing
- found by grok/grok-4.7 (desktop): The policy says to send a refund request "to support or to your account manager," but this page has no email, contact link, or request form. The only address on the site is billing@kestrelridge.example on the Billing FAQ, which is not a deliverable mailbox.
- suggestion: Add a working support email or a refund-request link on the refund article, and point Billing FAQ at a real mailbox.
- confirmed by argon/gemini-4-argon: The Refund Policy screenshot instructs users to send requests 'to support or to your account manager' without providing any contact link or email address on the page.

### grok-t3-1: The IdP settings are raw markdown, not a table: the screen shows "| Setting | Value |" and
- page: `/help/doc-support-kb-setting-up-single-sign-on.html` · severity: medium · category: broken
- found by grok/grok-4.7 (phone): The IdP settings are raw markdown, not a table: the screen shows "| Setting | Value |" and "|---|---|", and the ACS URL and Entity ID wrap onto their own lines with a trailing pipe. Error titles keep literal asterisks, such as **"Signature validation failed."**, and attribute names keep backticks, such as `email` and `firstName`.
- suggestion: Render the markdown: use a real table, or a stacked label-and-value list on a narrow screen, bold the error titles, and style attribute names as code so the URLs can be scanned and copied.
- confirmed by argon/gemini-4-argon: The SSO article screenshots show the IdP settings rendered as raw pipe-delimited text, along with literal double asterisks and backticks.

### grok-t3-2: Each section opens with a bracketed path that repeats the full article title, for example 
- page: `/help/doc-support-kb-setting-up-single-sign-on.html` · severity: medium · category: confusing
- found by grok/grok-4.7 (phone): Each section opens with a bracketed path that repeats the full article title, for example "[Support KB - Setting Up Single Sign-On > Setting up Okta]". On this screen those labels wrap to two lines and look like body text. The page has only the one title heading.
- suggestion: Replace the path strings with short headings such as Before you start, Values to give your IdP, and Setting up Okta so sections are easy to scan.
- confirmed by argon/gemini-4-argon: The SSO screenshots show every section starting with a bracketed path string styled identically to body text, wrapping onto two lines on phone width.

### grok-t4-1: Article body is unrendered markdown. Section labels appear as literal brackets, such as "[
- page: `/help/doc-about-kestrel-ridge.html` · severity: medium · category: content
- found by grok/grok-4.7 (desktop): Article body is unrendered markdown. Section labels appear as literal brackets, such as "[About Kestrel Ridge > Our story]" and "[About Kestrel Ridge > Our values]", and emphasis appears as asterisks ("**Trucking fleets**", "**Show the numbers.**"). The same pattern is on /help/doc-release-notes-september-2026.html, including "[Release Notes: September 2026 > New Features]", "**Lane-level fuel variance report.**", and backtick-wrapped paths like `/v1/loads/status`.
- suggestion: Render article markdown to HTML so those bracket labels become headings, **text** becomes bold, `code` becomes code, and dash lines become a real list.
- confirmed by argon/gemini-4-argon: The screenshots of About Kestrel Ridge and Release Notes clearly show unrendered markdown syntax including bracketed headers, double asterisks, and backticks.

### grok-t4-2: The accessibility tree exposes each article as one level-1 heading and a few long paragrap
- page: `/help/doc-about-kestrel-ridge.html` · severity: medium · category: accessibility
- found by grok/grok-4.7 (desktop): The accessibility tree exposes each article as one level-1 heading and a few long paragraphs. Section titles, bullet items, and bold phrases are plain text inside those paragraphs, so there is no heading or list structure to jump through. Same on the September 2026 release notes page.
- suggestion: Emit h2 elements for each section and ul/li for bullet items, and mark emphasized phrases with strong.
- confirmed by argon/gemini-4-argon: Visually, the About and Release Notes screenshots show only a single H1 title with all section headers, lists, and bold text rendered as plain text inside paragraphs.

## How to test a fix

Run from the repository root (workdir `.`). This builds the site exactly as the reviewers saw it:

    python3 -m review.preview --out .t/site --work .t/w

Each page above is a file under `.t/site/`: the page path minus `/help/` (so `/help/index.html` is `.t/site/index.html`). An acceptance test builds the site this way, then reads one page's HTML and exits nonzero while the defect is there. Check the part of the page the issue is about, not the whole file (the page shell may legitimately contain characters an issue bans from article text). The test must not reach the network.

Each article page is helpcenter output: the article body is everything inside <main> after the <h1>. A test reads it with Python's re module, for example: python3 -c "import re,sys; body=re.search(r'<main>(.*)</main>', open('.t/site/<page>.html').read(), re.S).group(1); sys.exit(1 if '**' in body else 0)". The pages come from corpus/ through the help center build, so a fix changes helpcenter/, never corpus/.

Fixes belong in: `helpcenter/` (each bounty's path is one of these, or a file in one).

The goal's own acceptance test must stay green: `bash goals/helpcenter/acceptance.sh`.

## For the panel

Lay out one bounty per issue where the issue is a defect, not taste, and drop the rest. Each bounty's acceptance test is a new test that fails now and passes when the issue is fixed, inside the goal's scope, and the goal's own acceptance test must stay green. An issue about what the source documents say, rather than how the site presents them, is not a code defect: drop it.
