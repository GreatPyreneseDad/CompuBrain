---
title: "Legal Memo - Open Source Licence Compliance"
source: legal-memo
scope: legal
---
# Legal Memo - Open Source Licence Compliance

## Privilege and Distribution

This memo is a privileged and confidential communication prepared at the request of counsel to provide legal advice. Do not forward it outside Legal, the VP of Engineering, and the Chief Product Officer without first checking with the General Counsel's office.

## Scope and Method

The audit covered all production and build dependencies for three Ridgeline components: the web application, the ingestion services, and the on-prem connector agent. The review used the `main` branch and the `release/4.8` branch as of 30 January 2026. Work ran from 12 January to 6 February 2026.

Automated SBOM generation identified 1,412 direct and transitive components:

- Permissive (MIT, BSD, Apache-2.0, ISC): 1,371
- Weak copyleft (MPL-2.0, LGPL-2.1 dynamically linked): 34
- Strong copyleft: 2
- Unknown or unresolved: 5

Engineering and Legal manually reviewed the 37 flagged packages.

## Findings

**Finding 1: AGPL-3.0 PDF rendering library.** A headless PDF renderer under AGPL-3.0 is used for report export. It ships inside the on-prem connector agent, which Kestrel Ridge distributes to customers, including two design-partner accounts. It is also reachable by users of the hosted service.

**Finding 2: GPL-3.0 geospatial parser.** A GPL-3.0 routing and geometry parser is statically linked into the connector agent binary. Because the agent is distributed, the GPL obligations attach to the combined work.

**Finding 3: Unresolved licences.** Four of the five unknown-licence items resolved to permissive licences on manual review. One vendored utility in the dashboard front end has no licence file and no identifiable upstream source.

## Analysis

Copyleft obligations are triggered mainly by distribution. Hosted-only use of GPL-3.0 code generally does not require source disclosure. AGPL-3.0 section 13 is different: if a modified AGPL program is made available for interaction over a network, users must be offered the corresponding source. The PDF renderer may be modified in our build, so we treat section 13 as applicable to the hosted service as well.

The connector agent is distributed, so the GPL-3.0 and AGPL-3.0 components in it carry source-offer and licence-propagation obligations. We do not think the design-partner deliveries fall outside those obligations. We have three remediation paths: replace the component, isolate it in a separately executed process with a documented interface, or comply with the licence terms in full. Full compliance would mean releasing source for the agent, which is not an acceptable outcome.

## Recommendations

1. **Replace the AGPL PDF renderer** with a permissively licensed alternative. Platform Engineering owns this work, with a target of 27 March 2026.
2. **Remove the GPL parser from the connector agent** by moving it into a separate helper process, or by replacing it. Target: release 4.9, planned for 17 April 2026.
