from django import forms
from django.core.files.uploadedfile import UploadedFile
from django.core.validators import ValidationError


class TextFileValidator:
    def __call__(self, value):
        if isinstance(value, UploadedFile):
            if value.content_type != 'text/plain':
                raise ValidationError("Invalid file type. Required content type is text.")


class UploadArtistsForm(forms.Form):
    artists_file = forms.FileField(label="Upload", validators=[TextFileValidator(),])
    russian_checkbox = forms.BooleanField(label="Russian artists list", initial=True, required=False)