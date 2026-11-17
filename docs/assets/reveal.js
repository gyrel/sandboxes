(function () {
  function reveal() {
    const words = document.querySelectorAll('[data-reveal] span');
    if (!words.length) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches || !('IntersectionObserver' in window)) {
      words.forEach(word => word.classList.add('is-visible'));
      return;
    }
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -18% 0px', threshold: 0.3 });
    words.forEach(word => observer.observe(word));
  }
  if (typeof document$ !== 'undefined') document$.subscribe(reveal);
  else document.addEventListener('DOMContentLoaded', reveal);
}());
