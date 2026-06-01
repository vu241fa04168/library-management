from django import forms
from .models import Book

class BookPublishForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'published_date', 'total_copies']
        widgets = {
            'published_date': forms.DateInput(attrs={
                'type': 'date',
                'placeholder': 'YYYY-MM-DD'
            }),
            'title': forms.TextInput(attrs={
                'placeholder': 'Enter book title'
            }),
            'author': forms.TextInput(attrs={
                'placeholder': 'Enter author name'
            }),
            'isbn': forms.TextInput(attrs={
                'placeholder': 'Enter 13-digit ISBN'
            }),
            'total_copies': forms.NumberInput(attrs={
                'min': '1',
                'placeholder': 'Number of copies'
            }),
        }

    def clean_total_copies(self):
        total_copies = self.cleaned_data.get('total_copies')
        if total_copies is not None and total_copies < 1:
            raise forms.ValidationError("Total copies must be at least 1.")
        return total_copies
