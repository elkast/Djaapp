// JavaScript pour Djaapp - animations et interactions légères côté client

document.addEventListener('DOMContentLoaded', function() {
    // Initialisation des animations
    initializeAnimations();
    initializeFadeInElements();
    initializeSmoothScroll();
});

// Animations d'entrée avec Intersection Observer
function initializeAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target); // Animation unique
            }
        });
    }, observerOptions);

    // Observer les cartes et éléments importants
    document.querySelectorAll('.card, .stats-card, .panier-item').forEach(el => {
        observer.observe(el);
    });
}

// Animation fade-in pour les éléments au chargement
function initializeFadeInElements() {
    const elements = document.querySelectorAll('.card, .alert, .badge');
    elements.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';

        setTimeout(() => {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, index * 100); // Délai échelonné
    });
}

// Smooth scroll pour les ancres
function initializeSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Animation de chargement pour les boutons
function showLoading(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Chargement...';
    button.disabled = true;

    return function() {
        button.innerHTML = originalText;
        button.disabled = false;
    };
}

// Animation de succès pour les actions
function showSuccess(element) {
    element.style.transition = 'all 0.3s ease';
    element.style.transform = 'scale(1.05)';
    element.style.boxShadow = '0 0 20px rgba(255, 127, 0, 0.3)';

    setTimeout(() => {
        element.style.transform = 'scale(1)';
        element.style.boxShadow = '';
    }, 300);
}

// Animation de pulsation pour attirer l'attention
function pulse(element) {
    element.style.animation = 'pulse 2s infinite';
    setTimeout(() => {
        element.style.animation = '';
    }, 4000);
}

// Animation de glissement pour les notifications
function slideIn(element, direction = 'right') {
    const directions = {
        right: 'translateX(100%)',
        left: 'translateX(-100%)',
        up: 'translateY(100%)',
        down: 'translateY(-100%)'
    };

    element.style.transform = directions[direction];
    element.style.opacity = '0';
    element.style.transition = 'all 0.5s ease';

    setTimeout(() => {
        element.style.transform = 'translateX(0)';
        element.style.opacity = '1';
    }, 100);
}

// Gestion des tooltips Bootstrap (si utilisés)
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Animation des compteurs (pour statistiques)
function animateCounter(element, target, duration = 2000) {
    const start = parseInt(element.textContent) || 0;
    const increment = (target - start) / (duration / 16); // 60 FPS
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= target) || (increment < 0 && current <= target)) {
            element.textContent = target;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current);
        }
    }, 16);
}

// Animation des progress bars
function animateProgressBar(progressBar, percentage) {
    progressBar.style.width = '0%';
    progressBar.style.transition = 'width 1.5s ease-in-out';

    setTimeout(() => {
        progressBar.style.width = percentage + '%';
    }, 100);
}

// Effet de hover amélioré pour les cartes
function enhanceCardHover() {
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 8px 25px rgba(0,0,0,0.15)';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '';
        });
    });
}

// Animation de chargement des images
function lazyLoadImages() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.classList.add('fade-in');
                        imageObserver.unobserve(img);
                    }
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
}

// Initialisation des animations au scroll
window.addEventListener('scroll', function() {
    const scrolled = window.pageYOffset;
    const rate = scrolled * -0.5;

    // Effet parallax pour les éléments avec data-parallax
    document.querySelectorAll('[data-parallax]').forEach(el => {
        el.style.transform = `translateY(${rate * 0.1}px)`;
    });
});

// Fonctions pour la gestion des produits commerçant
function modifierProduit(id, nom, description, prix, stock, categorie) {
    document.getElementById('modifNom').value = nom;
    document.getElementById('modifDescription').value = description;
    document.getElementById('modifPrix').value = prix;
    document.getElementById('modifStock').value = stock;
    document.getElementById('modifCategorie').value = categorie;
    document.getElementById('formModifierProduit').action = `/commercant/produit/${id}/modifier`;
}

function supprimerProduit(id, nom) {
    if (confirm(`Êtes-vous sûr de vouloir supprimer le produit "${nom}" ?`)) {
        // Créer un formulaire temporaire pour la suppression
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/commercant/produit/${id}/supprimer`;
        document.body.appendChild(form);
        form.submit();
    }
}

// Support pour les préférences de mouvement réduit
if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    // Désactiver les animations pour les utilisateurs qui préfèrent
    document.documentElement.style.setProperty('--transition', 'none');
    document.querySelectorAll('.fade-in').forEach(el => {
        el.classList.remove('fade-in');
    });
}
