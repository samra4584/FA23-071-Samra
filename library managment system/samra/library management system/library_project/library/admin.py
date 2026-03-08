"""
Admin configuration for Library Management System

This module registers models with Django admin for easy management.
"""

from django.contrib import admin
from .models import Book, Member, BookIssue


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Admin configuration for Book model."""
    list_display = ['id', 'title', 'author', 'isbn', 'published_year', 'available_copies']
    search_fields = ['title', 'author', 'isbn']
    list_per_page = 25
    ordering = ['-id']


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    """Admin configuration for Member model."""
    list_display = ['id', 'name', 'email', 'phone', 'membership_date']
    search_fields = ['name', 'email', 'phone']
    list_per_page = 25
    ordering = ['-id']


@admin.register(BookIssue)
class BookIssueAdmin(admin.ModelAdmin):
    """Admin configuration for BookIssue model."""
    list_display = ['issue_id', 'book', 'member', 'issue_date', 'due_date', 'status']
    list_filter = ['status', 'issue_date']
    search_fields = ['book__title', 'member__name']
    list_per_page = 25
    ordering = ['-issue_date']

