"""
Views for Library Management System

This module handles all the views for books, members, and the home page.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Book, Member, BookIssue


def home(request):
    """Home page view with statistics."""
    total_books = Book.objects.count()
    total_members = Member.objects.count()
    available_books = Book.objects.filter(available_copies__gt=0).count()
    borrowed_books = Book.objects.filter(available_copies=0).count()
    
    # Recent books
    recent_books = Book.objects.all()[:6]
    
    context = {
        'total_books': total_books,
        'total_members': total_members,
        'available_books': available_books,
        'borrowed_books': borrowed_books,
        'recent_books': recent_books,
    }
    return render(request, 'home.html', context)


def book_list(request):
    """List all books with search functionality."""
    books = Book.objects.all().order_by('-id')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(isbn__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'books/book_list.html', context)


def book_detail(request, book_id):
    """Display detailed view of a single book."""
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'books/book_detail.html', {'book': book})


def book_create(request):
    """Create a new book."""
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        isbn = request.POST.get('isbn')
        published_year = request.POST.get('published_year')
        available_copies = request.POST.get('available_copies')
        
        Book.objects.create(
            title=title,
            author=author,
            isbn=isbn,
            published_year=published_year,
            available_copies=available_copies
        )
        
        messages.success(request, 'Book created successfully!')
        return redirect('book_list')
    
    return render(request, 'books/book_form.html', {'book': None})


def book_update(request, book_id):
    """Update an existing book."""
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        book.title = request.POST.get('title')
        book.author = request.POST.get('author')
        book.isbn = request.POST.get('isbn')
        book.published_year = request.POST.get('published_year')
        book.available_copies = request.POST.get('available_copies')
        book.save()
        
        messages.success(request, 'Book updated successfully!')
        return redirect('book_list')
    
    context = {'book': book}
    return render(request, 'books/book_form.html', context)


def book_delete(request, book_id):
    """Delete a book with confirmation."""
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted successfully!')
        return redirect('book_list')
    
    context = {'book': book}
    return render(request, 'books/book_delete.html', context)


def member_list(request):
    """List all members with search functionality."""
    members = Member.objects.all().order_by('-id')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        members = members.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(members, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'members/member_list.html', context)


def member_create(request):
    """Create a new member."""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        membership_date = request.POST.get('membership_date')
        
        Member.objects.create(
            name=name,
            email=email,
            phone=phone,
            membership_date=membership_date
        )
        
        messages.success(request, 'Member created successfully!')
        return redirect('member_list')
    
    return render(request, 'members/member_form.html', {'member': None})


def member_update(request, member_id):
    """Update an existing member."""
    member = get_object_or_404(Member, id=member_id)
    
    if request.method == 'POST':
        member.name = request.POST.get('name')
        member.email = request.POST.get('email')
        member.phone = request.POST.get('phone')
        member.membership_date = request.POST.get('membership_date')
        member.save()
        
        messages.success(request, 'Member updated successfully!')
        return redirect('member_list')
    
    context = {'member': member}
    return render(request, 'members/member_form.html', context)


def member_delete(request, member_id):
    """Delete a member with confirmation."""
    member = get_object_or_404(Member, id=member_id)
    
    if request.method == 'POST':
        member.delete()
        messages.success(request, 'Member deleted successfully!')
        return redirect('member_list')
    
    context = {'member': member}
    return render(request, 'members/member_delete.html', context)

