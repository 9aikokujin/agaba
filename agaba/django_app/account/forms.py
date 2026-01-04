from django import forms
from django.core.exceptions import ValidationError

from .models import CustomUser, Company


class UpdateInformations(forms.ModelForm):
    """Форма для обновления информации пользователя."""

    image = forms.ImageField(required=False,)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    username = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(max_length=150, required=False)
    edo_id = forms.CharField(max_length=150, required=False)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'image']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and CustomUser.objects.filter(
            email=email
        ).exclude(id=self.instance.id).exists():
            raise ValidationError("Этот email уже используется.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if username == '':
            return self.instance.username

        if username and CustomUser.objects.filter(
            username=username
        ).exclude(id=self.instance.id).exists():
            raise ValidationError("Этот username уже используется.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)

        image_file = self.cleaned_data.get('image')
        if image_file:
            try:
                user.image = image_file
            except Exception as e:
                print(f"Ошибка при обработке изображения: {e}")
                raise ValidationError("Не удалось обработать изображение.")
        elif not image_file and 'image' in self.changed_data:
            user.image = None

        for field, value in self.cleaned_data.items():
            if field in self.changed_data:
                setattr(user, field, value)

        if commit:
            user.save()
        return user


class CompanyForm(forms.ModelForm):
    """Форма добавления компании."""
    is_hidden = forms.BooleanField(required=False)

    class Meta:
        model = Company
        fields = [
            'inn', 'name', 'kpp',
            'legal_address', 'ogrn',
            'edo', 'is_hidden'
        ]
