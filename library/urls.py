from django.urls import path
from . import views

urlpatterns = [
    path('books/', views.BookListView.as_view(), name='book_list'),
    path('books/<int:pk>/borrow/', views.BorrowBookView.as_view(), name='borrow_book'),
    path('my-books/', views.MyBorrowedBooksView.as_view(), name='my_books'),
    path('borrow-record/<int:pk>/return/', views.ReturnBookView.as_view(), name='return_book'),
    path('publisher/dashboard/', views.PublisherDashboardView.as_view(), name='publisher_dashboard'),
    path('publisher/publish/', views.PublishBookView.as_view(), name='publish_book'),
    path('publisher/login/', views.PublisherLoginView.as_view(), name='publisher_login'),
    path('publisher/books/<int:pk>/unpublish/', views.UnpublishBookView.as_view(), name='unpublish_book'),
]
