---
title: Lessons from History
description: "What 20 years of IAM open-source history teaches about protocol design, vendor lock-in, security debt, and the cost of architectural decisions."
sidebar:
  order: 3
---

# Chapter 15: Historical Parallels -- A Practitioner's Framework for Ancient and Modern Trust

## 1. Introduction: The Persistence of Trust Problems

Identity and access management is not a technology problem. It is a trust problem -- one that humans have solved repeatedly across five millennia, from Mesopotamian clay tablets to OAuth 2.0 bearer tokens. The mechanisms change; the underlying challenges do not. How do you prove you are who you claim to be? How does a gatekeeper verify that proof? How does trust transfer across jurisdictional boundaries? How do you revoke trust once granted? Every IAM protocol, every authentication module in OpenAM's 34+ module library, every federation standard documented in [Chapter 3: Federation Protocols](03-federation-protocols.md) addresses one or more of these perennial questions.

This chapter does not retrace the historical survey of [Chapter 14: Lessons from History](14-lessons-from-history.md). Instead, it builds a structured analytical framework that organizes both ancient and modern trust mechanisms by concept rather than chronology. The goal is practical: senior security architects who understand SAML, OAuth, and XACML should finish this chapter recognizing that the patterns they implement daily have been tested -- and sometimes solved better -- by civilizations that predate digital computers by thousands of years. Where modern systems have improved on ancient models, this chapter explains how. Where modern systems have regressed, it explains why and what to do about it.

The framework rests on a thesis: the "untranslated patterns" identified in pre-computer authentication research -- progressive trust escalation, community attestation, reputation decay, proximity-based verification, ritual authorization, and provenance chains (Mark 2015; Schulte Beerbuehl, EGO; Shamir 1979) -- represent the next frontier of IAM innovation. The protocols that will define the 2030s are likely digital translations of mechanisms refined over centuries of guild governance, merchant trade, and diplomatic practice.

The structure proceeds as follows: Section 2 organizes all mechanisms into seven fundamental trust pillars with detailed preserved/lost analysis. Section 3 traces split-knowledge through every era. Section 4 contrasts six ancient strengths against modern IAM failures with concrete recommendations. Section 5 maps authentication factor evolution. Section 6 analyzes the centralization-decentralization pendulum. Section 7 provides a practitioner's translation reference. Section 8 synthesizes the implications.

The intended audience is practitioners who build, configure, and maintain IAM infrastructure. Every parallel in this chapter connects an ancient mechanism to a specific modern protocol, RFC, or OIP component. The ambition is not merely academic: recognizing historical patterns can inform concrete architectural decisions about token design, federation topology, and authorization policy. When an architect sees that the Hanseatic League solved decentralized reputation across 200 cities without a central authority, the question becomes not whether that pattern applies to modern workload identity -- but why it has taken so long to translate it.

---

## 2. The Seven Pillars of Trust

All historical and modern trust mechanisms reduce to seven fundamental pillars. The table below maps each pillar to its ancient origin, modern protocol, and Open Identity Platform implementation. The subsections that follow analyze each pillar in depth, with particular attention to what was preserved and what was lost in the translation from physical to digital.

| Pillar | Ancient Example | Modern Protocol | OIP Implementation |
|--------|----------------|-----------------|-------------------|
| **Identity Binding** | Cylinder seals (~3500 BC) | X.509 certificates, PKI | OpenAM certificate auth module |
| **Bearer Proof** | Tessera hospitalis (~500 BC) | OAuth 2.0 bearer tokens, JWT | OpenAM OAuth2 provider, SSOToken |
| **Challenge-Response** | Shibboleth (~1200 BC), military watchwords | Kerberos, FIDO2/WebAuthn | OpenAM HOTP/TOTP modules, WebAuthn |
| **Delegated Trust** | Letters of safe-conduct (12th c.) | SAML federation, OIDC | OpenAM SAML IdP/SP, OIDC provider |
| **Progressive Access** | Guild apprenticeship (12th-18th c.) | Step-up auth, adaptive risk | OpenAM auth chains, Adaptive Risk module |
| **Reputation & Attestation** | Hanseatic merchant networks (12th-17th c.) | Certificate chains, SPIFFE | OpenAM policy evaluation, entitlements |
| **Non-repudiation** | Wax seals, dual-seal royal documents | Digital signatures, audit logs | OpenAM audit framework, signed assertions |

### Pillar 1: Identity Binding

The oldest known authentication system: Mesopotamian cylinder seals, small stone cylinders carved in intaglio with unique designs, rolled across wet clay to produce raised impressions. Each seal carried the owner's name, profession, genealogy, and hometown. A clay tablet bearing a seal impression was a signed document -- the seal itself never left the owner's possession, while the impression served as publicly verifiable proof of authorship. The Smithsonian's collection demonstrates this: each artifact represents a unique identity bound to a physical object that, once used to authenticate a document, left undeniable proof of the owner's intent (Mark 2015; Tanaka, Smithsonian Institution; *Archaeology Magazine* November 2025).

The practical operation was straightforward. A grain merchant in Ur, circa 2100 BC, receiving a shipment from Lagash would examine the seal impression on the shipping manifest's clay envelope. He would compare the raised impression to known seal patterns -- recognizing the sender's name, genealogy, and professional affiliation embedded in the seal's carved scene. If the seal was unfamiliar, the merchant would consult the local administrative registry, where seal ownership was recorded. The entire process -- identity verification via a unique physical artifact, checked against a registry of known identities -- took seconds and was understood by every literate participant in Mesopotamian commerce.

The seals themselves were personal possessions of considerable value. Craftsmen spent weeks carving each one. Some depicted mythological scenes specific to the owner's patron deity; others showed professional activities (a merchant with scales, a scribe with a tablet). The seal was worn around the neck or on the wrist -- always on the person, never left unattended. Losing a seal was a serious matter requiring administrative notification, analogous to reporting a stolen identity card. Deceased owners' seals were sometimes buried with them or deliberately defaced to prevent posthumous forgery.

The modern translation is precise. An X.509 certificate (RFC 5280) binds a public key to an identity, just as a seal impression binds a unique pattern to a named individual. The private key (the physical seal) never leaves the owner's hardware security module; the certificate (the impression) is distributed to verifiers. OpenAM's certificate authentication module (`OpenAM/openam-authentication/openam-auth-cert/`) validates client certificates via Java PKIX APIs (`CertPathValidator`), checking issuer trust chain, validity period, and revocation status via CRL or OCSP -- the digital equivalent of recognizing a known seal pattern and confirming it has not been defaced or revoked. The `CertAuthPrincipal` class wraps the certificate subject as a security principal for downstream authorization.

The registration process also has parallels. In Mesopotamia, seal ownership was socially recognized within administrative systems -- a seal's authority derived not just from its physical uniqueness but from the community's recognition of who owned it. This maps to certificate authority trust hierarchies: a self-signed certificate (an unregistered seal) carries no inherent trust; a CA-issued certificate (a socially recognized seal) carries the trust of the issuing authority's verification process.

**What was preserved:** The core principle -- a unique, hard-to-forge artifact that produces verifiable evidence without revealing itself -- translated perfectly into public key cryptography. Non-repudiation survives intact: a Mesopotamian merchant could not deny sealing a contract any more than a modern signer can deny a valid RSA-SHA256 signature. The concept of a registration authority (the social recognition of seal ownership within Mesopotamian administrative systems) maps to certificate authority trust hierarchies. The asymmetric nature -- the seal (private key) stays with the owner while impressions (public key / certificates) are freely distributed -- is identical in both systems.

**What was lost:** Social context and self-describing identity. A Mesopotamian seal carried genealogy and hometown -- rich identity metadata embedded in the authentication artifact itself. The seal told you not just who signed, but their lineage, their profession, their community standing. A seal impression from "Adda, son of Sargon, grain merchant of Ur, servant of the moon god Nanna" conveyed social context that no modern certificate achieves. Modern X.509 certificates carry a Distinguished Name and optional Subject Alternative Names, but the identity context is sparse. The seal's social signal has no equivalent in `CN=alice,O=ExampleCorp,C=US`. Self-describing identity credentials are only now returning via W3C Verifiable Credentials (W3C VC Data Model v2.0, 2024), which embed rich attribute sets alongside cryptographic proofs -- five millennia later, we are rediscovering what the Mesopotamians built in.

### Pillar 2: Bearer Proof

Roman tessera hospitalis tokens -- small objects of bronze, bone, or ivory, broken in two halves -- authenticated hereditary hospitality agreements. The traveler presented their half; it was physically matched against the host's half. Possession was proof. No further identity verification was required. The agreement was hereditary: descendants could present ancestral tokens, extending the trust relationship across generations. The tokens often bore the image of Jupiter Hospitalis as an authority stamp, and conferred specific legal rights: representation in courts, protection, and lodging (Smith 1875; Crisa 2020).

The day-to-day operation involved a Roman citizen arriving at a foreign city, approaching the household of a hereditary guest-friend (hospes), and presenting his half of the tessera. The host retrieved the matching half, and the two pieces were physically reunited. The unique fracture pattern -- the grain of bronze or the split of bone -- created an unmistakable match. If the halves fit, the traveler was granted full hospitality rights: a bed, meals, legal representation before the local magistrate, and safe passage through the host's territory. The entire verification was tactile -- you held the two halves together and the match was self-evident. No intermediary, no registry, no appeal process. Possession of the matching half was the complete and sufficient proof.

OAuth 2.0 bearer tokens (RFC 6749, RFC 6750) replicate this model exactly. Possession of the access token grants access to the protected resource. The resource server does not verify the bearer's identity beyond token possession -- just as the Roman host did not interrogate the tessera bearer beyond matching the token halves. OpenAM's OAuth2 provider issues bearer tokens stored in the Core Token Service (CTS) with configurable TTL, and resource servers validate them via introspection (RFC 7662) or JWT signature verification (see [Chapter 6: Token Formats](06-token-formats.md)). The scoped legal rights conferred by the tessera (court representation, protection, lodging) map to OAuth scopes (`read`, `write`, `admin`), documented in [Chapter 4: Authorization Frameworks](04-authorization-frameworks.md).

**What was preserved:** The elegance of bearer proof -- simple, fast, no interactive verification. The hereditary aspect of tessera tokens (descendants could present ancestral tokens) maps to OAuth refresh token chains: a refresh token produces new access tokens across sessions, carrying forward the original authorization grant. The token's scope limitation (specific legal rights, not unlimited authority) maps to OAuth scope-based authorization. The lack of identity verification beyond possession is both the strength and the risk -- OAuth explicitly embraces this trade-off with its bearer token model.

**What was lost:** Physicality as theft resistance. A tessera's unique break pattern was unforgeable -- the grain of bone or the fracture of bronze created a one-of-a-kind matching surface. You cannot photocopy a fracture. Matching two halves required physical proximity and produced unmistakable confirmation visible to both parties simultaneously. Digital bearer tokens are trivially copyable. An intercepted OAuth access token grants full access to anyone who possesses it -- a problem the tessera never had because you could not duplicate a fracture pattern. This regression drove the development of sender-constrained tokens: DPoP (RFC 9449, 2023) and mTLS-bound tokens (RFC 8705) bind tokens to cryptographic keys, reintroducing the "unforgeable physical match" property that the tessera had inherently (see [Chapter 12: Modern Architecture](12-modern-architecture.md), section 6). The ancient mechanism was secure by default; the modern mechanism requires opt-in security enhancement. This inversion -- where a 2,500-year-old system was more theft-resistant by default than its digital descendant -- should give every token architect pause.

### Pillar 3: Challenge-Response

In approximately 1200 BC, Gileadite guards at the Jordan River fords tested fleeing Ephraimites with a single word: "shibboleth" (meaning "ear of grain" or "stream"). The Ephraimites' inability to pronounce the "sh" sound -- saying "sibboleth" instead -- served as an unforgeable biometric marker. The test was binary: pass or fail, with no partial credit. Pronunciation habits are deeply ingrained and cannot be quickly faked. Forty-two thousand Ephraimites failed the test (Book of Judges 12:5-6; Kemmer, Rice University).

The shibboleth's power lay in its exploitation of an asymmetry: the Gileadites could pronounce both "shibboleth" and "sibboleth," but the Ephraimites could only produce the latter. This asymmetry -- where the verifier can produce both correct and incorrect responses but the imposter cannot -- is the structural foundation of every challenge-response protocol. A FIDO2 authenticator can produce a valid signature for its registered origin, but a phishing site cannot produce a valid signature for the legitimate origin. The asymmetry is structural, not memorizable.

Military watchwords formalized this into structured challenge-response pairs. Roman legions passed watchwords daily from commanders to guards via a wooden tablet (tessera) carried through the ranks. By D-Day in 1944, the system used three-part exchanges: the challenger called "Flash," the respondent answered "Thunder," and then provided the countersign "Welcome." Daily rotation prevented captured passwords from remaining useful. The U.S. military later developed mathematical challenge-response via DRYAD and AKAC-1553 cipher systems, where challenge number + response number equaled a pre-agreed sum -- introducing steganographic embedding where passwords were worked into sentences to hide them from eavesdroppers (ITS Tactical; U.S. Army Security Studies).

Modern challenge-response protocols -- CRAM, SCRAM (RFC 5802), CHAP (RFC 1994), FIDO2/WebAuthn -- are direct descendants. OpenAM's TOTP module (`OpenAM/openam-authentication/openam-auth-oath/`) implements RFC 6238 time-based one-time passwords: the server issues an implicit time-based challenge, the client proves knowledge of the shared secret through a correct HMAC-SHA response computed from the current 30-second time window. WebAuthn (`OpenAM/openam-authentication/openam-auth-webauthn/`) elevates challenge-response to asymmetric cryptography: the server sends a random challenge (nonce), the authenticator signs it with the origin-bound private key, and the server verifies with the stored public key. The origin binding -- a credential created for `example.com` cannot be used on `examp1e.com` -- makes phishing structurally impossible (see [Chapter 2: Authentication Protocols](02-authentication-protocols.md)).

**What was preserved:** The fundamental structure -- challenger issues stimulus, responder proves knowledge or capability, answer is time-limited. Daily watchword rotation became TOTP's 30-second time windows. The mathematical challenges of DRYAD (arithmetic operations on challenge numbers) prefigure HMAC computation. The binary pass/fail evaluation persists in every authentication protocol. The D-Day three-part exchange (Flash/Thunder/Welcome) is structurally identical to a three-way TLS handshake where client and server exchange nonces and verify each other's cryptographic responses.

**What was lost:** The shibboleth tested something inherent to the person -- an accent impossible to fake on the spot, shaped by a lifetime of linguistic development. No amount of coaching could change an Ephraimite's pronunciation in the moment of challenge. Modern challenge-response tests knowledge (passwords, PINs) or possession (FIDO key, phone), but rarely tests inherent characteristics. Behavioral biometrics (keystroke dynamics, voice patterns, gait analysis) represent the digital equivalent of the shibboleth test, but as noted in [Chapter 12: Modern Architecture](12-modern-architecture.md), section 10, these remain supplementary signals rather than primary authentication factors. The shibboleth was a single-factor test that achieved the security of modern multi-factor authentication because it tested an attribute that was both inherent and unforgeable. The inherent-factor gap is narrowing as continuous behavioral authentication matures, but no mainstream protocol treats behavioral signals as a primary factor with the same confidence that the shibboleth test commanded.

### Pillar 4: Delegated Trust

Royal letters of safe-conduct (12th century onward) granted bearers passage through foreign jurisdictions. The document contained the bearer's identity, purpose of travel, destination/route, and the issuing sovereign's seal or signature. The receiving state was obligated to honor the pass -- violating safe conduct was a grave diplomatic offense that could provoke military reprisal. Guarantor systems allowed travelers to provide character references or pay bonds, adding layered verification. The jurisdiction-specific nature was explicit: a pass from the King of England was valid in named territories along a stated route. A pass issued for travel to Rome via France would not grant passage through the Low Countries (*Epoch Magazine*; *Ancient Origins*; ORA Oxford).

The practical operation involved multiple verification steps at each border crossing. A traveler approaching a checkpoint would present the sealed document. The guard would examine the seal against known royal seal patterns, read the named route and purpose, verify the traveler's stated identity against the document's description, and check whether the document's validity period had passed. If the traveler carried additional character references (letters from known lords or merchants), these supplementary attestations strengthened the case for passage. The guarantor bond system added financial incentive: if the traveler caused harm, the guarantor forfeited the bond.

SAML 2.0 assertions and OIDC ID tokens replicate this pattern with precision. OpenAM's SAML IdP (`OpenAM/openam-federation/openam-federation-library/`, key classes `SAML2ConfigService`, `SAML2AssertionValidator`) issues signed XML assertions containing subject identity (`NameID`), authentication context (`AuthnContextClassRef`), and attribute statements -- the digital equivalent of the king's sealed letter. The SAML circle of trust directly parallels the network of diplomatic relations that determined which safe-conduct passes would be honored: just as England's safe-conduct pass was honored in allied kingdoms but not in hostile ones, a SAML assertion from a trusted IdP is accepted by SPs in the circle of trust but rejected by others. OIDC federation, documented in [Chapter 3: Federation Protocols](03-federation-protocols.md), automates trust chain validation via `/.well-known/openid-configuration` discovery -- the digital version of a receiving kingdom verifying that the seal on the letter belongs to a recognized sovereign. The assertion's `NotOnOrAfter` condition mirrors the safe-conduct pass's stated validity period. The `AudienceRestriction` element limits which SPs can consume the assertion, just as a safe-conduct pass named specific territories.

**What was preserved:** Scope limitation (passes applied only to specific routes; OAuth tokens carry scoped permissions). Revocability (safe conduct could be withdrawn; SAML assertions have `NotOnOrAfter` conditions and `AudienceRestriction` elements). Cross-jurisdictional trust transfer (the issuing sovereign vouches for the bearer to foreign authorities, just as an IdP vouches for a subject to SPs). The signed document model -- where a trusted authority creates a cryptographically verifiable statement about a subject -- is preserved with remarkable fidelity.

**What was lost:** The guarantor system. Medieval travelers could provide character references or pay bonds as supplementary trust signals -- layered attestation beyond the sovereign's word. A merchant carrying a safe-conduct pass from the King of England might also present letters of reference from the Hanseatic kontore in London, a bond certificate from a Florentine banking house, and personal vouching from a local lord known to the border guard. This multi-source corroboration made the trust decision richer and more resilient. Modern federation relies on a single IdP assertion with no supplementary attestation. There is no standard SAML or OIDC mechanism for "this assertion is backed by three character references and a financial bond." Multi-source identity corroboration -- combining IdP assertion with device trust, behavioral signals, and peer attestation -- remains an aspirational architecture rather than a protocol-level feature. The EU Digital Identity Wallet under eIDAS 2.0 begins to address this by enabling citizens to present credentials from multiple issuers, but the multi-attestation model is not yet standardized in enterprise IAM protocols.

### Pillar 5: Progressive Access

Medieval craft guilds enforced progression from Apprentice to Journeyman to Master over 7+ years. Secrets and techniques were revealed incrementally based on demonstrated competence (producing a "masterpiece"), peer assessment, and accumulated tenure. A newly admitted apprentice learned only basic techniques under close supervision; journeymen could work independently for pay but could not train others or open shops; masters could open workshops, train apprentices, vote in guild governance, and access the guild's financial records. Advancement required both time and proof -- not just administrative assignment (*Brewminate* 2019; *Annales de demographie historique*; *Encyclopaedia Britannica*).

The progression was not arbitrary. Each tier mapped to specific capabilities and associated risks:

- **Apprentice (years 1-3):** Basic tool handling, material preparation, simple tasks under direct supervision. Could not work unsupervised or handle valuable materials. Access to the workshop was conditional on the master's presence.
- **Apprentice (years 4-7):** More complex tasks, limited unsupervised work on non-critical pieces. Still could not access the guild's proprietary formulas (alloy compositions, dye recipes, tempering techniques).
- **Journeyman:** Independent work for pay, travel to other workshops (Wanderjahre). Could handle valuable materials and work unsupervised. Could not train others, open a shop, or vote in guild governance. Access to trade secrets was partial.
- **Master:** Full access to all guild knowledge, authority to train, authority to vote, authority to inspect other workshops. Could access financial records and participate in pricing decisions.

The "masterpiece" was not a symbolic exercise: a goldsmith's masterpiece was evaluated by existing masters for technical precision, artistic merit, and adherence to guild standards. Failure meant repeating another year as a journeyman. The evaluation was conducted by a panel of three to five masters, often including masters from neighboring cities to prevent favoritism. This was peer review with material consequences -- the closest pre-computer analog to a modern code review combined with a security certification exam.

The guild system embodied a principle that modern IAM has abandoned: trust is earned through sustained demonstration, not granted by administrative fiat. An apprentice who showed exceptional skill might be given additional responsibilities early, but never the full authority of a master. A journeyman who completed his wandering years (Wanderjahre, typically 3-4 years traveling to different workshops) had proven adaptability across contexts. The progression was not merely temporal -- it was evaluative at every stage.

Modern RBAC, as implemented in OpenAM's entitlements engine (`OpenAM/openam-entitlements/`, key classes `Entitlement`, `Privilege`, `ResourceMatch`) and formalized in Sandhu et al.'s foundational 1996 IEEE paper, grants full role permissions instantly upon assignment. A user assigned the "Developer" role on day one receives identical access to a ten-year veteran in the same role. Step-up authentication (OpenAM auth chains with `REQUIRED` module evaluation) adds friction for sensitive operations, but does not model accumulated trust over time. NIST SP 800-63 defines graduated Identity Assurance Levels (IAL1-3) for enrollment-time proofing, but not for ongoing trust accumulation based on behavior and tenure. The XACML 3.0 framework (OASIS 2013), as implemented in OpenAM's entitlements engine, could theoretically evaluate tenure-based attributes, but no standard policy template does so.

**What was preserved:** The concept of tiered access. OpenAM auth chains can require stronger authentication for higher-privilege operations, echoing the guild's requirement that masters demonstrate mastery before accessing the most sensitive techniques. XACML's `LEAuthLevelCondition` in OpenAM's policy engine evaluates authentication strength as a policy condition. The principle that more sensitive resources require more proof is well-established in modern IAM.

**What was lost:** Time as a trust factor. No mainstream IAM protocol models tenure-based privilege escalation. The guild's insight -- that trust must be earned over sustained demonstration of competence and integrity, not merely asserted -- has no digital equivalent. A compromised credential for a new hire grants the same access as a compromised credential for a veteran, because RBAC treats them identically. The blast radius of credential theft is independent of account maturity. The guild would never have given a first-day apprentice the master's keys to the treasury, yet modern systems routinely grant full role permissions to day-one employees because the role model has no concept of progressive trust.

### Pillar 6: Reputation and Attestation

The Hanseatic League (~1200-1669) maintained trust across approximately 200 merchant towns through decentralized reputation networks. Individual merchants maintained networks of 40-1,100+ trading partners built on personal relationships, not written contracts. Kontore (trading posts with judicial authority) in Bergen, London, Bruges, and Novgorod independently verified merchant standing. New merchants started with limited access and earned wider trade privileges through demonstrated reliability over multiple trading seasons. Fraudulent behavior led to expulsion and permanent reputation loss -- not just within the offending merchant's home city, but across the entire League, as kontore communicated sanctions to each other. The system was self-governing: no king or emperor administered it. The League's governance emerged from bilateral agreements, shared customs, and mutual economic interest (Schulte Beerbuehl, EGO; University of Heidelberg Working Paper; *Works in Progress Magazine*).

The kontore operated as distributed verification nodes. A merchant from Hamburg arriving in Bergen's kontore (the Bryggen wharf) would present himself, and the kontore officials would query their records and contacts to verify his standing. If the merchant was unknown, he needed sponsorship from an established member -- a process that could take weeks or months. If his reputation was good, he was granted trading privileges: access to warehouse space, permission to trade specific goods, and standing to bring disputes before the kontore's judicial proceedings. The system scaled to continental commerce without a central database, central authority, or unified identity standard. It worked because reputation was expensive to build and trivially destroyed.

Modern PKI certificate chains implement a centralized version of this pattern: trust flows from root CAs through intermediates to end-entity certificates. SPIFFE/SPIRE (CNCF graduated 2024) provides workload identity attestation in Kubernetes environments where SVIDs (SPIFFE Verifiable Identity Documents) are issued after both node attestation and workload attestation succeed (see [Chapter 12: Modern Architecture](12-modern-architecture.md), section 9). OpenAM's policy evaluation engine queries identity attributes from OpenDJ via PIP (Policy Information Point) integrations to make authorization decisions, as documented in [Chapter 4: Authorization Frameworks](04-authorization-frameworks.md). The PKI model is structurally a centralized hierarchy -- the opposite of the Hanseatic peer-to-peer model.

**What was preserved:** Chain-of-trust verification. Certificate chains validate that an end-entity certificate was issued by a trusted authority, just as a Hanseatic kontore verified that a merchant had been endorsed by a trusted counterpart in another city. Revocation mechanisms (CRL, OCSP) parallel the guild's expulsion process -- a revoked certificate, like an expelled merchant, is permanently excluded from the trust network. SPIFFE's workload attestation echoes the kontore's verification function: both serve as local nodes that independently verify identity within a distributed trust network.

**What was lost:** Decentralized, peer-to-peer trust evaluation and the concept of earned reputation. The Hanseatic model required no central authority -- reputation was emergent from bilateral relationships across a network. A merchant's standing was determined not by a certificate issued from a hierarchy, but by the aggregate of hundreds of independent trading relationships. Modern IAM centralizes trust in identity providers: a single IdP assertion determines access. W3C Verifiable Credentials (VC Data Model v2.0, 2024) and Decentralized Identifiers (DIDs v1.0, 2022) are the most promising attempt to restore decentralized attestation, but mainstream enterprise adoption remains nascent. No enterprise IAM platform natively supports "grant access if N trusted peers vouch for this person." The EU eIDAS 2.0 wallet architecture -- where citizens hold credentials from multiple issuers and present them selectively to verifiers -- directly implements the kontore model, but is still in pilot phases. The Hanseatic League proved that decentralized trust can scale to continental commerce for four centuries. The digital equivalent is still searching for its first decade of adoption.

### Pillar 7: Non-Repudiation

Wax seals and signet rings (ancient Egypt through medieval period) provided tamper-evident message integrity and legally binding sender authentication. Unique designs carved in intaglio on rings or stamps were pressed into heated wax to seal documents. Breaking the seal to read the document destroyed the authentication mark, proving tampering. By the 13th century, all levels of European society used seals for business and personal correspondence. Royal chanceries required dual seals held by different officials, implementing separation of duties centuries before the concept appeared in information security literature. Different wax colors distinguished document types and jurisdictions -- red for royal decrees, green for perpetual grants, natural for routine correspondence -- a form of metadata signaling (*Erica Weiner*; *Historic St. Mary's City Museum*; *TrustSignals*).

The dual-seal practice deserves particular attention. Important English royal documents (charters, treaties, grants of significant estates) required both the Great Seal of England (held by the Lord Chancellor) and the Privy Seal (held by the Lord Privy Seal). Neither official could unilaterally authorize a decree. The physical separation of the two seals -- kept in different buildings, controlled by different offices -- meant that forging a dual-sealed document required compromising two independent officials in two different locations. This is m-of-n authorization with m=2, n=2, physically enforced.

Digital signatures (XML-DSig for SAML assertions, JWS for JWTs as documented in [Chapter 6: Token Formats](06-token-formats.md)) replicate the integrity and non-repudiation properties. OpenAM signs SAML assertions using RSA-SHA256 via the IdP's signing certificate stored in a Java KeyStore. The signature verification process -- canonicalize XML via Exclusive C14N, compute SHA-256 digest, verify RSA signature against public key from SAML metadata -- mirrors the medieval practice of comparing a wax impression against a known seal design. The signet ring itself functioned as a hardware security module: the unique pattern (private key) never left the physical device (the ring), producing signatures (wax impressions) without revealing the underlying secret. Upon death, noble signet rings were traditionally destroyed to prevent posthumous forgery -- the medieval equivalent of key revocation.

**What was preserved:** Tamper evidence -- a modified SAML assertion fails signature verification just as a broken wax seal reveals tampering. Non-repudiation: the signer cannot deny creating the assertion, just as the seal owner could not deny sealing a document. The metadata signaling of wax colors maps to JWT `typ` and `cty` header fields distinguishing token types. The self-contained nature of a sealed document (it carries its own proof of authenticity) maps directly to the self-contained JWT model.

**What was lost:** Dual-control as a standard practice. Medieval dual-seal requirements were routine for important documents -- two separate officials applied their seals, and the document was invalid without both. Modern digital signing is typically single-party. Multi-party signing (m-of-n threshold signatures) exists mathematically since Shamir's 1979 paper and is being standardized by NIST (threshold cryptography workshop, January 2026), but no mainstream IAM platform implements threshold-signed assertions or tokens as a standard feature. OpenAM's auth chains support `REQUIRED` evaluation requiring multiple authentication modules to succeed, but this is workflow-based rather than cryptographically enforced -- a workflow approval is not the same as a threshold signature where the signed artifact itself is mathematically invalid without m parties participating in its creation. The Lord Chancellor and the Lord Privy Seal each applied their own independent seal -- the modern equivalent would be two independent cryptographic signatures, both required for validity, not a single signature preceded by a workflow approval.

---

## 3. The Split-Knowledge Principle Across Ages

One trust principle has been independently discovered in every era: no single entity should hold complete authority over a critical operation. Tracing this principle across five millennia reveals a pattern so persistent that modern systems violating it should be considered architecturally regressive.

### Ancient: Mesopotamian Bulla and Dual Seals

Mesopotamian bulla -- hollow clay envelopes containing small tokens representing the contents of a shipment -- implemented split knowledge circa 3500 BC. The tokens inside recorded the true contents (e.g., three cones = three measures of grain, two spheres = two units of oil); the seal impressions on the outside authenticated the sender. Breaking the envelope to inspect the tokens destroyed the seal impressions, creating a tamper-evident audit trail: you could verify the contents or verify the sender's attestation, but verifying one invalidated the other. This is functionally identical to modern message authentication codes where verification consumes a nonce. Royal chanceries extended this with dual-seal documents requiring separate officials to apply both seals, ensuring no single official could unilaterally authorize a decree. The physical separation of seal custody -- the Great Seal in the Chancery, the Privy Seal in the Wardrobe -- made collusion logistically difficult (*Archaeology Magazine* November 2025; *Erica Weiner*; *Seals of Identity*, Historic St. Mary's City).

### Medieval: Tally Sticks and Guild Verification

The English Exchequer's tally stick system (used from the 12th century through 1826) split a wooden stick lengthwise after notching the amount owed. The creditor kept the longer "stock" (origin of the word "stockholder"); the debtor kept the shorter "foil." Each party's half was useless alone; reuniting them verified the debt. The unique wood grain pattern at the split made forgery impossible -- a physical analog of a cryptographic key split. The system was so robust that it served as England's primary government accounting mechanism for over six centuries. When Parliament finally abolished tally sticks in 1826, the accumulated wooden records were burned in furnaces beneath the Houses of Parliament -- a fire that got out of control and destroyed the Palace of Westminster itself. The 1834 fire that gave Britain its current Parliament building was, quite literally, caused by destroying the world's longest-running split-knowledge accounting system.

Freemasonic degree systems required multiple officers -- Worshipful Master, Senior Warden, Junior Warden, Tyler (doorkeeper) -- to conduct initiation ceremonies. No single officer could confer a degree unilaterally. The Tyler guarded the door (access control); the Wardens examined the candidate (identity verification); the Master administered the obligation (authorization grant). Each officer held a specific piece of the ritual; the ceremony was invalid without all participants performing their designated functions in sequence. This is m-of-n authorization with n=4 and m=4 (Duncan, *Masonic Ritual and Monitor*; Province of Berkshire, UGLE).

### Early Digital: Shamir's Secret Sharing and HSMs

Adi Shamir formalized split knowledge mathematically in 1979: a secret S can be divided into n shares such that any m shares (where m <= n) can reconstruct S via polynomial interpolation, but fewer than m shares reveal absolutely nothing about S -- not even a single bit. This is provably information-theoretic secure, a property no computational assumption can weaken. The mathematics: choose a random polynomial of degree m-1 with the secret as the constant term; evaluate the polynomial at n distinct points; distribute the evaluations as shares. Reconstruction uses Lagrange interpolation. Hardware Security Module (HSM) key ceremonies implement this directly: root CA private keys are split across multiple smartcards held by different key custodians in different physical locations. The main vault at Fort Knox requires multiple combinations held by different individuals, none of whom alone can open it (Shamir 1979; NIST CSRC Threshold Cryptography; *The Architect Guild* 2024).

### Modern: Multi-Party Computation and SPIFFE Attestation

Threshold signatures (ECDSA, EdDSA, BLS, Schnorr variants) enable distributed signing where m-of-n parties produce a valid signature without any single party ever learning the complete private key. The FROST protocol (Flexible Round-Optimized Schnorr Threshold) achieves this in two rounds of communication, making it practical for real-time authorization decisions. Unlike Shamir's Secret Sharing, which requires reconstructing the secret (creating a moment of vulnerability), threshold signatures compute the signature collaboratively without ever reconstructing the key. NIST's ongoing threshold cryptography standardization (workshop January 2026) aims to bring these schemes into federal standards for broad adoption (*arXiv* 2311.05514, 2023; Doerner et al., NDSS 2024).

SPIFFE implements split attestation: both node attestation (is this compute node authorized in this trust domain?) and workload attestation (is this specific process authorized to receive this identity?) must succeed before an SVID is issued. This two-layer verification echoes the dual-seal model: compromise of the node alone or the workload alone is insufficient. The SPIRE server functions as the Worshipful Master, the node agent as the Warden, and the kernel/orchestrator as the Tyler -- each holding a piece of the attestation chain (see [Chapter 12: Modern Architecture](12-modern-architecture.md), section 9).

### The Regression

Despite this five-millennia lineage, modern enterprise IAM routinely violates the split-knowledge principle:

- **Single administrator accounts** with unrestricted privileges across entire identity platforms.
- **Root credentials** stored in a single password manager entry accessible to one person.
- **Service accounts** with long-lived, unrotated secrets shared via plaintext configuration files or environment variables.
- **OAuth client secrets** known to entire development teams and sometimes committed to version control.
- **Break-glass emergency accounts** accessible to a single individual without witnessing or audit.
- **HSM PINs** shared verbally between team members rather than split via Shamir shares.
- **Cloud IAM root accounts** with console access and no MFA, protected by a single email address.

Each of these is an architectural regression -- a single point of control that medieval chanceries, Masonic lodges, Exchequer clerks, and Fort Knox vault designers would have recognized as dangerous and preventable. The English Exchequer split a wooden stick because they understood that single-party control over financial records invited fraud. The Lord Chancellor and the Lord Privy Seal kept their seals in separate buildings because they understood that co-located keys were vulnerable to single-point compromise. These are not sophisticated insights -- they are obvious precautions that modern IAM systems routinely ignore.

The path forward is clear: threshold authorization for sensitive operations, m-of-n approval workflows with cryptographic enforcement (not just workflow-based approvals), and Shamir secret sharing for administrative credentials. The mathematics has been solved since 1979; the integration into mainstream IAM platforms remains overdue. OpenAM's auth chains support `REQUIRED` module evaluation, but this enforces sequential multi-factor authentication, not threshold authorization. OpenIDM's workflow engine (Activiti/BPMN 2.0) supports multi-party approval workflows, but these are human-readable workflow steps, not cryptographically enforced threshold operations. The gap between workflow approval and threshold signature is the gap between a manager clicking "Approve" and two officials independently applying their seals to a document.

---

## 4. What Ancient Trust Models Got Right That Modern IAM Gets Wrong

The seven pillars above demonstrate that the "easy" translations -- mechanisms that mapped cleanly to cryptographic primitives -- were digitized first. Seal becomes private key. Watchword becomes TOTP. Safe-conduct pass becomes SAML assertion. These are structural translations where the ancient mechanism and the modern protocol share the same mathematical properties.

The six patterns below are different. They are "hard" translations because they involve social, temporal, and contextual dimensions that have no direct cryptographic analog. They require modeling trust as a dynamic, multi-dimensional, decaying quantity rather than a binary, static, permanent permission. Ancient trust systems handled these dimensions naturally because they were embedded in social systems that continuously evaluated, updated, and communicated trust signals. Digital systems, built around static databases and binary access decisions, struggle with exactly these dimensions.

For each pattern, the ancient approach is contrasted with the modern failure, and a concrete implementation recommendation is provided.

### 1. Trust Decay

**Ancient approach:** Hanseatic merchants who stopped trading lost standing in the network. Guild members who stopped practicing lost rank. Military passwords expired daily. Diplomatic safe-conduct passes had explicit expiration dates tied to the stated purpose of travel. Trust was not permanent -- it required continuous reinforcement through active participation. A merchant absent from the kontore network for years would find his reputation diminished and his trading privileges curtailed upon return. He would need to rebuild relationships, demonstrate renewed reliability, and earn back the standing he once held. Trust was treated as a perishable resource requiring active maintenance, not a permanent credential (Schulte Beerbuehl, EGO; *Works in Progress Magazine*).

**Modern failure:** OAuth refresh tokens have fixed TTL regardless of behavioral signals. A user absent for two years retains the same RBAC role permissions as a daily active user. Adaptive authentication systems (OpenAM's `openam-auth-adaptive` module) adjust authentication requirements based on session recency and device fingerprint, but do not model long-term trust erosion across the identity lifecycle. Token expiry (a fixed TTL) is not the same as reputation decay (a dynamic function of activity). Access certification reviews in OpenIDM are periodic and administrator-initiated (typically annual), not continuous or automatic. A Hanseatic merchant would find it absurd that a trader who vanished for three years retained his full trading privileges upon return without any re-verification.

**Recommendation:** Implement continuous trust scoring with decay functions. The mathematical model:

```
trust_score(privilege) = base_score * exp(-decay_rate * days_since_last_use)
```

Where `decay_rate` is calibrated per privilege sensitivity:

- Low-sensitivity privileges (read-only access to non-PII data): decay_rate = 0.001 (half-life ~693 days)
- Medium-sensitivity privileges (write access to business data): decay_rate = 0.005 (half-life ~139 days)
- High-sensitivity privileges (admin access, PII access): decay_rate = 0.01 (half-life ~69 days)

Tie access thresholds to trust scores. When a user's trust score for a specific privilege drops below the threshold (e.g., 0.5), the privilege automatically downgrades to read-only, requiring re-verification (step-up authentication + manager approval) to restore full access. OpenAM's policy engine (`Entitlement` conditions in `openam-entitlements`) could evaluate time-since-last-access as a policy condition via a custom PIP querying OpenDJ for `lastAccessTime` attributes on user entries. OpenIDM's reconciliation engine could trigger automatic privilege downgrade for inactive accounts via scheduled sync mappings that compare current date against last-access timestamps.

Research on time-weighted trust scoring exists in blockchain reputation systems where "older actions lose weight over time" (*Preprints.org*, October 2025) and could be adapted for enterprise IAM. The key insight from the Hanseatic model: trust decay should be per-privilege, not per-identity. A merchant who traded grain regularly but hadn't traded cloth in years would retain his grain trading privileges while losing his cloth trading access.

### 2. Progressive Access Escalation

**Ancient approach:** Guild apprentices earned trust through seven or more years of demonstrated competence. At each stage, new techniques and trade secrets were revealed. The "masterpiece" -- a work produced as a final exam -- was evaluated by existing masters who voted on whether to admit the candidate. Advancement required both time-in-role and peer assessment of proficiency -- not just administrative assignment. The system incentivized learning and aligned access with demonstrated capability. A goldsmith who made flawed work would never see the guild's advanced metallurgical techniques, regardless of how many years he served (*Brewminate* 2019; *Encyclopaedia Britannica*).

**Modern failure:** RBAC (Sandhu et al. 1996, IEEE) grants full role permissions instantly upon assignment. A newly hired database administrator receives the same production access as a ten-year DBA veteran. The blast radius of a compromised credential is identical regardless of the account's tenure or demonstrated competence. Zero-trust architectures (NIST SP 800-207) assume every request is untrusted but ignore the dimension of accumulated trust over time -- they verify identity but not competence history.

**Recommendation:** Extend RBAC with competence-based and tenure-based escalation. New employees start with minimal permissions that expand as they complete training modules, pass certification exams, and accumulate tenure without security incidents. Define policy conditions in OpenAM's entitlements engine: `if (role='DBA' AND tenure > 180days AND certifications.includes('ProductionSafetyTraining') AND incidents.count == 0) then grant('ProductionWriteAccess')`. Store competence metadata (certifications, training completion dates, peer attestations) as attributes in OpenDJ user entries and query them via PIP during policy evaluation. This approach reduces blast radius for new accounts, incentivizes security training completion, and creates audit trails showing why individuals gained privileges.

### 3. Community Attestation

**Ancient approach:** Hanseatic merchants required multiple kontore to independently verify a newcomer's standing before granting full trading privileges. Guild advancement required vouching by existing masters -- typically three or more had to attest to the candidate's readiness. Medieval safe-conduct passes were strengthened by character references from known figures, and travelers could pay bonds as supplementary trust signals. The trust decision was never made by a single authority -- it was a multi-party evaluation (Kotsogiannis et al. 2018; NIST IR 8149; W3C VC Data Model v2.0).

**Modern failure:** Enterprise IAM relies on a single IdP assertion. One SAML assertion or OIDC ID token from one identity provider constitutes the entirety of identity evidence. If the IdP is compromised, all downstream assertions are tainted -- a single point of failure that a Hanseatic merchant would find reckless. There is no standard SAML or OIDC mechanism for multi-source identity corroboration. The `sub` claim in an ID token is authoritative because the IdP says so, not because multiple independent sources agree.

**Recommendation:** Multi-source identity corroboration for high-risk access decisions, combining: (1) IdP assertion (SAML/OIDC), (2) device trust attestation (TPM/Secure Enclave), (3) behavioral biometric signal (keystroke dynamics baseline match), and (4) N peer attestations stored as W3C Verifiable Credentials. Build social trust graphs in a graph database and query them from OpenAM's policy evaluation engine via a custom PIP. Define policy conditions: `if (attestations.filter(role='SeniorEngineer').count >= 3 AND device.attestation == 'trusted' AND behavior.anomaly_score < threshold) then grant('ProductionAccess')`. The W3C VC Data Model v2.0 (2024) supports multi-issuer attestations, providing the credential format. The EU eIDAS 2.0 wallet architecture validates the multi-source model at regulatory scale.

### 4. Ritual as Authorization

**Ancient approach:** Freemasonic degree ceremonies required four officers acting in concert: Worshipful Master, Senior Warden, Junior Warden, and Tyler. The candidate demonstrated proficiency through memorization and practical examination. In-person physical presence was mandatory -- grips and signs cannot be transmitted remotely. The ceremony itself was the authorization mechanism: it was impossible to gain access to the next degree's secrets without undergoing the multi-party verification ritual. The process was deliberately slow, deliberate, and solemn -- haste was antithetical to its purpose (Duncan, *Masonic Ritual and Monitor*; Province of Berkshire, UGLE).

**Modern failure:** MFA is binary: have second factor or do not. Approval workflows are single-party: one manager clicks "Approve." There is no concept of graduated authorization ceremonies for high-risk operations in standard IAM protocols. HSM key ceremonies -- requiring m-of-n key custodians physically present in a secure facility with auditors witnessing -- are the rare exception, applied to root CA signing events perhaps once per year. These ceremonies embody the Masonic model but are not available as a standard authorization pattern in enterprise IAM platforms.

**Recommendation:** Graduated authorization ceremonies for high-risk operations, cryptographically enforced. Define three ceremony tiers:

- **Tier 1 (routine):** Standard MFA -- WebAuthn + session token. Covers 95% of operations.
- **Tier 2 (sensitive):** MFA + real-time approval from one peer via push notification. Covers configuration changes, access to PII, deployment approvals.
- **Tier 3 (critical):** Multi-party cryptographic ceremony. Production database schema changes require: (1) the requesting developer's WebAuthn authentication, (2) threshold signatures from 2-of-3 senior engineers using FROST/TSS, (3) verification that all parties are authenticated from a secured network segment (proximity/network policy), and (4) a time-locked execution window (operation must complete within 30 minutes).

Implement Tier 3 via threshold signature libraries integrated into OpenAM's authorization engine. OpenIDM's Activiti workflow engine could orchestrate the human coordination, while the threshold cryptography layer provides the mathematical enforcement. The mathematical primitives exist and are being standardized (NIST threshold crypto, 2026); the integration into IAM workflows is the missing piece.

### 5. Proximity as Trust Signal

**Ancient approach:** Physical presence was the strongest authentication signal for millennia. Freemasonic handshakes (grips) required physical co-location -- they cannot be performed remotely. Guild examinations tested practical craft skills in person -- the masterpiece had to be produced in the guild hall under observation. Diplomatic credential exchange occurred face-to-face, with the ambassador presenting letters of credence to the sovereign in person. The assumption was axiomatic: if you are physically here, you are more trustworthy than if you are not. This was not naive -- it reflected the reality that impersonation at a distance was trivially easy while impersonation in person, before people who knew you, was vastly harder (Ehatisham-ul-Haq et al. 2022; Mahbub et al. 2020; *PMC* 2021).

**Modern failure:** Location is a secondary signal at best. OAuth scopes and SAML attributes have no standard representation for "user is physically near trusted device X." IP geofencing is coarse-grained (city-level accuracy) and easily spoofed via VPN. OpenAM's adaptive authentication module evaluates IP-based location as a risk signal but BLE/NFC proximity verification is not a standard IAM factor. NIST SP 800-63B defines authenticator assurance levels but does not treat continuous proximity as an authentication factor. Apple Watch unlocking a MacBook via Bluetooth proximity is a consumer example that has no enterprise IAM equivalent.

**Recommendation:** Elevate proximity from supplementary to primary factor for high-security contexts. Implement BLE beacon infrastructure in secure facilities; encode proximity claims as custom JWT claims in OpenAM-issued tokens (`proximity.beacon_rssi`, `proximity.nfc_tag`); define proximity-aware policies in the entitlements engine. For sensitive operations, require that the user's laptop, phone, and security key are within 2 meters of each other (verified via BLE RSSI > -50dBm), preventing remote credential exploitation even if all credentials are stolen. Address privacy via zero-knowledge proximity proofs -- proving "I am near the authorized location" without revealing exact coordinates.

### 6. Provenance Chains

**Ancient approach:** Letters of introduction created traceable delegation chains visible to every party in the chain. A merchant carrying a letter from King to Duke to local magistrate presented a verifiable chain of authority -- each link explicitly named and sealed. The magistrate could read the entire chain: "this bearer is vouched for by Duke A, who was authorized by King B." Roman tessera hospitalis tokens were hereditary, carrying multi-generational provenance. Guild apprentice lineages traced back to original masters, creating verifiable craft genealogies spanning centuries. The provenance was not hidden -- it was the source of the trust. A merchant whose chain included a known dishonest intermediary would be viewed with suspicion regardless of his own reputation (*Epoch Magazine*; *Ancient Origins*; Crisa 2020).

**Modern failure:** OAuth token exchange (RFC 8693) and SAML delegation profiles enable token transformation (documented in [Chapter 3: Federation Protocols](03-federation-protocols.md)), but the delegation history is opaque. A service-to-service token reveals who issued it immediately, but not the full chain: who authorized the issuer, who authorized them, and so on. Access grant metadata typically records the immediate granter but not the authorization lineage. Auditors asking "who ultimately authorized this access?" find no standardized answer in SAML assertions, OIDC ID tokens, or OAuth access tokens. The JWT `act` (actor) claim in RFC 8693 provides one level of delegation context, but not the complete chain.

**Recommendation:** Embed verifiable delegation histories in token metadata. When OpenAM issues a token on behalf of a delegated request, include a `delegation_chain` claim containing cryptographically signed links:

```json
{
  "delegation_chain": [
    {"issuer": "service-B", "authorized_by": "user-Alice", "scope": "read:reports",
     "sig": "eyJ..."},
    {"issuer": "user-Alice", "authorized_by": "admin-Carol", "scope": "read:*",
     "sig": "eyJ..."}
  ],
  "chain_depth": 2,
  "chain_root": "admin-Carol"
}
```

Implement chain validation at policy enforcement points:
1. Verify each signature in the chain (reject if any signature is invalid)
2. Check revocation status of each issuer in the chain (reject if any issuer is revoked)
3. Enforce chain length limits (e.g., maximum 5 delegation hops -- the ancient equivalent of limiting how many intermediaries could relay a letter of introduction)
4. Weight trust inversely with chain length (a direct delegation from a trusted authority is more trustworthy than one that passed through five intermediaries)
5. Verify scope narrowing (each delegation can only narrow, never widen, the granted scope)

Revoking an authority in the chain should automatically invalidate all downstream grants. The W3C Verifiable Credentials Lifecycle 1.0 specification covers delegation of authority and subordinate issuers. GS1's 2025 VC landscape document provides supply-chain provenance models directly adaptable to identity provenance (Stockburger et al. 2024; GS1 2025).

---

## 5. The Authentication Factor Evolution

Modern IAM typically recognizes three authentication factors: something you know, something you have, something you are. This taxonomy, codified by NIST SP 800-63B and embedded in every MFA product, is insufficient. Historical trust systems recognized at least seven distinct factor categories, four of which remain underdeveloped or absent in digital IAM. The following table traces each factor from its pre-computer origin through its modern form and likely future trajectory. The persistence of these categories -- despite the complete replacement of the underlying technology -- demonstrates that the factor taxonomy reflects fundamental trust properties, not implementation details.

The factors are ordered by their digital maturity: the first three are well-implemented in modern IAM, the fourth is emerging, and the last three represent significant gaps where ancient systems outperformed modern ones.

| Factor | Pre-Computer | Early Computer | Modern | Future |
|--------|-------------|----------------|--------|--------|
| **Something you know** | Shibboleth (~1200 BC), military watchwords | Passwords (MIT CTSS 1961) | PINs, security questions | Deprecated in favor of possession/biometric |
| **Something you have** | Seals, tessera, guild marks | RSA SecurID (1986) | FIDO2 security keys, phones | Passkeys (synced), SVIDs |
| **Something you are** | Pronunciation (shibboleth), handwriting | Fingerprint scanners (1970s) | Face ID, voice biometrics | Behavioral biometrics |
| **Something you do** | Masonic rituals, guild craft demonstrations | -- | Keystroke dynamics (experimental) | Continuous behavioral auth |
| **Someone who vouches** | Letters of introduction, guild attestation | Certificate authorities (1996) | SAML federation, OIDC | W3C VCs, DIDs |
| **Where you are** | Physical presence at guild hall | IP-based geo-blocking (1990s) | Geo-fencing, BLE proximity | Zero-trust continuous location |
| **What you've done** | Apprenticeship years, merchant reputation | -- | Adaptive risk scoring | Trust scores, reputation decay |

**Something You Know.** The oldest authentication factor. The shibboleth tested inherent linguistic knowledge -- an accent shaped by a lifetime in Ephraim. Military watchwords tested shared secret knowledge distributed daily from commanders to sentries. Modern passwords test memorized strings stored as salted hashes.

MIT's Compatible Time-Sharing System (CTSS, 1961) introduced computer passwords when researchers needed to share a single IBM 7094 mainframe. The password file was stored in plaintext -- within two years, a software bug displayed the entire file to every user, causing the first known password breach. OpenAM's LDAP bind module (`openam-auth-ldap`) validates passwords against directory-stored hashes (SSHA-512), a substantial improvement over CTSS's plaintext storage but still fundamentally testing a memorized secret.

The factor's trajectory is decline: the FIDO Alliance and platform vendors (Apple, Google, Microsoft) are actively deprecating passwords in favor of passkeys. Google reported in 2024 that passkey authentication is 4x faster and significantly more secure than passwords. What stayed constant across 3,200 years: proving identity through demonstrated knowledge. What changed: knowledge shifted from inherent (accent -- unforgeable) to memorized (password -- phishable) to deprecated (passkeys eliminate the factor entirely). The original shibboleth was more secure than its digital descendant precisely because it tested an inherent property rather than a memorized one.

**Something You Have.** Mesopotamian cylinder seals, Roman tesserae, medieval signet rings -- physical tokens whose possession conveyed authority. The progression through history:

- **3500 BC:** Cylinder seals -- unique, handcrafted, irreproducible. Possession proved identity because no two seals were alike.
- **500 BC:** Tessera hospitalis -- split tokens whose fracture pattern was as unique as a fingerprint. Possession of the matching half proved the relationship.
- **Medieval:** Signet rings -- heraldic designs carved into precious metal. Worn on the person at all times. Destroyed at death to prevent posthumous use.
- **1986:** RSA SecurID -- hardware OTP tokens displaying a new six-digit code every 60 seconds. First digital "something you have."
- **2019:** FIDO2 security keys (YubiKey, Google Titan) -- phishing-resistant possession proof via origin-bound public key cryptography.
- **2022+:** Passkeys -- synced platform credentials stored in platform keystores and synchronized across devices via iCloud Keychain, Google Password Manager, or Windows Hello.

OpenAM's WebAuthn module (`openam-auth-webauthn`) implements the server-side WebAuthn ceremony. What stayed constant across 5,500 years: possession as proof. What changed: unforgeable physicality of unique seals gave way to copyable digital tokens (a fundamental regression), then was partially restored by hardware-bound keys and DPoP sender constraints (RFC 9449). The trajectory is circular: from unforgeable physical tokens, to copyable digital tokens, back toward hardware-bound unforgeable digital tokens.

**Something You Are.** The shibboleth targeted inherent, unforgeable pronunciation shaped by a lifetime of linguistic development. The Gileadite guard was simultaneously a biometric sensor and a contextual evaluator -- he listened to the pronunciation, but he also observed the speaker's demeanor, clothing, companions, and behavior under stress. Modern biometrics (fingerprint, facial recognition, voice patterns) test similar inherent properties using mathematical template matching rather than human judgment.

WebAuthn authenticators (Touch ID, Face ID, Windows Hello) perform local biometric verification before signing challenges -- the biometric is verified locally and never transmitted, addressing the privacy concern of centralized biometric databases. This local-verification model has an interesting parallel: the Gileadite guard also performed verification locally at the checkpoint, without transmitting the pronunciation test result to a central authority.

What stayed constant: testing characteristics intrinsic to the person that cannot be easily transferred. What changed: social judgment by a human listener (the Gileadite guard) became mathematical comparison (template matching algorithms), eliminating the social dimension entirely. The guard's judgment could incorporate context (nervousness, inconsistent story, companion behavior); a fingerprint scanner cannot. The loss of contextual judgment is significant: a guard who noticed that a traveler claiming to be Gileadite was accompanied by known Ephraimites would deny passage regardless of pronunciation. No modern biometric system incorporates social context into its verification decision.

**Something You Do.** Masonic rituals tested through multi-step ceremonies requiring memorization of long passages, physical gestures (grips, signs, due-guards), and demonstrated proficiency in ritual conduct. The candidate did not merely know the words -- he had to perform the ritual correctly, demonstrating mastery through action rather than recitation. Guild masterpiece examinations tested craft competence -- the ability to produce a work of sufficient quality under observation. The goldsmith did not describe how to make a brooch; he made one, and it was judged.

Modern keystroke dynamics and behavioral biometrics are early digital equivalents, measuring typing cadence, mouse movement patterns, and interaction rhythms. Research shows these can achieve 95%+ accuracy in distinguishing users (Ehatisham-ul-Haq et al. 2022). However, this factor is the least developed digitally in terms of IAM platform integration. No mainstream IAM protocol includes "demonstrated competence" as an authentication factor. OpenAM has no behavioral biometrics module. NIST SP 800-63B does not define an assurance level for behavioral factors.

The gap is striking: the Masonic ritual simultaneously tested knowledge (memorized passages), ability (correct performance), and social compliance (acceptance by the officers) -- a richer multi-dimensional assessment than any modern MFA flow. Continuous behavioral authentication is the most promising path forward (*PMC* 2021), but remains in the research-to-production gap. The first IAM platform to implement behavioral factors as a native authentication module will be translating a pattern that is at least 300 years old.

**Someone Who Vouches.** Letters of introduction, guild attestation by existing masters, kontore verification of merchant standing -- trusted third parties attesting to identity based on personal knowledge. The medieval vouching process was fundamentally multi-source: a merchant seeking trading privileges in a new city might present:

1. A letter from his guild master in his home city (professional attestation)
2. A letter from a merchant already established in the destination city (peer attestation)
3. A letter from a noble or church official (authority attestation)
4. A financial bond from a banking house (economic attestation)

Each voucher contributed to the trust decision independently. No single voucher was sufficient for high-value trading privileges; the combination was required.

CAs formalized vouching digitally (VeriSign founded 1995). SAML assertions and OIDC ID tokens are signed vouches from IdPs: "I, the Identity Provider, attest that this subject authenticated at this time with this method." W3C Verifiable Credentials (2024) extend vouching to any issuer -- an employer, a university, a professional association -- potentially restoring the Hanseatic distributed model where multiple independent vouchers contributed to a trust decision. What changed: medieval attestation was multi-source and peer-to-peer; modern attestation consolidated into single IdPs, creating a single point of failure that did not exist in the historical model.

**Where You Are.** Physical presence at the guild hall, Roman forum, Masonic lodge, or royal court -- location as implicit and powerful authentication. If you were standing in the guild hall, you had already passed the Tyler at the door. The medieval assumption was layered: presence at a specific location implied you had already been verified by the access control mechanisms at that location's perimeter. Being inside the castle walls meant you had passed the gate guard. Being in the king's private chambers meant you had passed multiple checkpoints. Location was not just a signal -- it was evidence of prior successful authentication.

Digital translation: IP geoblocking (1990s), GPS geo-fencing, BLE/NFC proximity. OpenAM's adaptive authentication module evaluates IP geolocation as a risk signal, increasing authentication requirements for requests from unfamiliar locations. Zero trust (NIST SP 800-207) explicitly breaks the historical assumption that location confers trust, treating network location as untrusted by default. What changed: zero trust inverts the millennia-old assumption, treating location as one signal among many rather than as a primary trust factor. Whether this inversion is always correct is debatable -- physical proximity to a secure facility should arguably confer more trust than remote access, even in a zero-trust architecture. The medieval model was more nuanced: location was not binary trust but graduated trust proportional to proximity to the inner sanctum.

**What You've Done.** Guild apprenticeship years, Hanseatic merchant reputation built over decades, military service records, diplomatic track records -- past behavior as the strongest predictor of future trustworthiness. In the medieval world, "what you've done" was the most important factor of all. A merchant with thirty years of honest trading could negotiate deals on reputation alone. A knight with a distinguished service record was trusted with greater responsibility. A guild master who had trained twenty successful apprentices held enormous influence.

No mainstream IAM protocol models this longitudinally. Adaptive risk scoring evaluates recent session behavior (has this device been seen before? is this IP anomalous?) but not career-long trust accumulation. OpenAM's Adaptive Risk module (`openam-auth-adaptive`) considers session-level signals: login IP, device cookie, user agent, geolocation. It does not consider account-level history: years of clean operation, number of security training completions, absence of policy violations, history of responsible privilege use.

A user who has faithfully operated within their permissions for ten years receives no recognition for that track record; a user who triggers anomalies monthly receives no penalty beyond per-session step-up challenges. The medieval guild would have distinguished sharply between these two users -- the first would be on the path to master status, the second would be under scrutiny for expulsion.

This factor represents the largest gap between ancient and modern trust systems. Blockchain reputation decay models (*Preprints.org* October 2025) provide algorithmic approaches that enterprise IAM has not adopted. The mathematical tools exist (exponential decay functions, weighted moving averages, Bayesian trust updates); what is missing is the IAM platform integration that would make them actionable in policy decisions.

---

## 6. The Centralization-Decentralization Pendulum in Trust

A structural pattern recurs across millennia: trust authority oscillates between centralized and decentralized models, driven by three forces that reassert themselves in every era. [Chapter 14](14-lessons-from-history.md) identified this cycle; this section maps the forces to specific historical events and modern architectural decisions with enough detail to make the pattern predictive rather than merely descriptive.

| Era | Trust Model | Central Authority | Decentralized Mechanism |
|-----|------------|-------------------|------------------------|
| Ancient/Tribal | Clan-based | Village elder, tribal chief | Bilateral reputation among clans |
| Classical | Imperial | King/Emperor (royal seal) | Tessera hospitalis (peer-to-peer) |
| Medieval | Feudal/Guild | Crown, Church, Papacy | Guild self-governance, Hanseatic League (~200 cities) |
| Early Modern | Nation-state | Government (English passport, 1414) | Merchant letters, personal reputation networks |
| Mainframe (1960s) | Central IT | Single mainframe (all user accounts) | None |
| Client-Server (1980s) | Fragmented | Domain controller (per server) | None (identity silos) |
| Web SSO (2000s) | Re-centralized | Centralized IdP (Sun AM/OpenAM) | None |
| Federation (2010s) | Distributed-central | SAML IdP within federation | SAML circles of trust, InCommon (1000+ members) |
| Cloud (2020s) | Cloud-centralized | Cloud IdP (Okta, Entra ID) | Limited OIDC federation |
| **Next (2025+)** | **Hybrid** | **Institutional IdPs for convenience** | **DIDs, VCs, SPIFFE for sovereignty** |

### The Three Driving Forces

**Force 1: Scale limits.** Centralized systems become bottlenecks as the network grows. Medieval kingdoms could not administer justice across expanding territories -- a king in London could not personally adjudicate disputes in York and Bordeaux simultaneously. Feudal delegation emerged as a scaling mechanism: the king delegated authority to lords, who delegated to lesser lords, creating a hierarchical trust distribution. The Hanseatic League's ~200 towns exceeded any single authority's governance capacity; kontore-based decentralization emerged by necessity when the League's trade volume outgrew what any single city could manage. Sun Access Manager could not handle cloud-scale applications serving millions of users across thousands of SaaS providers; federated identity (SAML circles of trust) distributed the authentication load by allowing each organization to run its own IdP. In every case, the central authority hit a throughput or coordination limit, forcing distribution.

**Force 2: Trust boundary mismatches.** As interactions cross organizational or jurisdictional boundaries, centralized trust becomes insufficient because the central authority's writ does not extend to the foreign domain. A medieval English king's seal meant nothing in the Holy Roman Empire; letters of safe-conduct bridged the gap by creating bilateral trust agreements that spanned jurisdictions. An enterprise's internal SSO server (OpenAM, Sun AM) cannot authenticate partner employees who have no accounts in the enterprise's directory; SAML/OIDC federation was invented to solve this by enabling trust transfer between organizations without credential replication. The pattern is identical across eras: when the trust boundary of the central authority fails to encompass all parties in a transaction, delegation or federation must emerge to bridge the gap.

**Force 3: Sovereignty demands.** Entities resist ceding control of their identity infrastructure to external authorities, even when centralization would be more convenient. Hanseatic cities refused imperial control over their trade networks despite sustained pressure from both the Holy Roman Emperor and Scandinavian kings -- the cities valued their commercial autonomy over the efficiency a unified imperial trade system might have provided. Modern enterprises resist consolidating identity into a single cloud provider due to vendor lock-in risk and regulatory concerns (data residency, GDPR Article 28 processor requirements). The European Union mandated sovereign digital identity wallets under eIDAS 2.0 (Regulation 2024/1183, effective 2024) rather than relying on US-based cloud providers like Okta or Google -- an explicit sovereignty assertion. Healthcare organizations insist on controlling patient identity data under HIPAA. The sovereignty force is non-negotiable for certain contexts regardless of the convenience of centralized alternatives.

### The Current Moment and Historical Prediction

Enterprise IAM sits at a tension point in this cycle. Centralized cloud identity providers (Okta, Microsoft Entra ID, Google Cloud Identity) dominate enterprise deployments with convenience, integration, and managed operations. The centralization is deep: Okta alone processes billions of authentication events per month across thousands of enterprise customers, creating a trust concentration that would make a medieval monarch envious. Simultaneously, W3C Verifiable Credentials and Decentralized Identifiers promise individual control over portable credentials without any central registry. SPIFFE/SPIRE provides decentralized workload identity within Kubernetes clusters without a central IdP, using node-level attestation instead.

History predicts the resolution: neither extreme wins permanently. The Hanseatic League eventually gave way to nation-states with centralized bureaucracies; feudalism consolidated into centralized monarchies; but each centralization planted the seeds of the next decentralization. The British crown's centralization of power eventually provoked parliamentary demands for distributed authority. The mainframe's centralized identity model gave way to distributed client-server identity silos, which were then re-centralized by Web SSO, which was then re-distributed by federation.

The likely outcome for digital identity is a hybrid: centralized IdPs for employee authentication and SaaS integration (convenience), decentralized VCs for portable professional credentials and cross-border identity (sovereignty), and SPIFFE for machine identity within service meshes (scale). This mirrors the historical coexistence of royal seals (centralized state authority), guild marks (decentralized professional trust), and personal reputation (peer-to-peer trust) -- three trust systems operating simultaneously in the same medieval city, each suited to different contexts and coexisting without conflict.

### Implications for Practitioners

The pendulum model yields concrete architectural guidance:

1. **Design for the next swing.** Whatever architecture you build today, the opposite force will eventually assert itself. If you are building a centralized IdP today, design it to emit W3C VCs. If you are building a decentralized identity system, ensure it can integrate with centralized enterprise IdPs. Build in the connectors and abstraction layers that allow your system to accommodate the next phase.

2. **Map the three forces to your context.** Ask: (a) Will our user/service population outgrow a single IdP's capacity? (b) Do our trust boundaries match our authentication boundaries? (c) Will any stakeholder resist ceding identity control to our chosen central provider? If any answer is "yes," you are already experiencing the forces that drive the next swing.

3. **Study what caused previous swings.** The SAML-to-OIDC migration (2015-present) was driven by scale limits (SAML's XML processing cost at cloud scale) and trust boundary mismatches (mobile and SPA applications that could not handle SAML's redirect flows). The next migration will be driven by similar structural forces, not by vendor marketing.

4. **Coexistence is the norm, not the exception.** Medieval cities operated three trust systems simultaneously without conflict. Modern enterprises will likely operate centralized IdPs, decentralized VCs, and SPIFFE workload identity simultaneously, each serving a different trust context. Designing for a single "winner" is historically naive.

---

## 7. Practitioner's Translation Guide

The following reference table maps ancient trust concepts to their modern IAM equivalents, with specific protocol standards and OIP component implementations. Each row represents a conceptual lineage spanning centuries to millennia. The table is organized for reference use: practitioners encountering a modern IAM challenge can scan the "Modern IAM Term" column and look left to understand the historical precedent, or scan the "Ancient Concept" column and look right to find the modern implementation.

| Ancient Concept | Modern IAM Term | Protocol/Standard | OIP Component |
|----------------|-----------------|-------------------|---------------|
| Cylinder seal (unique carving) | Private key / digital signature | X.509, PKCS#11, RFC 5280 | OpenAM cert auth module (`openam-auth-cert`) |
| Seal impression (publicly verifiable) | Public key / certificate | X.509v3, DER/PEM encoding | OpenDJ certificate store |
| Tessera split-token (possession = access) | Bearer token | OAuth 2.0 (RFC 6749), RFC 6750 | OpenAM OAuth2 provider, CTS token store |
| Tessera break pattern (unforgeable match) | Sender-constrained token | DPoP (RFC 9449), mTLS (RFC 8705) | -- (requires protocol upgrade) |
| Shibboleth (linguistic challenge) | Challenge-response auth | FIDO2/WebAuthn (W3C), SCRAM (RFC 5802) | OpenAM WebAuthn module (`openam-auth-webauthn`) |
| Military watchword (daily rotation) | Time-based OTP | TOTP (RFC 6238), HOTP (RFC 4226) | OpenAM OATH module (`openam-auth-oath`) |
| Letter of safe-conduct (sovereign vouches) | Federated assertion | SAML 2.0 (OASIS 2005), OIDC Core 1.0 | OpenAM SAML IdP/SP, OIDC provider |
| Safe-conduct scope (named route only) | Scoped access token | OAuth 2.0 scopes, RAR (RFC 9396) | OpenAM OAuth2 scope configuration |
| Guild master mark (verified craftsman) | Role certificate / attestation | RBAC, X.509 attribute certs | OpenAM entitlements engine (`openam-entitlements`) |
| Apprentice progression (years of trust) | Step-up / progressive auth | Auth chains (JAAS), adaptive auth | OpenAM auth chains, Adaptive Risk module |
| Hanseatic reputation (earned standing) | Trust score / risk engine | Adaptive auth, behavioral analytics | OpenAM Adaptive Risk (`openam-auth-adaptive`) |
| Kontore (decentralized verifier) | Decentralized credential verifier | W3C VC Data Model v2.0, DIDs v1.0 | -- (no native OIP equivalent) |
| Dual-seal document (two officials) | Multi-party authorization | m-of-n signing, threshold crypto | OpenAM auth chains (REQUIRED mode) |
| Split-key vault (multiple keyholders) | Shamir's Secret Sharing | NIST threshold crypto (in progress) | -- (requires external integration) |
| Diplomatic pouch (sealed transport) | End-to-end encrypted channel | TLS 1.3 (RFC 8446), mTLS | OpenIG SSL/TLS termination |
| Courier immunity (transport protection) | Secure enclave / VPN tunnel | Intel SGX, ARM TrustZone, WireGuard | -- (infrastructure layer) |
| Freemasonic ritual (multi-step ceremony) | Multi-step auth workflow | Auth chains, BPMN 2.0 workflows | OpenIDM workflow engine (Activiti) |
| Masonic grip (physical presence proof) | Proximity authentication | BLE/NFC proximity, ZK location | -- (no standard IAM protocol) |
| Tally stick (split audit record) | Shared audit ledger | Distributed audit log, event sourcing | OpenAM audit framework |
| Royal court access (context-dependent) | Attribute-based access control | XACML 3.0 (OASIS 2013) | OpenAM entitlements engine |
| Bulla (clay envelope = tamper evidence) | Message authentication code | HMAC (RFC 2104), JWT signature (JWS) | OpenAM JWT signing (JWS, RFC 7515) |
| Trade route reputation (earned journeys) | Workload identity attestation | SPIFFE/SPIRE (CNCF 2024) | -- (no OIP equivalent; see Ch.12) |
| Hereditary tessera (multi-gen trust) | Delegation chain / token exchange | OAuth token exchange (RFC 8693) | OpenAM token exchange handler |
| Guild expulsion (reputation revocation) | Certificate/token revocation | CRL (RFC 5280), OCSP, token blacklist | OpenAM CTS JWT blacklist |
| Wax color coding (document type metadata) | Token type headers | JWT `typ`/`cty` headers (RFC 7519) | OpenAM JWT configuration |
| Wanderjahre (journeyman's travel years) | Cross-domain experience validation | Federated attribute exchange | SAML attribute statements |

### Reading the Table

**Untranslated patterns (OIP Component shows "--"):** These gaps are not failures of the Open Identity Platform specifically; they reflect the state of the entire IAM industry. No commercial or open-source IAM platform -- not Okta, not Keycloak, not Microsoft Entra ID -- implements proximity authentication, threshold-signed tokens, or reputation decay as standard features. The protocols and standards listed in those rows -- W3C VCs, SPIFFE, NIST threshold cryptography, BLE proximity -- are the technical vectors through which translation will occur over the next decade. Organizations planning IAM architecture today should monitor these standards for integration readiness and consider proof-of-concept implementations.

**Regression indicators (requires "protocol upgrade"):** These rows indicate cases where the ancient mechanism's security properties exceeded the modern default implementation. The tessera's unforgeable break pattern was inherently sender-constrained; OAuth bearer tokens are not. DPoP (RFC 9449) closes this gap but requires explicit adoption -- it is an opt-in security upgrade, not a default. The insight for practitioners: when an ancient mechanism was secure by default and its modern translation requires opt-in security, that gap represents a vulnerability in every deployment that uses the default. Favor protocols that are secure by default. Review your OAuth2 deployment: are your bearer tokens sender-constrained? If not, they are less theft-resistant than a 2,500-year-old Roman tessera.

**Solved translations (OIP component listed):** These rows represent the achievements of twenty years of IAM engineering. Bearer proof, challenge-response, delegated trust, non-repudiation, and tiered access all have robust, standards-based digital implementations in the Open Identity Platform. OpenAM's 34+ auth modules, OAuth2 provider, SAML federation library, and entitlements engine collectively implement the historical patterns that mapped cleanly to cryptographic primitives. These are the table's "green rows" -- translations that work.

**The pattern to watch:** The rows that transition from "--" to implemented components over the next decade will likely include workload identity (SPIFFE integration), multi-source attestation (W3C VC support), and threshold authorization (NIST threshold crypto adoption). Practitioners who prepare their architectures for these translations -- by implementing extensible policy evaluation, custom PIP integrations, and pluggable authentication chains -- will be positioned to adopt these capabilities as they mature.

---

## 8. Conclusion: Building the Next 5,000 Years of Trust

The patterns are eternal; the implementations are temporal. Consider the longevity comparison:

| Trust Mechanism | Duration of Use | Status |
|----------------|----------------|--------|
| Cylinder seals | ~3,000 years (3500 BC - 500 BC) | Replaced by alphabet-based signatures |
| Wax seals | ~2,500 years (500 BC - present, ceremonial) | Replaced by digital signatures |
| Tally sticks | ~700 years (1100 - 1826) | Abolished by Parliament |
| Guild apprentice system | ~600 years (1200 - 1800) | Replaced by industrial training |
| Hanseatic League reputation | ~450 years (1200 - 1669) | Replaced by nation-state commerce |
| LDAP directories | ~40 years (1993 - present) | Being demoted to legacy integration |
| SAML 2.0 | ~20 years (2005 - present) | Active but migrating to OIDC |
| OAuth 2.0 | ~13 years (2012 - present) | Active |
| WebAuthn/Passkeys | ~6 years (2019 - present) | Rapidly growing |

The mechanisms that endure longest are those that align with fundamental human trust dynamics: physical unforgability, social attestation, progressive earned trust, split authority, and reputation that decays without reinforcement. Digital protocols have not yet proven they can match the longevity of their ancient predecessors. See [Chapter 12: Modern Architecture](12-modern-architecture.md), section 2 for the ongoing demotion of LDAP from primary identity store to legacy integration point.

OpenAM's 34+ authentication modules (documented in [Chapter 2: Authentication Protocols](02-authentication-protocols.md)) represent twenty years of digital trust engineering. They successfully translate bearer proof (OAuth), challenge-response (TOTP/WebAuthn), delegated trust (SAML/OIDC), non-repudiation (signed assertions), and tiered access (auth chains). These are genuine achievements -- the solved rows in this chapter's translation table. But they are also the easy translations. The ancient mechanisms that mapped cleanly to cryptographic primitives were digitized first because the mapping was obvious: seal becomes private key, impression becomes certificate, watchword becomes TOTP.

The six untranslated patterns -- progressive trust escalation, community attestation, reputation decay, proximity authentication, ritual authorization, and provenance chains -- represent the hard translations. They require modeling trust as dynamic rather than static, social rather than centralized, contextual rather than universal, and temporal rather than binary. These are the properties that made the Hanseatic League resilient for four centuries, that made guild systems produce master craftsmen for six centuries, that made diplomatic safe-conduct function across hostile borders for eight centuries.

The standards and research needed to complete these translations exist today. W3C Verifiable Credentials provide the credential format for decentralized attestation and multi-source corroboration. NIST threshold cryptography standardization provides the mathematical foundation for ritual-as-authorization. Behavioral biometrics research (Ehatisham-ul-Haq et al. 2022; Mahbub et al. 2020) provides the sensing infrastructure for proximity and continuous authentication. Blockchain reputation decay models provide the algorithms for trust erosion. What remains is integration: embedding these capabilities into the policy engines, token formats, and federation protocols that enterprise IAM actually uses -- OpenAM's entitlements engine, OpenDJ's attribute store, OpenIDM's workflow orchestration, and the OIDC/SAML federation fabric.

The next decade of IAM innovation will likely digitize these ancient concepts, just as the past two decades digitized bearer tokens, challenge-response, and delegated trust. The W3C Verifiable Credentials ecosystem and decentralized identity standards are the most promising vehicles for this translation. The practitioners who recognize these historical patterns will build better systems -- not because history repeats, but because the trust problems are the same problems, and the solutions are the same solutions, waiting to be translated into code.

The best IAM architects should study history as much as RFCs. The problems have been solved before. The question is whether we will recognize the solutions when we encounter them -- not as quaint historical curiosities, but as battle-tested approaches to the exact challenges we face today.

A final observation: every mechanism in this chapter's translation table was invented by practitioners, not theorists. Cylinder seals were invented by merchants who needed to sign contracts. Tally sticks were invented by tax collectors who needed tamper-proof receipts. Military watchwords were invented by sentries who needed to distinguish friend from foe in the dark. The best IAM innovations of the next decade will similarly come from practitioners who recognize the pattern -- and translate it.

---

## Cross-References

- [Chapter 2: Authentication Protocols](02-authentication-protocols.md) -- OpenAM's 34+ auth modules as digital translations of historical trust mechanisms
- [Chapter 3: Federation Protocols](03-federation-protocols.md) -- SAML/OIDC as modern safe-conduct passes and diplomatic delegation
- [Chapter 4: Authorization Frameworks](04-authorization-frameworks.md) -- XACML, RBAC, and ReBAC as descendants of guild access control and royal court protocols
- [Chapter 6: Token Formats](06-token-formats.md) -- JWT, SAML assertions, DPoP, and VCs as modern bearer tokens and sealed documents
- [Chapter 12: Modern Architecture](12-modern-architecture.md) -- 14 architectural shifts reflecting the centralization-decentralization pendulum
- [Chapter 14: Lessons from History](14-lessons-from-history.md) -- The 11 historical mechanisms and 6 untranslated patterns that source this analysis

## Citations

This chapter draws on citations from the pre-computer authentication research extract, including:

- Mark, Joshua J. "Cylinder Seals in Ancient Mesopotamia." *World History Encyclopedia*, 2015.
- Tanaka, Terri. "Mesopotamian Cylinder Seal Inscriptions." Smithsonian Institution.
- *Archaeology Magazine*, November 2025. "What cylinder seals say about ancient and modern life."
- Smith, William. "Tessera" and "Hospitium." *A Dictionary of Greek and Roman Antiquities*, 1875.
- Crisa, A. "Tesseram conferre." *Historia* 69, no. 4 (2020): 482-518.
- Book of Judges 12:5-6, King James Bible.
- Kemmer, Suzanne. "The Story of the Shibboleth." Rice University.
- Duncan, Malcolm C. *Duncan's Masonic Ritual and Monitor*.
- Schulte Beerbuehl, Margrit. "Networks of the Hanseatic League." *European History Online (EGO)*.
- "Identity in Trade -- Evidence from the Legacy of the Hanseatic League." University of Heidelberg.
- Shamir, Adi. "How to share a secret." *Communications of the ACM* 22, no. 11 (1979): 612-613.
- "Multi-Party Threshold Cryptography." NIST CSRC.
- "A Comprehensive Survey of Threshold Digital Signatures." *arXiv* 2311.05514 (2023).
- Doerner, J. et al. "Secure Multiparty Computation of Threshold Signatures." *NDSS Symposium*, 2024.
- Sandhu, Ravi et al. "Role-Based Access Control Models." *IEEE Computer* 29, no. 2 (1996): 38-47.
- NIST SP 800-63 Digital Identity Guidelines.
- NIST SP 800-207 Zero Trust Architecture (2020).
- W3C Verifiable Credentials Data Model v2.0 (2024).
- W3C Decentralized Identifiers v1.0 (2022).
- W3C Verifiable Credentials Lifecycle 1.0.
- Kotsogiannis, I. et al. "Digital Identity: Trust and Reputation." *PLOS One* 13, no. 12 (2018).
- NIST IR 8149: "Developing Trust Frameworks to Support Identity Federations."
- Ehatisham-ul-Haq, M. et al. "Continuous user authentication via behavioral biometrics." *Multimedia Tools and Applications* 81 (2022).
- Mahbub, U. et al. "Behavioral Biometrics for Continuous Authentication." *IEEE IoT Journal* 7, no. 9 (2020).
- "Security, Privacy, and Usability in Continuous Authentication." *PMC* (2021).
- Stockburger, L. et al. "Survey on DIDs and VCs." *arXiv* 2402.02455 (2024).
- GS1. "VCs and DIDs: Technical Landscape." 2025.
- "A Review on Blockchain-Based Trust & Reputation." *Preprints.org*, October 2025.
- "Split Knowledge and Dual Control." *The Architect Guild*, 2024.
- Lindell, Y. "Secure Multiparty Computation." *IACR ePrint* 2020/300.

---

# Chapter 16: Identity Security Evolution Roadmaps — How Every Domain Got Here

## Introduction: Why "Identity Security" and Not Just "IAM"

The term "Identity and Access Management" was adequate for the 2005--2016 era, when the problem space was bounded: authenticate a human user via LDAP bind or SAML assertion, authorize access via RBAC or XACML policy, provision accounts via SPML or proprietary connectors. The Open Identity Platform stack -- OpenAM, OpenDJ, OpenIDM, OpenIG, OpenICF -- was built for that era, and it excelled within those boundaries.

That era is over. The problem space has expanded in every dimension simultaneously. Authentication now spans human users, machine workloads, IoT devices, and AI agents. Authorization extends from on-premises LDAP-backed policies to multi-cloud entitlements across AWS, Azure, and GCP. Threat detection has moved from post-hoc SIEM log correlation to real-time identity-layer behavioral analytics. Privacy regulations have transformed identity systems from authentication gateways into consent engines. Decentralized identity challenges the foundational assumption that a centralized IdP is the root of all trust. And the sheer ratio of non-human identities to human identities -- 50:1 or higher in large organizations -- has made "access management" a misleadingly narrow label for a domain that now encompasses secrets management, certificate lifecycle, workload attestation, and cloud infrastructure entitlements.

"Identity Security" is the umbrella term that captures this expansion. It encompasses:

- **IAM** (Identity & Access Management) -- the traditional core: authentication, SSO, federation, authorization
- **IGA** (Identity Governance & Administration) -- lifecycle management, access certification, SoD enforcement
- **PAM** (Privileged Access Management) -- vault-based credential management, session brokering, JIT access
- **ITDR** (Identity Threat Detection & Response) -- real-time detection of credential theft, lateral movement, privilege escalation
- **CIEM** (Cloud Infrastructure Entitlement Management) -- multi-cloud permission analysis, least-privilege enforcement
- **Decentralized Identity** -- W3C Verifiable Credentials, DIDs, self-sovereign identity wallets
- **Machine/Workload Identity** -- SPIFFE/SPIRE, short-lived certificates, non-human identity management
- **Privacy & Consent** -- GDPR/CCPA compliance, consent-as-code, data subject rights
- **Zero Trust** -- continuous verification, device trust, microsegmentation anchored to identity

This chapter traces 18 identity security domains from earliest origins through current state to projected future. Each roadmap is self-contained. The chapter concludes with the Grand Shift Table summarizing all 18 domains.

### How to Read This Chapter

Each roadmap is self-contained and can be read independently. Within each roadmap, entries proceed chronologically from earliest to latest. Every technology, protocol, and product mentioned carries one of four status tags:

| Tag | Meaning | Adoption Indicator |
|-----|---------|-------------------|
| `[ACTIVE]` | Widely deployed in production today | >25% of relevant market |
| `[LEGACY]` | Still exists in production but declining | Deployed but losing share to successors |
| `[EMERGING]` | Early adoption, <5% market penetration | Pilots, drafts, or first production deployments |
| `[OBSOLETE]` | Effectively dead; no new deployments | Mentioned for historical completeness only |

OpenAM/OIP implementation notes appear inline for every technology where OpenAM provides relevant functionality. Cross-references to earlier chapters are provided where deeper analysis exists.

---

## Roadmap 1: Authentication Methods

**Arc:** Shared secrets (1960s) --> directory-verified passwords (1993) --> network authentication protocols (1988-2000) --> one-time passwords (2005-2011) --> push notifications (2012) --> public-key passwordless (2014-present) --> continuous authentication (emerging).

### 1.1 Passwords and Shared Secrets (1960s-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 1961 | MIT CTSS implements first computer password system | Fernando Corbato, MIT | `[ACTIVE]` (concept) |
| 1976 | Unix crypt(3) introduces salted password hashing (DES-based) | Unix V7 | `[OBSOLETE]` (DES hash) |
| 1988 | Kerberos V4 replaces plaintext network passwords at MIT | Project Athena | `[OBSOLETE]` |
| 1993 | LDAP Simple Bind (RFC 1487, LDAPv1) -- password sent to directory for verification | IETF | `[ACTIVE]` |
| 1995 | LDAPv2 (RFC 1777) refines simple bind | IETF | `[OBSOLETE]` |
| 2000 | LDAPv3 adds StartTLS for encrypted password transmission | RFC 2830 | `[ACTIVE]` |
| 2000 | PKCS#5 PBKDF2 standardizes password-based key derivation | RFC 2898 | `[ACTIVE]` |
| 1999 | bcrypt published (Provos & Mazieres, OpenBSD) | USENIX 1999 | `[ACTIVE]` |
| 2009 | scrypt (Colin Percival) -- memory-hard password hashing | Percival, BSDCan 2009 | `[ACTIVE]` |
| 2013 | Password Hashing Competition launched | PHC | -- |
| 2015 | Argon2 wins PHC, becomes recommended hash | RFC 9106 (2021) | `[ACTIVE]` |
| 2017 | NIST SP 800-63B overhauls password guidance: no composition rules, no periodic rotation, check breached lists | NIST | `[ACTIVE]` guidance |

**What problem passwords solved:** Identity verification in multi-user systems. Before passwords, physical access was the access control.

**Why passwords persist:** Universal comprehension, zero hardware requirements, every protocol supports them. Estimated 80%+ of authentication events still involve a password as at least one factor.

**OpenAM implementation:** LDAP Bind module (`openam-auth-ldap`), Active Directory module (`openam-auth-ad`), DataStore module (`openam-auth-datastore`). Password hashing via SSHA-512, PBKDF2. Password policy enforcement at OpenDJ directory layer (complexity, history, lockout). See Ch.02 for detailed module analysis.

### 1.2 Kerberos (1988-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 1983 | Project Athena begins at MIT | MIT internal | Historical |
| 1988 | Kerberos V4 released publicly | MIT | `[OBSOLETE]` |
| 1993 | Kerberos V5 | RFC 1510 | Superseded |
| 2000 | Windows 2000 adopts Kerberos V5 as default AD authentication | Microsoft | `[ACTIVE]` |
| 2005 | Kerberos V5 revised specification | RFC 4120 | `[ACTIVE]` |
| 2005 | AES encryption replaces DES for Kerberos | RFC 3962 | `[ACTIVE]` |
| 2005 | PKINIT -- public key initial authentication | RFC 4556 | `[ACTIVE]` |
| 2006 | SPNEGO/Negotiate for HTTP | RFC 4559 | `[ACTIVE]` |
| 2018 | DES and RC4 formally deprecated | RFC 8429 | `[ACTIVE]` (deprecation) |

**What Kerberos solved:** Secure network authentication without transmitting passwords. Ticket-based system: user authenticates once to KDC (Key Distribution Center), receives TGT (Ticket Granting Ticket), then obtains service tickets for individual services without re-entering credentials. Mutual authentication -- both client and server prove identity.

**Architecture:** KDC (AS + TGS) issues tickets. AS-REQ/AS-REP for initial TGT. TGS-REQ/TGS-REP for service tickets. AP-REQ/AP-REP for application authentication. Cross-realm referrals for federated trust.

**OpenAM implementation:** Windows Desktop SSO module (`openam-auth-windowsdesktopsso`) -- SPNEGO/Negotiate handler accepting Kerberos tickets from browsers. Integrates with Active Directory KDC. Configuration: keytab file, SPN (Service Principal Name), KDC hostname. OpenAM validates Kerberos ticket, extracts principal name, maps to OpenAM user identity.

**Current relevance:** Foundational to every Active Directory domain. Every Windows login uses Kerberos. Also used in Hadoop/HDFS ecosystems. However, Kerberos is complex outside Windows AD, requires synchronized clocks, and is poorly suited to cloud-native architectures (no HTTP-native flow, no mobile support). `[ACTIVE]` in enterprise on-premises, `[LEGACY]` for new cloud-native projects.

### 1.3 X.509 Client Certificates (1988-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 1988 | X.509 v1 -- basic certificate structure | ITU-T X.509 | `[OBSOLETE]` |
| 1993 | X.509 v2 -- issuer/subject unique IDs | ITU-T | `[OBSOLETE]` |
| 1996 | X.509 v3 -- extensions framework (SANs, key usage, CRL distribution) | ITU-T | `[ACTIVE]` |
| 1999 | PKIX Internet profile for X.509 | RFC 2459 | Superseded |
| 2002 | PKIX updated | RFC 3280 | Superseded |
| 2008 | Definitive PKIX profile | RFC 5280 | `[ACTIVE]` |
| 2013 | Certificate Transparency | RFC 6962 | `[ACTIVE]` |
| 2015 | Let's Encrypt launches -- free automated DV certificates | ISRG | `[ACTIVE]` |
| 2019 | ACME protocol standardized | RFC 8555 | `[ACTIVE]` |
| 2021 | Certificate Transparency v2 | RFC 9162 | `[ACTIVE]` |

**What certificates solved:** Phishing-resistant mutual authentication. Client proves identity via private key possession; no shared secret transmitted. Device binding -- hardware-backed keys (TPM, Secure Enclave) prevent credential extraction.

**OpenAM implementation:** Certificate authentication module (`openam-auth-cert`). Extracts X.509 certificate from `javax.servlet.request.X509Certificate` attribute. Validates: CA chain, validity period, CRL/OCSP revocation. Maps certificate DN or SAN to user account. See Ch.02 for detailed flow.

**mTLS resurgence:** Mutual TLS is standard practice in service mesh architectures (Istio, Linkerd). SPIFFE/SPIRE (2017) uses X.509 SVIDs (SPIFFE Verifiable Identity Documents) for workload identity. OAuth 2.0 mTLS (RFC 8705) binds access tokens to client certificates. `[ACTIVE]` and growing.

### 1.4 RADIUS and TACACS+ (1991-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 1991 | Livingston Enterprises creates RADIUS for Merit Network dial-up | Internal | Historical |
| 1993 | Cisco develops TACACS+ (proprietary, based on original TACACS from 1984) | Cisco | `[ACTIVE]` (network) |
| 1997 | RADIUS standardized | RFC 2058/2059 | Superseded |
| 2000 | RADIUS definitive RFCs | RFC 2865 (auth), RFC 2866 (accounting) | `[ACTIVE]` |
| 2003 | RADIUS over EAP for 802.1X/Wi-Fi | RFC 3579 | `[ACTIVE]` |
| 2003 | Diameter protocol (RADIUS successor for telecom) | RFC 3588 (obsoleted by RFC 6733, 2012) | `[ACTIVE]` (telecom) |
| 2008 | Dynamic Authorization (CoA/Disconnect) | RFC 5176 | `[ACTIVE]` |
| 2012 | RadSec -- RADIUS over TLS | RFC 6614 | `[ACTIVE]` |

**What RADIUS solved:** Centralized authentication for network infrastructure devices (switches, APs, VPN gateways) that lack integrated directory clients. AAA: Authentication, Authorization, Accounting in one protocol.

**Fundamental weaknesses:** UDP transport, MD5-based authenticator (cryptographically weak), shared secrets between NAS and RADIUS server, no native encryption of full payload.

**OpenAM implementation:** RADIUS authentication module (`openam-auth-radius`). OpenAM acts as RADIUS client, forwarding credentials to external RADIUS server. Configuration: primary/secondary server, shared secret, timeout. Used to integrate hardware token vendors (RSA SecurID) and network access control.

**TACACS+:** Cisco-proprietary (draft-ietf-opsawg-tacacs-18 informational). Separates authentication, authorization, accounting into distinct operations. Encrypts full packet body (vs RADIUS encrypting only password). `[ACTIVE]` for Cisco network device management. No OpenAM module -- typically used between network devices and Cisco ISE/ACS.

**Diameter (RFC 3588/6733):** Intended RADIUS successor for telecom (3GPP). TCP/SCTP transport, larger AVP space, better security. Dominant in mobile network AAA (LTE/5G). Not used for enterprise Wi-Fi/VPN. `[ACTIVE]` in telecom, not relevant to OpenAM.

### 1.5 HTTP Authentication Schemes (1996-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 1996 | HTTP Basic Authentication | RFC 1945 (HTTP/1.0), RFC 2617 | `[LEGACY]` |
| 1997 | HTTP Digest Authentication | RFC 2069, RFC 2617 | `[OBSOLETE]` |
| 1999 | Form-based authentication (de facto, no RFC) | Industry practice | `[ACTIVE]` |
| 2006 | SPNEGO/Negotiate (Kerberos over HTTP) | RFC 4178, RFC 4559 | `[ACTIVE]` |
| 2012 | OAuth 2.0 Bearer Token in Authorization header | RFC 6750 | `[ACTIVE]` |
| 2014 | HTTP Authentication updated | RFC 7235 | `[ACTIVE]` |
| 2023 | DPoP token type | RFC 9449 | `[EMERGING]` |

**HTTP Basic:** Base64-encoded `username:password` in `Authorization` header. No encryption (relies entirely on TLS). Still used for API authentication (simple, universal), machine-to-machine calls, and development/testing. `[LEGACY]` for user-facing applications, `[ACTIVE]` for simple API auth.

**HTTP Digest:** Challenge-response avoiding plaintext password transmission. MD5-based (broken), complex implementation, poor proxy compatibility. Effectively dead. `[OBSOLETE]`

**Form-based:** HTML form POST with username/password. Server sets session cookie on success. No formal specification. Dominant for web applications from 2000-present. Being displaced by OIDC redirect flows and passkeys for new applications but remains ubiquitous.

**OpenAM implementation:** OpenAM's login page is form-based authentication. The `AuthContext` API accepts callbacks (NameCallback, PasswordCallback) and returns session tokens. OpenAM supports HTTP Basic via the `zero-page login` feature (REST authentication endpoint accepts Basic credentials).

### 1.6 One-Time Passwords (2005-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 1986 | RSA SecurID hardware token (proprietary algorithm) | RSA Security | `[LEGACY]` |
| 1998 | S/KEY one-time password system | RFC 2289 | `[OBSOLETE]` |
| 2004 | OATH consortium founded (Initiative for Open Authentication) | OATH | -- |
| 2005 | HOTP -- HMAC-Based One-Time Password | RFC 4226 | `[LEGACY]` |
| 2005-2010 | SMS OTP widespread deployment | Industry practice | `[LEGACY]` |
| 2010 | Google Authenticator launched (popularized TOTP) | Google | `[ACTIVE]` |
| 2011 | TOTP -- Time-Based One-Time Password | RFC 6238 | `[ACTIVE]` |
| 2017 | NIST SP 800-63B deprecates SMS OTP as "restricted" authenticator | NIST | `[ACTIVE]` (guidance) |

**HOTP (RFC 4226):** Counter-based. HMAC-SHA1(secret, counter) truncated to 6-8 digits. Problem: counter desynchronization between client and server. Requires look-ahead window. `[LEGACY]` -- superseded by TOTP for software tokens; still in some hardware tokens.

**TOTP (RFC 6238):** Time-based. HMAC-SHA1(secret, floor(time/30)). Eliminates counter desync. 30-second window with +/-1 tolerance. `[ACTIVE]` -- dominant software-based second factor. Every major service supports it. Vulnerable to real-time phishing (adversary-in-the-middle proxies code).

**SMS OTP:** Password sent via SMS text message. Convenient but insecure: SIM-swap attacks, SS7 interception, social engineering against mobile carriers. NIST deprecated as "restricted" authenticator in 2016. Still widely deployed due to universality of SMS. `[LEGACY]`

**OpenAM implementation:**
- HOTP module: `openam-auth-hotp` -- RFC 4226 implementation with SMS delivery gateway.
- TOTP/OATH module: `openam-auth-oath` -- RFC 6238 implementation. Configurable time step (30s default), code length (6/8 digits), HMAC algorithm (SHA-1/SHA-256/SHA-512). Shared secret stored in user LDAP profile. QR code enrollment via `otpauth://` URI.
- RSA SecurID module: `openam-auth-securid` -- proprietary protocol integration with RSA Authentication Manager.

See Ch.02 for detailed OTP module analysis.

### 1.7 Push Notifications (2012-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2010 | Duo Security founded (pioneer of push MFA) | Duo | `[ACTIVE]` |
| 2012 | Push authentication as MFA factor gains traction | Industry | `[ACTIVE]` |
| 2014 | Microsoft Authenticator adds push approval | Microsoft | `[ACTIVE]` |
| 2018 | Okta Verify push authentication | Okta | `[ACTIVE]` |
| 2022 | Number matching mandated (anti-fatigue) | Microsoft, others | `[ACTIVE]` |
| 2023 | Push fatigue attacks documented (Uber breach 2022, etc.) | Industry reports | -- |

**What push solved:** Better UX than TOTP (tap "Approve" vs type 6-digit code). Context display (IP, location, application) enables informed approval decisions. Can serve as passwordless primary factor, not just second factor.

**Push fatigue attacks:** Attacker repeatedly triggers push notifications until user accidentally or frustratedly approves. Mitigations: number matching (user must enter 2-digit code displayed on login screen), geographic context, rate limiting.

**OpenAM implementation:** Push authentication module (`openam-auth-push`). Supports APNs (iOS), FCM (Android), WebSocket fallback. Device enrollment via QR code. Multi-device management. Signed approval responses prevent replay. See Ch.02.

### 1.8 FIDO U2F (2014-2019)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2012 | FIDO Alliance founded | PayPal, Lenovo, Nok Nok Labs, others | -- |
| 2014 | FIDO U2F 1.0 -- Universal 2nd Factor | FIDO Alliance | Superseded |
| 2015 | Google deploys U2F for all employees -- phishing drops to zero | USENIX Security 2016 | -- |
| 2016 | FIDO U2F 1.2 -- NFC and BLE transports | FIDO Alliance | Superseded |
| 2018 | CTAP 1 (U2F renamed for FIDO2 compatibility) | FIDO Alliance | `[LEGACY]` |

**What U2F solved:** Phishing-resistant second factor. Per-origin key pairs: credential created for `example.com` cannot be used on `examp1e.com`. USB HID protocol, simple challenge-response. Google's 2015 deployment proved the concept at scale.

**Why superseded:** WebAuthn/FIDO2 subsumed U2F functionality with richer API, resident key support (passwordless), and platform authenticator support (biometrics). U2F hardware keys remain compatible via CTAP 1.

### 1.9 WebAuthn / FIDO2 (2018-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2018 | FIDO2 project announced (W3C + FIDO Alliance) | Joint | -- |
| 2018 | CTAP 2.0 -- resident credentials, PIN/biometric | FIDO Alliance | `[ACTIVE]` |
| 2019 | WebAuthn Level 1 -- W3C Recommendation | W3C | Superseded |
| 2021 | WebAuthn Level 2 -- enterprise attestation, large blobs | W3C | `[ACTIVE]` |
| 2021 | CTAP 2.1 -- credential management, min PIN length | FIDO Alliance | `[ACTIVE]` |
| 2024 | WebAuthn Level 3 -- Signal API | W3C Working Draft | `[EMERGING]` |

**What WebAuthn solved:** Phishing-resistant passwordless authentication. Public key cryptography eliminates shared secrets. Origin binding prevents credential use on phishing sites. Browser-native API (`navigator.credentials.create/get`) provides standardized interface.

**Two ceremonies:**
1. **Registration:** Server generates challenge. Authenticator generates key pair (private key stored in hardware). Returns public key + attestation. Server stores public key.
2. **Authentication:** Server generates challenge. Authenticator locates credential for origin, user performs biometric/PIN. Authenticator signs challenge with private key. Server verifies signature.

**OpenAM implementation:** WebAuthn module (`openam-auth-webauthn`). Classes: `WebAuthnAuthentication`, `WebAuthnRegistration`, `WebAuthnAuthenticationProcessor`, `WebAuthnRegistrationProcessor`. Credential ID + public key + signature counter stored in user LDAP profile. See Ch.02 for detailed flow.

### 1.10 Passkeys -- Synced WebAuthn Credentials (2022-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2022 Jun | Apple, Google, Microsoft announce passkey commitment | FIDO Alliance + platform vendors | -- |
| 2022 Sep | iOS 16 ships passkeys (iCloud Keychain sync) | Apple | `[ACTIVE]` |
| 2022 Oct | Android passkeys via Google Password Manager | Google | `[ACTIVE]` |
| 2023 May | Windows 11 23H2 passkey support | Microsoft | `[ACTIVE]` |
| 2023 Sep | 1Password, Dashlane, Bitwarden add passkey storage | Third-party managers | `[ACTIVE]` |
| 2023 | GitHub, Google, Amazon, PayPal, Best Buy offer passkey login | Industry | `[ACTIVE]` |
| 2024 | Conditional UI (passkey autofill) matures | Chrome, Safari, Edge | `[ACTIVE]` |
| 2024 | FIDO CXP/CXF -- Credential Exchange Protocol/Format | FIDO Alliance | `[EMERGING]` |
| 2025 | Enterprise device-bound passkeys gaining traction | YubiKey 5, Titan | `[ACTIVE]` |

**What passkeys solved:** WebAuthn's device portability problem. Traditional WebAuthn credentials tied to single device; passkeys sync across user's devices via platform credential manager (iCloud Keychain, Google Password Manager). Survives device loss without backup codes.

**Two types:**
- **Synced passkeys:** Stored in cloud credential manager. Cross-device. Convenient. Lower assurance (cloud backup is attack surface). Consumer use case.
- **Device-bound passkeys:** Tied to hardware (YubiKey). Cannot be extracted. Higher assurance. Enterprise/regulated use case.

**FIDO Alliance stats:** 12B+ accounts passkey-enabled as of 2024. Google: 100% employee usage. Major services adopting rapidly.

**OpenAM implementation:** Same WebAuthn module (`openam-auth-webauthn`). No protocol-level difference server-side; passkey sync handled by platform. `[ACTIVE]`

### 1.11 Continuous and Adaptive Authentication (2015-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 2015 | Risk-based / adaptive authentication enters mainstream | Industry | `[ACTIVE]` |
| 2017 | NIST SP 800-63B defines Authenticator Assurance Levels (AAL1-3) | NIST | `[ACTIVE]` |
| 2018 | PSD2 Strong Customer Authentication (SCA) mandated in EU | EU | `[ACTIVE]` |
| 2020 | OpenID Shared Signals Framework (CAEP + RISC) | OpenID Foundation | `[EMERGING]` |
| 2023 | CAEP (Continuous Access Evaluation Protocol) gaining adoption | IETF/OpenID | `[EMERGING]` |

**Adaptive authentication:** Context-aware risk scoring at point of login. Signals: device fingerprint, IP geolocation, time-of-day, velocity, threat intelligence. Low risk = password only. High risk = step-up to MFA or deny.

**Continuous authentication:** Goes beyond point-of-login. CAEP enables real-time session revocation when risk changes mid-session (device compromise reported, impossible travel detected, credential stuffing detected). Security Event Tokens (SET, RFC 8417; delivery via RFC 8935/8936) carry signals between providers.

**OpenAM implementation:**
- Adaptive module: `openam-auth-adaptive` -- pluggable risk evaluators.
- Device fingerprinting: `openam-auth-device-id` -- browser/device attribute collection.
- Scripted authentication: `openam-auth-scripted` -- Groovy/JavaScript for custom risk logic and external API calls.

See Ch.02 for detailed adaptive authentication analysis.

### 1.12 MFA Factor Evolution Table

| Generation | Factor Type | Examples | Phishing Resistant? | Era |
|------------|------------|---------|---------------------|-----|
| 1 | Knowledge | Passwords, PINs, security questions | No | 1960s-present |
| 2 | Possession (hardware) | RSA SecurID, smart cards | Partial | 1986-present |
| 3 | Possession (software OTP) | HOTP, TOTP, Google Authenticator | No | 2005-present |
| 4 | Possession (push) | Duo, Microsoft Authenticator, Okta Verify | No (fatigue attacks) | 2012-present |
| 5 | Inherence | Fingerprint, face, iris, voice | N/A (local verification) | 2013-present |
| 6 | Possession (public key) | FIDO U2F, WebAuthn, passkeys | **Yes** | 2014-present |
| 7 | Context | IP, geolocation, device trust, behavior | N/A (risk signal) | 2015-present |
| 8 | Continuous | CAEP, behavioral biometrics, session signals | N/A (ongoing) | `[EMERGING]` |

**Trajectory:** The industry is converging on passkeys (Generation 6) as the primary authentication factor, supplemented by contextual signals (Generation 7) and continuous evaluation (Generation 8). Passwords will persist as fallback for years but are no longer the recommended primary factor per NIST and FIDO Alliance guidance.

---

## Roadmap 2: Federation Protocols

**Arc:** Kerberos cross-realm (1988) --> proprietary SSO cookies (1990s) --> SAML 1.0 (2002) --> Liberty ID-FF (2003) --> SAML 2.0 (2005) --> WS-Federation (2003/2009) --> OpenID 2.0 (2007) --> OAuth 2.0 (2012) --> OpenID Connect (2014) --> OIDC extensions (2019-present) --> GNAP (draft) --> Verifiable Presentations (emerging).

### 2.1 Kerberos Cross-Realm Trust (1988-present)

| Year | Milestone | Reference | Status |
|------|-----------|-----------|--------|
| 1988 | Kerberos V4 cross-realm authentication | MIT | `[OBSOLETE]` |
| 1993 | Kerberos V5 cross-realm with transitive trust | RFC 1510 | `[ACTIVE]` (AD forests) |
| 2000 | Active Directory forest trusts use Kerberos cross-realm | Microsoft | `[ACTIVE]` |
| 2005 | Kerberos V5 revised | RFC 4120 | `[ACTIVE]` |
