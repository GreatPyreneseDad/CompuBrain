# Site review — 2026-11-05T02:07:39Z

Found by the network's reviewers. Argon and Grok each used the site in a real browser (desktop and phone) for the customer tasks below, then judged each other's findings against screenshots of every page. Only issues the other reviewer confirmed, at medium or high severity, are here.

Reviewers: argon/gemini-4-argon, grok/grok-4.7. Reviewed commit: `1adf2715d751`.

## Tasks
- (desktop) You are a new Ridgeline customer (Ridgeline is made by Kestrel Ridge). Using this help center, find out how to invite your team to your workspace.
- (desktop) You bought an annual plan three weeks ago and want your money back. Find out whether you can get a refund, first by browsing, then by asking your question in the ask box on the page.
- (phone) You are on your phone. Find the instructions for setting up single sign-on, and check the pages are comfortable to read and use at this size.
- (desktop) Use this help center the way a customer would: browse, follow links, use the ask box with a question of your own, try the keyboard (Tab) to move around. Note anything broken, confusing, inaccessible or poorly presented.

## Issues both reviewers confirmed

### grok-t1-1: The invite steps are raw Markdown. Labels show literal asterisks, such as **Settings > Use
- page: `/help/doc-support-kb-getting-started-with-ridgeline.html` · severity: medium · category: content
- found by grok/grok-4.7 (desktop): The invite steps are raw Markdown. Labels show literal asterisks, such as **Settings > Users > Invite** and **Send invitations**, section titles are bracket text like [Support KB: Getting Started with Ridgeline > Invite users], and the role list and numbered steps sit in one paragraph instead of formatted lists.
- suggestion: Render the article Markdown so UI labels are bold, sections are headings, and the invite steps are a real numbered list.
- confirmed by argon/gemini-4-argon: The Getting Started screenshot clearly shows unrendered Markdown asterisks (**Settings > Users > Invite**), bracketed section titles ([Support KB: Getting Started with Ridgeline > Invite users]), and unformatted lists.

### grok-t1-2: The only heading is the page title. Invite users, the three roles, and the four steps are 
- page: `/help/doc-support-kb-getting-started-with-ridgeline.html` · severity: medium · category: accessibility
- found by grok/grok-4.7 (desktop): The only heading is the page title. Invite users, the three roles, and the four steps are not headings or lists, so a screen reader cannot jump to the invite instructions or hear them as a list.
- suggestion: Mark each section as a heading and use ul/ol for roles and steps.
- confirmed by argon/gemini-4-argon: As visible in the Getting Started screenshot, only the main page title is rendered as a heading, while section titles, roles, and numbered steps are rendered as plain text paragraphs.

### grok-t1-3: Invite users lists only Administrator, Analyst, and Viewer. Release Notes - September 2026
- page: `/help/doc-support-kb-getting-started-with-ridgeline.html` · severity: medium · category: confusing
- found by grok/grok-4.7 (desktop): Invite users lists only Administrator, Analyst, and Viewer. Release Notes - September 2026 says Dispatcher and Dispatch Lead permissions are now separated. Someone inviting a dispatch team cannot tell which role to assign.
- suggestion: Use one role list in both articles, and include Dispatcher and Dispatch Lead in the invite steps if those roles can be assigned.
- confirmed by argon/gemini-4-argon: The Getting Started screenshot states 'Ridgeline uses three roles: Administrator, Analyst, Viewer', whereas the Release Notes screenshot mentions 'Dispatcher' and 'Dispatch Lead' roles.

### grok-t1-4: The IdP values are a raw Markdown table (| Setting | Value | and |---|---|) rather than a 
- page: `/help/doc-support-kb-setting-up-single-sign-on.html` · severity: medium · category: content
- found by grok/grok-4.7 (desktop): The IdP values are a raw Markdown table (| Setting | Value | and |---|---|) rather than a table, and the same literal ** markers and bracket section titles appear in the steps.
- suggestion: Render that Markdown as an HTML table and formatted headings so the ACS URL and other values can be copied cleanly.
- confirmed by argon/gemini-4-argon: The Setting Up Single Sign-On screenshot shows the IdP values rendered as a raw Markdown pipe table (| Setting | Value | and |---|---|) along with literal asterisks and bracketed section titles.

### grok-t1-5: Feature names show with literal asterisks (**Lane-level fuel variance report.**) and secti
- page: `/help/doc-release-notes-september-2026.html` · severity: medium · category: content
- found by grok/grok-4.7 (desktop): Feature names show with literal asterisks (**Lane-level fuel variance report.**) and section titles are bracket breadcrumbs such as [Release Notes: September 2026 > New Features], with dash bullets inside a paragraph.
- suggestion: Render release-note Markdown the same way as the other articles, with headings and lists.
- confirmed by argon/gemini-4-argon: The Release Notes screenshot shows literal asterisks around feature names (**Lane-level fuel variance report.**), bracketed section titles, and plain text dash bullets.

### grok-t2-1: Help articles show unrendered markdown. Billing FAQ displays literal **Adding seats:** and
- page: `/help/doc-support-kb-billing-faq.html` · severity: medium · category: content
- found by grok/grok-4.7 (desktop): Help articles show unrendered markdown. Billing FAQ displays literal **Adding seats:** and **Sales and use tax:** markers, and section titles as bracket text like [Support KB - Billing FAQ > Refunds] instead of headings. The Data Connectors article shows a raw pipe table (| Category | Default interval | Minimum interval |) that is not a readable table.
- suggestion: Render article markdown to HTML: real headings, bold, lists, and tables, and drop the bracket path prefixes.
- confirmed by argon/gemini-4-argon: The Billing FAQ and Data Connectors screenshots confirm unrendered Markdown including literal asterisks, bracketed section headings, and raw pipe tables.

### grok-t2-2: The Refunds section says eligibility is in the separate Refund Policy article and to refer
- page: `/help/doc-support-kb-billing-faq.html` · severity: medium · category: confusing
- found by grok/grok-4.7 (desktop): The Refunds section says eligibility is in the separate Refund Policy article and to refer to that article, but those words are plain text. The only link on the page is All articles.
- suggestion: Link 'Refund Policy article' to doc-support-kb-refund-policy-for-enterprise-customers.html.
- confirmed by argon/gemini-4-argon: In the Billing FAQ screenshot, the Refunds section tells users to refer to the separate Refund Policy article, but the text is plain and unlinked.

### grok-t2-3: The policy covers enterprise contracts (full refund within 30 days of contract start) and 
- page: `/help/doc-support-kb-refund-policy-for-enterprise-customers.html` · severity: medium · category: content
- found by grok/grok-4.7 (desktop): The policy covers enterprise contracts (full refund within 30 days of contract start) and monthly self-serve plans (current month not refunded), but never mentions annual plans. Someone who bought an annual plan three weeks ago cannot tell whether the 30-day rule applies.
- suggestion: State whether annual plans are enterprise contracts and whether a purchase three weeks ago is inside the refund window.
- confirmed by argon/gemini-4-argon: The Billing FAQ screenshot mentions annual plans ('Annual plans are invoiced by default'), while the Refund Policy screenshot only covers 'enterprise contract' and 'monthly' self-serve plans, leaving annual plans ambiguous.

### grok-t2-6: The only written contact path is billing@kestrelridge.example, which uses the reserved .ex
- page: `/help/doc-support-kb-billing-faq.html` · severity: medium · category: content
- found by grok/grok-4.7 (desktop): The only written contact path is billing@kestrelridge.example, which uses the reserved .example domain and cannot receive mail. The refund article says to contact support but gives no address or form.
- suggestion: Publish a working billing or support address, or an on-page request form, and repeat it on the refund policy page.
- confirmed by argon/gemini-4-argon: The Billing FAQ screenshot shows 'billing@kestrelridge.example' and the Refund Policy screenshot says to send requests 'to support or to your account manager' without providing a contact address or form.

### grok-t3-1: The article body is raw markdown. Section titles show as bracket paths such as "[Support K
- page: `/help/doc-support-kb-setting-up-single-sign-on.html` · severity: medium · category: content
- found by grok/grok-4.7 (phone): The article body is raw markdown. Section titles show as bracket paths such as "[Support KB - Setting Up Single Sign-On > Setting up Okta]", the IdP values are pipe rows including a "|---|---|" line, error names keep literal **asterisks**, and attribute names keep backticks (`email`).
- suggestion: Render the markdown: real headings, a stacked label/value list for the ACS URL and entity ID on small screens, bold error titles, and code styling without visible backticks.
- confirmed by argon/gemini-4-argon: The Setting Up Single Sign-On screenshots show raw Markdown throughout the body, including bracketed headings, pipe table rows, literal asterisks, and backticks around attribute names.

### grok-t3-2: Only the page title is a heading. Prerequisites, numbered steps, and common errors are one
- page: `/help/doc-support-kb-setting-up-single-sign-on.html` · severity: medium · category: accessibility
- found by grok/grok-4.7 (phone): Only the page title is a heading. Prerequisites, numbered steps, and common errors are one paragraph each, so there are no section headings or lists to move through on a long phone page.
- suggestion: Mark each section as an h2 and use ul/ol for prerequisites, setup steps, and errors.
- confirmed by argon/gemini-4-argon: In the Setting Up Single Sign-On screenshots, only the page title is styled as a heading while all sections, steps, and bullet points are rendered as plain text paragraphs.

### grok-t4-1: Article bodies are raw markdown, not formatted HTML. On this page the IdP settings are a p
- page: `/help/doc-support-kb-setting-up-single-sign-on.html` · severity: medium · category: content
- found by grok/grok-4.7 (desktop): Article bodies are raw markdown, not formatted HTML. On this page the IdP settings are a pipe table ('| Setting | Value |' and '|---|---|'), attribute names keep backticks (`email`, `firstName`), and error titles keep asterisks (**Signature validation failed.**). The same leak shows on About Kestrel Ridge (**Trucking fleets**, [About Kestrel Ridge > Our story]) and Billing FAQ (**Adding seats:**, [Support KB - Billing FAQ > Invoices]). Section titles are bracket paths inside paragraphs, not headings.
- suggestion: Render markdown to HTML: h2/h3 section headings, a real table for IdP values, bold and code styling, and ul/ol lists instead of dash-prefixed sentences.
- confirmed by argon/gemini-4-argon: The screenshots for Setting Up Single Sign-On, About Kestrel Ridge, and Billing FAQ all visibly display raw Markdown tables, backticks, asterisks, and bracketed section paths instead of formatted HTML.

### grok-t4-2: The accessibility tree exposes one h1 and a few large paragraphs. Section titles such as [
- page: `/help/doc-about-kestrel-ridge.html` · severity: medium · category: accessibility
- found by grok/grok-4.7 (desktop): The accessibility tree exposes one h1 and a few large paragraphs. Section titles such as [About Kestrel Ridge > Who we serve] and the dash bullet lists sit inside those paragraphs, so there are no headings or lists to jump to. The same structure is on the Billing FAQ and SSO articles.
- suggestion: Output real headings and lists so keyboard and screen-reader users can move by section and item.
- confirmed by argon/gemini-4-argon: Across the About Kestrel Ridge, Billing FAQ, and SSO screenshots, only the main title is rendered as a heading while sub-sections and lists are plain text inside paragraphs.

## How to test a fix

Run from the repository root (workdir `.`). This builds the site exactly as the reviewers saw it:

    python3 -m review.preview --out .t/site --work .t/w

Each page above is a file under `.t/site/`: the page path minus `/help/` (so `/help/index.html` is `.t/site/index.html`). An acceptance test builds the site this way, then reads one page's HTML and exits nonzero while the defect is there. Check the part of the page the issue is about, not the whole file (the page shell may legitimately contain characters an issue bans from article text). The test must not reach the network.

Fixes belong in: `helpcenter/` (each bounty's path is one of these, or a file in one).

The goal's own acceptance test must stay green: `bash goals/helpcenter/acceptance.sh`.

## For the panel

Lay out one bounty per issue where the issue is a defect, not taste, and drop the rest. Each bounty's acceptance test is a new test that fails now and passes when the issue is fixed, inside the goal's scope, and the goal's own acceptance test must stay green. An issue about what the source documents say, rather than how the site presents them, is not a code defect: drop it.
