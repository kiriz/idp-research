# Chapter 10: OpenIG Analysis

OpenIG (Open Identity Gateway) is the policy enforcement and credential mediation layer in the Open Identity Platform suite. It sits between clients and backend applications as a reverse proxy, intercepting HTTP traffic and applying authentication, authorization, header manipulation, and credential replay through a composable filter/handler pipeline. Its architectural signature -- declarative JSON route configuration, an Expression Language for dynamic behavior, and a Promise-based asynchronous execution model -- positions it as a programmable identity gateway rather than a general-purpose reverse proxy. This chapter examines OpenIG's architecture, evaluates its strengths and weaknesses against modern alternatives, and traces the broader evolution from policy agents to service mesh sidecars.

---

## 1. What OpenIG Does

OpenIG serves three primary functions within the OIP integration architecture described in [Chapter 12: Modern Architecture Patterns](12-modern-architecture.md):

**Policy Enforcement Gateway.** OpenIG intercepts HTTP requests destined for protected applications and delegates authentication and authorization decisions to OpenAM. It validates SSO tokens, enforces access policies, and blocks unauthorized requests before they reach the backend. This decouples security enforcement from application code -- applications need not implement any authentication logic themselves.

**Credential Replay Proxy.** OpenIG's most distinctive capability is credential replay: the ability to authenticate users via modern protocols (OAuth 2.0, SAML 2.0, OIDC) and then inject legacy credentials (HTTP Basic, form POST, custom headers) into upstream requests. This bridges the gap between modern identity providers and legacy applications that cannot be modified to support contemporary authentication standards.

**Identity-Aware Reverse Proxy.** Beyond authentication, OpenIG transforms requests and responses as they transit the pipeline. It can add, remove, or rewrite HTTP headers; query databases for user attributes; enforce rate limits; perform CSRF validation; and route requests conditionally based on any combination of request properties, session state, and external data. The gateway pattern described in the OIP architecture diagram (`Users/Apps --> OpenIG --> OpenAM --> OpenDJ`) positions OpenIG as the single entry point through which all external traffic flows.

Within the five-component OIP stack, OpenIG has the smallest codebase (~12 modules) but occupies a critical position in the request path. Every request to a protected resource passes through its filter chain.

---

## 2. Architecture Overview

### 2.1 Filter/Handler Pipeline

The core abstraction in OpenIG is a pipeline composed of **Filters** and **Handlers**. The architecture uses the Decorator pattern combined with Promise-based asynchronous execution.

The two fundamental interfaces, located in `OpenIG/openig-core/src/main/java/`, define the contract:

```java
// Filter: intercepts request, delegates to next handler
public interface Filter {
    Promise<Response, NeverThrowsException> filter(
        Context context, Request request, Handler next);
}

// Handler: terminal endpoint of pipeline, produces response
public interface Handler {
    Promise<Response, NeverThrowsException> handle(
        Context context, Request request);
}
```

Execution flows through filters sequentially. Each filter performs pre-processing on the request, delegates to the next handler in the chain via `next.handle(...)`, and optionally performs post-processing on the response via `thenOnResult()`. The final handler in the chain -- typically a `ClientHandler` -- forwards the request to the upstream backend application.

```
HTTP Request
  |
  Filter 1 (pre-process) --> next.handle() --> Filter 1 (post-process)
    |
    Filter 2 (pre-process) --> next.handle() --> Filter 2 (post-process)
      |
      ...
        |
        ClientHandler --> HTTP Backend
                       <-- HTTP Response
```

The Promise-based return type (`Promise<Response, NeverThrowsException>`) enables non-blocking, asynchronous request processing. Filters compose via `thenAsync()`, `thenOnResult()`, and `thenOnException()` -- a monadic chaining pattern that avoids blocking threads while requests are in flight. A thread pool handles concurrent requests, and backpressure is implicit in the Promise chain: if the backend is slow, the response Promise simply takes longer to resolve.

The **Context** object provides a parent-child hierarchy for nested calls and an attributes map for inter-filter communication. Filters read and write to `context.asContext(AttributesContext.class)` to pass data downstream -- for example, a token validation filter might set `attributes['userId']` for a subsequent header injection filter to consume.

### 2.2 Route Configuration (JSON)

Routes are defined as JSON files in the `config/routes/` directory of the OpenIG deployment. Each route declares a condition (when the route applies), a sequence of filters, and a terminal handler. Routes are **hot-reloadable**: modifying a route file takes effect without restart or downtime.

A representative route:

```json
{
  "name": "protected-api",
  "baseURI": "http://backend-server:8080",
  "condition": "${request.uri.path =~ '/api/.*'}",
  "filters": [
    {
      "type": "OAuth2ResourceServerFilter",
      "config": {
        "providerHandler": { "type": "ClientHandler" },
        "scopes": ["read", "write"],
        "realm": "example"
      }
    },
    {
      "type": "AddHeaderFilter",
      "config": {
        "headers": {
          "X-Authenticated-User": "${attributes.openid.sub}"
        }
      }
    }
  ],
  "handler": { "type": "ClientHandler" }
}
```

Route matching follows a **first-match-wins** strategy. Routes are processed in filename alphabetical order. A catch-all route (no condition) typically appears last as a default handler. This declarative configuration model means that non-developers -- security engineers or operations staff -- can define and modify gateway policies without writing Java code.

### 2.3 Expression Language

The Expression Language (EL) embedded in route configurations provides dynamic access to request state:

- Request properties: `${request.headers['Authorization']}`, `${request.uri.path}`, `${request.method}`
- Context attributes: `${attributes.userId}`, `${session.user.id}`
- Functions: `${request.headers['name'][0].toLowerCase()}`
- Conditionals: `${request.method == 'POST' ? 'write' : 'read'}`
- Null coalescing: `${request.headers['X-Custom'] ?: 'default'}`
- Regex matching: `${request.uri.path =~ '/admin/.*'}`

The EL is evaluated at runtime for each request, enabling routes to make dynamic decisions without custom code. It is Turing-incomplete by design -- complex logic that exceeds EL capabilities can be delegated to `ScriptableFilter` (Groovy or JavaScript).

### 2.4 Filter Inventory (50+ Types)

OpenIG ships with a rich catalog of built-in filters organized by function:

**Authentication Filters (5+):**
`HttpBasicAuthFilter`, `OAuth2ResourceServerFilter`, `SamlFederationFilter`, `OpenAmAuthenticationFilter`, `WindowsAuthenticationFilter`

**Credential Replay Filters (2):**
`CredentialReplayFilter`, `CredentialInjectFilter`

**Header and Cookie Manipulation (4+):**
`AddHeaderFilter`, `RemoveHeaderFilter`, `ReplaceHeaderFilter`, `CookieFilter`

**Security Filters (2+):**
`CsrfTokenFilter`, `RateLimitFilter`

**Routing Filters (3+):**
`SwitchFilter`, `RouterHandler` (trie-based), `SequenceHandler`

**Observability (3+):**
`CaptureFilter`, `MetricsFilter`, `LogAttachedExceptionFilter`

**Performance (2+):**
`ThrottlingFilter`, `RateLimitFilter`

**Data Integration (2+):**
`SqlAttributesFilter`, `SetAttributesFilter`

**Scripting (1):**
`ScriptableFilter` -- arbitrary Groovy or JavaScript logic without redeployment

**Response Processing (1+):**
`LocationHeaderFilter` -- rewrites backend URLs to client-visible URLs

### 2.5 Handler Inventory (16+ Types)

Handlers serve as pipeline endpoints or routing decision points:

`ClientHandler` (HTTP forwarding with connection pooling, timeouts, certificate pinning), `StaticContentHandler` (static file serving), `RouterHandler` (path-based sub-routing), `SwitchHandler` (conditional routing), `SequenceHandler` (sequential handler chain), `ExceptionHandler` (error transformation), `RedirectHandler` (HTTP redirects), `NotFoundHandler` (404 responses), `OpenAmHandler` (OpenAM policy delegation), `SamlFederationHandler` (SAML SSO), `OAuth2Handler` (OAuth grant flows), `UmaHandler` (User-Managed Access), `ScriptableHandler` (custom Groovy/JS logic).

### 2.6 Module Structure

The OpenIG codebase is organized into approximately 12 Maven modules:

| Module | Purpose |
|--------|---------|
| `openig-core` | Filter/handler framework, routing, EL engine, scripting |
| `openig-oauth2` | OAuth 2.0 resource server and client filters |
| `openig-saml` | SAML 2.0 federation filters and handlers |
| `openig-uma` | User-Managed Access 2.0 integration |
| `openig-openam` | OpenAM-specific policy agent, session validation |
| `openig-war` | WAR packaging for servlet container deployment |
| `openig-doc` | Documentation and examples |

The commercial equivalent of OpenIG is now **PingGateway**, part of the Ping Identity product suite following the Ping-ForgeRock merger in 2023 (see [Chapter 1: Historical Narrative](01-history.md)).

---

## 3. Strengths

**Flexible, composable pipeline.** The filter/handler model is genuinely elegant. Any combination of authentication, transformation, routing, and security filters can be composed declaratively without writing code. The Promise-based async model avoids thread-per-request scaling bottlenecks. This architecture is well-suited to organizations that need to define many distinct access policies for different backend applications.

**Credential replay for legacy applications.** This is OpenIG's most compelling differentiator. Many enterprises operate legacy applications (mainframes, packaged COTS software, older internal tools) that support only HTTP Basic, form-based login, or proprietary header-based authentication. OpenIG can authenticate users via OIDC or SAML at the gateway, then inject the appropriate legacy credentials into upstream requests. This avoids costly application rewrites. No modern API gateway provides this capability natively.

**Declarative JSON configuration.** Route definitions are human-readable JSON files, not code. Operations teams can modify gateway policies without Java expertise. Routes are stored as flat files, amenable to version control, code review, and GitOps workflows.

**Hot-reload without downtime.** Route file changes take effect immediately. In environments with many protected applications, this enables rapid policy iteration without the restart cycles typical of WAR-deployed Java applications.

**Scriptable extensibility.** When built-in filters are insufficient, `ScriptableFilter` and `ScriptableHandler` allow inline Groovy or JavaScript. This provides an escape hatch for custom logic without requiring a full Java development cycle, compilation, or redeployment.

**Deep OpenAM integration.** The `openig-openam` module provides first-class integration with OpenAM for session validation, policy enforcement, and token introspection. For organizations running the full OIP stack, this integration is seamless.

**Expression Language for dynamic behavior.** The EL enables conditional routing, dynamic header values, and request-dependent logic without resorting to scripting. For many common patterns (route-by-path, inject-user-header, strip-sensitive-header), EL expressions are sufficient.

---

## 4. Weaknesses

**Java overhead for a proxy role.** OpenIG is a Java application deployed as a WAR in a servlet container. For the reverse proxy use case -- which is fundamentally about forwarding HTTP requests with minimal transformation -- Java's memory footprint and startup time are disadvantages compared to purpose-built proxies written in C++ (Envoy), Go (Traefik), or Lua-on-C (Kong/Nginx). A cold-start OpenIG instance consumes hundreds of megabytes; a cold-start Envoy sidecar consumes tens of megabytes.

**Limited observability compared to modern gateways.** OpenIG provides `CaptureFilter` for debugging and `MetricsFilter` for basic instrumentation, but it lacks native integration with modern observability stacks. There is no built-in OpenTelemetry support, no distributed tracing propagation, no Prometheus metrics endpoint, and no structured logging in formats expected by Elasticsearch, Datadog, or Grafana Loki. Modern gateways (Envoy, Kong, Traefik) ship with these integrations by default.

**Niche use case.** The identity gateway concept -- a reverse proxy specifically designed for authentication mediation -- occupies a narrow space between general-purpose reverse proxies and full API gateways. Organizations evaluating gateway technology today are far more likely to encounter Kong, Envoy, or Traefik in vendor-neutral architecture discussions. OpenIG's identity-specific capabilities are valuable but not widely known outside the ForgeRock/OIP ecosystem.

**No native container orchestration support.** OpenIG predates the Kubernetes era and lacks a Helm chart, Kubernetes Operator, or native sidecar deployment model. Deploying OpenIG in Kubernetes requires manual containerization of the WAR file and custom health check configuration. Modern gateways are designed container-first.

**Small community.** OpenIG's community is a subset of the already-small OIP community. Feature requests, bug reports, and community-contributed filters are sparse compared to Kong (300+ contributors), Envoy (1,000+ contributors), or Traefik (780+ contributors).

**No native gRPC or HTTP/2 support.** Modern microservices increasingly communicate via gRPC. OpenIG's servlet-container deployment model is HTTP/1.1-centric. While HTTP/2 support depends on the underlying servlet container, gRPC proxying is not a supported use case.

**Vendor lock-in within OIP stack.** The `openig-openam` integration module creates a tight coupling to OpenAM for policy decisions. Using OpenIG with a non-OIP identity provider (Keycloak, Ory, Auth0) requires custom development via `ScriptableFilter` rather than first-class integration.

---

## 5. Modern Alternatives

### 5.1 OpenIG vs Kong

**Kong** is the most widely deployed open-source API gateway, built on Nginx with Lua plugin extensibility (Kong Gateway OSS) and a Go-based control plane (Kong Gateway Enterprise).

| Dimension | OpenIG | Kong |
|-----------|--------|------|
| Language | Java (servlet WAR) | C (Nginx core) + Lua (plugins) + Go (control plane) |
| Plugin system | Java filters + Groovy scripts | Lua plugins, Go plugins, Python plugins, JS plugins |
| Configuration | JSON route files | Declarative YAML/JSON, Admin API, DB-backed |
| Performance | Moderate (JVM overhead) | High (Nginx event loop, C-level proxying) |
| Observability | Basic (`MetricsFilter`, `CaptureFilter`) | Prometheus, OpenTelemetry, Datadog, Zipkin, StatsD |
| Auth integration | Deep OpenAM integration | OIDC plugin, JWT plugin, basic-auth, key-auth, LDAP |
| Rate limiting | `RateLimitFilter`, `ThrottlingFilter` | Advanced rate limiting (sliding window, fixed window, local/cluster) |
| Service mesh | None | Kong Mesh (Envoy-based, Kuma) |
| Kubernetes | Manual WAR containerization | Kong Ingress Controller, Helm charts, Operator |
| Community | Small (OIP ecosystem) | Large (300+ contributors, 40k+ GitHub stars) |
| Credential replay | Native (`CredentialReplayFilter`) | Not native; requires custom Lua plugin |
| License | CDDL 1.0 | Apache 2.0 (OSS), proprietary (Enterprise) |

Kong excels where OpenIG falls short: performance, observability, ecosystem breadth, and Kubernetes-native deployment. OpenIG's advantage is limited to credential replay and deep OIP stack integration.

### 5.2 OpenIG vs Envoy / Istio

**Envoy** is a high-performance L4/L7 proxy designed for service mesh deployments. **Istio** is the most widely adopted service mesh control plane, using Envoy as its data plane sidecar.

| Dimension | OpenIG | Envoy / Istio |
|-----------|--------|---------------|
| Deployment model | Centralized reverse proxy | Sidecar proxy per service (or ambient mode) |
| Protocol support | HTTP/1.1, HTTPS | HTTP/1.1, HTTP/2, gRPC, TCP, UDP, WebSocket |
| Auth integration | OpenAM session validation, OAuth2, SAML | External AuthZ (OPA, custom gRPC service), JWT validation |
| mTLS | Via servlet container TLS config | Automatic mTLS between all services (Istio) |
| Observability | Basic | Built-in distributed tracing, metrics, access logs |
| Configuration | JSON route files | xDS API (dynamic), YAML (static) |
| Performance | Moderate | Very high (C++, event-driven, zero-copy) |
| Identity model | User identity (SSO tokens, headers) | Workload identity (SPIFFE SVIDs, mTLS certificates) |
| Credential replay | Native | Not applicable (different problem domain) |

Envoy and Istio operate at a different architectural layer than OpenIG. They solve the service-to-service communication problem with mTLS, workload identity, and traffic management. OpenIG solves the user-to-application authentication mediation problem. In a modern architecture, both concerns may exist simultaneously: Istio handles east-west traffic, while an API gateway (Kong, Traefik, or conceivably OpenIG) handles north-south traffic.

### 5.3 OpenIG vs AWS API Gateway

**AWS API Gateway** is a fully managed service for creating, publishing, and managing APIs at any scale.

| Dimension | OpenIG | AWS API Gateway |
|-----------|--------|-----------------|
| Deployment | Self-hosted (WAR) | Fully managed (AWS) |
| Scaling | Manual (cluster + load balancer) | Automatic (serverless) |
| Auth integration | OpenAM, OAuth2, SAML | Cognito, Lambda authorizers, IAM |
| Customization | Filters, scripts, EL | Lambda functions, VTL transforms |
| Protocol | HTTP/1.1 | HTTP, WebSocket, REST, HTTP API |
| Pricing | Infrastructure cost only | Per-request ($1-3.50 per million) |
| Vendor lock-in | OIP stack coupling | AWS ecosystem lock-in |
| Credential replay | Native | Not available |

AWS API Gateway is the pragmatic choice for AWS-native deployments. Its serverless scaling model eliminates capacity planning entirely. However, it provides no credential replay capability and ties the organization to the AWS ecosystem. OpenIG's self-hosted model avoids cloud vendor lock-in but shifts operational burden to the deploying organization.

### 5.4 OpenIG vs Traefik

**Traefik** is a Go-based edge router designed for automatic service discovery in containerized environments.

| Dimension | OpenIG | Traefik |
|-----------|--------|---------|
| Language | Java | Go |
| Discovery | Manual route configuration | Auto-discovery (Docker, K8s, Consul, etc.) |
| Configuration | JSON files | Labels, YAML, TOML, dynamic providers |
| Let's Encrypt | Manual TLS cert management | Automatic ACME certificate provisioning |
| Dashboard | None built-in | Real-time dashboard |
| Middleware | 50+ Java filters | 25+ Go middleware (chain of responsibility) |
| Kubernetes | Manual | Native Ingress Controller, CRDs, Helm |
| Auth | Deep OpenAM integration | ForwardAuth, BasicAuth, DigestAuth |
| Community | Small | Large (780+ contributors, 52k+ GitHub stars) |
| Credential replay | Native | Not native |

Traefik's auto-discovery capability -- automatically detecting new services in Docker or Kubernetes and configuring routes -- is a paradigm OpenIG does not address. For dynamic, containerized environments, Traefik requires less manual configuration. For static environments with legacy applications requiring credential replay, OpenIG remains relevant.

### 5.5 OpenIG vs APISIX

**Apache APISIX** is a high-performance, cloud-native API gateway built on Nginx and Lua (etcd-backed).

| Dimension | OpenIG | APISIX |
|-----------|--------|--------|
| Language | Java | C (Nginx) + Lua |
| Performance | Moderate | Very high (Nginx event loop) |
| Configuration | JSON files | etcd-backed, Admin API, declarative YAML |
| Plugins | 50+ filters | 80+ plugins (auth, observability, traffic, serverless) |
| Service discovery | None | Consul, Nacos, Eureka, DNS, Kubernetes |
| Observability | Basic | Prometheus, Grafana, SkyWalking, Zipkin |
| Auth plugins | OpenAM, OAuth2, SAML | OIDC, JWT, key-auth, basic-auth, LDAP, wolf-rbac |
| gRPC | Not supported | Native gRPC proxying and transcoding |
| Community | Small | Active (Apache Top-Level Project, 600+ contributors) |

APISIX offers comparable plugin breadth to Kong with Apache Foundation governance and no dual-licensing concerns. Like all general-purpose API gateways, it lacks credential replay.

---

## 6. The Gateway Evolution

The architectural role that OpenIG fills has evolved through four distinct generations:

### Generation 1: Policy Agents (2000-2010)

Sun Access Manager and early ForgeRock deployments used **policy agents** -- lightweight native modules (C or Java) embedded directly in web servers (Apache httpd, IIS) or application servers (WebLogic, WebSphere, Tomcat). The agent intercepted requests at the container level, checked session cookies against the centralized policy decision point (OpenAM/OpenSSO), and enforced access decisions.

Agents were fast (in-process, no network hop for request interception) but operationally burdensome: they required installation on every web server, version compatibility with specific web server releases, and coordinated upgrades across the fleet. A single agent bug could destabilize the hosting web server.

### Generation 2: Reverse Proxy Gateways (2010-2018)

OpenIG represents this generation. Instead of embedding agents in every web server, a dedicated reverse proxy sits in front of all protected applications. The proxy centralizes policy enforcement, eliminates per-server agent installation, and enables credential replay for legacy applications that cannot accommodate agents.

This model traded the agent's in-process performance for operational simplicity: one gateway to deploy, configure, and monitor instead of agents on every server. The tradeoff was acceptable because network latency between the gateway and backends (typically milliseconds on a LAN) was negligible compared to authentication processing time.

### Generation 3: API Gateways (2016-2022)

Kong, Traefik, AWS API Gateway, and APISIX shifted the gateway concept from identity-centric to API-centric. The gateway became the entry point for all API traffic, not just identity-related traffic. Authentication was one capability among many: rate limiting, request transformation, load balancing, circuit breaking, caching, and observability were equally important.

This generation also introduced programmatic API management: developer portals, API keys, usage analytics, monetization, and lifecycle management. Identity was a plugin, not the raison d'etre.

### Generation 4: Service Mesh Sidecars (2018-Present)

Envoy, Istio, and Linkerd moved policy enforcement from a centralized gateway to per-service sidecar proxies. Every service instance gets its own proxy, which handles mTLS, authorization, load balancing, and observability. The sidecar model provides defense in depth -- even if the outer gateway is bypassed, inter-service communication is authenticated and encrypted.

Service meshes operate primarily on workload identity (SPIFFE SVIDs, Kubernetes service accounts) rather than user identity (SSO tokens, JWTs). They solve a different problem than OpenIG: east-west inter-service security rather than north-south user authentication.

**The implication for OpenIG:** modern architectures often require both an edge gateway (for user authentication, rate limiting, and API management) and a service mesh (for inter-service mTLS and authorization). OpenIG can serve as the edge gateway, but it competes against purpose-built tools with larger communities, better performance, and deeper integrations with cloud-native infrastructure.

---

## 7. Credential Replay: OpenIG's Unique Capability

Credential replay is worth examining in detail because it is the one capability where OpenIG has no direct modern equivalent.

### The Problem

Many enterprise applications -- particularly COTS (commercial off-the-shelf) software, ERP systems, mainframe web frontends, and internally built tools from the 2000s era -- authenticate users via HTTP Basic, form-based login (POST to a login endpoint with username/password fields), or proprietary header-based authentication (e.g., `X-Forwarded-User`). These applications cannot be modified to support OIDC or SAML because:

- The vendor no longer provides updates
- The source code is unavailable
- The application's authentication module is deeply coupled to its internal architecture
- The cost of modification exceeds the application's remaining business value

### How OpenIG Solves It

OpenIG's credential replay pipeline works as follows, using the OAuth2-to-HTTP-Basic scenario as a representative example:

```
1. User presents OAuth2 bearer token to OpenIG
2. OAuth2ResourceServerFilter validates token (introspection or JWT verification)
3. Filter extracts user identity: attributes['userId'] = "john"
4. CredentialReplayFilter reads attributes['userId']
5. Filter looks up credentials from secure store (vault, database, or attribute mapping)
6. Filter adds header: Authorization: Basic base64("john:password123")
7. Request forwarded to backend with injected HTTP Basic credentials
8. Backend validates credentials (unaware of OAuth2 or OpenIG)
9. Response returns through filter chain
10. CredentialReplayFilter optionally strips auth header from response
```

Credential sources include context attributes, session state, external vaults (HashiCorp Vault, AWS Secrets Manager), and database lookups (`SqlAttributesFilter`). Supported injection schemes include HTTP Basic (`Authorization: Basic`), bearer tokens (`Authorization: Bearer`), form POST (injecting form fields into request body), and custom headers (`X-API-Key`, `X-Forwarded-User`).

### When Credential Replay Is Needed

Credential replay is a transitional technology. It is appropriate when:

- An organization is modernizing its authentication infrastructure (moving to OIDC/SAML) but cannot modify all downstream applications simultaneously
- Legacy applications have a defined end-of-life but must remain operational during the migration period
- The application is vendor-managed and the vendor does not support modern authentication standards
- The application handles low-sensitivity data where the security implications of credential replay (passwords in transit, stored credentials) are acceptable given compensating controls (TLS, vault-based secret management, audit logging)

Credential replay is not appropriate as a permanent architecture. The stored credentials create a secret management burden, the replayed credentials are vulnerable to interception if TLS is misconfigured, and the pattern masks authentication failures (the backend sees valid credentials even if the upstream token was fraudulently obtained).

### Modern Alternatives to Credential Replay

Where credential replay can be avoided, organizations have better options:

- **Header-based identity propagation**: Backend trusts a header (`X-Forwarded-User`) set by the gateway. Simpler than full credential replay but requires the backend to accept header-based identity.
- **Token exchange (RFC 8693)**: Exchange the upstream token for a downstream token that the backend understands.
- **Application modernization**: Add OIDC support to the backend via a library (if source code is available).
- **Application wrapping**: Deploy a sidecar or adapter that handles OIDC authentication and exposes a simpler auth interface to the legacy application.

---

## 8. Verdict

OpenIG is a well-designed identity gateway whose architectural elegance -- the composable filter/handler pipeline, declarative JSON configuration, and Promise-based async execution -- compares favorably to any gateway framework from a software engineering perspective. The credential replay capability addresses a real enterprise problem that no modern API gateway solves natively.

However, OpenIG faces headwinds on multiple fronts. Its Java-based deployment model is heavy for a proxy role. Its observability, Kubernetes integration, and community support lag far behind Kong, Envoy, Traefik, and APISIX. Its identity-centric positioning is a narrow niche in a market dominated by general-purpose API gateways.

**For new greenfield deployments**, there is little reason to choose OpenIG over a modern API gateway (Kong, Traefik, or APISIX) combined with standard OIDC/OAuth2 plugins. These tools offer superior performance, observability, Kubernetes integration, and community support.

**For existing OIP deployments** that rely on deep OpenAM integration and credential replay for legacy applications, OpenIG remains the most practical option. Replacing it requires either modernizing the legacy applications (eliminating the need for credential replay) or implementing custom credential replay logic in another gateway's plugin system.

**For credential replay specifically**, OpenIG has no peer. Organizations with a significant estate of legacy applications that cannot support modern authentication should evaluate OpenIG for this capability alone, potentially deploying it behind a modern API gateway that handles rate limiting, observability, and general API management.

The broader market trajectory is clear: centralized identity gateways are giving way to API gateways with identity plugins and service mesh sidecars with workload identity (see [Chapter 12: Modern Architecture Patterns](12-modern-architecture.md), Section 4). OpenIG's future relevance depends on either its community adding modern integrations (OpenTelemetry, Kubernetes Operator, gRPC support) or its users migrating to general-purpose gateways as their legacy application estates shrink.
