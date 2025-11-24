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

  // ----------------------------
  // AJAX Add to Cart
  // ----------------------------
  document.querySelectorAll('.add-ajax-form').forEach(form => {
    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      const action = this.getAttribute('action');
      const formData = new FormData(this);
      try {
        const resp = await fetch(action, {
          method: 'POST',
          headers: {'X-CSRFToken': csrftoken, 'X-Requested-With': 'XMLHttpRequest'},
          body: formData
        });
        const data = await resp.json();
        if (data.success && data.mini_cart_html) {
          // update mini-cart
          const mini = document.getElementById('mini-cart-content');
          if (mini) mini.innerHTML = data.mini_cart_html;

          // update cart badge
          document.querySelectorAll('.badge.bg-danger').forEach(b => b.textContent = data.cart_count);

          // optional notification
          alert('Added to cart!');
        }
      } catch (err) {
        console.error('Add to cart failed', err);
      }
    });
  });

  // ----------------------------
  // AJAX Cart Update / Remove
  // ----------------------------
  document.querySelectorAll('form[action$="update_cart"]').forEach(form => {
    form.addEventListener('submit', async function(e){
      e.preventDefault();
      const formData = new FormData(this);
      try {
        const resp = await fetch(this.action, {
          method: 'POST',
          headers: {'X-CSRFToken': csrftoken, 'X-Requested-With': 'XMLHttpRequest'},
          body: formData
        });

        // reload mini cart HTML
        const miniResp = await fetch('/mini-cart/');
        const miniHtml = await miniResp.text();
        const mini = document.getElementById('mini-cart-content');
        if (mini) mini.innerHTML = miniHtml;

        // reload cart badge
        const cartCount = mini.querySelectorAll('li.list-group-item').length;
        document.querySelectorAll('.badge.bg-danger').forEach(b => b.textContent = cartCount);

        // optionally remove card if quantity is 0
        const action = formData.get('action');
        if (action === 'remove') {
          form.closest('.col').remove();
        } else {
          // reload page subtotal values (simple approach)
          location.reload();
        }

      } catch(err) {
        console.error('Cart update failed', err);
      }
    });
  });

  // ----------------------------
  // Quick view modal
  // ----------------------------
  document.querySelectorAll('.quick-view-btn').forEach(btn => {
    btn.addEventListener('click', async function (e) {
      e.preventDefault();
      const id = this.dataset.id;
      try {
        const resp = await fetch(`/quick-view/${id}/`);
        const html = await resp.text();
        let container = document.getElementById('quick-view-container');
        if (!container) {
          container = document.createElement('div');
          container.id = 'quick-view-container';
          document.body.appendChild(container);
        }
        container.innerHTML = html;

        // Close button inside quick view
        const closeBtn = container.querySelector('.quick-view button');
        if (closeBtn) {
          closeBtn.addEventListener('click', () => { container.innerHTML = ''; });
        }
      } catch (err) {
        console.error(err);
      }
    });
  });

});
