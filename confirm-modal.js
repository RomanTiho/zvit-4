// Custom Confirmation Modal System

// Show confirmation modal
function showConfirm(message, onConfirm, onCancel = null) {
    console.log('showConfirm called with message:', message);
    return new Promise((resolve, reject) => {
        // Remove any existing confirm modals
        const existingModal = document.getElementById('confirm-modal');
        if (existingModal) {
            existingModal.remove();
        }

        // Create modal overlay
        const modal = document.createElement('div');
        modal.id = 'confirm-modal';
        modal.className = 'confirm-modal';

        modal.innerHTML = `
            <div class="confirm-overlay"></div>
            <div class="confirm-dialog">
                <div class="confirm-header">
                    <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                        <circle cx="24" cy="24" r="22" stroke="currentColor" stroke-width="2"/>
                        <path d="M24 16v12M24 32h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </div>
                <div class="confirm-body">
                    <h3>Підтвердження дії</h3>
                    <p>${message}</p>
                </div>
                <div class="confirm-actions">
                    <button class="btn btn-secondary confirm-cancel">Скасувати</button>
                    <button class="btn btn-primary confirm-ok">OK</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Get buttons
        const okBtn = modal.querySelector('.confirm-ok');
        const cancelBtn = modal.querySelector('.confirm-cancel');
        const overlay = modal.querySelector('.confirm-overlay');

        // Handle OK
        const handleOk = () => {
            modal.classList.add('hiding');
            setTimeout(() => {
                modal.remove();
            }, 300);

            if (onConfirm) {
                onConfirm();
            }
            resolve(true);
        };

        // Handle Cancel
        const handleCancel = () => {
            modal.classList.add('hiding');
            setTimeout(() => {
                modal.remove();
            }, 300);

            if (onCancel) {
                onCancel();
            }
            resolve(false);
        };

        // Event listeners
        okBtn.addEventListener('click', handleOk);
        cancelBtn.addEventListener('click', handleCancel);
        overlay.addEventListener('click', handleCancel);

        // Keyboard support
        const handleKeydown = (e) => {
            if (e.key === 'Enter') {
                handleOk();
                document.removeEventListener('keydown', handleKeydown);
            } else if (e.key === 'Escape') {
                handleCancel();
                document.removeEventListener('keydown', handleKeydown);
            }
        };
        document.addEventListener('keydown', handleKeydown);

        // Show modal with animation
        setTimeout(() => {
            modal.classList.add('active');
        }, 10);
    });
}
