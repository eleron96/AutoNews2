from django import forms

from ..models import News, URL


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['author', 'link', 'title', 'content']

class URLForm(forms.ModelForm):
    class Meta:
        model = URL
        fields = ['address', 'description']