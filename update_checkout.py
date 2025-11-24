checkout_html = """{% extends 'store/base.html' %}
{% load widget_tweaks %}
{% load static %}

{% block content %}
<div class="container py-5">
  <div class="row g-5">
    <div class="col-lg-8">
      <h2 class="fw-bold mb-4">Checkout</h2>
      
      <div class="card border-0 shadow-sm rounded-4 p-4 mb-4">
        <h5 class="fw-bold mb-4"><i class="fa-solid fa-location-dot text-primary me-2"></i> Delivery Address</h5>
        
        <form method="post" id="checkout-form">
          {% csrf_token %}

          <div class="row g-3">
            <div class="col-12">
              <label class="form-label fw-semibold">Full Name</label>
              {% render_field form.full_name class="form-control form-control-lg bg-light border-0" placeholder="John Doe" %}
            </div>
            <div class="col-12">
              <label class="form-label fw-semibold">Street Address</label>
              {% render_field form.street class="form-control form-control-lg bg-light border-0" placeholder="123 Main St, Apt 4B" %}
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold">City</label>
              {% render_field form.city class="form-control form-control-lg bg-light border-0" placeholder="New York" %}
            </div>
            <div class="col-md-4">
              <label class="form-label fw-semibold">State</label>
              {% render_field form.state class="form-control form-control-lg bg-light border-0" placeholder="NY" %}
            </div>
            <div class="col-md-2">
              <label class="form-label fw-semibold">Zip</label>
              {% render_field form.postal_code class="form-control form-control-lg bg-light border-0" placeholder="10001" %}
            </div>
            <div class="col-12">
              <label class="form-label fw-semibold">Phone Number</label>
              {% render_field form.phone class="form-control form-control-lg bg-light border-0" placeholder="+1 (555) 000-0000" %}
            </div>
          </div>

          <div class="mt-5">
            <h5 class="fw-bold mb-4"><i class="fa-regular fa-credit-card text-primary me-2"></i> Payment</h5>
            <div class="alert alert-info border-0 bg-info bg-opacity-10 text-info rounded-3 mb-4">
              <i class="fa-solid fa-lock me-2"></i> Secure payment powered by Stripe
            </div>
            <button type="submit" class="btn btn-primary btn-lg w-100 py-3 rounded-3 fw-bold shadow-sm hover-scale">
              <i class="fa-solid fa-lock me-2"></i> Complete Order · ${{ total }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div class="col-lg-4">
      <div class="card border-0 shadow-sm rounded-4 p-4 sticky-top" style="top: 100px;">
        <h5 class="fw-bold mb-4">Order Summary</h5>
        <div class="d-flex flex-column gap-3 mb-4">
          {% for item in items %}
          <div class="d-flex align-items-center justify-content-between">
            <div class="d-flex align-items-center gap-3">
              <div class="position-relative">
                {% if item.medicine.image %}
                <img src="{{ item.medicine.image.url }}" alt="{{ item.medicine.name }}" class="rounded-3" style="width: 50px; height: 50px; object-fit: cover;">
                {% else %}
                <img src="{% static 'images/sample_medicine.jpg' %}" alt="Sample" class="rounded-3" style="width: 50px; height: 50px; object-fit: cover;">
                {% endif %}
                <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-secondary border border-white small">
                  {{ item.quantity }}
                </span>
              </div>
              <div>
                <h6 class="mb-0 small fw-bold text-truncate" style="max-width: 150px;">{{ item.medicine.name }}</h6>
                <small class="text-muted">{{ item.medicine.category }}</small>
              </div>
            </div>
            <span class="fw-semibold small">${{ item.get_total_price }}</span>
          </div>
          {% empty %}
          <div class="text-center text-muted py-3">
            <small>Your cart is empty</small>
          </div>
          {% endfor %}
        </div>
        
        <hr class="my-4">
        
        <div class="d-flex justify-content-between mb-2">
          <span class="text-muted">Subtotal</span>
          <span class="fw-bold">${{ total }}</span>
        </div>
        <div class="d-flex justify-content-between mb-2">
          <span class="text-muted">Shipping</span>
          <span class="text-success fw-bold">Free</span>
        </div>
        <div class="d-flex justify-content-between mb-4">
          <span class="text-muted">Tax</span>
          <span class="fw-bold">$0.00</span>
        </div>
        
        <div class="d-flex justify-content-between align-items-center pt-3 border-top">
          <span class="h5 fw-bold mb-0">Total</span>
          <span class="h4 fw-bold text-primary mb-0">${{ total }}</span>
        </div>
      </div>
    </div>
  </div>
</div>

<style>
.hover-scale:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(13, 110, 253, 0.3) !important;
}
</style>
{% endblock %}"""

with open('store/templates/store/checkout.html', 'w', encoding='utf-8') as f:
    f.write(checkout_html)

print("Successfully updated checkout.html")
