document.addEventListener("DOMContentLoaded", () => {
  // Attach Bootstrap modal load for featured quick view buttons that use data attributes
  const quickViewModalEl = document.getElementById('quickViewModal');
  if (quickViewModalEl) {
    quickViewModalEl.addEventListener('show.bs.modal', (event) => {
      // handled in main.js
    });
  }
});
