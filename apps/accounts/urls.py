from django.urls import path
from .views import register_customer, register_business, login, CustomTokenObtainPairView

urlpatterns = [
    path("register/customer/", register_customer, name="register_customer"),
    path("register/business/", register_business, name="register_business"),
    path("login/", login, name="login"),
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
]
