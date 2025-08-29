# Multi-User AI Chat Platform --- Source of Truth 

**Version:** 1.0

**Date:** 2025-08-06

**Sources:** PRD + Technical Implementation Specification

**Purpose:** Merge high-level requirements and low-level implementation
specs into a single anchor-linked master document for
retrieval-augmented development.

# {#table-of-contents} Table of Contents

1\. Goals & Context

    -   Background, product vision, and MVP scope.

2\. Functional Requirements (FR) 

    -   FR-001 --- User Account System (Email/Password, JWT Auth)
    -   FR-002 --- Create & Manage Chat Rooms
    -   FR-003 --- Join Chat Room via Shareable Link
    -   FR-004 --- Real-time Messaging
    -   FR-005 --- Explicit AI Invocation
    -   FR-006 --- Persistent Chat History
    -   FR-007 --- AI Rate Limiting

3\. Non-Functional Requirements (NFR) 

    -   NFR-001 --- UI Simplicity
    -   NFR-002 --- Modular Monolith Architecture
    -   NFR-003 --- Real-time Performance
    -   NFR-004 --- Data Reservoir Design
    -   NFR-005 --- Data Privacy & Compliance
    -   NFR-006 --- Accessibility (WCAG 2.1 AA)

4\. API Surface 

    -   Auth endpoints
    -   Room endpoints
    -   Messaging endpoints
    -   AI Invocation flow

5\. System Architecture 

    -   Client SPA layout
    -   Backend modular structure
    -   Real-time WebSocket layer
    -   Storage & ORM
    -   AI Gateway

6\. Data Models 

    -   Prisma schema (User, Room, RoomMembership, Message, AIInvocation, etc.)

7\. Acceptance Criteria & Test Mapping 

    -   High-level test coverage plan per FR/NFR.

8\. Implementation Notes 

    -   Key technical patterns
    -   Service layer boundaries
    -   Performance targets

9\. Future Epics 

    -   Monetization & tiering
    -   Education-specific features
    -   File sharing & media handling

# {#goals-context} 1. Goals & Context 

**Section ID:** GOALS-CONTEXT

**Version:** 1.0.0

**Tags:** vision, product-scope, mvp, background

**Background**

This project originated from a direct personal need:

-   There was no existing tool that allowed multiple users to collaboratively interact with an AI model in a single, shared-context session.
-   Current market offerings focus either on single-user AI chatbots or human-to-human chat apps without AI as a participant.

**Initial Concept**

-   A "shared assistant" experience for small teams, students, or friends working on projects.
-   Allows multiple human participants and the AI model to share the same conversation history and context.
-   Core idea validated in early discussions and prototypes.

**Educational Expansion**

-   Feedback from a Human-Computer Interaction (HCI) professor revealed significant potential in educational settings.
-   Long-term vision evolved into an Educational Platform that includes:
-   Teacher/student role management
-   Assignment workflows
-   Learning analytics ("Data Reservoir" concept)

**MVP Scope**

**The Minimum Viable Product (MVP) will:**

-   Deliver the Core Multi-User AI Chat experience with real-time capabilities.
-   Support persistent chat history.
-   Include basic identity & authentication.
-   Provide the technical foundation for later educational features without over-engineering at launch.

**Product Goals**

1.  Enable seamless, multi-user interaction with a single AI model in shared, persistent chat rooms.
2.  Organized workspace: allow users to manage multiple distinct rooms/projects and switch without losing context.
3.  Flexible & secure identity system with persistent user accounts and privacy guarantees.
4.  Sustainable monetization through tiered access to AI models, clear upgrade path from free to premium.

**Constraints**

-   Speed-to-market is prioritized over feature completeness.
-   All technical decisions must scale into the Educational Platform vision without major refactoring.
-   Maintain a lightweight architecture while supporting real-time collaboration.

**Acceptance Criteria**

-   MVP must allow at least 10 concurrent users to chat with AI in the same room without losing conversation context.
-   Users must be able to create rooms, invite others, and retain chat history after logout/login.
-   AI responses are explicitly invoked (no unsolicited messages).

# {#functional-requirements} 2. Functional Requirements (FR) 

### {#FR-001} FR-001 --- User Account System 

**Section ID:** FR-001\
**Version:** 1.0.0\
**Tags:** auth, accounts, security, jwt, user-management\
**Parent ID:** functional-requirements

#### {#FR-001-prd} PRD Requirement 

The system shall provide a user account system with sign-up and login capabilities.
-   Users must register with a valid email and strong password.
-   Duplicate email and username registrations must be prevented.
-   "Forgot password" flow must be available.
-   Authentication must be persistent across sessions via a secure token mechanism.

#### {#FR-001-data-model} Data Model 
```
model User {
    id String @id @default(uuid())\
    email String @unique\
    username String @unique\
    passwordHash String\
    tier String @default("Free")\
    createdAt DateTime @default(now())\
    memberships RoomMembership[]\
    messages Message[]\
    aiInvocations AIInvocation[]\
}
```
#### {#FR-001-api} API Endpoints 

1.  **POST /api/auth/register**

    a.  **Request Body:**

        i.  { "email": "string", "username": "string", "password":"string" }

    b.  **Validations:**

        i.  email: RFC 5322-compliant format; lowercase; unique in User.email.
        ii. username: 3--20 chars, alphanumeric only, unique in User.username.
        iii. password: ≥8 chars; must include upper/lowercase + number.
             > Regex: /^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).+$/

    c.  **Processing Steps:**

        i.  Normalize email to lowercase.
        ii. Hash password with bcrypt (cost factor = 12).
        iii. Create User records in DB.
        iv. Generate JWT (HS256) payload: { "userId": "uuid", "username": "string", "tier": "Free", "iat": <epoch>, "exp": <epoch+86400> }
        v.  Return **201 Created** with JWT in JSON.

2.  **POST** /api/auth/login

    a.  **Request Body:**

        i.  { "email": "string", "password": "string" }

    b.  **Processing Steps:**

        i.  Find User by email.
        ii. Compare password via bcrypt.compare().
        iii. On success, return JWT as above.

3.  **POST** /api/auth/forgot-password *(Optional MVP)*

    a.  Generate secure reset token (crypto.randomBytes(32)), store in PasswordReset table with expiry = 1 hour, send email link to user.

#### {#FR-001-security} Security Controls 

-   Passwords never logged or returned.
-   Rate-limit login attempts: max 5/min per IP → return HTTP 429 on exceed.
-   JWT expiry = 24h; refresh flow optional in MVP.
-   All endpoints require HTTPS/TLS 1.2+.

####  {#FR-001-acceptance} Acceptance Criteria

-   Registering with valid data returns 201 + valid JWT.
-   Duplicate email/username returns HTTP 400 with error:duplicate_entry.
-   Login with valid credentials returns 200 + valid JWT.
-   Login with incorrect password returns 401 Unauthorized.
-   JWT payload includes correct userId, username, and tier.

#### {#FR-001-tests} Test Cases 

1.  **TC-FR-001-01**: Register valid → 201 + JWT (verify payload claims).
2.  **TC-FR-001-02**: Register with duplicate email → 400.
3.  **TC-FR-001-03**: Login valid → 200 + JWT.
4.  **TC-FR-001-04**: Login wrong password → 401.
5.  **TC-FR-001-05**: Verify password hash in DB != plaintext.

### {#FR-002} FR-002 --- Create & Manage Chat Rooms 

**Section ID:** FR-002\
**Version:** 1.0.0\
**Tags:** chat, rooms, collaboration, real-time, workspace-management\
**Parent ID:** functional-requirements

####  {#FR-002-prd} PRD Requirement

The system shall allow authenticated users to create, list, and manage
**chat rooms**.
-   A room is a **persistent workspace** containing messages and participants.
-   Each room must have a **unique name** and a **shareable join link**.
-   Users must be able to view only the rooms they belong to.
-   Room creation is allowed for all authenticated users unless restricted by tier or role.

#### {#FR-002-data-model} Data Model 

```
model Room {\
    id String @id @default(uuid())\
    name String\
    shareableLink String @unique\
    isEducation Boolean @default(false)\
    memberships RoomMembership[]\
    messages Message[]\
    aiInvocations AIInvocation[]\
    createdAt DateTime @default(now())\
}
```

```
model RoomMembership {
    id String @id @default(uuid())\
    roomId String\
    userId String\
    role Role @default(MEMBER)\
    room Room @relation(fields: [roomId], references: [id], onDelete: Cascade, onUpdate: Cascade)\
    user User @relation(fields: [userId], references: [id], onDelete: Cascade, onUpdate: Cascade)\
    @@unique([roomId, userId], name: "room_user_unique")\
}

```
```
enum Role { OWNER MEMBER}
```
#### {#FR-002-api} API Endpoints 

1.  **POST** /api/rooms --- Create a Room

    a.  **Request Body:**

        i.  { "name": "string" }

    b.  **Validations:**

        i.  name: 3--50 chars, no HTML/emoji.

    c.  **Processing Steps:**

        i.  Validate auth JWT; get userId.
        ii. Generate shareableLink = UUIDv4 + short hash (≥32 chars).
        iii. Insert Room into DB.
        iv. Create RoomMembership with role = OWNER.
        v.  Return { roomId, shareableLink }.

2.  **GET** /api/rooms --- List My Rooms

    a.  **Processing Steps:**

        i.  Validate auth JWT.
        ii. Query Room via RoomMembership where userId matches.
        iii. Return { id, name, shareableLink, role } array.

3.  **POST** /api/rooms/join --- Join via Shareable Link

    a.  **Request Body:**

        i.  { "shareableLink": "string" }

    b.  **Processing Steps:**

        i.  Validate auth JWT.
        ii. Find Room by shareableLink
        iii. Insert into RoomMembership if not already a member (idempotent join).
        iv. Return { roomId, role }.

#### {#FR-002-security} Security Controls 

-   Shareable links must be **unguessable**; store as a single token (no incremental IDs).
-   All room actions must validate **membership** server-side.
-   Role-based permissions enforced (only OWNER can delete/rename rooms).
-   Input sanitization on name to prevent stored XSS.

#### {#FR-002-acceptance} Acceptance Criteria 

-   Creating a room returns 201 with roomId and shareableLink.
-   Listing rooms returns only rooms where the user is a member.
-   Joining with a valid shareableLink adds user as MEMBER.
-   Joining when already a member does not create a duplicate.
-   Joining with invalid link returns 404.

#### {#FR-002-tests} Test Cases 

1.  **TC-FR-002-01**: Create valid room → 201 + shareableLink.
2.  **TC-FR-002-02**: List rooms when user is in 2+ rooms → correct list.
3.  **TC-FR-002-03**: Join room via valid link → membership created.
4.  **TC-FR-002-04**: Join same room twice → no duplicate membership.
5.  **TC-FR-002-05**: Join with invalid link → 404.

### {#FR-003} FR-003 --- Join Chat Room via Shareable Link 

**Section ID:** FR-003\
**Version:** 1.0.0\
**Tags:** chat, rooms, invite-link, membership, access-control\
**Parent ID:** functional-requirements

#### {#FR-003-prd} PRD Requirement 

The system shall allow authenticated users to join a chat room using a
**shareable link**.

-   The shareable link must be **unguessable** and act as a direct invitation.
-   Users joining via link are automatically added to the room's membership list.
-   Duplicate joins (when already a member) must be ignored without error.

#### {#FR-003-data-model} Data Model Reuse 

Reuses Room and RoomMembership models from FR-002.

#### {#FR-003-api} API Endpoint 

1.  **POST** /api/rooms/join

    a.  **Request Body:**

        i.  { "shareableLink": "string" }

    b.  **Validations:**

        i.  shareableLink: required, exact match with Room.shareableLink.

    c.  **Processing Steps:**

        i.  Validate JWT; extract userId.
        ii. Query Room by shareableLink.
        iii. If no match → return 404 Not Found.
        iv. Check if RoomMembership exists for (roomId, userId).
            1.  If exists → return 200 OK with { roomId, role }.
            2.  If not → insert RoomMembership with default role = MEMBER.
        v.  Return { roomId, role }.

####  {#FR-003-security} Security Controls

-   Shareable link must be **≥32 characters** random token; never predictable.
-   Links are **opaque identifiers**; do not leak internal room IDs in the link.
-   All join requests must verify **auth** and **link validity** before adding membership.

#### {#FR-003-acceptance} Acceptance Criteria 

-   Joining with valid shareableLink adds the authenticated user as a MEMBER.
-   Joining when already a member returns success without duplication.
-   Joining with invalid shareableLink returns 404.
-   Only authenticated users can join rooms.

#### {#FR-003-tests} Test Cases 

1.  **TC-FR-003-01**: Join via valid link → 200, membership created.
2.  **TC-FR-003-02**: Join via valid link (already member) → 200, no duplication.
3.  **TC-FR-003-03**: Join via invalid link → 404.
4.  **TC-FR-003-04**: Join without auth token → 401 Unauthorized.
###  {#FR-004} FR-004 --- Real-Time Messaging

**Section ID:** FR-004\
**Version:** 1.0.0\
**Tags:** messaging, realtime, websocket, socket.io, fanout\
**Parent ID:** functional-requirements

#### {#FR-004-prd} PRD Requirement 

All room members must be able to **send and receive messages** in a
**real-time** stream with clear sender attribution (human or AI). The
interface should feel responsive and immediate.

#### {#FR-004-data-model} Data Model (reuse) 

Uses Message from persistence (defined fully under FR-006). Minimal
fields required at runtime:
```
model Message {\
    id String @id @default(uuid())\
    roomId String\
    userId String\
    content String\
    room Room @relation(fields: [roomId], references: [id], onDelete: Cascade, onUpdate: Cascade)\
    user User @relation(fields: [userId], references: [id], onDelete: Restrict, onUpdate: Cascade)\
    isFromAi Boolean @default(false)\
    createdAt DateTime @default(now())\
    @@index([roomId, createdAt])\
}
```
####  {#FR-004-ws-model} WebSocket Channel Model

-   Transport: **Socket.io** (WebSocket with fallback disabled if possible).
-   **Namespace:** /ws
-   **Room channels:** room:{roomId} (server joins/leaves sockets)

#### {#FR-004-events} Client↔Server Events 

1.  **Client → joinRoom**

    a.  { "roomId": "string" }

    b.  **Server behavior:**

        i.  Verify JWT (auth middleware)
        ii. Verify membership (roomId,userId)
        iii. socket.join("room:{roomId}")

2.  **Client → sendMessage**

    a.  { "roomId":"string", "content":"string" }

        i.  **Validation:** non-empty content (≤ 4,000 chars), membership check.

    b.  **Server behavior (hot path):**

        i.  Persist message { isFromAi:false }
        ii. Publish to Redis Pub/Sub (if clustered)
        iii. Broadcast to channel as receiveMessage:\
             a. **{\
                "id":"uuid","roomId":"...","userId":"...",\
                "content":"...","isFromAi":false,"createdAt":"iso8601"
                }**

3.  **Server → receiveMessage**

    a.  Delivered to all sockets in room:{roomId} except sender (sender can be echoed locally or included as broadcast).

    b.  Note: AI streaming events (aiChunk, aiComplete) are specified under FR-005 (Explicit AI Invocation).

####  {#FR-004-rest} REST Fallback 

-   POST /api/rooms/:roomId/messages as a fallback/send for legacy clients.
-   Server still emits **receiveMessage** to the room after persisting.

#### {#FR-004-ordering} Ordering & Delivery 

-   **Per-room ordering**: natural by createdAt, ties by id.
-   **At-least-once** delivery: the same message idempotently replaceable on client.
-   Client should de-dupe by id.

#### {#FR-004-slos} Latency SLOs 

-   **BASE profile:** p95 end-to-end (client→persist→fanout→client) < **500 ms** in-region.
-   Hot-path DB ops ≤ **50 ms**.
-   Track **publish→deliver** histogram per room.

#### {#FR-004-security} Security Controls 

-   All WS connections require a **valid JWT** at connect and periodic re-auth (e.g., every 15 min).
-   **Membership enforcement** on joinRoom and sendMessage.
-   **Content sanitization** on display (escape HTML) to prevent XSS.
-   **Rate limit** sendMessage per user (e.g., 20 msg / 10 s) to deter spam; emit 429 error event on exceed.
-   Backpressure: disconnect clients that exceed server queue thresholds.

#### {#FR-004-acceptance} Acceptance Criteria 

-   A member who calls **joinRoom** receives **roomJoined** and begins receiving **receiveMessage** events for that roomId.
-   When User A sends a message, User B (in same room) receives **receiveMessage** within SLO (p95).
-   Messages broadcast include correct id, roomId, userId, createdAt, isFromAi:false.
-   Non-members cannot join or send to a room (server rejects with auth/membership error).
-   Duplicate client receipt of the same id does not create duplicates in UI (client de-dupe).

#### {#FR-004-tests} Test Cases 

1.  **TC-FR-004-01**: Join a room with valid JWT & membership → **roomJoined** then **receiveMessage** on others' sends.
2.  **TC-FR-004-02**: Send message → persisted (DB), broadcast **receiveMessage** to all room members within SLO.
3.  **TC-FR-004-03**: Non-member tries **joinRoom**/**sendMessage** → denied with error.
4.  **TC-FR-004-04**: Rapid sends beyond rate limit → server returns 429 error event; subsequent compliant sends succeed.
5.  **TC-FR-004-05**: Cluster fan-out (Redis Pub/Sub) → messages received across nodes with no duplication (idempotent by id).

### {#FR-005} FR-005 --- Explicit AI Invocation 

**Section ID:** FR-005\
**Version:** 1.0.0\
**Tags:** ai, invocation, streaming, gateway, ratelimit\
**Parent ID:** functional-requirements

#### {#FR-005-prd} PRD Requirement 

The AI must **only** respond when **explicitly invoked** (e.g., mention
@AI).

-   The AI must **not** interject autonomously.
-   AI responses should **stream** into the room and be marked distinctly from human messages.

#### {#FR-005-detection} Invocation Detection 

-   On **sendMessage** (see FR-004), the server parses content for a configured **AI alias** (default: @AI, case-insensitive, word-bounded).

-   If detected:

    1.  Persist the **human** message as usual with isFromAi:false.
    2.  Enqueue an **AI job** for the room in the **AI Gateway** (async).
    3.  Return immediately to maintain low latency on the chat hot path.

Config: AI_ALIAS (default @AI), MAX_INPUT_TOKENS, MODEL_NAME.

#### {#FR-005-gateway} AI Gateway (Async Worker) 

-   Inputs: { roomId, userId, messageId, prompt, systemContext }.
-   **System context**: compact room transcript window + policy headers; truncate using token budget.
-   Calls external LLM API with **streaming** enabled.
-   Emits streaming events to the room:
    -   **aiChunk** { roomId, tmpId, delta }
    -   **aiComplete** { roomId, tmpId }
-   On completion, persists final **AI message**:
        ```
    -   model Message {\
            id String @id @default(uuid())\
            roomId String\
            userId String\
            content String\
            room Room @relation(fields: [roomId], references: [id], onDelete: Cascade, onUpdate: Cascade)\
            user User @relation(fields: [userId], references: [id], onDelete: Restrict, onUpdate: Cascade)\
            isFromAi Boolean @default(false)\
            createdAt DateTime @default(now())\
            @@index([roomId, createdAt])\
         }
        ```
#### {#FR-005-ledger} Invocation Ledger 

Track every invocation for observability and billing:

```
-   model AIInvocation {\
        id String @id @default(uuid())\
        roomId String\
        userId String // who invoked\
        triggerMsg String // human message id\
        model String\
        tokensIn Int?\
        tokensOut Int?\
        status String // QUEUED | RUNNING | SUCCEEDED | FAILED | TIMEOUT\
        errorCode String?\
        createdAt DateTime @default(now())\
        completedAt DateTime?\
        room Room @relation(fields: [roomId], references: [id], onDelete: Cascade, onUpdate: Cascade)\
        user User @relation(fields: [userId], references: [id], onDelete: Cascade, onUpdate: Cascade)\
        trigger Message @relation(fields: [triggerMsg], references: [id], onDelete: Restrict, onUpdate: Cascade)\
    }
```


#### {#FR-005-streaming} Streaming Protocol 

-   **Server → clients** (Socket.io in room:{roomId}):

    -   aiChunk: append delta to a client-side buffer under a temporary id tmpId.
    -   aiComplete: replace buffered text with a finalized message payload (or server later publishes the persisted message via receiveMessage).

-   **Ordering:** clients should display AI output **after** the triggering human message.

#### {#FR-005-context} Context Window Construction 

-   Use a **sliding window** of recent messages (by tokens, not count).
-   Strip prior **AI messages** if needed to favor **human prompts** within budget.
-   Include **room/system instructions** (e.g., "never reply unless invoked").
-   Sanitization: remove PII if policy requires; escape markup.

#### {#FR-005-rl} Rate Limiting 

-   Per-**user** and per-**room** quotas (e.g., **3 invocations/30s/user**, **10 invocations/30s/room**).
-   On exceed: emit error event aiRateLimited with retryAfterMs.

#### {#FR-005-retry-timeout} Retries & Timeouts 

-   **LLM call timeout** (e.g., 30s connect, 120s total stream).
-   **Retry policy**: up to 2 retries on 5xx/transient errors with jittered backoff.
-   On hard failure: mark AIInvocation.status=FAILED, emit aiError with errorCode.

#### {#FR-005-tiering} Multimodel / Tiering 

-   Choose model via user or room tier (Free, Premium), configured in the gateway.
-   Deny invocation if model not allowed; emit aiEntitlementError.

#### {#FR-005-security} Security & Compliance 

-   **No unsolicited AI**: server ignores AI generation unless trigger detected.
-   **Membership check** before streaming events to a socket.
-   **Prompt hygiene**: strip secrets; block dangerous patterns (server-side filters).
-   **Logging**: do **not** log raw prompts/replies; store IDs and token counts only.
-   **Abuse controls**: profanity/PII filters (optional) before sending to the model.

#### {#FR-005-acceptance} Acceptance Criteria 

-   When a human message includes @AI, the AI is **invoked exactly once**.
-   AI output arrives as **aiChunk → aiComplete** events and then appears as a **persisted** message with isFromAi:true.
-   Messages **without** @AI never trigger AI generation.
-   Rate limit breaches produce aiRateLimited with a **retry hint**.
-   Gateway failures produce aiError without crashing the room channel.
-   Invocation records exist with accurate status and (if available) token counts.

#### {#FR-005-tests} Test Cases 

1.  **TC-FR-005-01**: Message with @AI → aiChunk stream followed by aiComplete and a saved AI message.
2.  **TC-FR-005-02**: Message without @AI → **no** AI events.
3.  **TC-FR-005-03**: Rate limit exceeded → aiRateLimited with retryAfterMs.
4.  **TC-FR-005-04**: LLM 5xx error → retries then aiError; no duplicate AI messages persisted.
5.  **TC-FR-005-05**: Membership removed mid-stream → client stops receiving aiChunk events; persistence still completes server-side.
6.  **TC-FR-005-06**: Context window respects token cap; oldest messages drop first; no crashes.
7.  **TC-FR-005-07**: Entitlement mismatch (Free user requests premium model) → aiEntitlementError.

### {#FR-006} FR-006 --- Persistent Chat History 

**Section ID:** FR-006\
**Version:** 1.0.0\
**Tags:** history, persistence, pagination, cursor, storage\
**Parent ID:** functional-requirements

#### {#FR-006-prd} PRD Requirement 

The system shall **save all chat conversations** and allow users to
**view room history** they are members of.

-   History must be **persistent** and **securely stored**.
-   The UI should support **lazy loading / infinite scroll** to efficiently display long conversations.

#### {#FR-006-data-model} Data Model 

```
-   model Message {\
        id String @id @default(uuid())\
        roomId String\
        userId String\
        content String\
        room Room @relation(fields: [roomId], references: [id], onDelete: Cascade, onUpdate: Cascade)\
        user User @relation(fields: [userId], references: [id], onDelete: Restrict, onUpdate: Cascade)\
        isFromAi Boolean @default(false)\
        createdAt DateTime @default(now())\
        @@index([roomId, createdAt])\
    }
```
-   **Ordering key:** (createdAt, id) to guarantee stable pagination.
-   **Retention:** No auto-deletion in MVP (see "Retention & Privacy").

#### {#FR-006-api} History API 

1.  **GET** /api/rooms/:roomId/messages?cursor=<id>&direction=backward&limit=50\
    a.  **Auth:** JWT required; server validates room **membership**.\
    b.  **Params:**\

            i.  **cursor:** message id to paginate before (backfill).\
            ii. **direction:** "backward" (default) or "forward" (for resume).\
            iii. **limit:** default 50, max 100.\

    c.  **Behavior:**

        i.  If no cursor, return the most recent limit messages.
        ii. If direction=backward, return messages older than the cursor.
        iii. If direction=forward, return messages newer than the cursor (for catch-up after reconnect).

    d.  **Response:**

        i.  {
                "messages": [ { "id":"...", "roomId":"...",
                "userId":"...",
                "content":"...", "isFromAi":false,
                "createdAt":"iso8601" } ],
                "pageInfo": { "nextCursor":"...",
                "prevCursor":"...", "hasMore": true }
            }
        ii. **Indexing:** use composite index on (roomId, createdAt) for range scans.
        iii. **Consistency:** read-your-writes guaranteed within a region; clients de-dupe by id.

#### {#FR-006-ux} Infinite Scroll UX 

-   On room open: call **GET** (no cursor) → render newest page.
-   On scroll-up near top: call **GET** with cursor=<oldestVisibleId> and direction=backward.
-   Merge results **without gaps/duplication** by id.
-   Preserve **scroll position** after prepend (common virtual list pattern).

#### {#FR-006-realtime} Interaction with Real-Time 

-   New messages arrive via **receiveMessage** (see FR-004).
-   If the client was offline, use direction=forward from the **last seen id** to fetch missed messages, then resume WS.

#### {#FR-006-search} Search (Optional, Post-MVP) 

-   Keyword search endpoint is out of MVP scope; consider later full-text index.

#### {#FR-006-security} Security & Privacy 

-   Enforce **membership** on every history read.

-   **Do not** return deleted/forbidden messages if moderation features are added later.
-   **Logging:** Never log message **content**; log only roomId, messageId, timing metrics.
-   **Retention (MVP):** messages retained indefinitely; add configurable retention windows post-MVP.

#### {#FR-006-performance} Performance & Limits 

-   History read p95 < **300 ms** for limit=50 in-region.
-   DB query for page ≤ **50 ms** on hot indexes.
-   Payload size target: < **256 KB** per page (truncate limit if needed).

#### {#FR-006-acceptance} Acceptance Criteria 

-   Opening a room returns the **latest** page of messages the user is authorized to view.
-   Paginating **backward** yields older messages with **no duplicates** and **correct order**.
-   After reconnect, **forward** pagination fills any gap between last seen and live stream.
-   Non-members cannot read history (401/403).
-   PageInfo correctly signals hasMore and provides usable cursors.

#### {#FR-006-tests} Test Cases 

1.  **TC-FR-006-01**: GET without cursor → newest 50 messages ordered by createdAt asc in UI.
2.  **TC-FR-006-02**: Backward pagination twice → older messages appended at top, no duplicates, stable order.
3.  **TC-FR-006-03**: Forward pagination after offline gap → fills missed range, then WS resumes.
4.  **TC-FR-006-04**: Non-member requests history → 403 Forbidden.
5.  **TC-FR-006-05**: Large room (100k msgs) → page queries ≤ 50 ms, response p95 ≤ 300 ms.
6.  **TC-FR-006-06**: Mixed human/AI messages preserved with correct isFromAi flags.

### {#FR-007} FR-007 --- AI Rate Limiting 

**Section ID:** FR-007\
**Version:** 1.0.0\
**Tags:** ai, rate-limit, quotas, abuse-prevention, fair-usage\
**Parent ID:** functional-requirements

#### {#FR-007-prd} PRD Requirement 

The system shall provide **basic AI rate limiting** to prevent cost
blowups and unwanted AI spam.

-   Limits must apply when users explicitly invoke the AI (see FR-005).
-   Limits should be configurable and enforceable per **user** and per **room**.

#### {#FR-007-scopes} Scopes & Keys 

Apply rate limits at multiple scopes:

-   **Per-User** (global): ai:user:{userId}
-   **Per-Room**: ai:room:{roomId}
-   *(Optional)* **Per-IP** (edge): ai:ip:{ip}

Use all applicable scopes and **deny** if any scope exceeds its quota.

#### {#FR-007-algorithm} Algorithm 

-   **Token Bucket** per scope with a small **burst** allowance.
-   Backing store: **Redis** (INCR + EXPIRE or Lua script for atomicity).
-   Defaults (tunable via config/env):
    -   USER_BUCKET: **3 invocations / 30s**, burst **= 3**
    -   ROOM_BUCKET: **10 invocations / 30s**, burst **= 10**

#### {#FR-007-enforcement} Enforcement Point 

-   Enforce **before** enqueueing an AI job in the **AI Gateway** (see FR-005-gateway).
-   If over limit:
    -   **WebSocket**: emit aiRateLimited with { scope, retryAfterMs }.
    -   **REST (if applicable)**: return **429 Too Many Requests** with Retry-After header.

#### {#FR-007-tiers} Tier-Based Limits (Optional) 

-   Map tiers to buckets:
    -   Free: defaults above
    -   Premium: **6/30s** per user, **20/30s** per room
-   Deny if requested model exceeds entitlement (handled in FR-005 tiering), independent of rate.

#### {#FR-007-config} Configuration 

-   ENV vars:
    -   RL_USER_RATE, RL_USER_WINDOW_SEC, RL_ROOM_RATE, RL_ROOM_WINDOW_SEC
    -   RL_REDIS_URL, RL_BURST_MULTIPLIER
-   Feature flag to **disable** RL for internal/staging rooms.

#### {#FR-007-observability} Observability 

Emit metrics and logs (no PII):
-   Counters: ai_invocation_allowed_total, ai_invocation_denied_total{scope=\...}
-   Gauges: current bucket sizes (sampled), queue depth in AI Gateway
-   Traces: span around **rate-limit check** with tags { userId, roomId } (IDs only)

#### {#FR-007-security} Security & Abuse Controls 

-   Always validate **membership** (room) and **JWT** (user) before RL check.
-   Use **constant-time** comparisons for keys/tokens (defense-in-depth).
-   Avoid exposing exact limits to clients; return only retryAfterMs.
-   Protect Redis with TLS/auth; isolate RL keys with a dedicated prefix.

#### {#FR-007-acceptance} Acceptance Criteria 

-   When a user exceeds **per-user** quota, the next AI invocation is **denied** with aiRateLimited (WS) or **429** (REST).
-   When a room exceeds **per-room** quota, further invocations in that room are denied regardless of user.
-   Buckets **auto-refill** after their window; invocation succeeds post retryAfterMs.
-   Tier overrides (if enabled) adjust limits without code changes.
-   RL enforcement happens **before** the AI job is queued---no jobs enter the gateway when denied.

#### {#FR-007-tests} Test Cases 

1.  **TC-FR-007-01**: Exceed per-user rate → next invocation returns aiRateLimited with retryAfterMs > 0.
2.  **TC-FR-007-02**: Exceed per-room rate with multiple users → all further invocations in that room denied until window reset.
3.  **TC-FR-007-03**: Wait for retryAfterMs and invoke again → succeeds.
4.  **TC-FR-007-04**: Premium tier user has higher allowance → can invoke beyond Free thresholds but within Premium limits.
5.  **TC-FR-007-05**: Redis unavailable (degraded mode) → system **fails closed** (deny) or **fails open** per config flag RL_FAIL_OPEN.
6.  **TC-FR-007-06**: Concurrent invocations across cluster nodes → no double-allow; Lua script/atomic ops maintain correctness.

# {#non-functional-requirements} 3. Non-functional Requirements (NFR) 

### {#NFR-001} NFR-001 --- UI Simplicity 

**Section ID:** NFR-001\
**Version:** 1.0.0\
**Tags:** ui, ux, simplicity, design-system, accessibility\
**Parent ID:** non-functional-requirements

#### {#NFR-001-prd} PRD Requirement 

The MVP must prioritize **simplicity and ease of use**: a clean,
minimalist SPA where the **core chat** experience is the focus. UI
should have **low cognitive load**, be **mobile-first**, and feel
**responsive** to interactions.

#### {#NFR-001-design-system} Design System & Stack 

-   **Component library:** Use **shadcn/ui** for all interactive elements (buttons, inputs, dialogs, toasts).
-   **Styling:** Use **Tailwind CSS** utilities; avoid bespoke CSS except for rare layout fixes.
-   **Tokens:** Define a minimal **theme** (spacing/typography/semantic colors). Dark mode included.
-   **Icons:** Use **lucide-react** consistently.

#### {#NFR-001-layout} Layout & Navigation 

-   **SPA shell** with a **persistent sidebar** for Rooms; main panel = current Room.
-   **Zero full-page reloads** on core flows (auth, create/join room, messaging).
-   **Mobile-first** breakpoints; sidebar collapses to drawer on small screens.

#### {#NFR-001-interactions} Interaction Patterns 

-   **Inline, optimistic UX** where safe (e.g., sending a message shows immediately; reconcile on server ack).
-   **Loading**: use **skeletons** and **spinners**---never blank states.
-   **Errors**: show inline, human-readable error text with recovery actions (e.g., "Retry", "Copy error id").
-   **Empty states**: concise guidance (e.g., "No messages yet---say hello or invite someone").

#### {#NFR-001-message-view} Content & Message View 

-   Message list is **virtualized** (large rooms), preserves scroll position on history prepend.
-   Clear **attribution** (user vs AI), timestamps, and readable line lengths (≈60--80ch).

-   **Escape/strip HTML** in message content to prevent XSS.

#### {#NFR-001-a11y} Accessibility (baseline) 

-   **WCAG 2.1 AA**: color contrast, focus states, skip-links, ARIA for interactive components.
-   **Keyboard**: tab order, Enter to send, Shift+Enter newline, shortcuts discoverable.
-   **Announcements**: toast/live region for async events (e.g., "joined room", "message failed to send").

#### {#NFR-001-perf} Performance UX Budgets 

-   First interactive for main app route **< 2s** on a mid-range device.
-   Route transitions **< 200ms** perceptually (skeletons within 100ms).
-   Message send round-trip feedback **< 100ms** optimistic; real-time fanout per SLO.

#### {#NFR-001-guardrails} Do/Don't Guardrails 

-   **Do**: single clear primary action per view; concise copy consistent spacing/typography.
-   **Don't**: multi-step modals for basic actions; decorative animations that delay input; hidden critical actions.

#### {#NFR-001-acceptance} Acceptance Criteria 

-   All UI screens are built with **shadcn/ui + Tailwind**, following the shared theme.
-   The app runs as a **SPA** with sidebar + chat layout; no full reloads on core flows.
-   Loading states use **skeletons**; empty states provide **next-step guidance**.
-   Message list **virtualizes** and **preserves scroll** during history pagination.
-   Keyboard-only navigation completes **auth → enter room → send message** without mouse.

-   **Lighthouse** (mobile) performance ≥ **80** and accessibility ≥ **90** on the main chat route using a seeded room.

#### {#NFR-001-tests} Test Cases 

1.  **TC-NFR-001-01 (Design System):** Inspect UI---every button/input/dialog is a shadcn/ui component; no custom CSS files aside from Tailwind/global reset.
2.  **TC-NFR-001-02 (SPA Behavior):** Navigate auth → room list → room; confirm no full page reloads; transitions show skeletons.
3.  **TC-NFR-001-03 (Message Virtualization):** Load a room with 10k messages, paginate history up; FPS stays smooth; scroll position preserved.
4.  **TC-NFR-001-04 (Accessibility):** Keyboard-only task completion; axe/Lighthouse a11y score ≥ 90; visible focus rings on all interactive elements.
5.  **TC-NFR-001-05 (Performance):** Cold load TTI < 2s on mid-range profile; message send optimistic echo < 100ms; route transitions < 200ms.
6.  **TC-NFR-001-06 (Error/Empty States):** Simulate network error on send---inline error with "Retry"; empty room shows guidance to invite/send first message.

### {#NFR-002} NFR-002 --- Modular Monolith Architecture 

**Section ID:** NFR-002\
**Version:** 1.0.0\
**Tags:** architecture, modular-monolith, boundaries, services, scalability\
**Parent ID:** non-functional-requirements

#### {#NFR-002-prd} PRD Requirement 

The backend **must be a Modular Monolith** to enable rapid MVP delivery while preserving future scalability via clean module boundaries. Modules are distinct (e.g., User, Chat, AI Gateway) and loosely coupled to allow later extraction without rewrite.

#### {#NFR-002-tech} Technical Implementation Rules 

**Source layout:** Backend **must** adhere to the modules path
apps/web/src/server/modules/... (e.g., user, auth, chat, ai).

-   **Strict Boundary Rule:** Modules **MUST NOT** directly access other modules' ORM models. All inter-module access goes through a **service layer** (e.g., chatService may call userService.getUserById(); it must not query User directly).

-   **Future extraction seam:** Keep module interfaces stable so moving a module behind HTTP/RPC later doesn't force app-wide refactors. (Implied by the Modular Monolith intent and service-layer rule.)

-   **Schema source of truth:** Prisma schema is authoritative; altering core models requires **architectural review**.

#### {#NFR-002-perf} Performance & Scale Notes 

-   Real-time hot-path DB queries (e.g., send message) **under 50 ms**. Prepare for horizontal scale with **Redis Pub/Sub** for broadcast between instances (even if MVP runs single-node). (Ties to NFR3 but informs module boundaries.)

#### {#NFR-002-acceptance} Acceptance Criteria 

-   Server code resides under the prescribed **modules path** and respects the **Strict Boundary Rule** (no cross-module model imports).
-   Cross-module calls occur **only via services**; direct ORM access across module lines is absent in the codebase.
-   Schema change PRs show **architectural review** when core models are modified.

#### {#NFR-002-tests} Test Cases 

1.  **TC-NFR-002-01 (Lint/CI):** CI fails on any import of another module's ORM model (AST/lint rule).
2.  **TC-NFR-002-02 (Contract):** Replace dependent modules with **service mocks**; features still work (no direct DB cross-access).
3.  **TC-NFR-002-03 (Schema Control):** Attempt to change a core Prisma model without architectural review → CI blocks the merge.

### {#NFR-003} NFR-003 --- Real-time Performance 

**Section ID:** NFR-003\
**Version:** 1.0.0\
**Tags:** performance, realtime, latency, websocket\
**Parent ID:** non-functional-requirements

#### {#NFR-003-prd} PRD Requirement 

The system should deliver messages in **near real-time** with **p95
end-to-end latency < 500 ms**. Achieving this requires a
**WebSocket-based real-time layer (e.g., Socket.io)** and an efficient
backend broadcast path.

#### {#NFR-003-tech} Technical Implementation Rules 

-   **Hot-path DB budget:** All database queries involved in real-time operations (e.g., send message) **must complete in < 50 ms**.
-   **Fan-out readiness:** Use **Redis Pub/Sub** for broadcasting between server instances to prepare for horizontal scaling (even if MVP is single-instance).
-   **Transport & events:** Implement real-time via **Socket.io** with joinRoom / sendMessage → **persist** → **broadcast receiveMessage** flow.
-   **Architecture fit:** Real-time layer must align with the PRD's WebSocket requirement to meet the p95 < 500 ms SLO.


#### {#NFR-003-acceptance} Acceptance Criteria 

-   Under representative load, **p95 E2E latency < 500 ms** for message delivery in a room (client → persist → fan-out → client).
-   Measured DB time on the send-message hot path is **< 50 ms**.
-   Real-time transport uses **Socket.io**, and multi-instance deployments are configured with **Redis Pub/Sub** for broadcast.

#### {#NFR-003-tests} Test Cases 

1.  **TC-NFR-003-01 (Latency SLO):** Run a synthetic chat load; verify **p95 < 500 ms** message E2E latency.
2.  **TC-NFR-003-02 (DB budget):** Instrument the send path; confirm DB queries on hot path **< 50 ms**.
3.  **TC-NFR-003-03 (Broadcast readiness):** In a multi-instance setup, enable **Redis Pub/Sub** and verify cross-node delivery without added duplication.
4.  **TC-NFR-003-04 (Transport conformance):** Validate real-time flows use **Socket.io** with joinRoom/sendMessage → receiveMessage broadcast.

### {#NFR-004} NFR-004 --- Data Reservoir 

**Section ID:** NFR-004\
**Version:** 1.0.0\
**Tags:** data-reservoir, analytics, schema, etl, observability\
**Parent ID:** non-functional-requirements

#### {#NFR-004-prd} PRD Requirement 

Chat data must be stored in a **structured format suitable for future
ingestion into a data analytics pipeline** (the "Data Reservoir"
vision). This implies capturing message content plus **clear
relationships** between users, rooms, and messages with **accurate
timestamps**.

#### {#NFR-004-schema} Authoritative Schema & Governance 

-   The **Prisma schema is the single source of truth** for data structures. Core models (User, Room, Message) must not be altered without **architectural review**.
-   Keep ownership boundaries aligned with the Modular Monolith (User owns user data; Chat owns messages/rooms). (Consistent with NFR-002 service boundaries.)

#### {#NFR-004-entities} Entities & Relationships (Baseline) 

-   Maintain normalized relationships among **User ↔ Room ↔ Message** to enable reliable analytics joins later (IDs + timestamps): examples are provided in the spec for User, Room, and Message.
-   Ensure **stable identifiers** (uuid) and **monotonic creation timestamps** (createdAt) on all core tables to support cursoring and downstream CDC/ETL. (Aligned with history pagination & real-time paths.)

#### {#NFR-004-timestamps} Timestamp & Attribution Fidelity 

-   Every message must persist createdAt, roomId, userId, and isFromAi (true for AI outputs) to preserve **who/what/where/when** semantics required by analytics.

#### {#NFR-004-invariants} Write Path Invariants 

-   **Idempotent writes** for messages (de-dupe by id) to avoid double counts in analytics (consistent with real-time fan-out).
-   **No content logging** in app logs (IDs only) to keep analytics inputs clean and privacy-safe; PII must not leak via logs. (Privacy NFR cross-reference.)

#### {#NFR-004-export} Export & Ingestion Readiness (ELT/CDC) 

-   Design tables for **append-only** message events (no hard deletes in MVP; use soft-delete flags if moderation is added later) so downstream jobs can **incrementally load** by createdAt or id. (Derives from "future analytics pipeline" intent.)
-   Maintain **minimal, clean columns** (IDs, timestamps, foreign keys, booleans) to ensure CSV/Parquet exports are straightforward when the reservoir is built.

#### {#NFR-004-indexing} Queryability & Indexing 

-   Index (roomId, createdAt) for message history (already required for pagination) and to support time-sliced analytics.

#### {#NFR-004-acceptance} Acceptance Criteria 

-   Core data is represented by **authoritative Prisma models** (User, Room, Message) with unambiguous relationships and timestamps, ready for analytics ingestion.
-   Schema changes to these models require **architectural review** (recorded in PRs) before merge.
-   Message records always include roomId, userId, createdAt, and isFromAi, ensuring downstream attribution.
-   No logs contain **PII or message content**; logs use IDs only.

#### {#NFR-004-tests} Test Cases 

1.  **TC-NFR-004-01 (Schema Authority):** Attempt to add a new column to Message without architectural review → CI blocks per governance rule.
2.  **TC-NFR-004-02 (Attribution Completeness):** Insert a human and an AI message; verify userId, roomId, createdAt, isFromAi are present and correct.
3.  **TC-NFR-004-03 (Export Readiness):** Simulate an export selecting id, roomId, userId, content, isFromAi, createdAt; ensure no orphaned rows and CSV/Parquet round-trips without schema inference errors.
4.  **TC-NFR-004-04 (Privacy Logging):** Trigger message send and AI invocation flows; confirm logs contain **IDs only** (no emails/message text).

### {#NFR-005} NFR-005 --- Data Privacy & Compliance 

**Section ID:** NFR-005\
**Version:** 1.0.0\
**Tags:** privacy, compliance, pii, logging, security\
**Parent ID:** non-functional-requirements

#### {#NFR-005-prd} PRD Requirement 

The system must enforce **strict privacy and compliance practices** to
protect user data (emails, messages, credentials). This includes:

-   Preventing **leakage of PII** (Personally Identifiable Information) into logs or monitoring tools.
-   Ensuring **data handling and storage practices** align with future compliance obligations (e.g., FERPA, GDPR for education).
-   Designing **auditable, reviewable privacy boundaries** between services.

#### {#NFR-005-logging} Logging & Monitoring Restrictions 

-   **No sensitive fields** (passwords, message text, email addresses, JWTs) may be logged in plain text.
-   Application logs must include **IDs only** (userId, roomId, messageId) for traceability without exposing PII.

#### {#NFR-005-auth} Authentication & Token Handling 

-   JWT tokens must never be persisted in logs, DB, or analytics tables. They should remain ephemeral in transit (headers/cookies).
-   Passwords must be **salted and hashed** (e.g., bcrypt) with no plaintext recovery. This aligns with the FR-001 User Account System.

#### {#NFR-005-boundaries} Service Boundaries 

-   PII fields are **owned and isolated** in the User model (Auth service domain). Other services (e.g., Chat) may reference by userId but must not duplicate PII. (Consistency with Modular Monolith design.)

#### {#NFR-005-storage} Storage & Transmission 

-   All sensitive data in transit must use **TLS 1.2+**.
-   Sensitive fields at rest (user emails, hashed passwords) must be encrypted or stored using secure hashing.
-   Message contents (chat text, AI output) are persisted in DB but must be **excluded from logs**.

####  {#NFR-005-audit} Auditability

-   Any schema or service change affecting PII requires **architectural review** (same as schema governance rule).
-   Privacy-related incidents must be traceable via **userId-only logs**, not message text.

#### {#NFR-005-acceptance} Acceptance Criteria 

-   No logs contain message content, email addresses, JWT tokens, or passwords. Logs contain **IDs only**.
-   Passwords are verified to be salted and hashed in the DB. No plaintext credentials exist.
-   Only the User model contains PII; Chat/AI modules only reference userId.
-   All API requests and WebSocket connections use **TLS**.
-   Schema changes that introduce new PII require review and sign-off.

#### {#NFR-005-tests} Test Cases 

1.  **TC-NFR-005-01 (PII in Logs):** Simulate user signup, login, and message sending; verify logs show only IDs (no emails, no plaintext).
2.  **TC-NFR-005-02 (Password Storage):** Inspect DB user records; confirm passwords are stored as salted+hashed values.
3.  **TC-NFR-005-03 (Service Boundary):** Query Chat DB for email addresses; confirm none exist (only userId references).
4.  **TC-NFR-005-04 (Token Safety):** Trigger failed JWT validation; confirm logs exclude raw tokens.
5.  **TC-NFR-005-05 (Schema Review):** Propose adding a phone number field; verify review process is enforced before merge.

### {#NFR-006} NFR-006 --- Accessibility (WCAG 2.1 AA) 

**Section ID:** NFR-006\
**Version:** 1.0.0\
**Tags:** accessibility, wcag-2.1-aa, a11y\
**Parent ID:** non-functional-requirements

#### {#NFR-006-prd} PRD Requirement 

The product must target **WCAG 2.1 AA compliance** as a **non-negotiable
baseline**; design and development choices---**from color contrast to
keyboard navigation**---must meet this standard. The app is a
**responsive, mobile-first** web app that must remain accessible across
phone, tablet, and desktop.

#### {#NFR-006-keyboard} Keyboard-Only Operability 

All core flows (auth → create/join room → send message) must be fully
operable with the **keyboard alone**, reflecting the PRD's emphasis on
keyboard navigation.

#### {#NFR-006-contrast} Contrast & Visual Clarity 

UI components must present **clear visual contrast** and visible
focus/hover states to satisfy the PRD's accessibility baseline.

#### {#NFR-006-responsive} Responsive Accessibility 

Accessibility must hold on **mobile-first** layouts and scale gracefully
to larger screens (tablet/desktop), per target platforms.

#### {#NFR-006-acceptance} Acceptance Criteria 

-   A user can complete **login → enter/create room → send message** using **keyboard only** (no traps).
-   Interactive elements show **discernible focus** and maintain **readable contrast** consistent with the accessibility baseline.
-   The experience remains accessible on **mobile** and **desktop** per the PRD's target platforms.

#### {#NFR-006-tests} Test Cases 

1.  **TC-NFR-006-01 --- Keyboard Flow**: Complete auth → create/join room → send message using only the keyboard; verify focus order and absence of traps.
2.  **TC-NFR-006-02 --- Focus & Contrast States**: Inspect buttons, inputs, and links for visible focus and sufficient visual contrast across default/hover/active/disabled states.
3.  **TC-NFR-006-03 --- Mobile Accessibility**: On a phone-sized viewport, repeat TC-01 and verify controls remain operable and legible (mobile-first requirement).
4.  **TC-NFR-006-04 --- Desktop Accessibility**: On a desktop viewport, repeat TC-01 and confirm accessibility parity with mobile.

# {#api-surface} 4. API Surface 

**Section ID:** API Surface\
**Version:** 1.0.0\
**Tags:** api, rest, websocket, streaming\
**Parent ID:** specification

#### {#api-auth-register} POST /api/auth/register 

**Body:** { "email": "string", "username": "string",
"password": "string" }

**Notes:** Validate email format; username 3--20 alphanumeric & unique;
password ≥ 8 chars. Hash password (bcrypt). On success, create User and
**generate a JWT**

**JWT payload (spec example):**

{\
    "userId": "user-uuid",\
    "username": "user-display-name",\
    "tier": "Free",\
    "iat": 1672531200,\
    "exp": 1672617600\
}



---
#### **POST `/api/auth/login`**
**Body:**

```json :{ "email": "string", "password": "string" } ```
---

**Notes:** Find by email, bcrypt.compare(); on success **generate a
JWT**.

#### {#api-auth-tests} Test Cases 

-   **TC-API-AUTH-01 --- Register success returns JWT:** Send valid body → user created, JWT issued (payload fields as spec).
-   **TC-API-AUTH-02 --- Login success returns JWT:** Valid credentials → JWT issued.
-   **TC-API-AUTH-03 --- Validation rules enforced:** Bad email/short password/duplicate username → rejected per rules.

#### {#api-rooms-list} GET /api/rooms 

1.  Returns rooms the authenticated user is a member of.

#### {#api-rooms-create} POST /api/rooms 

1.  **Body:** { "name": "string" }

2.  Creates a Room, generates **unguessable shareableLink**, and creates RoomMembership (owner link).

#### {#api-rooms-join} POST /api/rooms/join 

-   **Body:** { "shareableLink": "string" }

-   Joins a room by shareableLink; creates RoomMembership for the user.

#### {#api-rooms-tests} Test Cases 

-   **TC-API-ROOMS-01 --- Create room generates link & membership:** POST /api/rooms → room record + shareable link + owner membership.
-   **TC-API-ROOMS-02 --- Join by link:** POST /api/rooms/join with valid shareableLink → membership created.
-   **TC-API-ROOMS-03 --- List rooms:** GET /api/rooms returns only rooms for the caller.

#### {#api-messages-ws} WebSocket (Socket.io) events 

-   **Client → joinRoom\
    Payload:** { "roomId": "string" } → server subscribes socket to room channel.
-   **Client → sendMessage\
    Payload:** { "roomId": "string", "content": "string" } → server **persists** message (isFromAi:false), then **broadcasts** receiveMessage.
-   **Server → receiveMessage\
    Payload:** Full Message object.

#### {#api-messages-history} History (HTTP) 

-   **GET** /api/rooms/:roomId/messages?cursor=<cursorId> → **cursor-based pagination** (fetch fixed count, e.g., 50 before cursor).

#### {#api-messages-tests} Test Cases 

-   **TC-API-MSG-01 --- joinRoom subscribes socket:** After joinRoom, messages to that room are received.
-   **TC-API-MSG-02 --- sendMessage persists & broadcasts:** Message stored with isFromAi:false; others receive receiveMessage.
-   **TC-API-MSG-03 --- History pagination:** GET history with cursor returns prior messages using cursor pagination (e.g., 50).

### {#api-ai} AI Invocation flow 

Behavior (within sendMessage handler):

1.  Parse content for **@AIName** mention; still save & broadcast as normal user message.
2.  Dispatch **async job** to **AI Gateway Module**.
3.  As the AI streams back, **Gateway emits aiChunk events** to the room.
4.  On completion, **create final Message** with isFromAi:true and persist.

**Note:** The PRD leaves the exact invocation UX (e.g., @mention vs
toggle) open; final method to be decided during UX prototyping.

#### {#api-ai-tests} Test Cases 

-   **TC-API-AI-01 --- @AI mention triggers Gateway job:** Message saved & broadcast; async AI job enqueued.
-   **TC-API-AI-02 --- Streaming chunks delivered:** Clients receive aiChunk stream for the room.
-   **TC-API-AI-03 --- Final AI message persisted:** After stream, Message with isFromAi:true exists.

# {#system-architecture} 5. System Architecture 

### {#arch-client} Client SPA layout 

**Section ID:** ARCH-CLIENT\
**Version:** 1.0.0\
**Tags:** spa, ui, mobile-first, sidebar, real-time\
**Parent ID:** system-architecture

#### {#arch-client-prd} PRD Intent 

Build a **clean, minimalist SPA** that keeps users "in flow" during
real-time collaboration, with a **persistent, collapsible sidebar for
room navigation** and an uncluttered, responsive UI. The app is
**mobile-first** and scales to tablet/desktop.

#### {#arch-client-layout} Composition & Layout 

-   **SPA shell** with **persistent/collapsible sidebar** (rooms list) + main panel (active room). No full-page reloads between core views.
-   **Core views:** Login/Sign-up → Main App (sidebar + active room) → Chat View (history, input, clear attribution).

#### {#arch-client-design} Design System & Styling 

-   Use **Shadcn/ui** components and **Tailwind** utilities for all interactive UI; avoid bespoke CSS where a library utility exists.

#### {#arch-client-interactions} Interaction & Feedback 

-   The SPA should feel **highly responsive**, giving immediate visual feedback to user actions to preserve a sense of direct manipulation.

-   **History display** uses **lazy loading/infinite scroll** to handle long conversations without heavy initial loads.

#### {#arch-client-a11y} Accessibility & Target Platforms 

-   Honor **WCAG 2.1 AA** baseline; keyboard-only operability and accessible semantics apply across **mobile-first** layouts that scale to desktop.

#### {#arch-client-acceptance} Acceptance Criteria 

-   The main app renders as a **SPA** with a **persistent/collapsible sidebar** and **no full page reloads** when navigating between rooms or core views.
-   **Chat View** presents message history, input box, and **clear attribution** (human vs AI).
-   **History** loads via **lazy loading/infinite scroll** to keep initial load light.
-   The UI behaves **mobile-first** and scales gracefully to tablet/desktop.
-   UI components are built with **Shadcn/ui + Tailwind** (no one-off CSS for standard patterns).

#### {#arch-client-tests} Test Cases 

1.  **TC-ARCH-CLIENT-01 --- SPA Navigation:** Navigate Login → Main App → different rooms; verify **no full page reloads** and sidebar persistence/collapse works.
2.  **TC-ARCH-CLIENT-02 --- Chat View Completeness:** Open a room; verify **history + input + attribution** are present and functional.
3.  **TC-ARCH-CLIENT-03 --- Infinite Scroll History:** Seed long history; confirm **lazy loading/infinite scroll** loads older messages smoothly without spiking initial load.
4.  **TC-ARCH-CLIENT-04 --- Mobile-First Responsiveness:** On a phone viewport, complete TC-01/02/03; verify operability and readability, then repeat on desktop.
5.  **TC-ARCH-CLIENT-05 --- Design System Enforcement:** Inspect components (buttons, inputs, modals); confirm **Shadcn/ui + Tailwind** usage and absence of bespoke CSS where utilities exist.

### {#arch-backend} Backend modular structure 

**Section ID:** ARCH-BACKEND\
**Version:** 1.0.0\
**Tags:** modular-monolith, service-layer, boundaries, prisma\
**Parent ID:** system-architecture

#### {#arch-backend-prd} PRD Intent 

Implement a **Modular Monolith** so the codebase is split into distinct,
loosely-coupled modules (e.g., **User**, **Chat**, **AI Gateway**) with
**strict boundaries**, enabling later extraction without a rewrite.

#### {#arch-backend-layout} Source layout 

-   Backend code **must** follow: apps/web/src/server/modules/{user,auth,chat,ai,...}.

#### {#arch-backend-boundary} Strict Boundary Rule 

-   A module **must not** access another module's ORM models directly (e.g., chat cannot import user's Prisma model).

#### {#arch-backend-communication} Inter-module communication 

-   Cross-module calls go **only via service interfaces** (e.g., chatService → userService.getUserById()), never direct DB queries across boundaries.

#### {#arch-backend-modules} Module taxonomy (minimum) 

-   **user/auth** (identity, JWT issuance), **chat** (rooms, messages), **ai-gateway** (external AI callout/stream). (Examples per PRD modularization.)

#### {#arch-backend-schema} Schema ownership & governance 

-   **Prisma schema is authoritative**; core models (User, Room, Message) changes require **architectural review**.

#### {#arch-backend-realtime-seam} Real-time integration seam 

-   chat module persists messages and triggers broadcast; history exposed via cursor-based HTTP API. (Detailed flow covered under Real-time/WebSocket.)

#### {#arch-backend-scale} Scale seam (future) 

-   Prepare to add **Redis Pub/Sub** for cross-instance fan-out without changing service interfaces.

#### {#arch-backend-acceptance} Acceptance Criteria 

-   Source tree matches apps/web/src/server/modules/* layout.
-   No module imports another module's Prisma model; all cross-module access is via services.
-   Prisma is the **single source of truth**; core model changes show architectural review.
-   Chat flow: **persist → broadcast** implemented in chat module; history endpoint uses **cursor pagination**.

#### {#arch-backend-tests} Test Cases 

1.  **TC-ARCH-BACKEND-01 --- Source layout check:** Repository paths conform to apps/web/src/server/modules/....
2.  **TC-ARCH-BACKEND-02 --- Boundary compliance:** Code search shows **no cross-module ORM imports** (e.g., chat importing user model).
3.  **TC-ARCH-BACKEND-03 --- Service-only integration:** Contract test stubs userService and verifies chat never queries User directly.
4.  **TC-ARCH-BACKEND-04 --- Schema governance:** Attempted changes to User/Room/Message require recorded architectural review.
5.  **TC-ARCH-BACKEND-05 --- Chat flow correctness:** sendMessage persists (isFromAi:false) and emits broadcast; history API paginates by cursor.
6.  **TC-ARCH-BACKEND-06 --- Scale seam ready:** Deploy with Redis Pub/Sub adapter; verify no code changes to module interfaces.

### {#arch-realtime} Real-time WebSocket layer 

**Section ID:** ARCH-REALTIME\
**Version:** 1.0.0\
**Tags:** websocket, socket.io, realtime, streaming, redis-pubsub\
**Parent ID:** system-architecture

#### {#arch-realtime-prd} PRD Intent 

Deliver **near real-time messaging (p95 < 500 ms)** using a
**WebSocket-based layer (e.g., Socket.io)**. The AI should respond
**only when explicitly invoked** (e.g., @mention). Room history must be
**persistent** and efficiently loadable.

#### {#arch-realtime-events} Transport & Core Events 

-   Use **Socket.io** for the real-time transport. Implement events:
    -   **Client → joinRoom** { roomId } → server subscribes socket to that room/channel.
    -   **Client → sendMessage** { roomId, content } → **persist** message with isFromAi:false, then **broadcast** receiveMessage to the room.
    -   **Server → receiveMessage** → emits the full **Message** object.

#### {#arch-realtime-history} History Retrieval (HTTP) 

-   Expose **GET** /api/rooms/:roomId/messages?cursor=<cursorId> with **cursor-based pagination** (e.g., fetch 50 before cursor) for efficient history loading.

#### {#arch-realtime-ai} AI Streaming Integration 

-   Within sendMessage, **detect @AIName** mentions. If present, still **save & broadcast** the human message. Then enqueue an **async job** to the **AI Gateway** which **streams aiChunk events** back to the room; on completion, **persist a final Message** with isFromAi:true.

#### {#arch-realtime-perf} Performance Budgets & Scale Readiness 

-   **DB hot-path budget:** queries involved in real-time ops (e.g., send) **< 50 ms**.

-   **End-to-end SLO:** in-region p95 **< 500 ms** for message delivery.

-   **Horizontal fan-out:** prepare a **Redis Pub/Sub** adapter for cross-instance broadcasting (recommended even if MVP runs single instance).

Note: Ordering/back-pressure policies are not specified in the Source of
Truth.

#### {#arch-realtime-acceptance} Acceptance Criteria 

-   joinRoom subscribes sockets to room channels; users in the room receive subsequent broadcasts.
-   sendMessage **persists** (isFromAi:false) and **broadcasts** receiveMessage.
-   History API returns paginated results using **cursor-based** queries (e.g., 50 before cursor).
-   AI flow: @mention triggers async **Gateway**; clients receive **aiChunk** stream; final AI message is **persisted** with isFromAi:true.
-   p95 E2E latency **< 500 ms**; DB time on hot path **< 50 ms**; Redis Pub/Sub configured for multi-instance broadcast.

#### {#arch-realtime-tests} Test Cases 

1.  **TC-ARCH-REALTIME-01 --- Room Subscription:** After joinRoom, publish a message to that room; client receives it via receiveMessage.
2.  **TC-ARCH-REALTIME-02 --- Persist-then-Broadcast:** Invoke sendMessage; verify DB insert with isFromAi:false and broadcast delivery to other members.
3.  **TC-ARCH-REALTIME-03 --- Cursor Pagination:** Call history API with a cursor; confirm prior **N** (e.g., 50) messages are returned and ordering matches expectations.
4.  **TC-ARCH-REALTIME-04 --- AI Streaming Path:** Send a message containing **@AIName**; verify human message saved/broadcast, **aiChunk** events streamed, and final AI message persisted with isFromAi:true.
5.  **TC-ARCH-REALTIME-05 --- Performance SLOs:** Synthetic load test shows p95 E2E latency **< 500 ms** and DB time **< 50 ms** on the send path.
6.  **TC-ARCH-REALTIME-06 --- Cross-Node Broadcast:** Deploy two instances with **Redis Pub/Sub**; verify messages fan out across nodes without code changes to module interfaces.

### {#arch-storage} Storage & ORM 

**Section ID:** ARCH-STORAGE\
**Version:** 1.0.0\
**Tags:** prisma, schema, cursor-pagination, data-reservoir, privacy\
**Parent ID:** system-architecture

#### {#arch-storage-prd} PRD Intent 

Persist room history and relationships in a **structured schema** that
supports efficient loading now and analytics later ("Data Reservoir").
Treat chat content as **sensitive data** with provisions for secure
handling.

#### {#arch-storage-orm} Authoritative ORM 

-   Use **Prisma**; the Prisma schema is the **single source of truth**. Changes to core models require **architectural review**.

#### {#arch-storage-models} Core Models (baseline shown in spec) 

-   **User**: id (uuid), email @unique, username @unique.
-   **Room**: id (uuid), name.
-   **Message**: id (uuid), content, isFromAi @default(false); relations exist but are not expanded in the excerpt.

#### {#arch-storage-history} History Retrieval 

-   Provide **GET** /api/rooms/:roomId/messages?cursor=<cursorId> using **cursor-based pagination**; fetch a fixed page (e.g.,**50**) before the cursor. Implemented with Prisma.

#### {#arch-storage-invariants} Write Path Invariants 

-   On send, **persist** message first, then broadcast; AI replies are saved as final **Message with isFromAi:true** after streaming.

#### {#arch-storage-reservoir} Data Reservoir Readiness 

-   Design schemas for clear **User ↔ Room ↔ Message** relationships and accurate timestamps to support future analytics ingestion.

#### {#arch-storage-privacy} Privacy & Logging 

-   **Do not log PII or message content**; use IDs for traceability. Encrypt **sensitive data** at rest when applicable (e.g., future BYOK keys).

Encryption at rest/in transit is a PRD expectation for sensitive user
data; exact fields/algorithms are not specified in the excerpts.

#### {#arch-storage-acceptance} Acceptance Criteria 

-   Prisma schema exists with core models **User/Room/Message** as specified; alterations to these models show **architectural review**.
-   History endpoint returns paginated results using **cursor-based queries** (e.g., 50 prior messages).
-   Send path **persists then broadcasts**; AI final output is stored with **isFromAi:true**.
-   Logs contain **IDs only**; **no PII/message text** is written.

#### {#arch-storage-tests} Test Cases 

1.  **TC-ARCH-STORAGE-01 --- Schema Authority:** Attempt to change a core model (e.g., Message); CI/process requires **architectural review** before merge.
2.  **TC-ARCH-STORAGE-02 --- Cursor Pagination:** Call history API with a valid cursor; verify **≤ 50** earlier messages returned and ordering is consistent.
3.  **TC-ARCH-STORAGE-03 --- Persist-then-Broadcast:** On sendMessage, confirm DB insert precedes broadcast; AI stream concludes with a stored message where **isFromAi:true**.
4.  **TC-ARCH-STORAGE-04 --- Privacy Logging:** Exercise auth, room, and messaging flows; inspect logs for **IDs-only**, with no emails or message bodies.

### {#arch-ai-gateway} AI Gateway 

**Section ID:** ARCH-AI-GATEWAY\
**Version:** 1.0.0\
**Tags:** ai-gateway, streaming, @mention, async-jobs, privacy\
**Parent ID:** system-architecture

#### {#arch-ai-gateway-prd} PRD Intent 

The AI must respond **only when explicitly addressed** (e.g., via an
@mention), preserving human conversation flow and controlling cost. AI
replies appear in the same room stream, clearly attributed as AI.

#### {#arch-ai-gateway-invoke} Invocation Detection (within sendMessage) 

-   On each sendMessage, parse content for an **@AIName**.
-   Regardless of invocation, **save & broadcast** the human message first.
-   If invoked, enqueue a **separate asynchronous job** to the **AI Gateway Module**.

#### {#arch-ai-gateway-stream} Provider Call & Streaming 

-   The **AI Gateway** calls the external AI API and **streams tokens back** to the room as **aiChunk** WebSocket events.
-   When the stream completes, create a **final Message** with **isFromAi:true** and persist it.

#### {#arch-ai-gateway-delivery} Room Delivery Contract 

-   Streaming goes to the **same room** as the triggering human message; clients subscribe via joinRoom and receive receiveMessage/aiChunk accordingly. (See Real-time layer.)

#### {#arch-ai-gateway-perf} Performance Alignment 

-   Gateway behavior must not violate the **near real-time** SLO (p95 **< 500 ms** E2E delivery target). **DB hot-path** queries remain **< 50 ms**. (The SLO is defined in NFR-003 / PRD.)

#### {#arch-ai-gateway-ratelimit} Rate Limiting (cross-ref FR/NFR) 

-   **Basic AI rate limiting** is part of the MVP scope; enforce limits at or before the Gateway boundary. (Implementation specifics are defined in the FR/NFR sections.)

#### {#arch-ai-gateway-privacy} Privacy & Secrets Handling 

-   **Do not log PII or message content**; use IDs for tracing.
-   Any **BYOK API keys (future)** must be **encrypted at rest**; tokens/keys must never appear in logs.

Not specified in the Source of Truth: exact aiChunk payload shape,
retry/timeout policies, and provider selection. These will be finalized
during implementation.

#### {#arch-ai-gateway-acceptance} Acceptance Criteria 

-   Messages **without** an @mention **do not** invoke the AI; messages **with** an @mention **do** enqueue a Gateway job. The human message is **persisted and broadcast** in both cases.
-   During invocation, clients in the room receive **aiChunk** stream events, and a **final AI message** is persisted with **isFromAi:true**.
-   System meets **p95 < 500 ms** E2E chat experience target; DB hot-path **< 50 ms**.
-   Logs contain **IDs only** (no PII, no tokens); if BYOK is enabled, keys are **encrypted**.

#### {#arch-ai-gateway-tests} Test Cases 

1.  **TC-ARCH-AI-01 --- Explicit Invocation Only:** Send a message **without** @mention → **no** AI job fired. Send message **with** @mention → **job enqueued**. In both, human message is saved & broadcast.
2.  **TC-ARCH-AI-02 --- Streaming Delivery:** For an invoked message, verify room receives **aiChunk** events and a **final persisted** AI message (isFromAi:true).
3.  **TC-ARCH-AI-03 --- Real-time SLO Compliance:** Under synthetic load, confirm p95 E2E **< 500 ms** and DB hot-path **< 50 ms** during AI streaming.
4.  **TC-ARCH-AI-04 --- Privacy Logging Guard:** Exercise invocation; inspect logs to ensure **no PII or tokens**, IDs-only tracing.
5.  **TC-ARCH-AI-05 --- Rate Limit Enforcement (MVP):** Trigger multiple rapid invocations; verify **basic AI rate limit** blocks excess per MVP story.

# {#data-models} 6. Data Models 

**Section ID:** DATA-MODELS\
**Version:** 1.0.0\
**Tags:** schema, prisma, user-room-message, membership, ai-invocation, privacy\
**Parent ID:** specification

#### {#data-models-prd} PRD Intent 

Persist chat history and relationships in a structured schema that
supports current features (auth, rooms, real-time messaging, history)
and the future **Data Reservoir** vision. Treat chat content as
**sensitive data** with provisions for encryption and future
export/deletion workflows.

#### {#model-user} User 

The Prisma schema below is authoritative; no changes to core models
without architectural review.

```
model User {
    id String @id @default(uuid())\
    email String @unique\
    username String @unique\
    passwordHash String\
    tier String @default("Free")\
    createdAt DateTime @default(now())\
    memberships RoomMembership[]\
    messages Message[]\
    aiInvocations AIInvocation[]\
}
```

#### {#model-room} Room 

The Prisma schema below is authoritative; no changes to core models
without architectural review.

```
model Room {
    id String @id @default(uuid())\
    name String\
    shareableLink String @unique\
    isEducation Boolean @default(false)\
    memberships RoomMembership[]\
    messages Message[]\
    aiInvocations AIInvocation[]\
    createdAt DateTime @default(now())\
}
```

#### {#model-roommembership} RoomMembership (linking table) 

The spec **explicitly uses** a RoomMembership record when creating or
joining a room (owner membership on create; member on join). **Field
list is not enumerated** in the schema excerpt; implement as a standard
**User↔Room** link during development.

The Prisma schema below is authoritative; no changes to core models
without architectural review.

```
model RoomMembership {\
    id String @id @default(uuid())\
    roomId String\
    userId String\
    role Role @default(MEMBER)\
    room Room @relation(fields: [roomId], references: [id], onDelete:\ Cascade, onUpdate: Cascade)\
    user User @relation(fields: [userId], references: [id], onDelete:\ Cascade, onUpdate: Cascade)\
    @@unique([roomId, userId], name: "room_user_unique")\
}
```

enum Role { OWNER MEMBER }

#### {#model-message} Message 

The Prisma schema below is authoritative; no changes to core models
without architectural review.

```
model Message {\
    id String @id @default(uuid())\
    roomId String\
    userId String\
    content String\
    room Room @relation(fields: [roomId], references: [id], onDelete: Cascade, onUpdate: Cascade)\
    user User @relation(fields: [userId], references: [id], onDelete: restrict, onUpdate: Cascade)\
    isFromAi Boolean @default(false)\
    createdAt DateTime @default(now())\
    @@index([roomId, createdAt])\
}
```

#### {#model-aiinvocation} AIInvocation 

The spec describes an **async job** to an **AI Gateway** and a **final
persisted Message with isFromAi:true**. No separate AIInvocation model
is shown; if needed, define during implementation to track provider
status/timing.

The Prisma schema below is authoritative; no changes to core models
without architectural review.

```
model AIInvocation {\
    id String @id @default(uuid())\
    roomId String\
    userId String // who invoked\
    triggerMsg String // human message id\
    model String\
    tokensIn Int?\
    tokensOut Int?\
    status String // QUEUED | RUNNING | SUCCEEDED | FAILED | TIMEOUT\
    errorCode String?\
    createdAt DateTime @default(now())\
    completedAt DateTime?\
    room Room @relation(fields: [roomId], references: [id], onDelete: Cascade, onUpdate: Cascade)\
    user User @relation(fields: [userId], references: [id], onDelete: Cascade, onUpdate: Cascade)\
    trigger Message @relation(fields: [triggerMsg], references: [id],
    onDelete: Restrict, onUpdate: Cascade)\
}
```

#### {#data-models-relationships} Data Model Relationships 

**Purpose:** lock down **cardinalities, foreign keys, and referential actions** so querying, pagination, and analytics are reliable an RAG-friendly.

Relationship map (cardinality)

-   **User 1 --- ↔ --- N RoomMembership --- ↔ --- 1 Room ** (membership is the join table; each user can belong to many rooms, each room has many users)
-   **Room 1 --- N Message** (all messages live inside exactly one room)
-   **User 1 --- N Message** (each message has exactly one author; AI messages use a reserved AI user id)
-   **Room 1 --- N AIInvocation**, **User 1 --- N AIInvocation**, **Message 1 --- 0..1 AIInvocation** (optional link from the human "trigger" message to its AI generation)

Constraints & indexes (at-a-glance)

-   **Uniqueness:** one membership per (roomId, userId) pair.
-   **History pagination:** compound index on (roomId, createdAt) for GET /rooms/:roomId/messages?cursor=....
-   **Integrity on deletes:**
    -   Deleting a **room** cascades its **memberships**, **messages**, and **AIInvocation** records.
    -   Deleting a **user** cascades **memberships** but **restricts** if there are authored messages (prevents orphaned content).
    -   Deleting a **trigger message** is **restricted** if it has an AIInvocation (preserve ledger integrity).

#### {#data-models-notes} Notes (for migrations & RAG clarity) 

-   **@@unique([roomId, userId])** replaces the non-unique index so a user can't join the same room twice.
-   **onDelete: Restrict for Message.user** preserves authored history; if you need GDPR-style deletion later, switch to soft-deletes or userId reassignment to an anonymized "DeletedUser".
-   **AIInvocation.trigger** keeps a verifiable chain from a human message → AI output; restrict delete to avoid breaking lineage.
-   All relation names are explicit to make chunked retrieval and codegen simpler for your RAG pipeline.

#### {#data-models-history} History & Pagination 

HTTP: **GET** /api/rooms/:roomId/messages?cursor=<cursorId> with
**cursor-based pagination**; fetch a fixed count (e.g., **50**) before
the cursor. (Implies ordered index on message time/ID.)

#### {#data-models-privacy} Privacy & Logging Constraints (schema-adjacent) 

**Encrypt sensitive data** (esp. future BYOK keys) and **never log PII
or message content**; use IDs for tracing. These constraints guide
column choices and audit fields.

#### {#data-models-acceptance} Acceptance Criteria 

-   The repository contains the **Prisma schema** with User, Room, and Message models exactly as specified; changes to these models require **architectural review**.
-   Room creation and joining flows **create RoomMembership** records per spec logic.
-   AI flows **persist a final Message** with isFromAi:true after streaming.
-   History endpoint implements **cursor-based pagination** (e.g., 50 messages) via Prisma.
-   Logs contain **IDs only** (no emails or message bodies); sensitive secrets are **encrypted** at rest.

#### {#data-models-tests} Test Cases 

1.  **TC-DATA-MODELS-01 --- Schema Authority:** Attempt to modify User/Room/Message without architectural review → change is blocked per governance.
2.  **TC-DATA-MODELS-02 --- Membership Creation:**
    -   Create room → verify owner **RoomMembership** exists.
    -   Join by link → verify new **RoomMembership** for the joining user.
3.  **TC-DATA-MODELS-03 --- AI Finalization:** Invoke AI → confirm a final Message with **isFromAi:true** is persisted after the stream.
4.  **TC-DATA-MODELS-04 --- Cursor Pagination:** Populate long history; GET with cursor returns **≤ 50** prior messages in correct order.
5.  **TC-DATA-MODELS-05 --- Privacy Logging:** Exercise auth/room/message flows; verify logs contain **IDs only** and no PII/message text; BYOK secrets (if present) are encrypted.

# {#acceptance-tests} 7. Acceptance Criteria & Test Mapping 

**Section ID:** ACCEPTANCE-MAP\
**Version:** 1.0.0\
**Tags:** traceability, acceptance, tests, coverage\
**Parent ID:** specification

#### {#acceptance-tests-fr} Traceability Matrix --- Functional Requirements 

-   **FR-001 --- Auth**

    -   **Interfaces:** POST /api/auth/register, POST /api/auth/login; **Model:** User.
    -   **Acceptance (key):** Validations enforced; JWT returned on success.
    -   **Tests:** TC-FR-001-01...05 (register/login happy paths, dupes, password hashing). *(As defined under FR-001.)*

-   **FR-002 --- Create & Manage Rooms**

    -   **Interfaces:** GET /api/rooms, POST /api/rooms, POST /api/rooms/join; **Model:** Room, **link:** RoomMembership.
    -   **Acceptance (key):** Room creation emits **shareableLink** and owner membership; join by link creates membership.
    -   **Tests:** TC-FR-002-01...04 (list/create/join/roles). *(From FR-002 section.)*

-   **FR-003 --- Join via Shareable Link**

    -   **Interfaces:** POST /api/rooms/join; **Model:** RoomMembership.
    -   **Acceptance (key):** Valid link → membership created; auth required.
    -   **Tests:** TC-FR-003-01...03.

-   **FR-004 --- Real-time Messaging**

    -   **Interfaces (WS):** joinRoom, sendMessage → **persist** → broadcast receiveMessage;
    -   **History (HTTP):** cursor pagination.
    -   **Acceptance (key):** Persist-then-broadcast; subscribed clients receive; history pages by cursor.
    -   **Tests:** TC-FR-004-01...06.

-   **FR-005 --- Explicit AI Invocation**

    -   **Behavior:** AI replies **only** when explicitly invoked (e.g., @mention); stream aiChunk; persist final AI message (isFromAi:true).
    -   **Tests:** TC-FR-005-01...07.

-   **FR-006 --- Persistent Chat History**

    -   **Interfaces:** GET /api/rooms/:roomId/messages?cursor=<id>; **Index:** @@index([roomId, createdAt]).
    -   **Acceptance (key):** Backward/forward pagination with stable ordering and no dupes. *(See FR-006 acceptance.)*
    -   **Tests:** TC-FR-006-01...06.

-   **FR-007 --- AI Rate Limiting**

    -   **Behavior:** Token-bucket style limits per user/room; deny over-quota before enqueue. *(MVP scope.)*
    -   **Tests:** TC-FR-007-01...06.

-   Anything marked "Post-MVP / Not specified in the Source of Truth" will get tests when those epics are formally scoped in the PRD/Tech Spec.

#### {#acceptance-tests-nfr} Traceability Matrix --- Non-Functional Requirements 

-   **NFR-001 --- UI Simplicity**
    -   **Focus:** Minimalist SPA, mobile-first, shadcn/ui + Tailwind.
    -   **Tests:** TC-NFR-001-01...06.

-   **NFR-002 --- Modular Monolith Architecture**
    -   **Focus:** apps/web/src/server/modules/*, service-only cross-talk, no cross-ORM imports, Prisma as source of truth.
    -   **Tests:** TC-NFR-002-01...04.

-   **NFR-003 --- Real-time Performance**
    -   **SLOs:** p95 E2E **< 500 ms**; DB hot path **< 50 ms**; Socket.io + Redis Pub/Sub readiness.
    -   **Tests:** TC-NFR-003-01...04.

-   **NFR-004 --- Data Reservoir Design**
    -   **Focus:** Structured User↔Room↔Message with timestamps; append-friendly; analytics-ready; no content in logs.
    -   **Tests:** TC-NFR-004-01...04.

-   **NFR-005 --- Data Privacy & Compliance**
    -   **Focus:** No PII/message text in logs; passwords hashed; PII owned by User and referenced by IDs.
    -   **Tests:** TC-NFR-005-01...05.

-   **NFR-006 --- Accessibility (WCAG 2.1 AA)**
    -   **Focus:** Keyboard-only operability; visible focus/contrast; mobile & desktop.
    -   **Tests:** TC-NFR-006-01...04.

#### {#acceptance-tests-plan} Execution Plan & Coverage Notes 

-   **Smoke (P0):** FR-001/002/004/005 paths; NFR-003 latency checks at low load.
-   **Core Regression (P1):** History pagination, rate limiting, schema governance.
-   **Non-functional (P1/P2):** Accessibility pass (keyboard/contrast), privacy log audit.

# {#implementation-notes} 8. Implementation Notes 

**Section ID:** IMPLEMENTATION-NOTES\
**Version:** 1.0.0\
**Tags:** patterns, service-layer, performance, privacy, governance\
**Parent ID:** specification

#### {#implementation-notes-patterns} Key technical patterns 

-   **Modular Monolith discipline.** Keep backend under apps/web/src/server/modules/; **no cross-module ORM access**; all cross-module calls happen via **service interfaces**.
-   **Real-time "persist → broadcast".** sendMessage must **persist** (isFromAi:false) then **broadcast** receiveMessage; joinRoom subscribes sockets; history over HTTP with cursor pagination.
-   **AI streaming path.** On explicit invocation, dispatch async job to **AI Gateway**; stream **aiChunk** events; on completion, **persist final Message** with isFromAi:true.
-   **Design system enforcement.** Frontend uses **shadcn/ui + Tailwind**; avoid bespoke CSS where utilities exist.
-   **Schema governance.** **Prisma schema is the source of truth**; changing core models requires **architectural review**.
-   **Room onboarding flows.** On create: generate **unguessable shareableLink** + owner RoomMembership; on join: create membership from shareableLink.
-   **Privacy-by-default.** **Encrypt** sensitive data (e.g., future BYOK keys). **Do not log PII or message bodies**; use IDs for tracing.

**Not specified in the Source of Truth:** retry/back-pressure policies,
exact aiChunk payload shape.

#### {#implementation-notes-boundaries} Service layer boundaries 

-   **Boundary rule.** A module must **not** import another module's Prisma models (e.g., chat cannot read user tables directly). Use service methods (e.g., userService.getUserById) for cross-module reads.
-   **AI Gateway contract.** Invocation is **explicit only** (per PRD). sendMessage still saves/broadcasts the human message before enqueuing Gateway work; Gateway owns provider calls and streaming.
-   **Real-time/HTTP seam.** WebSocket handles live fan-out; **history** is HTTP with **cursor** queries (fixed page, e.g., 50).
-   **Security at the boundary.** Enforce "IDs-only logging" and secret storage rules across services (Gateway included).

#### {#implementation-notes-performance} Performance targets 

-   **End-to-end chat latency:** **p95 < 500 ms** (in-region).
-   **DB hot path (send/history):** **< 50 ms** for real-time operations.
-   **History paging:** **Cursor-based pagination** with fixed page size (e.g., 50).
-   **Scale readiness:** Prepare **Redis Pub/Sub** for cross-instance broadcasts (even if MVP is single-instance).

**Not specified in the Source of Truth:** precise queue time budgets,
ordering guarantees under load.

#### {#implementation-notes-acceptance} Acceptance Criteria 

-   All backend packages follow apps/web/src/server/modules/*; **no cross-module ORM imports**; cross-module calls use services.
-   sendMessage path implements **persist → broadcast**; AI path streams **aiChunk** and persists final AI message.
-   History API uses **cursor** queries and returns a fixed page (e.g., 50).
-   System observes **p95 < 500 ms** and **DB hot path < 50 ms** in baseline tests; Redis adapter is deployable.
-   Logs contain **IDs only**; sensitive secrets are **encrypted at rest**.

#### {#implementation-notes-tests} Test Cases 

1.  **TC-IMPL-01 --- Boundary compliance scan:** Search codebase for cross-module Prisma imports; fail build if found.
2.  **TC-IMPL-02 --- Persist-then-broadcast:** Unit/integration test for sendMessage: DB insert precedes broadcast; receiveMessage observed by room peers.
3.  **TC-IMPL-03 --- AI streaming contract:** Invoke via explicit mention; verify human message saved/broadcast, **aiChunk** events streamed, final AI message persisted (isFromAi:true).
4.  **TC-IMPL-04 --- Cursor pagination:** Populate long history; call GET /rooms/:roomId/messages?cursor and assert fixed page behavior and ordering.
5.  **TC-IMPL-05 --- Performance budget:** Load test shows chat p95 **< 500 ms** and DB hot path **< 50 ms**; document Redis Pub/Sub readiness.

# {#future-epics} 9. Future Epics 

**Section ID:** FUTURE_EPICS\
**Version:** 1.0.0\
**Tags:** post-mvp, monetization, education, file-sharing\
**Parent ID:** specification

These epics are explicitly **post-MVP** in the PRD roadmap. Details
below are grounded to the PRD's "Post-MVP Vision" section.

#### {#future-epics-monetization} Monetization & Tiering 

**PRD Intent**

Implement **Free**, **Premium**, and **Bring Your Own Key (BYOK)** user
tiers. Integrate a payment gateway (e.g., **Stripe**), add a
**subscription management UI** in account settings, and enforce
**feature entitlements** in the backend per tier.

**Scope & Notes (from PRD)**

-   Payment processing via a third-party provider (example given: Stripe).
-   Settings surface for subscription status and (future) API keys.
-   Backend checks to gate features by tier.

**Acceptance Outline (to refine when scoped)**

-   Users can start/cancel a paid plan and see current tier in **Settings**.
-   Entitlement checks prevent access to features outside a user's tier.

**Test Cases (shell)**

-   **TC-FUTURE-MON-01**: Starting a subscription updates tier and unlocks premium entitlements.
-   **TC-FUTURE-MON-02**: BYOK flow stores keys in Settings (UI present) but respects privacy/encryption rules when implemented.

#### {#future-epics-education} Education-Specific Features 

**PRD Intent**

Deliver an **Educational Platform**: **teacher dashboard**, **content
moderation & safety filters**, **student engagement analytics**, and
tools for creating **assignments** within the platform.

**Scope & Notes** (from PRD)

-   Admin/teacher oversight of student chats.
-   Safety and moderation layer appropriate for classrooms.
-   Analytics for engagement.
-   Assignment authoring inside the app.

**Acceptance Outline** (to refine when scoped)

-   Teachers can view classroom activity and apply moderation actions.
-   Assignment creation and distribution are available in the teacher workflow.

**Test Cases** (shell)

-   **TC-FUTURE-EDU-01**: Teacher dashboard lists classes/rooms an recent student activity.
-   **TC-FUTURE-EDU-02**: Moderation action (e.g., restrict) is applied and reflected in room behavior.
-   **TC-FUTURE-EDU-03**: Assignment creation publishes to a target cohort.

#### {#future-epics-files} File Sharing & Media Handling 

**PRD Intent**

Enable users to **upload and share files** (images, documents, code
snippets) in chat. Use **object storage** (e.g., **AWS S3**). Provide a
**secure upload/download pipeline** and **in-chat previews**.

**Scope & Notes (from PRD)**

-   Storage provider integration and signed URLs for secure transfer (implied by "secure pipeline").
-   Rendering previews within the chat interface.

**Acceptance Outline (to refine when scoped)**

-   A user can upload a file; others in the room can securely download it.
-   In-chat preview renders for supported types.

**Test Cases (shell)**

-   **TC-FUTURE-FILES-01**: Upload → generates object-store URL; download works only for room members.
-   **TC-FUTURE-FILES-02**: Preview displays for images/docs listed as supported.
