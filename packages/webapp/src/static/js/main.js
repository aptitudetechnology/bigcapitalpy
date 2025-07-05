/**
 *     // Initialize the application
    init() {
        this.initializeSidebar();
        this.setupTooltips();
        this.setupFormValidation();
        this.setupAjaxDefaults();
        console.log('BigCapitalPy initialized with vertical dropdown sidebar');
    },alPy JavaScript Application
 * Main JavaScript file for frontend functionality
 */

// Application namespace
const BigCapitalPy = {
    // Initialize the application
    init() {
        this.initializeSidebar();
        this.setupTooltips();
        this.setupFormValidation();
        this.setupAjaxDefaults();
        console.log('BigCapitalPy initialized');
    },

    // Vertical Dropdown Sidebar functionality
    setupVerticalDropdownSidebar() {
        const sidebar = document.getElementById('sidebar');
        const sidebarToggle = document.getElementById('sidebar-toggle');
        const sidebarCollapse = document.getElementById('sidebar-collapse');
        const sidebarOverlay = document.getElementById('sidebar-overlay');
        const mainContent = document.getElementById('main-content');

        if (!sidebar) return;

        // Mobile sidebar toggle
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => {
                sidebar.classList.toggle('show');
                sidebarOverlay.classList.toggle('show');
                document.body.style.overflow = sidebar.classList.contains('show') ? 'hidden' : '';
            });
        }

        // Desktop sidebar collapse/expand
        if (sidebarCollapse) {
            sidebarCollapse.addEventListener('click', () => {
                sidebar.classList.toggle('collapsed');
                localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
                
                // Close all dropdowns when collapsing
                if (sidebar.classList.contains('collapsed')) {
                    this.closeAllDropdowns();
                }
            });
        }

        // Restore sidebar state from localStorage
        const sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        if (sidebarCollapsed) {
            sidebar.classList.add('collapsed');
        }

        // Overlay click to close sidebar on mobile
        if (sidebarOverlay) {
            sidebarOverlay.addEventListener('click', () => {
                sidebar.classList.remove('show');
                sidebarOverlay.classList.remove('show');
                document.body.style.overflow = '';
            });
        }

        // Setup dropdown toggles
        this.setupDropdownToggles();

        // Setup submenu toggles
        this.setupSubmenuToggles();

        // Add tooltips for collapsed sidebar
        this.setupSidebarTooltips();

        // Close sidebar on navigation (mobile)
        this.setupMobileNavigation();
    },

    // Setup dropdown toggles
    setupDropdownToggles() {
        const dropdownToggles = document.querySelectorAll('[data-dropdown]');
        
        dropdownToggles.forEach(toggle => {
            toggle.addEventListener('click', (e) => {
                e.preventDefault();
                const dropdownId = toggle.getAttribute('data-dropdown');
                const dropdown = document.getElementById(dropdownId);
                const sidebar = document.getElementById('sidebar');
                
                if (!dropdown || sidebar.classList.contains('collapsed')) return;

                const isOpen = dropdown.classList.contains('show');
                
                // Close all other dropdowns
                this.closeAllDropdowns();
                
                // Toggle current dropdown
                if (!isOpen) {
                    dropdown.classList.add('show');
                    toggle.setAttribute('aria-expanded', 'true');
                    toggle.classList.add('active');
                } else {
                    dropdown.classList.remove('show');
                    toggle.setAttribute('aria-expanded', 'false');
                    toggle.classList.remove('active');
                }
            });
        });
    },

    // Setup submenu toggles
    setupSubmenuToggles() {
        const submenuToggles = document.querySelectorAll('[data-submenu]');
        
        submenuToggles.forEach(toggle => {
            toggle.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                const submenuId = toggle.getAttribute('data-submenu');
                const submenu = document.getElementById(submenuId);
                const sidebar = document.getElementById('sidebar');
                
                if (!submenu || sidebar.classList.contains('collapsed')) return;

                const isOpen = submenu.classList.contains('show');
                
                // Close all other submenus in the same dropdown
                const parentDropdown = toggle.closest('.dropdown-content');
                if (parentDropdown) {
                    const otherSubmenus = parentDropdown.querySelectorAll('.submenu-content.show');
                    otherSubmenus.forEach(sub => {
                        if (sub !== submenu) {
                            sub.classList.remove('show');
                            const otherToggle = parentDropdown.querySelector(`[data-submenu="${sub.id}"]`);
                            if (otherToggle) {
                                otherToggle.setAttribute('aria-expanded', 'false');
                                otherToggle.classList.remove('active');
                            }
                        }
                    });
                }
                
                // Toggle current submenu
                if (!isOpen) {
                    submenu.classList.add('show');
                    toggle.setAttribute('aria-expanded', 'true');
                    toggle.classList.add('active');
                } else {
                    submenu.classList.remove('show');
                    toggle.setAttribute('aria-expanded', 'false');
                    toggle.classList.remove('active');
                }
            });
        });
    },

    // Close all dropdowns
    closeAllDropdowns() {
        const dropdowns = document.querySelectorAll('.dropdown-content.show');
        const submenus = document.querySelectorAll('.submenu-content.show');
        
        dropdowns.forEach(dropdown => {
            dropdown.classList.remove('show');
        });
        
        submenus.forEach(submenu => {
            submenu.classList.remove('show');
        });
        
        const toggles = document.querySelectorAll('[data-dropdown], [data-submenu]');
        toggles.forEach(toggle => {
            toggle.setAttribute('aria-expanded', 'false');
            toggle.classList.remove('active');
        });
    },

    // Setup tooltips for collapsed sidebar
    setupSidebarTooltips() {
        const sidebarLinks = document.querySelectorAll('.sidebar-link, .dropdown-link');
        
        sidebarLinks.forEach(link => {
            const textElement = link.querySelector('.sidebar-text, span');
            if (textElement) {
                const tooltipText = textElement.textContent.trim();
                link.setAttribute('data-tooltip', tooltipText);
            }
        });
    },

    // Setup mobile navigation behavior
    setupMobileNavigation() {
        const navLinks = document.querySelectorAll('.sidebar-link[href], .dropdown-link[href], .submenu-link[href]');
        const sidebar = document.getElementById('sidebar');
        const sidebarOverlay = document.getElementById('sidebar-overlay');
        
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth <= 768) {
                    sidebar.classList.remove('show');
                    sidebarOverlay.classList.remove('show');
                    document.body.style.overflow = '';
                }
            });
        });
    },

    // Handle window resize for responsive behavior
    handleResize() {
        const sidebar = document.getElementById('sidebar');
        const sidebarOverlay = document.getElementById('sidebar-overlay');
        
        window.addEventListener('resize', () => {
            if (window.innerWidth > 768) {
                sidebar.classList.remove('show');
                sidebarOverlay.classList.remove('show');
                document.body.style.overflow = '';
            }
        });
    },

    // Setup active states for current page
    setupActiveStates() {
        const currentPath = window.location.pathname;
        const sidebarLinks = document.querySelectorAll('.sidebar-link[href], .dropdown-link[href], .submenu-link[href]');
        
        sidebarLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && currentPath.includes(href) && href !== '/') {
                link.classList.add('active');
                
                // Open parent dropdowns if this is a nested link
                let parent = link.closest('.dropdown-content');
                while (parent) {
                    parent.classList.add('show');
                    const toggle = document.querySelector(`[data-dropdown="${parent.id}"]`);
                    if (toggle) {
                        toggle.classList.add('active');
                        toggle.setAttribute('aria-expanded', 'true');
                    }
                    parent = parent.parentElement.closest('.dropdown-content');
                }
                
                // Open parent submenu if this is a submenu link
                const submenuParent = link.closest('.submenu-content');
                if (submenuParent) {
                    submenuParent.classList.add('show');
                    const submenuToggle = document.querySelector(`[data-submenu="${submenuParent.id}"]`);
                    if (submenuToggle) {
                        submenuToggle.classList.add('active');
                        submenuToggle.setAttribute('aria-expanded', 'true');
                    }
                }
            }
        });
    },

    // Initialize all sidebar functionality
    initializeSidebar() {
        this.setupVerticalDropdownSidebar();
        this.setupActiveStates();
        this.handleResize();
    },

    // Setup Bootstrap tooltips
    setupTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    },

    // Form validation setup
    setupFormValidation() {
        // Add custom validation styles
        const forms = document.querySelectorAll('.needs-validation');
        Array.prototype.slice.call(forms).forEach(function (form) {
            form.addEventListener('submit', function (event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
    },

    // Setup AJAX defaults
    setupAjaxDefaults() {
        // Add CSRF token to all AJAX requests
        const csrfToken = document.querySelector('meta[name=csrf-token]');
        if (csrfToken) {
            // Setup fetch defaults for CSRF
            const originalFetch = window.fetch;
            window.fetch = function(url, options = {}) {
                if (options.method && options.method.toUpperCase() !== 'GET') {
                    options.headers = options.headers || {};
                    options.headers['X-CSRFToken'] = csrfToken.getAttribute('content');
                }
                return originalFetch(url, options);
            };
        }
    },

    // Utility functions
    utils: {
        // Format currency
        formatCurrency(amount, currency = 'USD') {
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: currency
            }).format(amount);
        },

        // Format date
        formatDate(date, format = 'short') {
            const options = format === 'short' 
                ? { year: 'numeric', month: 'short', day: 'numeric' }
                : { year: 'numeric', month: 'long', day: 'numeric' };
            
            return new Intl.DateTimeFormat('en-US', options).format(new Date(date));
        },

        // Show loading spinner
        showLoading(element) {
            const spinner = document.createElement('div');
            spinner.className = 'spinner-border spinner-border-sm me-2';
            spinner.setAttribute('role', 'status');
            element.insertBefore(spinner, element.firstChild);
            element.disabled = true;
        },

        // Hide loading spinner
        hideLoading(element) {
            const spinner = element.querySelector('.spinner-border');
            if (spinner) {
                spinner.remove();
            }
            element.disabled = false;
        },

        // Show toast notification
        showToast(message, type = 'info') {
            // Create toast container if it doesn't exist
            let toastContainer = document.querySelector('.toast-container');
            if (!toastContainer) {
                toastContainer = document.createElement('div');
                toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
                document.body.appendChild(toastContainer);
            }

            // Create toast element
            const toastEl = document.createElement('div');
            toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
            toastEl.setAttribute('role', 'alert');
            toastEl.innerHTML = `
                <div class="d-flex">
                    <div class="toast-body">${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            `;

            toastContainer.appendChild(toastEl);
            const toast = new bootstrap.Toast(toastEl);
            toast.show();

            // Remove toast after it's hidden
            toastEl.addEventListener('hidden.bs.toast', () => {
                toastEl.remove();
            });
        },

        // Confirm dialog
        confirm(message, callback) {
            if (window.confirm(message)) {
                callback();
            }
        },

        // Debounce function
        debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }
    },

    // API helper functions
    api: {
        // Generic API call
        async call(url, options = {}) {
            try {
                const response = await fetch(url, {
                    headers: {
                        'Content-Type': 'application/json',
                        ...options.headers
                    },
                    ...options
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                return await response.json();
            } catch (error) {
                console.error('API call failed:', error);
                BigCapitalPy.utils.showToast('An error occurred. Please try again.', 'danger');
                throw error;
            }
        },

        // GET request
        get(url) {
            return this.call(url);
        },

        // POST request
        post(url, data) {
            return this.call(url, {
                method: 'POST',
                body: JSON.stringify(data)
            });
        },

        // PUT request
        put(url, data) {
            return this.call(url, {
                method: 'PUT',
                body: JSON.stringify(data)
            });
        },

        // DELETE request
        delete(url) {
            return this.call(url, {
                method: 'DELETE'
            });
        }
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    BigCapitalPy.init();
});

// Export for use in other scripts
window.BigCapitalPy = BigCapitalPy;
