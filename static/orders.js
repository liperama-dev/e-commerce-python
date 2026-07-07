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
                loadProducts();
                loadOrders();
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
    }, 1500);
}
