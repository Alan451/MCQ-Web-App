from django import forms
from django.forms import ValidationError
from django.contrib.auth.models import User
from .models import UserType, Quiz, Question
from django.contrib.auth.password_validation import MinimumLengthValidator, NumericPasswordValidator


class UserForm(forms.ModelForm):
    re_password = forms.CharField(max_length=20, widget=forms.PasswordInput,
                                  label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 're_password']
        widgets = {
            'password': forms.PasswordInput
        }

    def clean(self):
        word = self.cleaned_data['password']
        repass = self.cleaned_data['re_password']
        if MinimumLengthValidator().validate(password=word) is not None:
            raise ValidationError
        if NumericPasswordValidator().validate(password=word) is not None:
            raise ValidationError
        if word != repass:
            raise ValidationError('Passwords do not match')


class UserTypeForm(forms.ModelForm):
    class Meta:
        model = UserType
        fields = ['user_type']


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['name', 'number_of_questions']

    def clean(self):
        quiz = Quiz.objects.all().filter(name=self.cleaned_data['name'])
        if quiz:
            raise ValidationError('A Quiz already Exist with the provided name. Try Changing the Name.')


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        exclude = ['quiz', 'marks_not_attempted']
