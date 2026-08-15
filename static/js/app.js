setTimeout(() => {
    document.querySelectorAll('.alert').forEach((el) => {
        el.style.transition = 'opacity 0.4s ease';
        
        setTimeout(() => {
            el.style.opacity = '0';
        }, 3500);
    });
}, 100);