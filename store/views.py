# store/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import stripe
from django.conf import settings
from .models import Product, Price

# Stripe API key setup
stripe.api_key = settings.STRIPE_SECRET_KEY

class HomeView(TemplateView):
    template_name = 'store/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        context['cart'] = self.request.session.get('cart', {})
        context['stripe_publishable_key'] = settings.STRIPE_PUBLISHABLE_KEY
        return context

class ProductListView(ListView):
    model = Product
    template_name = 'store/product_list.html'
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = self.request.session.get('cart', {})
        context['stripe_publishable_key'] = settings.STRIPE_PUBLISHABLE_KEY  # Add this line
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'store/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stripe_publishable_key'] = settings.STRIPE_PUBLISHABLE_KEY
        return context

class CreateCheckoutView(View):
    def post(self, request, *args, **kwargs):
        cart = request.session.get('cart', {})
        payment_method = request.POST.get('payment_method')

        try:
            if payment_method == 'stripe':
                line_items = []
                if 'pk' in kwargs:
                    price = get_object_or_404(Price, pk=kwargs["pk"])
                    line_items.append({
                        'price_data': {
                            'currency': 'kes',
                            'product_data': {
                                'name': price.product.name,
                            },
                            'unit_amount': int(price.price * 100),
                        },
                        'quantity': 1,
                    })
                else:
                    if not cart:
                        return JsonResponse({'error': 'Cart is empty'}, status=400)
                    for price_id, quantity in cart.items():
                        price = get_object_or_404(Price, pk=price_id)
                        line_items.append({
                            'price_data': {
                                'currency': 'kes',
                                'product_data': {
                                    'name': price.product.name,
                                },
                                'unit_amount': int(price.price * 100),
                            },
                            'quantity': quantity,
                        })

                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=line_items,
                    mode='payment',
                    success_url=request.build_absolute_uri(reverse('store:success')),
                    cancel_url=request.build_absolute_uri(reverse('store:cancel')),
                )
                return JsonResponse({'redirect_url': checkout_session.url})
            elif payment_method == 'mpesa':
                phone_number = request.POST.get('phone_number')
                if not phone_number:
                    return JsonResponse({'error': 'Phone number is required for M-Pesa'}, status=400)
                return JsonResponse({'message': 'STK Push sent to your phone'})
            else:
                return JsonResponse({'error': 'Invalid payment method'}, status=400)
        except stripe.error.StripeError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'An unexpected error occurred'}, status=500)

class SuccessView(TemplateView):
    template_name = 'store/success.html'

class CancelView(TemplateView):
    template_name = 'store/cancel.html'

class AboutView(TemplateView):
    template_name = 'store/about.html'

class ContactView(TemplateView):
    template_name = 'store/contact.html'

class MpesaCallbackView(View):
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        return JsonResponse({"status": "received"})

class StripeWebhookView(View):
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError:
            return JsonResponse({'error': 'Invalid payload'}, status=400)
        except stripe.error.SignatureVerificationError:
            return JsonResponse({'error': 'Invalid signature'}, status=400)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            return JsonResponse({'status': 'success'})

        return JsonResponse({'status': 'event not handled'})

class AddToCartView(View):
    def post(self, request, pk):
        cart = request.session.get('cart', {})
        cart[str(pk)] = cart.get(str(pk), 0) + 1
        request.session['cart'] = cart
        request.session.modified = True
        return JsonResponse({'message': 'Added to cart', 'cart_count': cart[str(pk)]})

class RemoveFromCartView(View):
    def post(self, request, pk):
        cart = request.session.get('cart', {})
        if str(pk) in cart:
            cart[str(pk)] -= 1
            if cart[str(pk)] <= 0:
                del cart[str(pk)]
        request.session['cart'] = cart
        request.session.modified = True
        return JsonResponse({'message': 'Removed from cart', 'cart_count': cart.get(str(pk), 0)})