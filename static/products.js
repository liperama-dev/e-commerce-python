async function fetchProducts(query = '', include_drafts = false) {
    try {
        const response = await fetch(`${API_URL}/products?q=${encodeURIComponent(query)}&include_drafts=${include_drafts}`);
        return await response.json();
    } catch (error) {
        console.error("Error fetching products:", error);
        return [];
    }
}

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
                <h3>${p.name}</h3>
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
