# Library Management System - Project Documentation

---

## A Comprehensive Technical Report

**Course:** Software Engineering  
**Project:** Library Management System  
**Date:** Academic Year 2024-2025  
**Technology Stack:** Django, Bootstrap 5, REST API  

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Models Description](#3-models-description)
4. [Bootstrap UI Components](#4-bootstrap-ui-components)
5. [REST API Design](#5-rest-api-design)
6. [HTTP Methods Explanation](#6-http-methods-explanation)
7. [Statelessness in REST](#7-statelessness-in-rest)
8. [Idempotent Methods](#8-idempotent-methods)
9. [Conclusion](#9-conclusion)

---

## 1. Project Overview

### 1.1 Introduction

The Library Management System is a web-based application developed using Django (Python) and Bootstrap 5. This system provides comprehensive functionality for managing library resources, including book inventory management, member administration, and borrowing operations.

### 1.2 Objectives

The primary objectives of this project are:

1. To provide a user-friendly interface for library staff to manage books and members
2. To implement RESTful API endpoints for third-party integrations
3. To demonstrate modern web development practices using Bootstrap 5
4. To showcase understanding of REST architecture principles

### 1.3 Technology Stack

| Component | Technology |
|-----------|------------|
| Backend Framework | Django 4.x |
| Frontend Framework | Bootstrap 5 |
| Database | SQLite3 |
| Programming Language | Python 3.x |
| HTML/CSS | HTML5, CSS3 |
| Icons | Bootstrap Icons |

---

## 2. System Architecture

### 2.1 Overview

The system follows the Model-View-Template (MVT) architecture pattern, which is Django's implementation of the Model-View-Controller (MVC) pattern.

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Home      │  │   Books     │  │     Members          │ │
│  │   Page      │  │   Pages     │  │     Pages            │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Django Views (Controllers)               │   │
│  │  • home()    • book_list()    • member_list()      │   │
│  │  • book_create()  • member_create()                 │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  Django Models                       │   │
│  │  • Book    • Member    • BookIssue                 │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Project Structure

```
library_project/
├── manage.py
├── settings.py
├── urls.py
├── wsgi.py
├── library/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── migrations/
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── books/
│   │   ├── book_list.html
│   │   ├── book_detail.html
│   │   ├── book_form.html
│   │   └── book_delete.html
│   └── members/
│       ├── member_list.html
│       ├── member_detail.html
│       ├── member_form.html
│       └── member_delete.html
└── static/
    ├── css/
    ├── js/
    └── images/
```

### 2.3 URL Routing

The application uses Django's URL dispatcher to map URLs to views:

```python
# library/urls.py
urlpatterns = [
    path('', views.home, name='home'),
    path('books/', views.book_list, name='book_list'),
    path('books/create/', views.book_create, name='book_create'),
    path('books/<int:book_id>/', views.book_detail, name='book_detail'),
    path('books/<int:book_id>/update/', views.book_update, name='book_update'),
    path('books/<int:book_id>/delete/', views.book_delete, name='book_delete'),
    path('members/', views.member_list, name='member_list'),
    path('members/create/', views.member_create, name='member_create'),
    path('members/<int:member_id>/update/', views.member_update, name='member_update'),
    path('members/<int:member_id>/delete/', views.member_delete, name='member_delete'),
]
```

---

## 3. Models Description

### 3.1 Book Model

The Book model represents books in the library inventory.

```python
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13)
    published_year = models.IntegerField(
        validators=[MinValueValidator(1000), MaxValueValidator(datetime.now().year)]
    )
    available_copies = models.IntegerField(default=1)
    
    class Meta:
        ordering = ['title']
```

**Fields:**
| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| title | CharField(200) | Book title |
| author | CharField(200) | Author name |
| isbn | CharField(13) | ISBN number |
| published_year | IntegerField | Year of publication |
| available_copies | IntegerField | Number of available copies |

### 3.2 Member Model

The Member model represents library members.

```python
class Member(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    membership_date = models.DateField()
    
    class Meta:
        ordering = ['-id']
```

**Fields:**
| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| name | CharField(200) | Member full name |
| email | EmailField | Email address |
| phone | CharField(20) | Contact number |
| membership_date | DateField | Date of membership |

### 3.3 BookIssue Model

The BookIssue model tracks book borrowing operations.

```python
class BookIssue(models.Model):
    STATUS_CHOICES = [
        ('issued', 'Issued'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ]
    
    issue_id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    notes = models.TextField(blank=True)
```

**Fields:**
| Field | Type | Description |
|-------|------|-------------|
| issue_id | AutoField | Primary key |
| book | ForeignKey | Reference to Book |
| member | ForeignKey | Reference to Member |
| issue_date | DateField | Date book was issued |
| due_date | DateField | Due date for return |
| return_date | DateField | Actual return date |
| status | CharField | Issue status |
| notes | TextField | Additional notes |

---

## 4. Bootstrap UI Components

### 4.1 Navigation Bar

The application uses a sticky-top navbar with shadow for persistent navigation.

```html
<nav class="navbar navbar-expand-lg sticky-top shadow">
    <div class="container">
        <a class="navbar-brand" href="/">
            <i class="bi bi-book-half"></i> Library System
        </a>
        <div class="collapse navbar-collapse">
            <ul class="navbar-nav ms-auto">
                <li class="nav-item">
                    <a class="nav-link" href="/">Home</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="/books/">Books</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="/members/">Members</a>
                </li>
            </ul>
        </div>
    </div>
</nav>
```

**Classes Used:**
- `navbar` - Base navbar component
- `navbar-expand-lg` - Responsive expansion
- `sticky-top` - Fixed position at top
- `shadow` - Drop shadow effect

### 4.2 Dashboard Cards

The dashboard displays statistic cards with icons and hover effects.

```html
<div class="row g-4 mb-4">
    <div class="col-md-6">
        <div class="card shadow-lg rounded-3 h-100">
            <div class="card-body">
                <div class="d-flex align-items-center">
                    <div class="icon-wrapper books me-4">
                        <i class="bi bi-book"></i>
                    </div>
                    <div>
                        <div class="stat-value">{{ total_books }}</div>
                        <div class="stat-label">Total Books</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
```

**Bootstrap Utilities Applied:**
| Class | Purpose |
|-------|---------|
| `row` | Flex container |
| `g-4` | Gutter spacing |
| `col-md-6` | 6-column width on medium screens |
| `shadow-lg` | Large shadow |
| `rounded-3` | Rounded corners |
| `h-100` | Full height |
| `d-flex` | Flex display |
| `align-items-center` | Vertical alignment |

### 4.3 Book Cards (Grid Layout)

Books are displayed in a responsive card grid.

```html
<div class="row g-4 mb-4">
    {% for book in page_obj %}
    <div class="col-md-4">
        <div class="card shadow-lg rounded-3 h-100 book-card">
            <div class="card-body p-3">
                <!-- Book Info -->
                <h5 class="card-title">{{ book.title }}</h5>
                <div class="info-item">
                    <i class="bi bi-person"></i>
                    <span>{{ book.author }}</span>
                </div>
                <!-- Action Buttons -->
                <div class="d-flex gap-2">
                    <a href="..." class="btn btn-edit">
                        <i class="bi bi-pencil"></i> Edit
                    </a>
                    <a href="..." class="btn btn-delete">
                        <i class="bi bi-trash"></i> Delete
                    </a>
                </div>
            </div>
        </div>
    </div>
    {% endfor %}
</div>
```

### 4.4 Forms

Enhanced form components with input groups and icons.

```html
<div class="row g-4">
    <div class="col-md-6">
        <label for="title" class="form-label">Book Title</label>
        <div class="input-group">
            <span class="input-group-text">
                <i class="bi bi-book"></i>
            </span>
            <input type="text" class="form-control" id="title" name="title">
        </div>
    </div>
</div>
```

**Form Enhancement Classes:**
| Class | Purpose |
|-------|---------|
| `form-label` | Form label styling |
| `input-group` | Icon prefix container |
| `input-group-text` | Icon styling |
| `form-control` | Input field styling |
| `rounded-3` | Rounded corners |

### 4.5 Buttons

Gradient buttons with icon support.

```html
<a href="..." class="btn btn-primary-custom">
    <i class="bi bi-plus-circle"></i> Add Book
</a>

<a href="..." class="btn btn-action btn-edit">
    <i class="bi bi-pencil"></i> Edit
</a>

<a href="..." class="btn btn-action btn-delete">
    <i class="bi bi-trash"></i> Delete
</a>
```

---

## 5. REST API Design

### 5.1 API Endpoints

The API follows RESTful principles using plural nouns and HTTP methods.

#### Books API

| HTTP Method | Endpoint | Description | Example |
|-------------|----------|-------------|---------|
| GET | `/api/books` | List all books | ✓ |
| GET | `/api/books/{id}` | Get single book | ✓ |
| POST | `/api/books` | Create new book | ✓ |
| PUT | `/api/books/{id}` | Update book | ✓ |
| DELETE | `/api/books/{id}` | Delete book | ✓ |

#### Members API

| HTTP Method | Endpoint | Description |
|-------------|----------|-------------|
| GET | `/api/members` | List all members |
| GET | `/api/members/{id}` | Get single member |
| POST | `/api/members` | Create new member |
| PUT | `/api/members/{id}` | Update member |
| DELETE | `/api/members/{id}` | Delete member |

#### Hierarchical Resources

| HTTP Method | Endpoint | Description |
|-------------|----------|-------------|
| GET | `/api/members/{id}/books` | Get member's borrowed books |

### 5.2 Request/Response Examples

#### GET /api/books
```json
{
    "count": 2,
    "results": [
        {
            "id": 1,
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "isbn": "978-0743273565",
            "published_year": 1925,
            "available_copies": 3
        }
    ]
}
```

#### POST /api/books
```json
Request:
{
    "title": "New Book",
    "author": "Author Name",
    "isbn": "978-1234567890",
    "published_year": 2024,
    "available_copies": 5
}

Response: 201 Created
{
    "id": 3,
    "title": "New Book",
    "author": "Author Name",
    "isbn": "978-1234567890",
    "published_year": 2024,
    "available_copies": 5
}
```

---

## 6. HTTP Methods Explanation

### 6.1 Overview

HTTP defines a set of request methods to indicate the desired action to be performed on a resource.

| Method | Description | Request Body | Response Body |
|--------|-------------|--------------|---------------|
| GET | Retrieve data | No | Yes |
| POST | Create resource | Yes | Yes |
| PUT | Replace resource | Yes | Yes |
| PATCH | Partial update | Yes | Yes |
| DELETE | Remove resource | No | Optional |

### 6.2 GET Method

The GET method requests a representation of the specified resource.

**Characteristics:**
- Safe method (does not modify resources)
- Idempotent
- Can be cached
- Should only retrieve data

**Example:**
```
GET /api/books/1 HTTP/1.1
Host: example.com
Accept: application/json

HTTP/1.1 200 OK
Content-Type: application/json

{
    "id": 1,
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald"
}
```

### 6.3 POST Method

The POST method submits data to be processed by the identified resource.

**Characteristics:**
- Not safe (modifies server state)
- Not idempotent (multiple calls create multiple resources)
- Used for creating new resources

**Example:**
```
POST /api/books HTTP/1.1
Host: example.com
Content-Type: application/json

{
    "title": "New Book",
    "author": "Author Name"
}

HTTP/1.1 201 Created
Location: /api/books/5
```

### 6.4 PUT Method

The PUT method replaces all current representations of the target resource.

**Characteristics:**
- Not safe (modifies server state)
- Idempotent (multiple calls produce same result)
- Used for full resource updates

**Example:**
```
PUT /api/books/1 HTTP/1.1
Host: example.com
Content-Type: application/json

{
    "title": "Updated Title",
    "author": "Updated Author",
    "isbn": "978-0743273565",
    "published_year": 1925,
    "available_copies": 10
}
```

### 6.5 DELETE Method

The DELETE method removes the specified resource from the server.

**Characteristics:**
- Not safe (modifies server state)
- Idempotent (deleting same resource multiple times)
- Returns 404 on subsequent calls

**Example:**
```
DELETE /api/books/1 HTTP/1.1
Host: example.com

HTTP/1.1 204 No Content
```

---

## 7. Statelessness in REST

### 7.1 Definition

REST is fundamentally **stateless**. This means the server does not store any client state between requests. Each request from the client must contain all information the server needs to process that request.

### 7.2 Key Principles

1. **No Server-Side Session**
   - The server does not store user session data
   - Each request is independent

2. **Self-Contained Requests**
   - Each request includes authentication credentials
   - No reliance on previous requests

3. **Client-Side State**
   - Client maintains application state
   - State is passed with each request

### 7.3 Comparison

#### Stateful Approach (Traditional)
```
1. Client logs in
2. Server creates session: {session_id: "abc123", user: "john"}
3. Client requests page
4. Server checks session → "User is logged in"
5. Problem: If server restarts, session is lost
```

#### REST Stateless Approach
```
1. Client sends credentials with EVERY request
2. Request: GET /api/books
   Headers: Authorization: Bearer eyJhbGciOiJIUzI1...
3. Server validates token (no session storage)
4. If server restarts, nothing is lost
5. Each request works independently
```

### 7.4 Example: Pagination

**Stateful Pagination:**
```
1. Client requests page 1
2. Server caches: {page_1: [books...]}
3. Client requests page 2
4. Server uses cache to return page 2
5. Problem: Cache invalidation issues
```

**REST Stateless Pagination:**
```
1. Client requests: GET /api/books?page=1&limit=10
2. Server returns page 1
3. Client requests: GET /api/books?page=2&limit=10
4. Server processes independently - no cache needed
5. Each request is complete and self-contained
```

### 7.5 Advantages of Statelessness

| Advantage | Description |
|-----------|-------------|
| **Scalability** | Server can handle more clients without session storage |
| **Reliability** | No state to lose if server crashes |
| **Simplicity** | No session management code needed |
| **Visibility** | Each request is self-contained, easier to debug |
| **Cacheability** | Responses can be cached properly |

### 7.6 Disadvantages

| Disadvantage | Description |
|--------------|-------------|
| **Bandwidth** | More data sent per request (authentication tokens) |
| **Client Complexity** | Client must manage state locally |
| **Repeat Data** | Same auth data sent with every request |

---

## 8. Idempotent Methods

### 8.1 Definition

An idempotent HTTP method is a method that can be called multiple times without producing different results beyond the initial application. The side-effect of calling the method once should be identical to calling it multiple times.

### 8.2 Idempotent vs Non-Idempotent

| Method | Idempotent | Why |
|--------|------------|-----|
| GET | ✓ Yes | Retrieving data doesn't change state |
| HEAD | ✓ Yes | Same as GET but without body |
| PUT | ✓ Yes | Replacing with same data = same result |
| DELETE | ✓ Yes | First deletes, subsequent calls return 404 |
| OPTIONS | ✓ Yes | Returns same allowed methods |
| POST | ✗ No | Creates new resource each time |
| PATCH | ✗ No | Partial updates can accumulate |

### 8.3 Examples

#### GET - Idempotent
```
Request: GET /api/books
Request: GET /api/books
Request: GET /api/books

Result: Same response every time (list of books)
```

#### PUT - Idempotent
```
Request: PUT /api/books/1
Body: {"title": "New Title", "author": "Author"}

Request: PUT /api/books/1
Body: {"title": "New Title", "author": "Author"}

Result: Book 1 has "New Title" both times
```

#### DELETE - Idempotent
```
Request: DELETE /api/books/1
Result: 204 No Content (Book deleted)

Request: DELETE /api/books/1
Result: 404 Not Found (Already deleted)
```

#### POST - Non-Idempotent
```
Request: POST /api/books
Body: {"title": "New Book"}

Result: Book created with ID=1

Request: POST /api/books
Body: {"title": "New Book"}

Result: Book created with ID=2 (Different book!)
```

### 8.4 Practical Implications

**Why Does This Matter?**

1. **Retry Logic**
   - Idempotent methods can be safely retried on network failure
   - Non-idempotent methods may cause duplicate operations

2. **Client Implementation**
   - GET, PUT, DELETE: Safe to retry
   - POST, PATCH: Need careful error handling

**Example: Network Failure**
```
Scenario: User clicks "Submit" but network fails

If POST /api/books:
  - Don't auto-retry (might create duplicate book)
  - Show error to user

If PUT /api/books/1:
  - Safe to auto-retry (same result)
```

---

## 9. Conclusion

### 9.1 Summary

This project demonstrates the implementation of a Library Management System using Django and Bootstrap 5. The system incorporates:

- **MVT Architecture**: Clean separation of concerns with Models, Views, and Templates
- **RESTful API Design**: Proper use of HTTP methods and idempotent operations
- **Modern UI**: Bootstrap 5 components with responsive design
- **REST Principles**: Stateless communication and resource-based URLs

### 9.2 Key Learnings

1. **REST Architecture**: Understanding of stateless communication and resource-based URLs
2. **HTTP Methods**: Proper application of GET, POST, PUT, DELETE methods
3. **Idempotency**: Understanding which operations can be safely retried
4. **Bootstrap 5**: Modern UI component implementation

### 9.3 Future Enhancements

1. Implement the REST API using Django REST Framework
2. Add authentication and authorization
3. Add book borrowing functionality
4. Implement search and filtering
5. Add user authentication system

---

## References

1. Django Documentation. (2024). https://docs.djangoproject.com/
2. Bootstrap Documentation. (2024). https://getbootstrap.com/
3. Fielding, R. T. (2000). Architectural Styles and the Design of Network-based Software Architectures.
4. REST API Tutorial. (2024). https://restfulapi.net/

---

**Document Prepared By:** Software Engineering Team  
**Date:** Academic Year 2024-2025  
**Version:** 1.0


