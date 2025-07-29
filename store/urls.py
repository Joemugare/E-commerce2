from django.urls import path
from . import views

app_name = 'store'  # Define the namespace

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('create-checkout-session/<int:pk>/', views.CreateCheckoutView.as_view(), name='create_checkout_session'),
    path('create-checkout-session/', views.CreateCheckoutView.as_view(), name='create_checkout_session'),  # For cart-based checkout
    path('success/', views.SuccessView.as_view(), name='success'),
    path('cancel/', views.CancelView.as_view(), name='cancel'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('mpesa-callback/', views.MpesaCallbackView.as_view(), name='mpesa_callback'),
    path('stripe-webhook/', views.StripeWebhookView.as_view(), name='stripe_webhook'),
    path('add-to-cart/<int:pk>/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('remove-from-cart/<int:pk>/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
]