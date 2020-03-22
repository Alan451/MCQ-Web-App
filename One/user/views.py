from django.shortcuts import render, redirect
from . import forms, models
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages


# Create your views here.
def index(request):
    return render(request, 'registration/index.html')


def is_teacher(user):
    if user.usertype.user_type == "Teacher":
        return True
    else:
        return False


def is_student(user):
    if user.usertype.user_type == "Student":
        return True
    else:
        return False


@login_required
def logout_(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("user_home")


def login_(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('user_home')
    return render(request, 'registration/login.html', {"form": form})


def register(request):
    user_form = forms.UserForm()
    type_form = forms.UserTypeForm()
    if request.method == "POST":
        user_form = forms.UserForm(data=request.POST)
        type_form = forms.UserTypeForm(data=request.POST)

        if user_form.is_valid() and type_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            type_ = type_form.save(commit=False)
            type_.user = user
            type_.save()
            messages.success(request, "Registration for " + request.POST[
                'username'] + " is successful. Please Login to continue")
            return redirect("user_login")

    return render(request, 'registration/register.html',
                  {'user_form': user_form, 'type_form': type_form})


@login_required()
@user_passes_test(is_teacher)
def create_quiz(request):
    quiz_form = forms.QuizForm()
    username = request.user
    if request.method == "POST":
        quiz_form = forms.QuizForm(data=request.POST)

        if quiz_form.is_valid():
            quiz_ = quiz_form.save(commit=False)
            quiz_.created_by = username
            quiz_.save()
            request.session['quiz_'] = quiz_
            request.session['number'] = quiz_.number_of_questions
            request.session['counter'] = -1
            return redirect('user_add_question')
    return render(request, 'registration/create_quiz.html',
                  {'quiz_form': quiz_form})


@login_required()
@user_passes_test(is_teacher)
def add_questions(request):
    total = request.session['number']
    if request.session['counter'] == -1:
        request.session['counter'] = 1
    else:
        request.session['counter'] += 1
    question_form = forms.QuestionForm()
    if request.method == "POST":
        question_form = forms.QuestionForm(data=request.POST)

        if question_form.is_valid():
            question_ = question_form.save(commit=False)
            question_.quiz = request.session['quiz_']
            question_.save()
            request.session['counter'] -= 1
            if request.session['counter'] == total:
                messages.success(request, 'Quiz-' + request.session['quiz_'].name + ' created successfully')
                return redirect('user_home')
            else:
                return redirect('user_add_question')
    return render(request, 'registration/add_question.html',
                  {'question_form': question_form, 'i': request.session['counter'], 'total': total})


@login_required()
@user_passes_test(is_teacher)
def view_quizzes(request):
    quiz_objects = models.Quiz.objects.all().filter(created_by=request.user)
    return render(request, 'registration/view_quiz.html', {'quiz_objects': quiz_objects})


@login_required()
@user_passes_test(is_teacher)
def edit_quizzes(request, s, q_no):
    quiz_object = models.Quiz.objects.get(pk=s)
    question_objects = models.Question.objects.all().filter(quiz=s)
    primary_key = question_objects.first().id - 1 + q_no
    total = quiz_object.number_of_questions
    question = models.Question.objects.get(pk=primary_key)
    question_form = forms.QuestionForm(instance=question)
    if request.method == "POST":
        question_form = forms.QuestionForm(request.POST, instance=question)
        question_form.save()
        if q_no == total:
            return redirect('user_view_quiz')
        else:
            return redirect('../' + str(q_no + 1))
    return render(request, 'registration/edit_question.html',
                  {'question_form': question_form, 'question': question, 'i': q_no, 'total': total})


@login_required()
@user_passes_test(is_teacher)
def delete_quizzes(request, pk):
    if request.method == "POST":
        if '_confirm' in request.POST:
            messages.info(request, "The Quiz- " + str(models.Quiz.objects.get(pk=pk)) + " is Deleted Successfully")
            models.Quiz.objects.filter(pk=pk).delete()
            return redirect('user_view_quiz')
        else:
            return redirect('user_view_quiz')
    return render(request, 'registration/delete_confirm.html', {})


@login_required()
@user_passes_test(is_student)
def see_quizzes(request):
    quiz_objects = models.Quiz.objects.all()
    request.session['count'] = 0
    return render(request, 'registration/see_quiz.html', {'quiz_objects': quiz_objects})


@login_required()
@user_passes_test(is_student)
def take_quizzes(request, s, q_no):
    quiz_object = models.Quiz.objects.get(pk=s)
    question_objects = models.Question.objects.all().filter(quiz=s)
    primary_key = question_objects.first().id - 1 + q_no
    total = quiz_object.number_of_questions
    if q_no == 1:
        if models.Marks_scored.objects.all().filter(quiz=quiz_object, user=request.user):
            print(models.Marks_scored.objects.all().filter(quiz=quiz_object, user=request.user))
            messages.info(request, "You Have Already Given this Test")
            return redirect('user_see_quiz')
        else:
            marks = models.Marks_scored()
            marks.quiz = quiz_object
            marks.user = request.user

    else:
        marks = models.Marks_scored.objects.get(quiz=quiz_object, user=request.user)
    question = models.Question.objects.get(pk=primary_key)
    print(request.session['count'])
    request.session['count'] += question.marks_correct
    if request.method == "POST":
        if request.POST['choices'] == question.correct_answer:
            marks.marks += question.marks_correct

        else:
            marks.marks += question.marks_incorrect
        marks.save()
        if q_no == total:
            messages.success(request,
                             "You Have Successfully Completed the Quiz. You Have scored " + str(marks.marks)
                             + " marks out of " + str(int(request.session['count'] / 2)))
            return redirect('user_home')
        else:
            return redirect('../' + str(q_no + 1))
    return render(request, 'registration/take_quiz.html', {'question': question, 'q_no': q_no, 'total': total})
