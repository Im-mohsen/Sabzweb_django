from django import forms
from .models import *


class TicketForm(forms.Form):
    SUBJECT_CHOICES = (
        ('پیشنهاد', 'پیشنهاد'),
        ('انتقاد', 'انتقاد'),
        ('گزارش', 'گزارش'),
    )
    message = forms.CharField(widget=forms.Textarea, required=True, label="پیام")
    name = forms.CharField(max_length=250, required=True, label="نام")
    email = forms.EmailField(max_length=250, required=True, label="ایمیل")
    phone = forms.CharField(min_length=11, max_length=11, required=True, label="شماره تماس")
    subject = forms.ChoiceField(choices=SUBJECT_CHOICES, label="موضوع")

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if phone:
            if not phone.isnumeric():
                raise forms.ValidationError("شماره تلفن عددی نیست!!")
            else:
                return phone


class CommentForm(forms.ModelForm):
    def clean_name(self):
        name = self.cleaned_data['name']
        if name:
            if len(name) < 3:
                raise forms.ValidationError("نام کوتاه است!!")
            else:
                return name

    class Meta:
        model = Comment
        # exclude = ['post', 'updated', 'created', 'active']
        fields = ['name', 'email', 'body']
        widgets = {
            'body': forms.TextInput(attrs={'class': 'body_boxe_form'}),
            'name': forms.TextInput(attrs={'class': 'boxes_form'}),
            'email': forms.TextInput(attrs={'class': 'boxes_form'})
        }


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'description', 'reading_time']

    def clean_title(self):
        title = self.cleaned_data['title']
        if title:
            if len(title) < 4:
                raise forms.ValidationError("نام کوتاه است!!")
            else:
                return title
        else:
            raise forms.ValidationError("نوشتن عنوان الزامی است!")

    def clean_reading_time(self):
        reading_time = self.cleaned_data['reading_time']

        if reading_time == 0:
            raise forms.ValidationError("مقدار زمان مطالعه پست را وارد کنید نمیتواند صفر باشد!!")
        else:
            return reading_time
