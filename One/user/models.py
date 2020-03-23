from django.db import models
from django.contrib.auth.models import User
from enum import Enum
from datetime import datetime
from django.utils.timezone import now


class Type(Enum):
    Teacher = "Teacher"
    Student = "Student"


class UserType(models.Model):
    user = models.OneToOneField(User, models.CASCADE, primary_key=True)
    user_type = models.CharField(max_length=10, choices=[(tag.name, tag.value) for tag in Type])

    def __str__(self):
        return self.user.username + '-' + self.user_type


class Quiz(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    number_of_questions = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question_title = models.CharField(max_length=200)
    marks_correct = models.IntegerField(default=1)
    marks_incorrect = models.IntegerField(default=0)
    marks_not_attempted = models.IntegerField(default=0)
    choice1 = models.CharField(max_length=30)
    choice2 = models.CharField(max_length=30)
    choice3 = models.CharField(max_length=30)
    choice4 = models.CharField(max_length=30)
    correct_answer = models.CharField(max_length=30)

    def __str__(self):
        return self.quiz.name + '-' + str(self.pk)


class Marks_scored(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    marks = models.IntegerField(default=0)
    total_marks = models.IntegerField(default=0)
    def __str__(self):
        return self.user.username + '-' + self.quiz.name
