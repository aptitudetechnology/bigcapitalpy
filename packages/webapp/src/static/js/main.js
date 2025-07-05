/**
 * BigCapitalPy JavaScript Application
 * Main JavaScript file for frontend functionality
 */

// Application namespace
const BigCapitalPy = {
    // Initialize the application
    init() {
        this.setupSidebar();
        this.setupTooltips();
        this.setupFormValidation();
        this.setupAjaxDefaults();
        console.log('BigCapitalPy initialized');
    },

    // Sidebar functionality
    setupSidebar() {
        const sidebarToggle = document.getElementById('sidebar-toggle');
        const sidebar = document.getElementById('sidebar');
        
        if (sidebarToggle && sidebar) {
            sidebarToggle.addEventListener('click', () => {
                sidebar.classList.toggle('show');
            });
        }

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 768) {
                if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                    sidebar.classList.remove('show');
                }
            }
        });
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
