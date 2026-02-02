# TaskSync API Testing Guide

This document provides all the API endpoints with request/response examples for testing with Postman or integrating with a frontend.

**Base URL:** `http://localhost:8000/api/v1`

---

## Authentication

All endpoints (except login/register) require a JWT token in the header:

```
Authorization: Bearer <your_token>
```

### Get Token (Login)

```http
POST /users/login
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

---

## Boards

### Create Board

```http
POST /boards/
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "Project Alpha",
  "description": "Main project board",
  "color": "#FF5733"
}
```

**Response (201):**
```json
{
  "id": 1,
  "name": "Project Alpha",
  "description": "Main project board",
  "color": "#FF5733",
  "owner_id": 1,
  "created_at": "2026-02-02T10:00:00Z",
  "member_count": 1
}
```

### Get All Boards

```http
GET /boards/
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Project Alpha",
    "description": "Main project board",
    "color": "#FF5733",
    "owner_id": 1,
    "created_at": "2026-02-02T10:00:00Z",
    "member_count": 2
  }
]
```

### Get Board by ID

```http
GET /boards/1
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "name": "Project Alpha",
  "description": "Main project board",
  "color": "#FF5733",
  "owner_id": 1,
  "created_at": "2026-02-02T10:00:00Z",
  "member_count": 2,
  "members": [
    {
      "user_id": 1,
      "email": "owner@example.com",
      "role": "admin",
      "joined_at": "2026-02-02T10:00:00Z"
    }
  ]
}
```

### Update Board

```http
PUT /boards/1
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "Project Alpha v2",
  "color": "#3B82F6"
}
```

### Delete Board

```http
DELETE /boards/1
Authorization: Bearer <token>
```

**Response:** `204 No Content`

### Add Member to Board

```http
POST /boards/1/members
Content-Type: application/json
Authorization: Bearer <token>

{
  "email": "teammate@example.com",
  "role": "member"
}
```

### Remove Member from Board

```http
DELETE /boards/1/members/2
Authorization: Bearer <token>
```

---

## Lists

### Create List

```http
POST /boards/1/lists
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "To Do"
}
```

**Response (201):**
```json
{
  "id": 1,
  "name": "To Do",
  "position": 0,
  "board_id": 1,
  "created_at": "2026-02-02T10:00:00Z"
}
```

### Get All Lists for Board

```http
GET /boards/1/lists
Authorization: Bearer <token>
```

**Response:**
```json
[
  {"id": 1, "name": "To Do", "position": 0, "board_id": 1, "created_at": "..."},
  {"id": 2, "name": "In Progress", "position": 1, "board_id": 1, "created_at": "..."},
  {"id": 3, "name": "Done", "position": 2, "board_id": 1, "created_at": "..."}
]
```

### Get List by ID

```http
GET /lists/1
Authorization: Bearer <token>
```

### Update List

```http
PUT /lists/1
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "Backlog"
}
```

### Move/Reorder List

```http
PATCH /lists/3/move
Content-Type: application/json
Authorization: Bearer <token>

{
  "position": 0
}
```

**Result:** Moves "Done" list from position 2 to position 0, shifting other lists.

### Delete List

```http
DELETE /lists/1
Authorization: Bearer <token>
```

---

## Labels

### Create Label

```http
POST /boards/1/labels
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "Bug",
  "color": "#FF0000"
}
```

**Response (201):**
```json
{
  "id": 1,
  "name": "Bug",
  "color": "#FF0000",
  "board_id": 1,
  "created_at": "2026-02-02T10:00:00Z"
}
```

### Get All Labels for Board

```http
GET /boards/1/labels
Authorization: Bearer <token>
```

**Response:**
```json
[
  {"id": 1, "name": "Bug", "color": "#FF0000", "board_id": 1, "created_at": "..."},
  {"id": 2, "name": "Feature", "color": "#00FF00", "board_id": 1, "created_at": "..."},
  {"id": 3, "name": "Urgent", "color": "#FFA500", "board_id": 1, "created_at": "..."}
]
```

### Get Label by ID

```http
GET /labels/1
Authorization: Bearer <token>
```

### Update Label

```http
PUT /labels/1
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "Critical Bug",
  "color": "#CC0000"
}
```

### Delete Label

```http
DELETE /labels/1
Authorization: Bearer <token>
```

### Attach Label to Card

```http
POST /cards/1/labels/2
Authorization: Bearer <token>
```

**Response (201):**
```json
{
  "message": "Label attached successfully"
}
```

### Detach Label from Card

```http
DELETE /cards/1/labels/2
Authorization: Bearer <token>
```

---

## Cards

### Create Card

```http
POST /lists/1/cards
Content-Type: application/json
Authorization: Bearer <token>

{
  "title": "Fix login bug",
  "description": "Users can't login with email",
  "priority": "high",
  "due_date": "2026-02-15T10:00:00Z"
}
```

**Response (201):**
```json
{
  "id": 1,
  "title": "Fix login bug",
  "description": "Users can't login with email",
  "completed": false,
  "priority": "high",
  "position": 0,
  "due_date": "2026-02-15T10:00:00Z",
  "list_id": 1,
  "user_id": 1,
  "created_at": "2026-02-02T10:00:00Z",
  "updated_at": null
}
```

### Get Cards in List

```http
GET /lists/1/cards
Authorization: Bearer <token>
```

**Response:**
```json
[
  {"id": 1, "title": "Fix login bug", "position": 0, "list_id": 1, "...": "..."},
  {"id": 2, "title": "Add dark mode", "position": 1, "list_id": 1, "...": "..."}
]
```

### Get Card Details (with members & labels)

```http
GET /cards/1
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "title": "Fix login bug",
  "description": "Users can't login with email",
  "completed": false,
  "priority": "high",
  "position": 0,
  "due_date": "2026-02-15T10:00:00Z",
  "list_id": 1,
  "user_id": 1,
  "created_at": "2026-02-02T10:00:00Z",
  "updated_at": null,
  "members": [
    {"user_id": 2, "email": "dev@example.com", "assigned_at": "..."}
  ],
  "labels": [
    {"id": 1, "name": "Bug", "color": "#FF0000"}
  ]
}
```

### Update Card

```http
PUT /cards/1
Content-Type: application/json
Authorization: Bearer <token>

{
  "title": "Fix login bug (critical)",
  "completed": true,
  "priority": "high"
}
```

### Move Card

```http
PATCH /cards/1/move
Content-Type: application/json
Authorization: Bearer <token>

{
  "position": 2,
  "list_id": 2
}
```

**Result:** Moves card to position 2 in list 2 (from current list).

### Delete Card

```http
DELETE /cards/1
Authorization: Bearer <token>
```

### Assign User to Card

```http
POST /cards/1/members/2
Authorization: Bearer <token>
```

**Response (201):**
```json
{
  "message": "User assigned successfully"
}
```

### Unassign User from Card

```http
DELETE /cards/1/members/2
Authorization: Bearer <token>
```

---

## Common Color Codes

| Color | Hex Code | Use Case |
|-------|----------|----------|
| Red | `#FF0000` | Bug, Urgent |
| Green | `#00FF00` | Feature, Done |
| Blue | `#3B82F6` | Default board |
| Orange | `#FFA500` | Warning, Medium Priority |
| Purple | `#8B5CF6` | Enhancement |
| Yellow | `#FBBF24` | In Review |
| Gray | `#6B7280` | Backlog |

---

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "User not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Access denied to this board"
}
```

### 404 Not Found
```json
{
  "detail": "Board not found"
}
```

### 422 Validation Error
```json
{
  "detail": "Validation error",
  "errors": [
    {"field": "body.name", "message": "Field required"}
  ]
}
```

---

## Postman Collection Setup

1. Create environment variable: `base_url` = `http://localhost:8000/api/v1`
2. Create environment variable: `token` = `<your_jwt_token>`
3. For all requests, use header: `Authorization: Bearer {{token}}`

### Suggested Folder Structure

```
TaskSync API
├── Auth
│   └── Login
├── Boards
│   ├── Create Board
│   ├── Get All Boards
│   ├── Get Board by ID
│   ├── Update Board
│   ├── Delete Board
│   ├── Add Member
│   └── Remove Member
├── Lists
│   ├── Create List
│   ├── Get Lists for Board
│   ├── Update List
│   ├── Move List
│   └── Delete List
├── Labels
│   ├── Create Label
│   ├── Get Labels for Board
│   ├── Update Label
│   ├── Delete Label
│   ├── Attach to Card
│   └── Detach from Card
└── Cards
    ├── Create Card
    ├── Get Cards in List
    ├── Get Card Details
    ├── Update Card
    ├── Move Card
    ├── Delete Card
    ├── Assign Member
    └── Unassign Member
```

---

## Frontend Integration Notes

### Endpoints by Feature

| Feature | Endpoints |
|---------|-----------|
| Board List Page | `GET /boards/` |
| Board Detail Page | `GET /boards/{id}`, `GET /boards/{id}/lists`, `GET /boards/{id}/labels` |
| Create Board Modal | `POST /boards/` |
| List Management | `POST /boards/{id}/lists`, `PATCH /lists/{id}/move` |
| Label Management | `POST /boards/{id}/labels`, `PUT /labels/{id}` |
| Card Detail Modal | `GET /cards/{id}` (returns members & labels) |
| Card Management | `POST /lists/{id}/cards`, `PUT /cards/{id}`, `PATCH /cards/{id}/move` |
| Assign Members | `POST /cards/{id}/members/{user_id}` |
| Attach Labels | `POST /cards/{id}/labels/{label_id}` |

### WebSocket/Polling (Future)

For real-time updates, consider polling `GET /boards/{id}` every 30 seconds or implementing WebSocket support.
