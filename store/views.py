from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.utils import timezone
import stripe
import random
import uuid
from io import BytesIO
import requests
from xhtml2pdf import pisa


from .models import Medicine, CartItem, Address
from .forms import SignupForm, LoginForm, AddressForm

User = get_user_model()
stripe.api_key = settings.STRIPE_SECRET_KEY

# ---------- HELPER ----------
def _cart_count():
    return CartItem.objects.count() if CartItem.objects.exists() else 0

# ---------- HOME ----------
def home(request):
    featured = Medicine.objects.filter(is_featured=True)[:8]
    new_arrivals = Medicine.objects.filter(is_new=True).order_by('-created_at')[:8]
    return render(request, 'store/home.html', {
        'featured': featured,
        'new_arrivals': new_arrivals,
        'categories': Medicine.CATEGORY_CHOICES,
        'cart_count': _cart_count(),
    })

# ---------- SIGNUP ----------
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = SignupForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()
            messages.success(request, "Signup successful! You can now log in.")
            return redirect('account_login')
        messages.error(request, "Please correct the errors below.")
    return render(request, 'account/signup.html', {'form': form})

# ---------- LOGIN ----------
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')
        messages.error(request, "Invalid username/email or password.")
    return render(request, 'account/login.html', {'form': form})

# ---------- LOGOUT ----------
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('home')

# ---------- PRODUCT LIST ----------
def product_list(request):
    q = request.GET.get('q')
    category = request.GET.get('category')
    brand = request.GET.get('brand')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    medicines = Medicine.objects.all().order_by('pk')
    if q:
        medicines = medicines.filter(name__icontains=q)
    if category:
        medicines = medicines.filter(category=category)
    if brand:
        medicines = medicines.filter(name__icontains=brand)
    if min_price:
        medicines = medicines.filter(price__gte=min_price)
    if max_price:
        medicines = medicines.filter(price__lte=max_price)

    paginator = Paginator(medicines, 12)
    page = request.GET.get('page')
    meds_page = paginator.get_page(page)

    return render(request, 'store/product_list.html', {
        'medicines': meds_page,
        'categories': Medicine.CATEGORY_CHOICES,
        'cart_count': _cart_count(),
    })

# ---------- PRODUCT DETAIL ----------
def product_detail(request, pk):
    med = get_object_or_404(Medicine, pk=pk)
    return render(request, 'store/product_detail.html', {
        'med': med,
        'cart_count': _cart_count(),
    })

# ---------- CART ----------
def cart(request):
    items = CartItem.objects.select_related('medicine').all()
    print(f"DEBUG: Cart items count: {items.count()}")
    for item in items:
        print(f"DEBUG: Item: {item.medicine.name}, Price: {item.medicine.price}, Qty: {item.quantity}")
    total = sum([item.get_total_price() for item in items])
    return render(request, 'store/cart.html', {
        'items': items,
        'total': total,
        'cart_count': _cart_count()
    })

@require_POST
def update_cart(request):
    action = request.POST.get('action')
    item_id = request.POST.get('item_id')
    try:
        item = CartItem.objects.get(pk=item_id)
    except CartItem.DoesNotExist:
        return redirect('cart')

    if action == 'increase':
        item.quantity += 1
        item.save()
    elif action == 'decrease':
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()
    elif action == 'remove':
        item.delete()
    return redirect('cart')

# ---------- MINI CART ----------
def mini_cart(request):
    items = CartItem.objects.select_related('medicine').all()
    total = sum([it.get_total_price() for it in items])
    html = render_to_string('store/partials/_mini_cart.html', {'items': items, 'total': total}, request=request)
    return HttpResponse(html)

# ---------- ADD TO CART ----------
def add_to_cart(request, medicine_id):
    quantity = int(request.GET.get('quantity', 1))
    item, created = CartItem.objects.get_or_create(medicine_id=medicine_id)
    item.quantity += quantity if not created else quantity
    item.save()
    return redirect('cart')

@require_POST
def add_to_cart_ajax(request, medicine_id):
    quantity = int(request.POST.get('quantity', 1))
    item, created = CartItem.objects.get_or_create(medicine_id=medicine_id)
    item.quantity += quantity if not created else quantity
    item.save()
    mini_html = render_to_string('store/partials/_mini_cart.html', {
        'items': CartItem.objects.select_related('medicine').all(),
        'total': sum([float(it.get_total_price()) for it in CartItem.objects.all()])
    }, request=request)
    return JsonResponse({'success': True, 'mini_cart_html': mini_html, 'cart_count': _cart_count()})

# ---------- QUICK VIEW ----------
def quick_view(request, pk):
    med = get_object_or_404(Medicine, pk=pk)
    html = render_to_string('store/partials/_quick_view.html', {'med': med}, request=request)
    return HttpResponse(html)

# ---------- CHECKOUT ----------
@login_required(login_url='account_login')
def checkout(request):
    items = CartItem.objects.select_related('medicine').all()
    
    # Check if cart is empty
    if not items.exists():
        messages.warning(request, "Your cart is empty. Please add items before checking out.")
        return redirect('cart')
    
    total_amount = sum([item.get_total_price() for item in items])
    addresses = Address.objects.filter(user=request.user)

    if request.method == 'POST':
        # Double-check cart isn't empty on POST
        if not items.exists():
            messages.warning(request, "Your cart is empty. Please add items before checking out.")
            return redirect('cart')
            
        selected_address_id = request.POST.get('selected_address')
        if selected_address_id:
            selected_address = get_object_or_404(Address, pk=selected_address_id, user=request.user)
        else:
            form = AddressForm(request.POST)
            if form.is_valid():
                selected_address = form.save(commit=False)
                selected_address.user = request.user
                selected_address.save()
            else:
                messages.error(request, "Please fill all required address fields.")
                return render(request, 'store/checkout.html', {
                    'items': items, 'total': total_amount, 'addresses': addresses,
                    'form': form, 'cart_count': _cart_count(),
                    'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
                })

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': item.medicine.name},
                    'unit_amount': int(item.medicine.price * 100),
                },
                'quantity': item.quantity,
            } for item in items],
            mode='payment',
            success_url=request.build_absolute_uri('/success/'),
            cancel_url=request.build_absolute_uri('/checkout/'),
        )
        return redirect(session.url, code=303)
    else:
        form = AddressForm()

    return render(request, 'store/checkout.html', {
        'items': items, 'total': total_amount, 'addresses': addresses,
        'form': form, 'cart_count': _cart_count(),
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    })

# ---------- SUCCESS WITH ORDER ID AND EMAIL ----------
@login_required(login_url='account_login')
def success(request):
    user_email = request.user.email
    cart_items = CartItem.objects.select_related('medicine').all()
    if not cart_items.exists():
        messages.info(request, "Your cart is empty.")
        return redirect('home')

    # Order summary with float conversion
    order_summary = [
        {
            "name": item.medicine.name,
            "quantity": item.quantity,
            "price": float(item.get_total_price())
        } for item in cart_items
    ]
    total_price = sum(item["price"] for item in order_summary)

    # Generate unique Order ID
    order_id = str(uuid.uuid4()).split('-')[0].upper()

    # Save order_summary in session for PDF download later
    request.session[f"order_{order_id}"] = order_summary

    # Email context
    context = {
        "username": request.user.username,
        "order_id": order_id,
        "order_items": order_summary,
        "total_price": total_price,
        "home_url": request.build_absolute_uri('/'),
        "now": timezone.now(),
        "pdf_url": request.build_absolute_uri(f'/orders/{order_id}/invoice/'),
    }

    # Generate email
    subject = f"Order Confirmation - {order_id}"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [user_email]

    html_content = render_to_string("email/order_confirmation_email.html", context)
    text_content = f"Thank you {request.user.username} for your order!\n" + \
                   "\n".join([f"{i['name']} x {i['quantity']} = ${i['price']}" for i in order_summary]) + \
                   f"\nTotal: ${total_price}"

    # Generate PDF
    pdf_buffer = BytesIO()
    pdf_html = render_to_string("email/order_invoice.html", context)
    pisa_status = pisa.CreatePDF(pdf_html, dest=pdf_buffer)
    pdf_buffer.seek(0)

    try:
        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        if not pisa_status.err:
            msg.attach(f"Invoice_{order_id}.pdf", pdf_buffer.read(), "application/pdf")
        msg.send()
        messages.success(request, f"Order confirmation email sent to {user_email}")
        print(f"✅ Email sent successfully to {user_email}")
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        messages.warning(request, f"Order placed successfully, but we couldn't send the confirmation email. Please contact support with Order ID: {order_id}")

    # Clear cart
    CartItem.objects.all().delete()

    return render(request, "store/success.html", {
        "cart_count": 0,
        "order_summary": order_summary,
        "total_price": total_price,
        "order_id": order_id,
    })

# ---------- PDF INVOICE ----------
@login_required(login_url='account_login')
def order_invoice_pdf(request, order_id):
    order_items = request.session.get(f"order_{order_id}", [])
    if not order_items:
        return HttpResponse("No order found for this invoice.", status=404)

    total_price = sum(float(item['price']) for item in order_items)
    context = {
        "username": request.user.username,
        "order_id": order_id,
        "order_items": order_items,
        "total_price": total_price,
        "now": timezone.now(),
    }

    pdf_buffer = BytesIO()
    html_string = render_to_string('email/order_invoice.html', context)
    pisa_status = pisa.CreatePDF(html_string, dest=pdf_buffer)
    pdf_buffer.seek(0)

    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)

    response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{order_id}.pdf"'
    return response

# ---------- UPLOAD PRESCRIPTION ----------
def upload_prescription(request):
    if request.method == 'POST' and request.FILES.get('prescription'):
        uploaded_file = request.FILES['prescription']
        
        # Prepare file for FastAPI
        files = {'file': (uploaded_file.name, uploaded_file.read(), uploaded_file.content_type)}
        fastapi_url = f"{settings.FASTAPI_URL}/prescription"
        
        try:
            response = requests.post(fastapi_url, files=files, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            # Pass results to a template or redirect with data in session
            # For unifcation, we show results in the same product list style or a dedicated results page.
            # Here we just flash the message and redirect for now, simulating the "unification" flow
            # In a real scenario, we'd render 'store/prescription_results.html' with 'result['products']'
            
            product_names = [p['name'] for p in result.get('products', [])]
            if product_names:
                messages.success(request, f"Prescription processed! Found: {', '.join(product_names)}")
            else:
                messages.warning(request, "Prescription processed, but no specific medicines matched in stock.")
                
            return redirect('product_list')
            
        except requests.exceptions.RequestException as e:
            messages.error(request, f"Error processing prescription: {str(e)}")
            return redirect('home')

    return redirect('home')

# ---------- PASSWORD RESET ----------
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        users = User.objects.filter(email=email)
        if not users.exists():
            messages.error(request, "No account registered with that email.")
            return render(request, 'store/forgot_password.html')

        otp = "{:06d}".format(random.randint(0, 999999))
        request.session['pw_reset_email'] = email
        request.session['pw_reset_otp'] = otp
        try:
            send_mail(
                subject='MedPlus Password Reset OTP',
                message=f"Your password reset OTP is: {otp}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False
            )
            messages.success(request, "OTP sent to your email address.")
            return redirect('reset_password')
        except Exception as e:
            print("OTP send failed:", e)
            messages.error(request, "Failed to send OTP email. Try again later.")
    return render(request, 'store/forgot_password.html')

def reset_password(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        session_otp = request.session.get('pw_reset_otp')
        email = request.session.get('pw_reset_email')

        if not (session_otp and email):
            messages.error(request, "Session expired. Please request OTP again.")
            return redirect('forgot_password')

        if otp != session_otp:
            messages.error(request, "Invalid OTP.")
            return render(request, 'store/reset_password.html')

        if password != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'store/reset_password.html')

        users = User.objects.filter(email=email)
        for user in users:
            user.set_password(password)
            user.save()

        request.session.pop('pw_reset_otp', None)
        request.session.pop('pw_reset_email', None)
        messages.success(request, "Password reset successful. Please log in.")
        return redirect('account_login')

    return render(request, 'store/password_reset.html')
