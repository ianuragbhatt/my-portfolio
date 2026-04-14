document.addEventListener('DOMContentLoaded', () => {

    // ─── Smooth Scrolling ────────────────────────────────────
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // ─── Navbar scroll state ─────────────────────────────────
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        navbar.classList.toggle('scrolled', window.scrollY > 50);
    });

    // ─── Scroll-triggered fade-up animations ─────────────────
    const scrollObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                scrollObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -60px 0px' });

    document.querySelectorAll('[data-animate]').forEach(el => scrollObserver.observe(el));

    // ─── Hero cascade on load ─────────────────────────────────
    // Each hero element fades+slides in sequentially
    document.querySelectorAll('[data-hero]').forEach(el => {
        const order = parseInt(el.getAttribute('data-hero'), 10);
        setTimeout(() => el.classList.add('hero-visible'), 120 + order * 160);
    });

    // ─── Stat counter animation ───────────────────────────────
    function animateCounter(el, target, suffix, duration = 1400) {
        const start = performance.now();
        const update = (now) => {
            const progress = Math.min((now - start) / duration, 1);
            // Ease-out cubic: fast start, slow finish
            const eased = 1 - Math.pow(1 - progress, 3);
            el.textContent = Math.round(eased * target) + suffix;
            if (progress < 1) requestAnimationFrame(update);
        };
        requestAnimationFrame(update);
    }

    const statsRow = document.querySelector('.stats-row');
    if (statsRow) {
        const counterObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.querySelectorAll('.stat-num[data-count]').forEach(el => {
                        const target = parseInt(el.dataset.count, 10);
                        const suffix = el.dataset.suffix || '';
                        animateCounter(el, target, suffix);
                    });
                    counterObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.6 });
        counterObserver.observe(statsRow);
    }

    // ─── Active nav link on scroll ────────────────────────────
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-links a[href^="#"]');

    const navObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                navLinks.forEach(a => a.classList.remove('active'));
                const active = document.querySelector(
                    `.nav-links a[href="#${entry.target.id}"]`
                );
                if (active) active.classList.add('active');
            }
        });
    }, { threshold: 0.3, rootMargin: '-15% 0px -60% 0px' });

    sections.forEach(s => navObserver.observe(s));

});
