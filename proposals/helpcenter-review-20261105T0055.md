# Site review — 2026-11-05T00:55:23Z

Found by the network's reviewers. Argon and Grok each used the site in a real browser (desktop and phone) for the customer tasks below, then judged each other's findings against screenshots of every page. Only issues the other reviewer confirmed, at medium or high severity, are here.

Reviewers: argon/gemini-4-argon, grok/grok-4.7. Reviewed commit: `1adf2715d751`.

## Tasks
- (desktop) You are a new Ridgeline customer (Ridgeline is made by Kestrel Ridge). Using this help center, find out how to invite your team to your workspace.
- (desktop) You bought an annual plan three weeks ago and want your money back. Find out whether you can get a refund, first by browsing, then by asking your question in the ask box on the page.
- (phone) You are on your phone. Find the instructions for setting up single sign-on, and check the pages are comfortable to read and use at this size.
- (desktop) Use this help center the way a customer would: browse, follow links, use the ask box with a question of your own, try the keyboard (Tab) to move around. Note anything broken, confusing, inaccessible or poorly presented.

## Issues both reviewers confirmed

### grok-t1-2: Invite steps are unrendered markdown in one paragraph: section titles show as bracket labe
- page: `/help/doc-support-kb-getting-started-with-ridgeline.html` · severity: medium · category: content
- found by grok/grok-4.7 (desktop): Invite steps are unrendered markdown in one paragraph: section titles show as bracket labels like [Support KB: Getting Started with Ridgeline > Invite users], and controls show literal asterisks (**Settings > Users > Invite**, **Send invitations**). There are no real subheadings or lists. The same raw asterisks and backticks appear on the September 2026 release notes.
- suggestion: Render markdown to HTML so section titles become headings, **labels** become bold, and the role list and numbered invite steps become real lists.
- confirmed by argon/gemini-4-argon: The screenshots of Getting Started with Ridgeline and the September 2026 Release Notes clearly show unrendered markdown with bracketed section headers, literal double asterisks, and raw backticks.

### grok-t1-3: The IdP values (ACS URL, Audience URI, Name ID format, and the rest) are printed as a raw 
- page: `/help/doc-support-kb-setting-up-single-sign-on.html` · severity: medium · category: content
- found by grok/grok-4.7 (desktop): The IdP values (ACS URL, Audience URI, Name ID format, and the rest) are printed as a raw markdown table, including the | Setting | Value | header and |---|---| separator, not as a table.
- suggestion: Render that block as an HTML table with Setting and Value columns.
- confirmed by argon/gemini-4-argon: The screenshot of Setting Up Single Sign-On shows the IdP configuration values rendered as raw pipe-delimited markdown text rather than an HTML table.

### grok-t2-1: Section titles are raw bracket text such as "[Refund Policy for Enterprise Customers > The
- page: `/help/doc-support-kb-refund-policy-for-enterprise-customers.html` · severity: medium · category: content
- found by grok/grok-4.7 (desktop): Section titles are raw bracket text such as "[Refund Policy for Enterprise Customers > The policy]" rather than headings. The same unrendered markdown shows on the billing FAQ (**Adding seats:** and "- **Sales and use tax:**") and on Data Connectors, where the sync table is left as pipe text ("| Category | Default interval | Minimum interval |").
- suggestion: Render article Markdown to HTML so headings, bold, lists, and tables display as formatted content.
- confirmed by argon/gemini-4-argon: The screenshots of the Refund Policy, Billing FAQ, and Data Connectors pages all display unrendered markdown including bracketed headers, literal asterisks, and raw pipe tables.

### grok-t2-2: The policy allows a full refund within 30 days only for an enterprise contract, and says s
- page: `/help/doc-support-kb-refund-policy-for-enterprise-customers.html` · severity: medium · category: content
- found by grok/grok-4.7 (desktop): The policy allows a full refund within 30 days only for an enterprise contract, and says self-serve plans are monthly with the current month not refunded. It never says whether an annual plan bought three weeks ago qualifies, even though the billing FAQ says annual plans exist and are invoiced by default.
- suggestion: State the annual-plan rule explicitly, for example that an annual plan started within 30 days is or is not refundable, and how to request it.
- confirmed by argon/gemini-4-argon: Comparing the Refund Policy screenshot (which only mentions 30-day enterprise contract refunds and monthly self-serve plans) with the Billing FAQ screenshot (which mentions annual plans) confirms that non-enterprise annual plan refunds are not addressed.

### grok-t2-3: The Refunds section tells the reader to use the separate Refund Policy article, but "Refun
- page: `/help/doc-support-kb-billing-faq.html` · severity: medium · category: confusing
- found by grok/grok-4.7 (desktop): The Refunds section tells the reader to use the separate Refund Policy article, but "Refund Policy article" is ordinary black text, not a link.
- suggestion: Link that phrase to doc-support-kb-refund-policy-for-enterprise-customers.html.
- confirmed by argon/gemini-4-argon: In the Billing FAQ screenshot under the Refunds section, the phrase 'Refund Policy article' is rendered as plain black text rather than a hyperlink.

### grok-t3-1: The IdP values are shown as raw markdown pipes, including a '|---|---|' row. On this scree
- page: `/help/doc-support-kb-setting-up-single-sign-on.html` · severity: medium · category: content
- found by grok/grok-4.7 (phone): The IdP values are shown as raw markdown pipes, including a '|---|---|' row. On this screen each row wraps, so labels like 'Single sign-on URL (ACS URL)' split from 'https://app.kestrelridge.com/saml/acs'.
- suggestion: Render a real table, or on a phone a stacked label-and-value list, so each setting stays with its URL or value.
- confirmed by argon/gemini-4-argon: The phone screenshot of Setting Up Single Sign-On shows the raw markdown pipe table wrapping across lines, separating the setting labels from their URLs.

### grok-t3-2: Section titles are raw path strings such as '[Support KB - Setting Up Single Sign-On > Set
- page: `/help/doc-support-kb-setting-up-single-sign-on.html` · severity: medium · category: content
- found by grok/grok-4.7 (phone): Section titles are raw path strings such as '[Support KB - Setting Up Single Sign-On > Setting up Okta]', error names show literal asterisks like '**"Signature validation failed."**', and attribute names show backticks (`email`). They are not headings, bold, or code.
- suggestion: Render the article markdown: short h2 titles (Before you start, Setting up Okta, Common errors), bold error names, and code-formatted attribute names.
- confirmed by argon/gemini-4-argon: The screenshot of Setting Up Single Sign-On clearly shows raw bracketed section paths, literal double asterisks around error names, and backticks around attribute names.

### grok-t3-3: The accessibility tree exposes each section, including the numbered Okta and Entra steps a
- page: `/help/doc-support-kb-setting-up-single-sign-on.html` · severity: medium · category: accessibility
- found by grok/grok-4.7 (phone): The accessibility tree exposes each section, including the numbered Okta and Entra steps and the 'You need' bullets, as a single paragraph. Only the page title is a heading, so a screen reader cannot jump to a section or hear a real list.
- suggestion: Use h2 headings and ol/ul elements for the steps and prerequisites.
- confirmed by argon/gemini-4-argon: The visual rendering in the Setting Up Single Sign-On screenshot shows that sections, bulleted lists, and numbered steps are formatted as plain text blocks without heading styles or list indentation.

### grok-t4-1: Article text is unrendered source. Section labels appear as literal brackets, e.g. "[About
- page: `/help/doc-about-kestrel-ridge.html` · severity: medium · category: content
- found by grok/grok-4.7 (desktop): Article text is unrendered source. Section labels appear as literal brackets, e.g. "[About Kestrel Ridge > Our story]" and "[About Kestrel Ridge > Contact]", and bold is left as asterisks ("**Trucking fleets**", "**Show the numbers.**"). The same pattern is on Release Notes ("[Release Notes: September 2026 > New Features]", "**Lane-level fuel variance report.**").
- suggestion: Render the article markup: drop or convert the bracket paths into real headings, and show bold as bold instead of **asterisks**.
- confirmed by argon/gemini-4-argon: The screenshots of About Kestrel Ridge and Release Notes show literal bracketed section labels and unrendered double asterisks instead of headings and bold text.

### grok-t4-2: Dash items (lane reports, customer groups, values) are one paragraph with leading hyphens,
- page: `/help/doc-about-kestrel-ridge.html` · severity: medium · category: accessibility
- found by grok/grok-4.7 (desktop): Dash items (lane reports, customer groups, values) are one paragraph with leading hyphens, not a list, and the bracketed section titles are not headings. The accessibility tree exposes only the page h1 plus long paragraphs, so a screen reader gets no list or section structure. Release Notes has the same dash-list treatment.
- suggestion: Mark those items up as ul/li and each section title as an h2.
- confirmed by argon/gemini-4-argon: The screenshots of About Kestrel Ridge and Release Notes show dash-prefixed items and bracketed section titles rendered as plain paragraph text rather than structured HTML lists and headings.

## For the panel

Lay out one bounty per issue where the issue is a defect, not taste, and drop the rest. Each bounty's acceptance test is a new test that fails now and passes when the issue is fixed, inside the goal's scope, and the goal's own acceptance test must stay green.
