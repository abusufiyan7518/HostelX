document.addEventListener('DOMContentLoaded', function () {
  // Live date badge
  const el = document.getElementById('live-date');
  if (el) {
    const d = new Date();
    el.textContent = d.toLocaleDateString('en-IN', {
      weekday: 'short', year: 'numeric', month: 'short', day: 'numeric'
    });
  }

  // Animate fee bars on scroll into view
  const fills = document.querySelectorAll('.fee-bar-fill');
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.width = entry.target.dataset.width || entry.target.style.width;
      }
    });
  }, { threshold: 0.3 });
  fills.forEach(fill => observer.observe(fill));
});