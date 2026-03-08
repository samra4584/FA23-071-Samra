"""
URL configuration for library app.

This module defines all URL patterns for the library application.
"""

from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Books - CRUD
    path('books/', views.book_list, name='book_list'),
    path('books/create/', views.book_create, name='book_create'),
    path('books/<int:book_id>/', views.book_detail, name='book_detail'),
    path('books/<int:book_id>/update/', views.book_update, name='book_update'),
    path('books/<int:book_id>/delete/', views.book_delete, name='book_delete'),
    
    # Members - CRUD
    path('members/', views.member_list, name='member_list'),
    path('members/create/', views.member_create, name='member_create'),
    path('members/<int:member_id>/update/', views.member_update, name='member_update'),
    path('members/<int:member_id>/delete/', views.member_delete, name='member_delete'),
]

