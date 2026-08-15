setTimeout(() => {
  document.querySelectorAll('.alert').forEach(el => {
    el.style.transition = 'opacity .4s';
    setTimeout(() => el.style.opacity = '0', 3500);
  });
}, 100);
