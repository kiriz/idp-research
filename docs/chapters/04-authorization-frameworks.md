# Chapter 4: Authorization Frameworks

Authorization frameworks answer the question "what is this authenticated user allowed to do?" These systems range from centralized policy engines evaluating complex attribute-based rules to distributed authorization models enabling fine-grained resource sharing. This chapter examines XACML 3.0, OAuth 2.0 scopes, UMA 2.0, legacy policy agents, and modern alternatives that have emerged in response to XACML's complexity and the cloud-native era's demands.

## XACML 3.0: The Enterprise Policy Standard

The eXtensible Access Control Markup Language (XACML) represents the most comprehensive attempt at standardizing policy-based authorization. OASIS published XACML 1.0 in 2003, followed by XACML 2.0 in 2005 and XACML 3.0 in 2013. Despite this long standardization history and enterprise adoption, XACML faces significant headwinds from developer friction, operational complexity, and cloud-native alternatives.

### Policy Structure and Components

XACML policies organize authorization decisions around four key attributes:

- **Subject**: Who is making the request (user identity, roles, group memberships, attributes like clearance level)
- **Resource**: What is being accessed (file path, database table, API endpoint, resource attributes)
- **Action**: What operation is requested (read, write, delete, execute, approve)
- **Environment**: Context of the request (time of day, IP address, authentication method, risk score)

A complete XACML policy set contains:

**Policy Set**: Top-level container grouping multiple policies. Uses a combining algorithm to resolve conflicts between policies.

**Policy**: Contains one or more rules targeting specific subject-resource-action combinations.

**Rule**: Atomic decision unit returning Permit or Deny. Contains:
- **Target**: Defines when the rule applies via match expressions on subject/resource/action/environment
- **Condition**: Boolean expression evaluated if the target matches
- **Effect**: Permit or Deny if the condition evaluates to true
- **Obligations**: Actions that must be performed when the rule fires (logging, notification, attribute assertions)
- **Advice**: Optional actions that the PEP may choose to perform

Example XACML 3.0 policy fragment:

```xml
<Policy PolicyId="ExamplePolicy"
        RuleCombiningAlgId="urn:oasis:names:tc:xacml:3.0:rule-combining-algorithm:deny-overrides">
  <Target>
    <AnyOf>
      <AllOf>
        <Match MatchId="urn:oasis:names:tc:xacml:1.0:function:string-equal">
          <AttributeValue DataType="http://www.w3.org/2001/XMLSchema#string">resource:document</AttributeValue>
          <AttributeDesignator AttributeId="resource-type"
                               Category="urn:oasis:names:tc:xacml:3.0:attribute-category:resource"
                               DataType="http://www.w3.org/2001/XMLSchema#string"
                               MustBePresent="true"/>
        </Match>
      </AllOf>
    </AnyOf>
  </Target>

  <Rule RuleId="PermitManagerAccess" Effect="Permit">
    <Target>
      <AnyOf>
        <AllOf>
          <Match MatchId="urn:oasis:names:tc:xacml:1.0:function:string-equal">
            <AttributeValue DataType="http://www.w3.org/2001/XMLSchema#string">read</AttributeValue>
            <AttributeDesignator AttributeId="action-id"
                                 Category="urn:oasis:names:tc:xacml:3.0:attribute-category:action"
                                 DataType="http://www.w3.org/2001/XMLSchema#string"
                                 MustBePresent="true"/>
          </Match>
        </AllOf>
      </AnyOf>
    </Target>

    <Condition>
      <Apply FunctionId="urn:oasis:names:tc:xacml:1.0:function:string-is-in">
        <AttributeValue DataType="http://www.w3.org/2001/XMLSchema#string">manager</AttributeValue>
        <AttributeDesignator AttributeId="user-role"
                             Category="urn:oasis:names:tc:xacml:1.0:subject-category:access-subject"
                             DataType="http://www.w3.org/2001/XMLSchema#string"
                             MustBePresent="false"/>
      </Apply>
    </Condition>

    <ObligationExpressions>
      <ObligationExpression ObligationId="log-access" FulfillOn="Permit">
        <AttributeAssignmentExpression AttributeId="access-timestamp">
          <Apply FunctionId="urn:oasis:names:tc:xacml:1.0:function:dateTime-one-and-only">
            <AttributeDesignator AttributeId="current-dateTime"
                                 Category="urn:oasis:names:tc:xacml:3.0:attribute-category:environment"
                                 DataType="http://www.w3.org/2001/XMLSchema#dateTime"
                                 MustBePresent="true"/>
          </Apply>
        </AttributeAssignmentExpression>
      </ObligationExpression>
    </ObligationExpressions>
  </Rule>
</Policy>
```

### PEP/PDP/PIP/PAP Architecture

XACML defines a distributed architecture with clear separation of concerns:

**Policy Enforcement Point (PEP)**: Intercepts access requests from applications and enforces PDP decisions. The PEP constructs an XACML request containing subject, resource, action, and environment attributes, sends it to the PDP, receives a decision (Permit/Deny/NotApplicable/Indeterminate), and enforces the decision by allowing or blocking access. The PEP also executes any obligations specified in the PDP response.

**Policy Decision Point (PDP)**: Evaluates policies against requests and returns authorization decisions. The PDP loads applicable policies from the PAP, retrieves any additional attributes from PIPs, evaluates rules according to combining algorithms, and returns a decision with obligations/advice.

**Policy Information Point (PIP)**: Provides external attribute values needed for policy evaluation. PIPs abstract attribute sources including LDAP directories (user attributes, group memberships), databases (resource metadata, relationship data), REST APIs (risk scores, reputation data), and external services (geolocation, device fingerprinting). PIPs enable dynamic attribute-based access control without hardcoding attribute values in policies.

**Policy Administration Point (PAP)**: Manages the policy repository. The PAP provides interfaces for policy authoring, testing, versioning, and deployment. It distributes policies to PDPs and maintains policy metadata including effective dates, owners, and audit trails.

Request flow:

```
1. Application attempts resource access
2. PEP intercepts request, constructs XACML request
3. PEP sends request to PDP
4. PDP identifies applicable policies from PAP
5. PDP queries PIPs for missing attributes
6. PIPs return attribute values from external sources
7. PDP evaluates policies using combining algorithms
8. PDP returns decision (Permit/Deny) with obligations
9. PEP enforces decision, executes obligations
10. Application receives allow/deny result
```

### Combining Algorithms

When multiple policies or rules apply to a request, combining algorithms resolve conflicts:

**Deny-overrides**: If any policy evaluates to Deny, the final decision is Deny. Used when any prohibition must be enforced regardless of other permissions. Most restrictive algorithm.

**Permit-overrides**: If any policy evaluates to Permit, the final decision is Permit (unless a Deny appears first). Used when any grant of access should allow the action.

**First-applicable**: The decision of the first policy whose target matches is returned. Policy ordering matters. Used for performance optimization when policy precedence is clear.

**Only-one-applicable**: Exactly one policy must match; if zero or more than one matches, an error is returned. Used to detect policy conflicts at evaluation time.

**Deny-unless-permit**: Default decision is Deny unless a policy explicitly evaluates to Permit. Fail-safe for least-privilege enforcement.

**Permit-unless-deny**: Default decision is Permit unless a policy explicitly evaluates to Deny. Used in open systems where access is default-allow.

XACML 3.0 also introduced combining algorithms for ordered policy evaluation (ordered-deny-overrides, ordered-permit-overrides) where policy evaluation stops at the first definitive decision.

### OpenAM Entitlements Implementation

OpenAM implements XACML 3.0 policy evaluation through its entitlements service located in `OpenAM/openam-entitlements/`. The implementation provides both a native policy evaluation engine and XACML 3.0 import/export capabilities.

**Core classes** (`OpenAM/openam-entitlements/`):

- `com.sun.identity.entitlement.xacml3.XACMLReaderWriter`: Marshals between XACML 3.0 XML and OpenAM's internal policy representation
- `com.sun.identity.entitlement.xacml3.XACMLPrivilegeUtils`: Converts OpenAM privileges to XACML policies and vice versa
- `org.forgerock.openam.xacml.v3.XACMLApplicationUtils`: Manages XACML policy sets and application context

OpenAM stores policies in two formats: the native JSON-based format optimized for evaluation performance, and XACML 3.0 XML for standards compliance and portability. Administrators can define policies through the admin console using the native format, then export to XACML for integration with third-party policy engines.

Policy structure in OpenAM (`OpenAM/openam-core/src/main/java/com/sun/identity/entitlement/`):

**Entitlement**: Core class representing a policy decision. Contains resource name, actions (Map<String, Boolean>), attributes (Map<String, Set<String>>), and advice/obligations.

**Privilege**: Container for a policy. Includes EntitlementSubject (who), ResourceAttributes (resource matching), Condition (context evaluation), and Entitlement (what actions are allowed).

**Subject implementations**: UserSubject, GroupSubject, RoleSubject, AuthenticatedUsers, IdentitySubject. Each implements subject matching logic.

**Condition implementations**: IPv4Condition, IPv6Condition, TimeCondition, LEAuthLevelCondition (authentication level), SessionPropertyCondition, ScriptCondition (Groovy/JavaScript custom logic).

**Resource matching**: Supports exact match, prefix match, wildcard match (`*`), and regex patterns. The `ResourceMatch` interface abstracts pattern matching strategies.

Policy evaluation flow in OpenAM:

```
1. Client calls OpenAM REST API: POST /json/policies?_action=evaluate
2. Request contains subject, resource, action, environment attributes
3. PolicyEvaluator loads applicable policies from data store (LDAP/Cassandra)
4. For each policy:
   a. Evaluate subject match (user/group/role)
   b. Evaluate resource match (path pattern)
   c. Evaluate action match (HTTP verb, custom action)
   d. Evaluate conditions (IP, time, auth level)
5. Apply combining algorithm (deny-overrides default)
6. Construct Entitlement with permitted actions and advice
7. Cache decision (TTL-based)
8. Return JSON response with actions and advice
```

OpenAM's policy evaluation engine caches policy decisions to reduce latency. Cache entries include subject+resource+action hash, decision, and TTL. Policy modifications invalidate related cache entries. This caching strategy reduces LDAP queries and policy evaluation overhead in high-throughput scenarios.

### JSON Policy Profile

XACML 3.0 introduced a JSON request/response profile to address developer complaints about XML verbosity. The JSON profile maps XACML concepts to JSON structures while maintaining semantic equivalence.

Example JSON request:

```json
{
  "Request": {
    "AccessSubject": {
      "Attribute": [
        {
          "AttributeId": "user-id",
          "Value": "alice"
        },
        {
          "AttributeId": "user-role",
          "Value": ["manager", "employee"]
        }
      ]
    },
    "Resource": {
      "Attribute": [
        {
          "AttributeId": "resource-type",
          "Value": "document"
        },
        {
          "AttributeId": "resource-id",
          "Value": "/files/project/plan.pdf"
        }
      ]
    },
    "Action": {
      "Attribute": [
        {
          "AttributeId": "action-id",
          "Value": "read"
        }
      ]
    },
    "Environment": {
      "Attribute": [
        {
          "AttributeId": "current-time",
          "Value": "2025-02-13T14:30:00Z"
        }
      ]
    }
  }
}
```

Example JSON response:

```json
{
  "Response": [
    {
      "Decision": "Permit",
      "Status": {
        "StatusCode": {
          "Value": "urn:oasis:names:tc:xacml:1.0:status:ok"
        }
      },
      "Obligations": [
        {
          "Id": "log-access",
          "AttributeAssignment": [
            {
              "AttributeId": "access-timestamp",
              "Value": "2025-02-13T14:30:00Z"
            }
          ]
        }
      ]
    }
  ]
}
```

Despite the JSON profile, XACML adoption remained limited compared to simpler alternatives. The JSON format reduced syntax complexity but did not address the fundamental complexity of the XACML model itself.

### Why XACML Adoption Stalled

XACML achieved OASIS standardization and enterprise deployments but never became the dominant authorization standard. Key factors:

**1. Excessive complexity**: XML policies are verbose and difficult to author without specialized tools. Simple "allow managers to read documents" requires 50+ lines of XML. Policy debugging is painful without dedicated tooling.

**2. Performance concerns**: Multi-tier architecture (PEP -> PDP -> PIP) introduces latency. Network round trips to external PIPs for attribute retrieval add milliseconds per decision. Real-time authorization decisions in high-throughput APIs cannot tolerate this overhead.

**3. Developer friction**: XML-heavy in a JSON-native world. No native SDK ecosystem for popular languages (JavaScript, Python, Go). Most implementations were Java-based, limiting adoption. Steep learning curve for new developers.

**4. Deployment complexity**: Requires deploying and managing PDP servers, PAP servers, and PIP integrations. Clustering PDPs for high availability adds operational burden. Contrast with embedded policy engines that run in the application process.

**5. Lack of cloud-native tooling**: No Kubernetes-native deployments, no serverless integration, no auto-scaling patterns. XACML predates the cloud-native era and retrofitting it proved difficult.

**6. Vendor lock-in**: Most production XACML implementations were commercial (Axiomatics, IBM, Oracle). Open-source implementations (SunXACML, HERAS-AF, WSO2 Balana) lacked enterprise support and polish. This created hesitation for adoption without vendor commitment.

**7. Limited composability**: XACML policies are monolithic. Difficult to compose policies from multiple teams or domains. No clear pattern for microservices architectures where each service owns its authorization logic.

### Current Relevance

XACML 3.0 remains an active OASIS standard. Organizations with existing XACML deployments continue to use it, particularly in government, healthcare, and financial services where policy auditability and formal compliance requirements favor standardized policy languages. However, greenfield projects rarely choose XACML. The standard serves as conceptual foundation knowledge but not as the recommended implementation approach.

OpenAM's XACML implementation provides export/import capability for standards compliance and migration scenarios, but the native entitlements API is used for runtime policy evaluation.

## OAuth 2.0 Scopes as Authorization

OAuth 2.0 (RFC 6749, 2012) defines scopes as a mechanism for limiting access granted to client applications. While OAuth 2.0 is fundamentally an authorization framework for delegated access, scopes have evolved into a general-purpose authorization mechanism far beyond their original intent.

### Scope Syntax and Semantics

Scopes are space-delimited strings included in authorization requests and access tokens. RFC 6749 does not mandate scope syntax; common patterns include:

**Simple naming**: `read`, `write`, `admin`, `delete`

**Resource-based**: `files:read`, `files:write`, `users:read`, `users:write`

**Hierarchical**: `api`, `api.read`, `api.read.public`, `api.write`

**URN format**: `urn:example:api:read`, `urn:example:api:write`

**Audience-scoped**: `https://api.example.com/files.read`, `https://api.example.com/files.write` (combines audience and scope)

Example authorization request:

```
GET /authorize?
  response_type=code&
  client_id=webapp&
  redirect_uri=https://app.example.com/callback&
  scope=files.read%20files.write%20profile&
  state=xyz
```

The authorization server presents a consent screen to the user showing the requested scopes in human-readable form ("This application wants to read and write your files and access your profile"). Upon user approval, the authorization code is issued with the granted scopes, which may be a subset of the requested scopes if the user denied some permissions.

Access token response includes `scope` parameter:

```json
{
  "access_token": "eyJhbGc...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "tGzv3JOkF0XG5Qx2TlKWIA",
  "scope": "files.read files.write profile"
}
```

### Scope Validation at Resource Servers

Resource servers (APIs) validate scopes to enforce authorization. The validation pattern:

1. Extract access token from `Authorization: Bearer <token>` header
2. Validate token signature and expiration
3. Extract scopes from token claims (JWT) or introspection response (opaque token)
4. Check that required scope for the endpoint is present
5. Allow or deny request based on scope match

Example scope validation in OpenAM's OAuth2 implementation (`OpenAM/openam-oauth2/src/main/java/org/forgerock/oauth2/core/`):

```java
// OAuth2Request wraps incoming request
OAuth2Request request = ...;

// Extract access token
String tokenString = request.getParameter("access_token");

// Validate token and get scopes
AccessToken accessToken = tokenStore.readAccessToken(tokenString);
Set<String> grantedScopes = accessToken.getScope();

// Check required scope
String requiredScope = "files.write";
if (!grantedScopes.contains(requiredScope)) {
    throw new InsufficientScopeException("Missing required scope: " + requiredScope);
}
```

### Scope Hierarchies and Wildcards

Some implementations support hierarchical scope checking. If a token has scope `api.write`, it implicitly grants `api.write.files`, `api.write.users`, etc. This pattern requires server-side logic to parse and evaluate scope prefixes.

Wildcard scopes like `api.*` or `files:*` grant all permissions under a prefix. This reduces scope explosion but requires careful validation logic to prevent overly broad grants.

OpenAM OAuth2 scopes are flat strings without built-in hierarchy support. Hierarchical validation requires custom `ScopeValidator` implementations.

### Scope Consent and Dynamic Consent

User consent for scopes occurs during the authorization flow. The authorization server presents a consent screen enumerating requested scopes with descriptions. Best practices:

- Group related scopes (e.g., "Read and write files" instead of listing `files.read` and `files.write` separately)
- Highlight sensitive scopes (e.g., "Full access to your account")
- Support granular consent (user can approve some scopes and deny others)
- Remember consent to avoid repeated prompts (subject to security policies)

Dynamic consent allows resource servers to request additional scopes during API usage via `WWW-Authenticate` header with `insufficient_scope` error:

```
HTTP/1.1 403 Forbidden
WWW-Authenticate: Bearer realm="api",
                   scope="files.write",
                   error="insufficient_scope",
                   error_description="The request requires write access"
```

The client then redirects the user back to the authorization server with the additional scope in the authorization request.

### Grant Types as Authorization Patterns

OAuth 2.0 grant types encode different authorization models:

**Authorization Code**: User delegates access to a client application. The user's presence is required, and the user can consent or deny access. This models delegation scenarios: "Allow App X to access my data."

**Client Credentials**: Machine-to-machine authorization. No user involvement. The client is the resource owner. Models service accounts and daemon processes.

**Resource Owner Password Credentials** (deprecated in OAuth 2.1): User provides credentials directly to the client. No delegation layer. Used for first-party apps where the user trusts the client completely. Deprecated due to security concerns (phishing risk, credential exposure).

**Device Authorization (RFC 8628)**: User authorizes on a separate device (e.g., authorizing a smart TV from a phone). Models constrained-input devices.

**Token Exchange (RFC 8693)**: Exchanges one token type for another (e.g., OAuth2 token for SAML assertion, or user token for delegated service token). Models delegation chains in microservices architectures.

OpenAM OAuth2 module (`OpenAM/openam-oauth2/src/main/java/org/forgerock/oauth2/core/`) implements all grant types via `GrantTypeHandler` SPI:

- `AuthorizationCodeGrantTypeHandler`
- `ClientCredentialsGrantTypeHandler`
- `ResourceOwnerPasswordCredentialsGrantTypeHandler`
- `RefreshTokenGrantTypeHandler`
- `DeviceCodeGrantTypeHandler`
- `JwtBearerGrantTypeHandler` (JWT Bearer, RFC 7523)
- `TokenExchangeGrantTypeHandler` (RFC 8693)

Each handler validates request parameters, authenticates the client, and issues tokens with appropriate scopes.

### OAuth 2.0 Limitations for Fine-Grained Authorization

OAuth 2.0 scopes provide coarse-grained authorization. Scopes answer "can this client access this API category?" but not "can this user edit document ID 12345?" Fine-grained resource authorization requires additional mechanisms:

**1. Resource identifiers in scopes**: Encoding resource IDs in scope names (`files:read:12345`) leads to scope explosion and token bloat. Not practical for large resource sets.

**2. Token introspection with context**: Resource server calls introspection endpoint with resource context, and the authorization server returns a decision based on backend policies. Adds network latency.

**3. Separate authorization service**: Resource server calls an external policy engine (XACML, OPA, Cedar) after OAuth2 authentication. OAuth2 handles authentication; separate service handles fine-grained authorization.

**4. Rich Authorization Requests (RAR, RFC 9396)**: Extends OAuth 2.0 with `authorization_details` parameter allowing structured authorization requests beyond simple scope strings. Clients can request specific resources, actions, and constraints. RAR is gaining adoption for banking (Open Banking), financial APIs, and complex resource delegation scenarios.

Example RAR authorization request:

```json
{
  "authorization_details": [
    {
      "type": "payment_initiation",
      "actions": ["initiate", "status", "cancel"],
      "locations": ["https://bank.example.com"],
      "instructedAmount": {
        "currency": "EUR",
        "amount": "123.50"
      },
      "creditorName": "Merchant A",
      "creditorAccount": {
        "iban": "DE02100100109307118603"
      }
    }
  ]
}
```

The authorization server can evaluate fine-grained policies against these structured requests and issue tokens with the granted authorization details embedded.

### Current Relevance

OAuth 2.0 scopes remain the dominant authorization mechanism for API access control. Every major identity provider (Okta, Auth0, Entra ID, Keycloak, OpenAM) supports scope-based authorization. The pattern is well-understood, tooling is mature, and developer adoption is universal.

Scopes work well for coarse-grained API authorization. For fine-grained resource access control, scopes are supplemented with policy engines or embedded authorization logic. RAR (RFC 9396) extends scopes for structured authorization in specialized domains.

## UMA 2.0: User-Managed Access

User-Managed Access (UMA) 2.0, published by the Kantara Initiative in January 2018, standardizes user-controlled authorization for resource sharing. UMA addresses scenarios where a resource owner wants to grant access to their resources held at a service provider to third-party requestors, with fine-grained policies enforced by an authorization server.

### Problem Statement

Traditional OAuth 2.0 assumes the resource owner is present during the authorization flow to consent to access. UMA 2.0 decouples resource owner consent from access requests, enabling asynchronous authorization scenarios:

- Alice stores documents at a file service. Bob requests access to a specific document. Alice is offline. The authorization server applies Alice's pre-configured policy to grant or deny Bob's access without requiring Alice's presence.
- A patient (resource owner) shares medical records (resource) with a researcher (requesting party) subject to IRB approval policies. The authorization decision is made by the authorization server based on policies, not real-time user consent.

UMA 2.0 extends OAuth 2.0 with a permission ticket mechanism and claims gathering flow to support policy-based, user-managed authorization.

### UMA Architecture and Token Flow

UMA 2.0 defines four primary roles:

**Resource Owner (RO)**: The user who controls access policies for their resources.

**Authorization Server (AS)**: Manages policies, evaluates access requests, issues tokens. Implements UMA 2.0 endpoints.

**Resource Server (RS)**: Hosts protected resources. Registers resources at the AS. Enforces access by requiring valid Requesting Party Tokens (RPTs).

**Client / Requesting Party**: The party requesting access to resources on behalf of a user (requesting party).

Two token types:

**Protection API Token (PAT)**: OAuth 2.0 access token issued to the resource server, authorizing it to register resources and manage policies at the authorization server. Long-lived.

**Requesting Party Token (RPT)**: OAuth 2.0 access token issued to the client, proving the requesting party has been granted access to specific resources. Short-lived, scoped to specific resources.

UMA 2.0 authorization flow:

```
1. Resource Owner registers resources at Authorization Server
   - RS uses PAT to POST /resource_set (resource metadata: URI, scopes, name)
   - AS returns resource ID

2. Resource Owner defines authorization policies at AS
   - Policies specify: subject (user, group), resource, scopes, conditions
   - Example: "Allow users in group 'researchers' to read resource X if authenticated"

3. Requesting Party (via Client) attempts to access resource at RS
   - Client: GET /files/123 HTTP/1.1
   - RS: No RPT provided -> deny access

4. RS requests permission ticket from AS
   - RS POSTs to AS /permission endpoint with resource ID and required scopes
   - AS returns permission ticket (opaque string)

5. RS returns 401 with UMA ticket
   - HTTP/1.1 401 Unauthorized
   - WWW-Authenticate: UMA realm="api",
                        as_uri="https://as.example.com",
                        ticket="eyJhbGci..."

6. Client requests RPT from AS
   - POST /token with grant_type=urn:ietf:params:oauth:grant-type:uma-ticket
   - Include permission ticket and any claims about the requesting party

7. AS evaluates policies against requesting party claims
   - If policies satisfied: AS issues RPT
   - If additional claims needed: AS returns need_info error with claim redirect

8. [Optional] Claims gathering flow
   - Client redirects user to AS to collect additional claims
   - User authenticates, provides additional attributes
   - AS returns updated ticket

9. Client retries RPT request with updated ticket
   - AS evaluates policies with new claims
   - AS issues RPT if authorized

10. Client accesses resource with RPT
    - GET /files/123
    - Authorization: Bearer <RPT>
    - RS validates RPT (introspection or JWT validation)
    - RS checks RPT permissions match resource and scope
    - RS returns resource if authorized
```

### Permission Tickets

Permission tickets are opaque strings representing a pending authorization request. The ticket encodes:

- Resource ID(s) being requested
- Scopes required for each resource
- Timestamp and expiration
- Any pre-collected claims about the requesting party

The ticket acts as a correlation identifier between the resource server's access denial and the client's RPT request to the authorization server.

### Claims Gathering and Interactive Flow

If the authorization server cannot immediately grant access based on provided claims, it returns a `need_info` error with a redirect URI:

```json
{
  "error": "need_info",
  "error_description": "Additional authentication required",
  "ticket": "new_ticket_value",
  "redirect_user": true,
  "redirect_uri": "https://as.example.com/claims?ticket=new_ticket_value"
}
```

The client redirects the requesting party's user agent to the claims gathering URI. The user authenticates to the AS, provides additional information (e.g., purpose of access, organizational affiliation), and the AS updates the permission ticket. The client then retries the RPT request with the enriched ticket.

This interactive claims gathering flow enables complex authorization scenarios:

- Step-up authentication (require stronger auth method)
- Purpose-of-use declarations (user states why they need access)
- Terms of service acceptance (user agrees to data usage policies)
- Multi-factor authentication challenges

### OpenAM UMA 2.0 Implementation

OpenAM implements UMA 2.0 in the `OpenAM/openam-uma/` module with supporting classes in `OpenAM/openam-oauth2/`.

**Core classes** (`OpenAM/openam-uma/src/main/java/org/forgerock/openam/uma/`):

- `UmaGuiceModule`: Dependency injection configuration for UMA services
- `UmaServiceEndpointApplication`: JAX-RS application exposing UMA endpoints
- `IdTokenClaimGatherer`: Collects identity claims for policy evaluation
- `UmaLabelsStore`: Manages resource set labels and metadata

**Endpoints** (`OpenAM/openam-uma/`):

- `/oauth2/resource_set`: Resource registration (RS uses PAT)
- `/oauth2/permission`: Permission ticket issuance
- `/oauth2/token`: RPT issuance (grant_type=urn:ietf:params:oauth:grant-type:uma-ticket)
- `/oauth2/introspect`: RPT introspection (RFC 7662)

OpenAM stores UMA resources in the Core Token Service (CTS) alongside OAuth2 tokens. Resource sets are persisted as CTS tokens with type `UMA_RESOURCE_SET`. Authorization policies are managed via OpenAM's standard entitlements framework.

Policy evaluation in OpenAM UMA flow:

```
1. Client requests RPT with permission ticket
2. OpenAM extracts resource IDs and scopes from ticket
3. OpenAM loads resource set metadata from CTS
4. OpenAM queries entitlements service for policies matching resource URIs
5. Policies evaluated against requesting party claims (from OAuth2 subject)
6. If authorized: RPT issued with permissions claim
7. RPT contains JSON array of granted resources and scopes
```

Example RPT introspection response:

```json
{
  "active": true,
  "permissions": [
    {
      "resource_id": "abc-123",
      "resource_scopes": ["read", "write"],
      "exp": 1676419200
    }
  ],
  "sub": "requesting_party_user_id",
  "exp": 1676419200,
  "iat": 1676415600
}
```

### Why UMA Adoption Remained Limited

Despite standardization and technical sophistication, UMA 2.0 adoption remained niche:

**1. Complexity**: Three-party authorization flow (resource owner, requesting party, authorization server) is conceptually complex compared to two-party OAuth2. Additional round trips for permission tickets and claims gathering add latency.

**2. User experience challenges**: End users struggle with fine-grained resource policies. "Who can access what under which conditions?" is difficult to visualize and manage in UI. Most users default to simple sharing models (public, private, specific users).

**3. Chicken-and-egg adoption**: Few resource servers implement UMA, so few authorization servers invest in UMA support, so few clients implement UMA flows. Network effects favor OAuth 2.0's simpler model.

**4. OAuth 2.0 sufficiency**: Most delegation scenarios are adequately handled by OAuth 2.0 scopes with user consent. UMA's asynchronous, policy-based model solves edge cases not commonly encountered.

**5. Policy management burden**: Maintaining fine-grained authorization policies per resource is labor-intensive. Users lack incentive to configure policies unless required by compliance or high-value resources.

**6. Limited vendor investment**: Only a few IdPs implemented UMA (ForgeRock/OpenAM, Gluu, WSO2, Keycloak). Major cloud providers (AWS, Azure, Google) did not adopt UMA, signaling lack of market demand.

### UMA Niche Use Cases

UMA found adoption in specific verticals:

**Healthcare**: Patient-controlled health record sharing. Health Relationship Trust (HEART) working group at Kantara profiles UMA for FHIR resource authorization. Patients define policies for researchers, providers, family members accessing EHR data.

**Financial services**: Limited use in Open Banking for account data sharing. However, most Open Banking implementations use simpler OAuth 2.0 patterns with dynamic consent rather than full UMA.

**Personal data stores**: MyData, Solid project concepts align with UMA's vision of user-controlled data sharing. Individuals maintain personal data pods and use UMA-like mechanisms to authorize third-party access.

### Current Relevance

UMA 2.0 is an active Kantara specification but adoption remains niche. The broader concept of user-managed consent is being addressed by regulation (GDPR consent management, CCPA opt-out mechanisms) rather than a unified protocol. OAuth 2.0 with RAR (RFC 9396) addresses some UMA use cases with less complexity.

OpenAM's UMA implementation provides standards compliance for organizations with UMA integration requirements, particularly in healthcare and regulated industries. For most use cases, OAuth 2.0 scopes with user consent screens suffice.

## Policy Agents and Legacy Authorization

Before OAuth 2.0 and modern API gateways, OpenAM used policy agents for authorization enforcement. Policy agents are plugins installed on web servers (Apache HTTP, IIS, Nginx) or application servers (Tomcat, JBoss) that intercept requests and enforce OpenAM policies.

### Policy Agent Architecture

Policy agents operate as reverse proxies or inline filters:

**Web Agent**: Module installed in web server process (e.g., Apache `mod_auth_agent`, IIS ISAPI filter). Intercepts HTTP requests before they reach the backend application. Validates session cookies, enforces URL-based policies, injects user identity headers.

**J2EE Agent**: Java servlet filter installed in application server. Integrates with servlet container authentication (JAAS). Protects servlets and JSPs based on URL patterns.

**Agent flow**:

```
1. User accesses protected URL: http://app.example.com/admin/config
2. Web/J2EE agent intercepts request
3. Agent checks for OpenAM session cookie (iPlanetDirectoryPro)
4. If no session: redirect to OpenAM login page
5. User authenticates at OpenAM
6. OpenAM issues session cookie, redirects back to original URL
7. Agent validates session with OpenAM (session validation REST call)
8. Agent requests policy decision from OpenAM:
   - Subject: user ID from session
   - Resource: /admin/config
   - Action: GET
9. OpenAM evaluates policies, returns decision (allow/deny)
10. If allowed: agent forwards request to application, injecting headers:
    - X-Forwarded-User: alice
    - X-Forwarded-Groups: admin, engineering
11. If denied: agent returns 403 Forbidden
```

Policy agents cache session validation results and policy decisions locally to reduce OpenAM round trips. Cache TTL is configurable (default 3 minutes). Agents also support cookie domain-wide SSO: a session created at app1.example.com is valid at app2.example.com without re-authentication.

### Limitations and Evolution

Policy agents have several limitations in modern cloud-native environments:

**1. Monolithic coupling**: Agents tightly couple authorization logic to web/app servers. Upgrading agents requires restarting servers. Agent bugs can crash the entire web server.

**2. Language/platform lock-in**: Separate agent implementations for each web server and language (C module for Apache, C# for IIS, Java for J2EE). Maintaining agent compatibility across server versions is burdensome.

**3. No API-first support**: Agents designed for browser-based web apps with session cookies. REST APIs with Bearer tokens require different enforcement patterns.

**4. Scalability bottlenecks**: Session validation and policy evaluation require network calls to OpenAM. High-traffic applications experience latency and OpenAM load.

**5. Limited cloud-native support**: Agents not designed for containers, sidecars, or service mesh architectures. Difficult to deploy in Kubernetes without baking agents into container images.

Policy agents have been superseded by API gateways (OpenIG, Kong, Apigee, Ambassador) and service meshes (Istio, Linkerd) that provide authorization enforcement without per-server plugins. Modern architectures use:

- **API gateway**: Centralized enforcement point at network edge. OAuth2 token validation, rate limiting, policy enforcement. Examples: OpenIG, Kong, AWS API Gateway.
- **Service mesh**: Sidecar proxies (Envoy) enforce authorization between microservices. mTLS for service-to-service auth, policy evaluation via OPA or external authz service.
- **Application-level**: Authorization logic embedded in application code. Libraries validate JWTs, check scopes, call policy engines. Reduces network hops but distributes policy logic.

OpenAM policy agents remain supported for legacy deployments but new projects should use API gateway or service mesh patterns.

### OpenIG as Policy Enforcement Gateway

OpenIG (OpenAM Identity Gateway) provides a policy enforcement gateway alternative to agents. OpenIG is a standalone Java application that acts as a reverse proxy with filter/handler pipeline architecture (detailed in component architecture chapter).

OpenIG integrates with OpenAM for authorization:

**Filter configuration** (`config/routes/protected-app.json`):

```json
{
  "name": "ProtectedApp",
  "baseURI": "http://backend-app:8080",
  "condition": "${request.uri.path == '/app'}",
  "filters": [
    {
      "type": "OAuth2ResourceServerFilter",
      "config": {
        "tokenIntrospectionEndpoint": "https://openam.example.com/oauth2/introspect",
        "requireHttps": false,
        "realm": "api",
        "scopes": ["read"]
      }
    },
    {
      "type": "OpenAmAuthenticationFilter",
      "config": {
        "openamUrl": "https://openam.example.com/openam",
        "realm": "/",
        "ssoTokenHeader": "iPlanetDirectoryPro"
      }
    },
    {
      "type": "PolicyEnforcementFilter",
      "config": {
        "openamUrl": "https://openam.example.com/openam",
        "pepUsername": "policy-agent",
        "pepPassword": "password123",
        "application": "iPlanetAMWebAgentService",
        "ssoTokenHeader": "iPlanetDirectoryPro"
      }
    }
  ],
  "handler": "ClientHandler"
}
```

OpenIG's PolicyEnforcementFilter calls OpenAM's policy evaluation endpoint (`/json/policies?_action=evaluate`) with subject, resource, and action. OpenAM returns the policy decision and OpenIG enforces it by allowing or denying the request. This decouples policy enforcement from backend applications while leveraging OpenAM's policy engine.

OpenIG is more flexible than agents (no per-server plugins, hot-reloadable configuration, expression language for custom logic) but adds an extra network hop. Modern deployments prefer lightweight API gateways (Kong, Traefik) or service mesh with embedded policy engines.

## Modern Authorization Alternatives

The limitations of XACML and policy agents have driven development of cloud-native authorization solutions. These alternatives prioritize developer experience, performance, and cloud-native deployment patterns.

### Open Policy Agent (OPA) and Rego

OPA (CNCF graduated 2021, 10k+ GitHub stars) is a general-purpose policy engine. Policies are written in Rego, a declarative query language. OPA is embedded as a library or run as a sidecar, eliminating external PDP network calls.

**Architecture**: Application code calls OPA's REST API with input data. OPA evaluates Rego policies and returns a decision. All policy evaluation happens in-process or localhost, providing microsecond latency.

**Example Rego policy**:

```rego
package authz

default allow = false

allow {
    input.method == "GET"
    input.path[0] == "files"
    input.user.role == "reader"
}

allow {
    input.method == "POST"
    input.path[0] == "files"
    input.user.role == "writer"
}

allow {
    input.user.role == "admin"
}
```

**Application integration**:

```java
// Construct input document
Map<String, Object> input = Map.of(
    "method", "GET",
    "path", List.of("files", "123"),
    "user", Map.of("id", "alice", "role", "reader")
);

// Query OPA
String opaUrl = "http://localhost:8181/v1/data/authz/allow";
HttpResponse response = httpClient.post(opaUrl, json(Map.of("input", input)));
boolean allowed = response.json().path("result").booleanValue();
```

**Advantages over XACML**:

- **Embeddable**: No external PDP; OPA runs in same process or sidecar
- **Fast**: Nanosecond to microsecond evaluation; no network calls
- **Developer-friendly**: Rego is declarative but less verbose than XML; JSON input/output
- **Cloud-native**: Kubernetes-native (Gatekeeper), Envoy integration, sidecar pattern
- **Ecosystem**: CNCF backing, active community, mature tooling (IDE plugins, testing, REPL)

**Kubernetes integration (Gatekeeper)**: OPA is deployed as a Kubernetes admission controller. Cluster administrators define constraint templates (Rego policies for Kubernetes objects). Gatekeeper validates admission requests against policies, rejecting non-compliant resources.

Example constraint: "All containers must specify resource limits."

**Use cases**: Kubernetes admission control, microservice authorization, infrastructure policy (Terraform, Docker), data filtering (SQL authorization).

### Cedar (AWS)

Cedar (open-sourced May 2023, Apache 2.0, 4k+ GitHub stars) is Amazon's purpose-built authorization policy language. Cedar powers Amazon Verified Permissions (AVP) and AWS IAM Identity Center.

**Design philosophy**: Authorization-specific (not general-purpose). Formally verified for correctness. Analyzable policies (detect conflicts, prove properties).

**Policy syntax**:

```cedar
// Permit managers in the engineering group to read project files
permit (
    principal in Group::"engineering",
    action == Action::"read",
    resource in Folder::"projects"
) when {
    principal.role == "manager"
};

// Deny access outside business hours
forbid (
    principal,
    action,
    resource
) when {
    context.currentTime < Time("09:00:00") ||
    context.currentTime > Time("17:00:00")
};
```

**Entity model**: Cedar defines a hierarchical entity model. Entities have types (User, Group, File, Folder) and parent relationships. Policies reference entities and entity hierarchies.

**Static analysis**: Cedar policies can be validated against a schema before deployment. The analyzer detects:

- Conflicting permit/forbid policies
- Unreachable policies (dead code)
- Type errors (referencing non-existent entity attributes)
- Overly broad or overly narrow policies

**Formal verification**: Cedar has a machine-checked proof of soundness in Lean 4. Authorization decisions are mathematically proven to match policy semantics. This level of rigor is unique in the authorization space and critical for high-stakes applications (banking, healthcare).

**Amazon Verified Permissions (AVP)**: Managed service wrapping Cedar. Applications call AVP APIs to evaluate authorization requests. AVP stores policies and entity data. Offers centralized policy management with Cedar's formal guarantees.

**Comparison with OPA**:

| Dimension | OPA/Rego | Cedar |
|-----------|----------|-------|
| Scope | General-purpose policy | Authorization-specific |
| Language | Rego (declarative Datalog) | Cedar (authorization DSL) |
| Verification | Limited static analysis | Formal proof of soundness |
| Entity model | User-defined | Built-in hierarchical |
| Deployment | Embedded or sidecar | AVP (SaaS) or embedded |
| Maturity | Mature (CNCF graduated) | Young (2023), AWS backing |
| Adoption | Kubernetes, cloud-native | AWS-centric, growing |

Cedar is newer but has strong momentum. For AWS-native applications, Cedar+AVP provides seamless integration. For cross-cloud or Kubernetes-native, OPA has broader ecosystem support.

### Zanzibar-Inspired Systems

Google's Zanzibar paper (USENIX ATC 2019) described Google's internal authorization system handling trillions of authorization checks per day with millisecond latency. Zanzibar uses relationship-based access control (ReBAC): authorization is determined by relationships in a graph.

**Zanzibar data model**: Relation tuples encoding subject-relation-object triples.

Example tuples:

```
user:alice#member@group:engineering
user:bob#member@group:engineering
group:engineering#viewer@doc:123
user:alice#owner@doc:456
doc:123#parent@folder:projects
folder:projects#viewer@group:sales
```

**Authorization query**: "Can user:alice view doc:123?"

**Evaluation**: Check if there exists a path from `user:alice` to `doc:123` via any of:
1. Direct `viewer` relation
2. Membership in a group with `viewer` relation
3. Parent folder with inherited permissions

Zanzibar's query engine traverses the relationship graph and evaluates transitive closures efficiently.

**Open-source implementations**:

**OpenFGA** (Okta/Auth0, CNCF sandbox, ~3k stars): Go-based ReBAC engine. Zanzibar-style relation tuples, REST API, fine-grained authorization.

Example OpenFGA authorization model:

```
type user

type group
  relations
    define member: [user]

type document
  relations
    define parent: [folder]
    define owner: [user]
    define viewer: [user, group#member] or owner or parent.viewer
```

**SpiceDB** (Authzed, ~5k stars): High-performance ReBAC engine with global consistency. Provides consistency models (fully consistent, minimally stale, prefer cache) and distributed deployment.

**Ory Keto** (Ory, ~4.9k stars): Part of Ory stack. Zanzibar-style relation tuples, Check/Expand/List APIs, Kubernetes-native.

**Use cases for ReBAC**:

- Multi-tenant SaaS applications with complex sharing (Google Workspace model)
- Hierarchical resource structures (folders, projects, organizations)
- Fine-grained resource-level authorization (who can edit document X?)
- Dynamic group membership and role hierarchies

ReBAC complements OAuth 2.0 and OIDC: OAuth handles authentication and coarse-grained API authorization; ReBAC handles fine-grained resource authorization.

### Casbin

Casbin (Go, ~18k stars, 15+ language ports) is a lightweight authorization library supporting multiple access control models: ACL, RBAC, ABAC, RESTful. Casbin is embedded in applications (not a service).

**Policy syntax (CONF format)**:

```ini
[request_definition]
r = sub, obj, act

[policy_definition]
p = sub, obj, act

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = r.sub == p.sub && r.obj == p.obj && r.act == p.act
```

**Policy file (CSV)**:

```csv
p, alice, /files/123, read
p, bob, /files/*, write
p, admin, /*, *
```

**Application integration**:

```go
enforcer, _ := casbin.NewEnforcer("model.conf", "policy.csv")

allowed, _ := enforcer.Enforce("alice", "/files/123", "read")
if allowed {
    // grant access
}
```

Casbin is lightweight (no external dependencies) and flexible (supports many models). However, it lacks built-in distributed caching, centralized policy management, and real-time policy updates. Best suited for applications with embedded, static policies.

### Comparison and Recommendations

| Use Case | Recommended Solution | Rationale |
|----------|---------------------|-----------|
| Kubernetes admission control | OPA/Gatekeeper | CNCF standard, mature ecosystem |
| AWS application authz | Cedar + AVP | Native AWS integration, formal verification |
| Fine-grained resource sharing | OpenFGA, SpiceDB | ReBAC model fits hierarchical resources |
| Microservice authz | OPA (sidecar) | Low latency, embeddable, Envoy integration |
| API gateway authz | OPA, Cedar, or custom | Depends on cloud provider and policy complexity |
| Embedded app authz | Casbin, Cedar | Lightweight, no external service required |
| Legacy enterprise | XACML (if existing) | Maintain existing deployments; avoid new |

OAuth 2.0 scopes remain the baseline for API authorization. Fine-grained authorization supplements OAuth with OPA, Cedar, or ReBAC engines.

OpenAM's XACML implementation provides standards compliance but modern alternatives offer better developer experience, performance, and cloud-native integration. Organizations with existing OpenAM deployments can migrate policy logic to OPA/Cedar over time while maintaining XACML export for compliance documentation.

## Summary

Authorization frameworks have evolved from centralized, XML-heavy policy engines (XACML) to cloud-native, developer-friendly alternatives (OPA, Cedar, ReBAC). OAuth 2.0 scopes provide coarse-grained API authorization, supplemented by fine-grained policy engines for resource-level decisions. UMA 2.0 addressed niche asynchronous authorization scenarios but failed to achieve broad adoption. Policy agents, once the standard for web application authorization, have been superseded by API gateways and service meshes.

Modern best practice: OAuth 2.0/OIDC for authentication and API authorization, OPA or Cedar for policy-based fine-grained authorization, and ReBAC systems (OpenFGA, SpiceDB) for complex resource sharing scenarios. XACML remains relevant for regulatory compliance in legacy enterprises but is not recommended for greenfield projects.

References: OpenAM source code at `/Users/kirane/projects/idp/OpenAM/openam-entitlements/`, `/Users/kirane/projects/idp/OpenAM/openam-oauth2/`, `/Users/kirane/projects/idp/OpenAM/openam-uma/`. XACML 3.0 (OASIS), OAuth 2.0 RFCs (6749, 6750, 7662, 9396), UMA 2.0 (Kantara), Zanzibar paper (Google, 2019).
