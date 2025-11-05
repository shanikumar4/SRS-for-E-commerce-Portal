from django.urls import path
from app.views import signupview, updateUser, loginview, logoutview, addproduct, userdetails, gender




urlpatterns = [
    path('signup/', signupview),
    path('login/', loginview),
    path('updateuser/', updateUser),
    path('logout/', logoutview),
    path('addproduct/', addproduct),
    path('details/', userdetails),
    path('gender/', gender),
    

] 



