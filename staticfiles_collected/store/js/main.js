document.addEventListener('DOMContentLoaded', function () {
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  const csrftoken = getCookie('csrftoken');

  document.querySelectorAll('.quick-view-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      const id = btn.dataset.id;
      const url = `/quick-view/${id}/`;
      try {
        const resp = await fetch(url);
        const html = await resp.text();
        document.getElementById('quick-view-content').innerHTML = html;
        const qModal = new bootstrap.Modal(document.getElementById('quickViewModal'));
        qModal.show();

        attachQtyButtons();
        attachAjaxForms();
      } catch (err) {
        console.error(err);
        alert('Failed to load product details.');
      }
    });
  });

  function attachAjaxForms() {
    document.querySelectorAll('.add-ajax-form').forEach(form => {
      form.removeEventListener('submit', ajaxHandler);
      form.addEventListener('submit', ajaxHandler);
    });
  }

  async function ajaxHandler(e) {
    e.preventDefault();
    const form = e.currentTarget;
    const action = form.getAttribute('action');
    const formData = new FormData(form);

    try {
      const resp = await fetch(action, {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        body: formData
      });
      const data = await resp.json();
      if (data.success) {
        const mini = document.getElementById('mini-cart-content');
        if (mini && data.mini_cart_html) mini.innerHTML = data.mini_cart_html;
        const badges = document.querySelectorAll('.badge.bg-danger');
        badges.forEach(b => b.textContent = data.cart_count);
        showToast('Added to cart');
      } else {
        showToast('Could not add to cart', true);
      }
    } catch (err) {
      console.error(err);
      showToast('Error adding to cart', true);
    }
  }

  attachAjaxForms();

  function attachQtyButtons() {
    document.querySelectorAll('.qty-decrease').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const input = e.target.closest('.modal-content').querySelector('.qty-input');
        if (!input) return;
        let v = parseInt(input.value) || 1;
        v = Math.max(1, v - 1);
        input.value = v;
      });
    });
    document.querySelectorAll('.qty-increase').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const input = e.target.closest('.modal-content').querySelector('.qty-input');
        if (!input) return;
        let v = parseInt(input.value) || 1;
        input.value = v + 1;
      });
    });
  }

  function showToast(message, isError=false) {
    const toast = document.createElement('div');
    toast.className = 'toast align-items-center text-bg-white border shadow-sm';
    toast.style.position = 'fixed';
    toast.style.right = '20px';
    toast.style.bottom = '20px';
    toast.style.zIndex = 2000;
    toast.innerHTML = `<div class="d-flex"><div class="toast-body">${message}</div>
      <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button></div>`;
    document.body.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast, {delay: 2000});
    bsToast.show();
    toast.addEventListener('hidden.bs.toast', () => toast.remove());
  }

  const miniToggle = document.getElementById('miniCartToggle');
  if (miniToggle) {
    miniToggle.addEventListener('shown.bs.dropdown', async () => {
      try {
        const res = await fetch('/mini-cart/');
        const html = await res.text();
        document.getElementById('mini-cart-content').innerHTML = html;
      } catch (err) {
        console.error('Failed to refresh mini cart', err);
      }
    });
  }
});
