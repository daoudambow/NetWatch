// main.js - NetWatch - Gestion sidebar, toasts, animations

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');
    
    sidebar.classList.toggle('-translate-x-full');
    overlay.classList.toggle('opacity-0');
    overlay.classList.toggle('pointer-events-none');
}

// Gestion des flash messages → toasts flottants
document.addEventListener('DOMContentLoaded', () => {
    // Toast pour les messages flash de Flask
    const flashes = document.querySelectorAll('.flash-message'); // ajoute class="flash-message" aux div flash si besoin
    if (flashes.length > 0) {
        const container = document.getElementById('toast-container');
        
        flashes.forEach(flash => {
            const text = flash.textContent.trim();
            const category = flash.dataset.category || 'info';
            const bg = category === 'success' ? 'bg-green-600/95' : 
                       category === 'error' ? 'bg-red-600/95' : 'bg-blue-600/95';
            
            const toast = document.createElement('div');
            toast.className = `p-5 rounded-2xl shadow-2xl text-white backdrop-blur-lg animate-slide-in-right ${bg} border border-gray-700/50`;
            toast.innerHTML = `
                <div class="flex items-center gap-4">
                    <i class="fas ${category === 'success' ? 'fa-check-circle' : 'fa-exclamation-triangle'} text-xl"></i>
                    <span class="font-medium">${text}</span>
                </div>
            `;
            container.appendChild(toast);

            setTimeout(() => {
                toast.classList.add('animate-slide-out-right');
                setTimeout(() => toast.remove(), 500);
            }, 5000);
        });
    }

    // Animation fade-in des cartes au scroll
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('opacity-100', 'translate-y-0');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.15 });

    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        el.classList.add('opacity-0', 'translate-y-12', 'transition-all', 'duration-800');
        observer.observe(el);
    });
});
