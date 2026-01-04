# from django import forms

# from .models import Question, Answer, ProductReview, CustomUser


# class QuestionForm(forms.ModelForm):
#     username = forms.CharField(label="Имя пользователя", max_length=150)  # ✅ Строка, а не выбор из списка

#     class Meta:
#         model = Question
#         fields = ['username', 'text']

#     def clean_username(self):
#         username = self.cleaned_data['username'].strip()  # Убираем лишние пробелы
#         user = CustomUser.objects.filter(username=username).first()

#         if not user:
#             raise forms.ValidationError("Такого пользователя не существует. Зарегистрируйтесь.")
            

#         return user  # ✅ Возвращаем объект `CustomUser`


# class AnswerForm(forms.ModelForm):
#     """Форма для заполнения ответов на вопросы к товарам."""
    
#     class Meta:
#         model = Answer
#         fields = ['text']


# class ReviewForm(forms.ModelForm):
#     """Форма для отзывов к товарам."""
#     class Meta:
#         model = ProductReview
#         fields = ['rating', 'comment', 'pros', 'cons', 'image']
