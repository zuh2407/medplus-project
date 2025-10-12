from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("products/", views.product_list, name="product_list"),
    path("product/<int:pk>/", views.product_detail, name="product_detail"),

    # Cart URLs
    path("cart/", views.cart, name="cart"),
    path("cart/add/<int:medicine_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/add-ajax/<int:medicine_id>/", views.add_to_cart_ajax, name="add_to_cart_ajax"),
    path("cart/update/", views.update_cart, name="update_cart"),

    # Checkout
    path("checkout/", views.checkout, name="checkout"),
    path("success/", views.success, name="success"),

    # Authentication
    path("signup/", views.signup_view, name="account_signup"),
    path("login/", views.login_view, name="account_login"),
    path("logout/", views.logout_view, name="account_logout"),

    # Password reset
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("reset-password/", views.reset_password, name="reset_password"),
    
    # PDF invoice download
    path('orders/<str:order_id>/invoice/', views.order_invoice_pdf, name='order_invoice_pdf'),

]
