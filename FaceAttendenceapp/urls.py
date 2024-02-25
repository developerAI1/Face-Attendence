from django.urls import path 
from . import views
from django.conf import settings
from django.conf.urls.static import static
from FaceAttendenceapp.views import *


urlpatterns = [
    path('register/', UserRegistrationView.as_view(),name='register'),
    path('login/', UserLoginView.as_view(),name='loginin'),
    path('userprofile/', UserProfileView.as_view(),name='userprofile'),
    path('logout/', LogoutUser.as_view(),name='logout'),
    path('videocap/', Videocapture.as_view(),name='videocap')

]