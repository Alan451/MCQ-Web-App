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
            return redirect('../add_questions/' + str(quiz_.pk) + '/1/')
    return render(request, 'registration/create_quiz.html',
                  {'quiz_form': quiz_form})


@login_required()
@user_passes_test(is_teacher)
def add_questions(request, s, q_no):
    quiz_object = models.Quiz.objects.get(pk=s)
    total = quiz_object.number_of_questions
    question_form = forms.QuestionForm()
    if request.method == "POST":
        question_form = forms.QuestionForm(data=request.POST)

        if question_form.is_valid():
            question_ = question_form.save(commit=False)
            question_.quiz = quiz_object
            question_.save()
            if q_no == total:
                messages.success(request, 'Quiz-' + quiz_object.name + ' created successfully')
                return redirect('user_home')
            else:
                return redirect('../' + str(q_no + 1))
    return render(request, 'registration/add_question.html',
                  {'question_form': question_form, 'i': q_no, 's': s, 'total': total})


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
        if request.POST['confirm_key'] == "Confirm":
            messages.info(request, "The Quiz- " + str(models.Quiz.objects.get(pk=pk)) + " is Deleted Successfully")
            models.Quiz.objects.filter(pk=pk).delete()
            return redirect('user_view_quiz')
        elif request.POST['confirm_key'] == "Cancel":
            return redirect('user_view_quiz')
    return render(request, 'registration/delete_confirm.html', {})


@login_required()
@user_passes_test(is_student)
def see_teachers(request):
    user_type_objects = models.UserType.objects.all().filter(user_type="Teacher")
    return render(request, 'registration/see_teachers.html', {'user_type_objects': user_type_objects})


@login_required()
@user_passes_test(is_student)
def see_quizzes(request, s):
    marks = models.Marks_scored.objects.all()
    teacher = models.User.objects.get(pk=s)
    quiz_objects = models.Quiz.objects.all().filter(created_by=teacher)
    request.session['count'] = 0
    return render(request, 'registration/see_quiz.html',
                  {'quiz_objects': quiz_objects, 'marks': marks, 'teacher': teacher})


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
            messages.warning(request, "You Have Already Given this Test")
            return redirect('user_see_teachers')
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
            marks.total_marks = int(request.session['count'] / 2)
            marks.save()
            messages.success(request,
                             "You Have Successfully Completed the Quiz. You Have scored " + str(marks.marks)
                             + " marks out of " + str(int(request.session['count'] / 2)))
            return redirect('user_home')
        else:
            return redirect('../' + str(q_no + 1))
    return render(request, 'registration/take_quiz.html', {'question': question, 'q_no': q_no, 'total': total})


@login_required()
@user_passes_test(is_student)
def see_results(request):
    marks_objects = models.Marks_scored.objects.all().filter(user=request.user)
    return render(request, 'registration/see_results.html', {'marks_objects': marks_objects})
