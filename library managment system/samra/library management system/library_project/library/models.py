"""
Models for Library Management System

This module defines the data models for books and members.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime, timedelta


class Book(models.Model):
    """Model representing a book in the library."""
    
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13)
    published_year = models.IntegerField(
        validators=[MinValueValidator(1000), MaxValueValidator(datetime.now().year)]
    )
    available_copies = models.IntegerField(default=1)
    
    class Meta:
        ordering = ['title']
    
    def __str__(self):
        return f"{self.title} by {self.author}"


class Member(models.Model):
    """Model representing a library member."""
    
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    membership_date = models.DateField()
    
    class Meta:
        ordering = ['-id']
    
    def __str__(self):
        return self.name


class BookIssue(models.Model):
    """Model representing a book issue/borrowing record."""
    
    STATUS_CHOICES = [
        ('issued', 'Issued'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ]
    
    issue_id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='issues')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='issues')
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='issued')
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-issue_date']
    
    def __str__(self):
        return f"{self.book.title} - {self.member.name}"
    
    @property
    def is_overdue(self):
        if self.status == 'returned':
            return False
        return datetime.now().date() > self.due_date

