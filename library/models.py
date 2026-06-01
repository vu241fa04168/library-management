from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True, verbose_name="ISBN")
    published_date = models.DateField()
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    publisher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='published_books')

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.title} by {self.author}"


class BorrowRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrow_records')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrow_records')
    borrow_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    returned_date = models.DateTimeField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)

    class Meta:
        ordering = ['-borrow_date']

    def __str__(self):
        return f"{self.user.username} borrowed {self.book.title}"

    @property
    def is_overdue(self):
        if not self.is_returned and self.due_date:
            return timezone.now() > self.due_date
        return False

    def save(self, *args, **kwargs):
        # Automatically calculate a default 14-day due date if it isn't set yet
        if not self.due_date:
            self.due_date = timezone.now() + timedelta(days=14)
        super().save(*args, **kwargs)
