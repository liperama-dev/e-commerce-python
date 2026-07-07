const API_URL = '/api';

// Navigation
function showSection(sectionId) {
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

// Data Fetching
async function fetchProducts(query = '', include_drafts = false) {
    try {
        const response = await fetch(`${API_URL}/products?q=${encodeURIComponent(query)}&include_drafts=${include_drafts}`);
        return await response.json();
    } catch (error) {
        console.error("Error fetching products:", error);
        return [];
    }
}

// Shop Section
async function loadProducts() {
    const products = await fetchProducts('', false);
    renderProductGrid(products);
}

async function searchProducts() {
    const query = document.getElementById('searchInput').value;
    const products = await fetchProducts(query, false);
    renderProductGrid(products);
}

function renderProductGrid(products) {
    const grid = document.getElementById('product-grid');
    grid.innerHTML = '';
    
    if (products.length === 0) {
        grid.innerHTML = '<p>No products found.</p>';
        return;
    }

    products.forEach(p => {
        const outOfStock = p.stock == null || p.stock <= 0;
        const card = document.createElement('div');
        card.className = 'product-card';
        card.innerHTML = `
            <div class="product-header">
                <h3>${p.name ? p.name : naTag()}</h3>
                <span class="product-price">${p.price != null ? '$' + p.price.toFixed(2) : 'N/A'}</span>
            </div>
            <div class="product-meta">
                <span>SKU: ${p.sku}</span>
                <span>Category: ${p.category}</span>
            </div>
            <p class="product-desc">${p.description || ''}</p>
            <div class="product-meta">
                <span style="color: ${outOfStock ? 'var(--danger)' : 'var(--success)'}">
                    ${outOfStock ? 'Out of Stock' : `${p.stock} in stock`}
                </span>
                <span>${p.weight_kg != null ? p.weight_kg + ' kg' : 'N/A'}</span>
            </div>
            <button class="btn-primary" 
                    ${outOfStock ? 'disabled style="opacity: 0.5; cursor: not-allowed;"' : ''} 
                    onclick='openPurchaseModal(${JSON.stringify(p).replace(/'/g, "&#39;")})'>
                ${outOfStock ? 'Out of Stock' : 'Buy Now'}
            </button>
        `;
        grid.appendChild(card);
    });
}

// Helpers
function naTag() {
    return `<span style="background: rgba(148,163,184,0.2); color: #94a3b8; padding: 1px 6px; border-radius: 4px; font-size: 0.75rem; font-style: italic;">N/A</span>`;
}
function draftBadge() {
    return `<span style="background: var(--danger); color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; margin-left: 8px;">DRAFT</span>`;
}

// Admin Section
async function loadAdminProducts() {
    const allProducts = await fetchProducts('', true);
    const tbody = document.getElementById('admin-product-list');
    const filterValue = document.getElementById('adminFilter') ? document.getElementById('adminFilter').value : 'all';
    const searchInput = document.getElementById('adminSearchInput');
    const keyword = (searchInput ? searchInput.value : '').toLowerCase().trim();

    // Update draft banner
    const draftCount = allProducts.filter(p => p.is_draft).length;
    const banner = document.getElementById('draftsBanner');
    const bannerText = document.getElementById('draftsBannerText');
    if (draftCount > 0) {
        bannerText.textContent = `${draftCount} product${draftCount > 1 ? 's' : ''} need${draftCount === 1 ? 's' : ''} your attention`;
        banner.style.display = 'flex';
    } else {
        banner.style.display = 'none';
    }

    tbody.innerHTML = '';
    
    allProducts.forEach(p => {
        if (filterValue === 'drafts' && !p.is_draft) return;
        if (filterValue === 'published' && p.is_draft) return;
        if (keyword) {
            const haystack = `${p.name || ''} ${p.sku} ${p.description || ''} ${p.category}`.toLowerCase();
            if (!haystack.includes(keyword)) return;
        }

        const tr = document.createElement('tr');
        const badge = p.is_draft ? draftBadge() : '';
        const displayName = p.name ? p.name : naTag();
        const priceCell = p.price != null ? `$${p.price.toFixed(2)}` : naTag();
        const stockCell = p.stock != null ? p.stock : naTag();
        const weightCell = p.weight_kg != null ? `${p.weight_kg.toFixed(2)} kg` : naTag();
        tr.innerHTML = `
            <td>${p.sku}</td>
            <td>${displayName} ${badge}</td>
            <td>${p.category}</td>
            <td>${priceCell}</td>
            <td>${stockCell}</td>
            <td>${weightCell}</td>
            <td>
                <button class="btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;" onclick='editProduct(${JSON.stringify(p).replace(/'/g, "&#39;")})'>Edit</button>
                <button class="btn-danger" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;" onclick="deleteProduct(${p.id})">Delete</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function activateDraftFilter() {
    const filter = document.getElementById('adminFilter');
    filter.value = 'drafts';
    loadAdminProducts();
}

// Orders Section
async function loadOrders() {
    try {
        const response = await fetch(`${API_URL}/orders`);
        const orders = await response.json();
        renderOrders(orders);
    } catch (error) {
        console.error('Error fetching orders:', error);
    }
}

function renderOrders(orders) {
    const tbody = document.getElementById('orders-list');
    const empty = document.getElementById('orders-empty');
    tbody.innerHTML = '';

    if (!orders || orders.length === 0) {
        empty.style.display = 'block';
        return;
    }
    empty.style.display = 'none';

    orders.forEach(o => {
        const tr = document.createElement('tr');
        const total = o.unit_price != null ? (o.unit_price * o.quantity).toFixed(2) : 'N/A';
        const unitPrice = o.unit_price != null ? `$${o.unit_price.toFixed(2)}` : 'N/A';
        const date = new Date(o.created_at).toLocaleString();
        tr.innerHTML = `
            <td style="color: var(--text-secondary); font-size: 0.85rem;">#${o.id}</td>
            <td>${o.product_name || '—'}</td>
            <td style="color: var(--text-secondary);">${o.product_sku || '—'}</td>
            <td>${o.quantity}</td>
            <td>${unitPrice}</td>
            <td style="color: var(--accent); font-weight: 600;">$${total}</td>
            <td style="color: var(--text-secondary); font-size: 0.85rem;">${date}</td>
        `;
        tbody.appendChild(tr);
    });
}

// Authentication helper for admin operations
function getAdminKey() {
    let key = localStorage.getItem('admin_key');
    if (!key) {
        key = prompt("Please enter the Admin Secret Key:");
        if (key) {
            localStorage.setItem('admin_key', key);
        }
    }
    return key;
}

async function fetchWithAdmin(url, options = {}) {
    const key = getAdminKey();
    if (!key) {
        throw new Error("Admin key is required");
    }
    options.headers = {
        ...options.headers,
        'X-Admin-Key': key
    };
    const response = await fetch(url, options);
    if (response.status === 401) {
        localStorage.removeItem('admin_key');
        alert("Invalid Admin Key. Please try again.");
    }
    return response;
}

async function uploadCsv() {
    const fileInput = document.getElementById('csvFile');
    if (!fileInput.files[0]) {
        alert("Please select a file first");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    try {
        const response = await fetchWithAdmin(`${API_URL}/products/import`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            if (response.status !== 401) {
                const result = await response.json();
                alert(result.detail || "Error importing CSV");
            }
            return;
        }

        const result = await response.json();
        const jobId = result.job_id;

        // Show status banner of background processing
        let statusDiv = document.getElementById('import-status-banner');
        if (!statusDiv) {
            statusDiv = document.createElement('div');
            statusDiv.id = 'import-status-banner';
            statusDiv.style = "background: rgba(59,130,246,0.15); border: 1px solid rgba(59,130,246,0.4); border-radius: 10px; padding: 1rem; margin-bottom: 1.5rem; color: #93c5fd;";
            const adminSection = document.getElementById('admin-section');
            adminSection.insertBefore(statusDiv, adminSection.firstChild);
        }
        statusDiv.style.display = 'block';
        statusDiv.innerHTML = `<strong>CSV processing...</strong> Job ID: ${jobId}`;

        // Poll status
        const pollInterval = setInterval(async () => {
            try {
                const statusRes = await fetchWithAdmin(`${API_URL}/products/import/${jobId}`);
                if (!statusRes.ok) {
                    clearInterval(pollInterval);
                    statusDiv.style.display = 'none';
                    return;
                }
                const statusData = await statusRes.json();
                if (statusData.status === 'completed') {
                    clearInterval(pollInterval);
                    statusDiv.style.display = 'none';
                    
                    let alertMsg = `Import Complete!\n\nImported: ${statusData.imported_count}\nDiscarded: ${statusData.discarded_count}\n`;
                    if (statusData.discard_reasons && statusData.discard_reasons.length > 0) {
                        alertMsg += `\nReasons:\n` + statusData.discard_reasons.map(r => `Row ${r.row}: ${r.reason}`).join("\n");
                    }
                    alert(alertMsg);
                    
                    fileInput.value = '';
                    loadAdminProducts();
                    loadProducts();
                } else if (statusData.status === 'failed') {
                    clearInterval(pollInterval);
                    statusDiv.style.display = 'none';
                    alert(`Import failed: ${statusData.error}`);
                }
            } catch (err) {
                console.error(err);
                clearInterval(pollInterval);
                statusDiv.style.display = 'none';
            }
        }, 1000);

    } catch (error) {
        console.error("Error:", error);
        alert("Failed to upload CSV");
    }
}

async function flushDatabase() {
    if (!confirm("Are you sure you want to flush the database? This will delete all products immediately.")) return;
    
    try {
        const response = await fetchWithAdmin(`${API_URL}/products/flush`, {
            method: 'POST'
        });
        if (response.ok) {
            alert("Database flushed successfully!");
            loadAdminProducts();
            loadProducts();
        } else if (response.status !== 401) {
            alert("Error flushing database");
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Failed to flush database");
    }
}

// CRUD Operations
function openModal(modalId) {
    document.getElementById(modalId).classList.add('show');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('show');
    if (modalId === 'productModal') {
        document.getElementById('productForm').reset();
        document.getElementById('productId').value = '';
        document.getElementById('modalTitle').innerText = 'Add Product';
        // Reset publish toggle button
        const btn = document.getElementById('publishToggleBtn');
        btn.style.display = 'none';
        btn.removeAttribute('data-product-id');
    }
}

function editProduct(product) {
    document.getElementById('modalTitle').innerText = 'Edit Product';
    document.getElementById('productId').value = product.id;
    document.getElementById('name').value = product.name;
    document.getElementById('sku').value = product.sku;
    document.getElementById('description').value = product.description || '';
    document.getElementById('category').value = product.category || '';
    // Leave blank if null so user sees empty field
    document.getElementById('price').value = product.price != null ? product.price : '';
    document.getElementById('stock').value = product.stock != null ? product.stock : '';
    document.getElementById('weight_kg').value = product.weight_kg != null ? product.weight_kg : '';

    // Configure the publish/unpublish toggle button
    const btn = document.getElementById('publishToggleBtn');
    btn.setAttribute('data-product-id', product.id);
    btn.setAttribute('data-is-draft', product.is_draft);
    btn.style.display = 'inline-block';
    if (product.is_draft) {
        btn.textContent = '✔ Publish';
        btn.className = 'btn-primary';
        btn.style.background = 'var(--success)';
    } else {
        btn.textContent = 'Unpublish';
        btn.className = 'btn-secondary';
        btn.style.background = '';
    }
    
    openModal('productModal');
}

async function togglePublish() {
    const btn = document.getElementById('publishToggleBtn');
    const id = btn.getAttribute('data-product-id');
    const isDraft = btn.getAttribute('data-is-draft') === 'true';
    const action = isDraft ? 'publish' : 'unpublish';
    
    try {
        const response = await fetch(`${API_URL}/products/${id}/${action}`, { method: 'POST' });
        if (response.ok) {
            closeModal('productModal');
            loadAdminProducts();
            loadProducts();
        } else {
            const err = await response.json();
            alert(err.detail || `Failed to ${action} product`);
        }
    } catch (error) {
        console.error("Error:", error);
        alert(`Failed to ${action} product`);
    }
}

async function saveProduct(e) {
    e.preventDefault();
    const id = document.getElementById('productId').value;
    
    const priceVal = document.getElementById('price').value;
    const stockVal = document.getElementById('stock').value;
    const weightVal = document.getElementById('weight_kg').value;

    const product = {
        name: document.getElementById('name').value,
        sku: document.getElementById('sku').value,
        description: document.getElementById('description').value,
        category: document.getElementById('category').value,
        price: priceVal !== '' ? parseFloat(priceVal) : null,
        stock: stockVal !== '' ? parseInt(stockVal, 10) : null,
        weight_kg: weightVal !== '' ? parseFloat(weightVal) : null,
    };

    const method = id ? 'PUT' : 'POST';
    const url = id ? `${API_URL}/products/${id}` : `${API_URL}/products`;

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(product)
        });

        if (response.ok) {
            closeModal('productModal');
            loadAdminProducts();
            loadProducts();
        } else {
            const err = await response.json();
            alert(err.detail || "Error saving product");
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Failed to save product");
    }
}

async function deleteProduct(id) {
    if (!confirm("Are you sure you want to delete this product?")) return;
    
    try {
        const response = await fetch(`${API_URL}/products/${id}`, {
            method: 'DELETE'
        });
        if (response.ok) {
            loadAdminProducts();
            loadProducts();
        } else {
            alert("Error deleting product");
        }
    } catch (error) {
        console.error("Error:", error);
    }
}

// Purchase Flow
function openPurchaseModal(product) {
    document.getElementById('purchaseProductId').value = product.id;
    const infoDiv = document.getElementById('purchaseProductInfo');
    infoDiv.innerHTML = `
        <div style="background: rgba(0,0,0,0.2); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <h3 style="margin-bottom: 0.5rem;">${product.name}</h3>
            <div style="display: flex; justify-content: space-between;">
                <span>Total Amount:</span>
                <strong style="color: var(--accent)">${product.price != null ? '$' + product.price.toFixed(2) : 'N/A'}</strong>
            </div>
        </div>
    `;
    document.getElementById('purchaseForm').reset();
    openModal('purchaseModal');
}

function autoFillPayment() {
    document.getElementById('ccName').value = "John Doe";
    document.getElementById('ccNumber').value = "4111 1111 1111 1111";
    document.getElementById('ccExp').value = "12/26";
    document.getElementById('ccCvc').value = "123";
}

async function confirmPurchase(e) {
    e.preventDefault();
    const id = document.getElementById('purchaseProductId').value;
    
    // Simulate payment processing delay
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerText;
    submitBtn.innerText = "Processing...";
    submitBtn.disabled = true;
    
    setTimeout(async () => {
        try {
            const response = await fetch(`${API_URL}/products/${id}/purchase`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            });
            
            if (response.ok) {
                alert("Payment successful! Your order is confirmed.");
                closeModal('purchaseModal');
                loadProducts(); // refresh stock
                loadOrders();   // reflect new order in history
            } else {
                const err = await response.json();
                alert(err.detail || "Purchase failed");
            }
        } catch (error) {
            console.error("Error:", error);
            alert("Failed to process purchase");
        } finally {
            submitBtn.innerText = originalText;
            submitBtn.disabled = false;
        }
    }, 1500); // 1.5s fake delay
}

// Init
window.onload = loadProducts;
