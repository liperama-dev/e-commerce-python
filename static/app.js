function showSection(sectionId) {
    if ((sectionId === 'admin' || sectionId === 'orders') && !isLoggedIn()) {
        openModal('loginModal');
        return;
    }
    document.querySelectorAll('section').forEach(s => s.classList.remove('active-section'));
    document.getElementById(`${sectionId}-section`).classList.add('active-section');

    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    event.currentTarget.classList.add('active');

    if (sectionId === 'products') {
        loadProducts();
    } else if (sectionId === 'admin') {
        loadAdminProducts();
    } else if (sectionId === 'orders') {
        loadOrders();
    }
}

function openModal(modalId) {
    document.getElementById(modalId).classList.add('show');
    if (modalId === 'loginModal') {
        fetchHint();
    }
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('show');
    if (modalId === 'productModal') {
        document.getElementById('productForm').reset();
        document.getElementById('productId').value = '';
        document.getElementById('modalTitle').innerText = 'Add Product';
        const btn = document.getElementById('publishToggleBtn');
        btn.style.display = 'none';
        btn.removeAttribute('data-product-id');
    }
}

function naTag() {
    return `<span style="background: rgba(148,163,184,0.2); color: #94a3b8; padding: 1px 6px; border-radius: 4px; font-size: 0.75rem; font-style: italic;">N/A</span>`;
}

function draftBadge() {
    return `<span style="background: var(--danger); color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; margin-left: 8px;">DRAFT</span>`;
}

async function initAuth() {
    updateNavForAuth();
    loadProducts();
}

window.onload = initAuth;
