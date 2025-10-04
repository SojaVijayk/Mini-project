// Toast Notification System
class ToastNotification {
    constructor() {
        // Only create container if DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.createToastContainer();
            });
        } else {
            this.createToastContainer();
        }
    }

    createToastContainer() {
        if (document.getElementById('toast-container')) return;
        
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            max-width: 400px;
            pointer-events: none;
        `;
        document.body.appendChild(container);
    }

    show(message, type = 'info', duration = 4000) {
        const toast = document.createElement('div');
        const toastId = 'toast-' + Date.now() + Math.random();
        toast.id = toastId;
        
        // Toast styling based on type
        const colors = {
            success: { bg: '#10b981', border: '#059669', icon: '✅' },
            error: { bg: '#ef4444', border: '#dc2626', icon: '❌' },
            warning: { bg: '#f59e0b', border: '#d97706', icon: '⚠️' },
            info: { bg: '#7c3aed', border: '#5b21b6', icon: 'ℹ️' }
        };
        
        const color = colors[type] || colors.info;
        
        toast.style.cssText = `
            background: linear-gradient(135deg, ${color.bg}, ${color.border});
            color: white;
            padding: 16px 20px;
            margin-bottom: 12px;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
            border-left: 4px solid ${color.border};
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            font-size: 14px;
            line-height: 1.4;
            max-width: 100%;
            word-wrap: break-word;
            pointer-events: auto;
            cursor: pointer;
            transform: translateX(100%);
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 12px;
        `;
        
        toast.innerHTML = `
            <span style="font-size: 16px;">${color.icon}</span>
            <span style="flex: 1;">${message}</span>
            <span style="opacity: 0.7; font-size: 18px; cursor: pointer;" onclick="toastManager.remove('${toastId}')">×</span>
        `;
        
        const container = document.getElementById('toast-container');
        container.appendChild(toast);
        
        // Trigger animation
        setTimeout(() => {
            toast.style.transform = 'translateX(0)';
        }, 10);
        
        // Auto remove
        setTimeout(() => {
            this.remove(toastId);
        }, duration);
        
        // Click to dismiss
        toast.addEventListener('click', () => {
            this.remove(toastId);
        });
    }

    remove(toastId) {
        const toast = document.getElementById(toastId);
        if (toast) {
            toast.style.transform = 'translateX(100%)';
            toast.style.opacity = '0';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }
    }

    success(message, duration = 4000) {
        this.show(message, 'success', duration);
    }

    error(message, duration = 5000) {
        this.show(message, 'error', duration);
    }

    warning(message, duration = 4500) {
        this.show(message, 'warning', duration);
    }

    info(message, duration = 4000) {
        this.show(message, 'info', duration);
    }
}

// Global toast manager
let toastManager;

// Initialize toast manager when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        toastManager = new ToastNotification();
    });
} else {
    toastManager = new ToastNotification();
}

// Global functions for easy access
function showToast(message, type = 'info', duration = 4000) {
    if (toastManager) {
        toastManager.show(message, type, duration);
    }
}

function showSuccess(message, duration = 4000) {
    if (toastManager) {
        toastManager.success(message, duration);
    }
}

function showError(message, duration = 5000) {
    if (toastManager) {
        toastManager.error(message, duration);
    }
}

function showWarning(message, duration = 4500) {
    if (toastManager) {
        toastManager.warning(message, duration);
    }
}

function showInfo(message, duration = 4000) {
    if (toastManager) {
        toastManager.info(message, duration);
    }
}