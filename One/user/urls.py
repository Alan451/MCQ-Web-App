from django.urls import include, path
from . import views

urlpatterns = [
    path('register/', views.register, name="user_register"),
    path('', views.index, name="user_home"),
    path('login/', views.login_, name="user_login"),
    path('logout/', views.logout_, name="user_logout"),
    path('create_view/', views.create_quiz, name="user_create_quiz"),
    path('add_questions/', views.add_questions, name="user_add_question"),
    path('view_quizzes/', views.view_quizzes, name="user_view_quiz"),
    path('edit_quizzes/<int:s>/<int:q_no>/', views.edit_quizzes,name="user_edit_quiz"),
    path('delete_quizzes/<int:pk>/', views.delete_quizzes,name="delete_quiz"),
    path('see_quizzes/', views.see_quizzes, name="user_see_quiz"),
    path('see_quizzes/<int:s>/<int:q_no>/', views.take_quizzes),
    path('', include('django.contrib.auth.urls')),

]
