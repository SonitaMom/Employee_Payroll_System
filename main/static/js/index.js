document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.getElementById('appSidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarOverlay = document.getElementById('sidebarOverlay');

    function isMobile() {
        return window.innerWidth < 992;
    }

    // Toggle Sidebar Function
    function toggleSidebar() {
        if (isMobile()) {
            // On mobile/tablet screens: show/hide offcanvas overlay sidebar
            if (sidebar) {
                sidebar.classList.toggle('show');
            }
            if (sidebarOverlay) {
                sidebarOverlay.classList.toggle('show');
            }
        } else {
            // On desktop: default is open; toggle collapses/expands sidebar
            document.body.classList.toggle('sidebar-collapsed');
        }
    }

    // Close Sidebar (useful for mobile overlay click or ESC key)
    function closeSidebar() {
        if (isMobile()) {
            if (sidebar) {
                sidebar.classList.remove('show');
            }
            if (sidebarOverlay) {
                sidebarOverlay.classList.remove('show');
            }
        }
    }

    // Toggle button click handler
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function (e) {
            e.stopPropagation();
            toggleSidebar();
        });
    }

    // Close when clicking overlay (mobile)
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function () {
            closeSidebar();
        });
    }

    // Close sidebar on pressing Escape
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            closeSidebar();
        }
    });

    // Handle window resize cleanly
    window.addEventListener('resize', function () {
        if (!isMobile()) {
            // Clean up mobile overlay classes when transitioning to desktop
            if (sidebar) {
                sidebar.classList.remove('show');
            }
            if (sidebarOverlay) {
                sidebarOverlay.classList.remove('show');
            }
        }
    });

    // Auto-highlight active sidebar links if matches current pathname
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.sidebar-menu .nav-link-custom');

    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && href !== '#' && currentPath.includes(href)) {
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        }
    });
});
