# Library Management System - REST API Documentation

## Overview

This document describes the RESTful API design for the Library Management System following REST architecture principles.

### REST Design Principles Used:
1. **Plural nouns in URIs** - `/books`, `/members` (not `/book`, `/member`)
2. **No verbs in URIs** - Actions are determined by HTTP methods
3. **Stateless communication** - Each request contains all information needed
4. **Resource-based hierarchy** - `/members/{id}/books`

---

## Books API Endpoints

| HTTP Method | Endpoint | Description | Idempotent |
|-------------|----------|-------------|------------|
| GET | `/api/books` | Retrieve all books | Yes |
| GET | `/api/books/{id}` | Retrieve a specific book | Yes |
| POST | `/api/books` | Create a new book | No |
| PUT | `/api/books/{id}` | Update an existing book (full update) | Yes |
| PATCH | `/api/books/{id}` | Partial update a book | No |
| DELETE | `/api/books/{id}` | Delete a book | Yes |

### Example Requests:

```
GET /api/books
Response: 200 OK
[
    {
        "id": 1,
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "isbn": "978-0743273565",
        "published_year": 1925,
        "available_copies": 3
    },
    {
        "id": 2,
        "title": "1984",
        "author": "George Orwell",
        "isbn": "978-0451524935",
        "published_year": 1949,
        "available_copies": 5
    }
]
```

```
GET /api/books/1
Response: 200 OK
{
    "id": 1,
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "isbn": "978-0743273565",
    "published_year": 1925,
    "available_copies": 3
}
```

```
POST /api/books
Request Body:
{
    "title": "New Book",
    "author": "Author Name",
    "isbn": "978-1234567890",
    "published_year": 2024,
    "available_copies": 5
}
Response: 201 Created
```

```
PUT /api/books/1
Request Body:
{
    "title": "Updated Title",
    "author": "Updated Author",
    "isbn": "978-0743273565",
    "published_year": 1925,
    "available_copies": 10
}
Response: 200 OK
```

```
DELETE /api/books/1
Response: 204 No Content
```

---

## Members API Endpoints

| HTTP Method | Endpoint | Description | Idempotent |
|-------------|----------|-------------|------------|
| GET | `/api/members` | Retrieve all members | Yes |
| GET | `/api/members/{id}` | Retrieve a specific member | Yes |
| POST | `/api/members` | Create a new member | No |
| PUT | `/api/members/{id}` | Update an existing member (full update) | Yes |
| PATCH | `/api/members/{id}` | Partial update a member | No |
| DELETE | `/api/members/{id}` | Delete a member | Yes |

### Example Requests:

```
GET /api/members
Response: 200 OK
[
    {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+1234567890",
        "membership_date": "2024-01-15"
    }
]
```

```
GET /api/members/1
Response: 200 OK
{
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "membership_date": "2024-01-15"
}
```

```
POST /api/members
Request Body:
{
    "name": "Jane Smith",
    "email": "jane@example.com",
    "phone": "+0987654321",
    "membership_date": "2024-02-01"
}
Response: 201 Created
```

---

## Hierarchical Resource Routing

### Member's Books Endpoint

| HTTP Method | Endpoint | Description | Idempotent |
|-------------|----------|-------------|------------|
| GET | `/api/members/{id}/books` | Get all books borrowed by a member | Yes |

```
GET /api/members/1/books
Response: 200 OK
[
    {
        "issue_id": 1,
        "book": {
            "id": 1,
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald"
        },
        "issue_date": "2024-01-20",
        "due_date": "2024-02-20",
        "return_date": null,
        "status": "issued"
    }
]
```

---

## HTTP Methods Idempotency

### Idempotent Methods (Safe to retry)

| Method | Description | Example |
|--------|-------------|---------|
| **GET** | Retrieve data without side effects | Calling GET `/api/books` 10 times returns the same result |
| **PUT** | Replace existing resource | Calling PUT `/api/books/1` with same data produces same state |
| **DELETE** | Remove resource | Calling DELETE `/api/books/1` multiple times - first deletes, subsequent return 404 |
| **HEAD** | Like GET but without response body | Same idempotent properties as GET |
| **OPTIONS** | Returns allowed HTTP methods | Always returns same allowed methods |

### Non-Idempotent Methods (Not safe to retry)

| Method | Description | Example |
|--------|-------------|---------|
| **POST** | Create new resource | Calling POST `/api/books` creates a new book each time - different IDs |
| **PATCH** | Partial update | Applying PATCH multiple times may produce different intermediate states |

### Why Idempotency Matters:

```python
# Example: Non-idempotent POST
# First call creates book with ID=1
POST /api/books
# Second call creates book with ID=2 (different resource!)

# Example: Idempotent PUT
# First call updates book to new state
PUT /api/books/1
# Second call updates to same state (no change in result)
```

---

## REST Statelessness Explained

### What is Statelessness?

In REST architecture, **the server does not store any client state**. Each request from a client must contain all information the server needs to process that request. The server does not remember previous requests.

### Key Characteristics:

1. **No Session Storage** - Server doesn't store client context
2. **Self-Descriptive Messages** - Each request contains all needed information
3. **Every Request is Independent** - Server processes each request in isolation

### Example 1: Authentication Without State

**Without REST (Stateful):**
```
Client logs in once
Server stores session: {user_id: 123, logged_in: true}
Client makes request
Server checks: Is user logged in? → YES
```

**With REST (Stateless):**
```
Client sends credentials with EVERY request
Request: GET /api/books
Headers: Authorization: Bearer eyJhbGciOiJIUzI1...
Server validates token for EVERY request
Server never stores session
```

### Example 2: Shopping Cart

**Stateful Approach:**
```
1. Client adds item to cart
2. Server stores: {cart_id: 1, items: [book1]}
3. Client adds another item
4. Server updates: {cart_id: 1, items: [book1, book2]}
5. If server crashes, cart is lost
```

**REST Stateless Approach:**
```
1. Client stores cart locally: {items: [book1]}
2. Client sends complete cart with order:
   POST /api/orders
   {items: [book1, book2], shipping_address: "..."}
3. Server processes order - doesn't need to know previous state
4. If client refreshes, cart is still in localStorage
```

### Example 3: Pagination

**Stateful:**
```
1. Client requests page 1
2. Server stores: {user_page_1: [...]} in cache
3. Client requests page 2
4. Server uses cache to return page 2
```

**REST Stateless:**
```
1. Client requests: GET /api/books?page=1&limit=10
2. Server returns page 1 (knows nothing about previous requests)
3. Client requests: GET /api/books?page=2&limit=10
4. Server returns page 2 (completely independent request)
5. Each request contains all info needed: page=2, limit=10
```

### Advantages of Statelessness:

| Advantage | Description |
|-----------|-------------|
| **Scalability** | Server doesn't need to store client state; can handle more clients |
| **Reliability** | No state to lose if server crashes |
| **Simplicity** | Server logic is simpler - no session management |
| **Cacheability** | Responses can be cached since each request is complete |
| **Visibility** | Each request is self-contained - easier to debug and monitor |

### Disadvantages:

| Disadvantage | Description |
|--------------|-------------|
| **Bandwidth** | More data sent per request (authentication tokens) |
| **Client Complexity** | Client must manage state (localStorage, tokens) |
| **Repeat Data** | Same auth data sent with every request |

---

## Summary

| Concept | Description |
|---------|-------------|
| **REST** | Representational State Transfer |
| **Idempotent** | Same result no matter how many times called |
| **Stateless** | Each request contains all info needed |
| **Resources** | Nouns (books, members), not verbs (getBooks) |
| **HTTP Methods** | GET=Read, POST=Create, PUT=Replace, DELETE=Remove |

---

## Quick Reference

```
📚 Books
  GET    /api/books           → List all books
  GET    /api/books/{id}      → Get single book
  POST   /api/books           → Create book
  PUT    /api/books/{id}      → Update book
  DELETE /api/books/{id}      → Delete book

👥 Members
  GET    /api/members              → List all members
  GET    /api/members/{id}         → Get single member
  POST   /api/members              → Create member
  PUT    /api/members/{id}         → Update member
  DELETE /api/members/{id}         → Delete member

📖 Hierarchical
  GET    /api/members/{id}/books   → Get member's borrowed books
```

