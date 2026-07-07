async function loadAdminProducts() {
    const allProducts = await fetchProducts('', true);
    const tbody = document.getElementById('admin-product-list');
    const filterValue = document.getElementById('adminFilter') ? document.getElementById('adminFilter').value : 'all';
    const searchInput = document.getElementById('adminSearchInput');
    const keyword = (searchInput ? searchInput.value : '').toLowerCase().trim();

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

function editProduct(product) {
    document.getElementById('modalTitle').innerText = 'Edit Product';
    document.getElementById('productId').value = product.id;
    document.getElementById('name').value = product.name || '';
    document.getElementById('sku').value = product.sku;
    document.getElementById('description').value = product.description || '';
    document.getElementById('category').value = product.category || '';
    document.getElementById('price').value = product.price != null ? product.price : '';
    document.getElementById('stock').value = product.stock != null ? product.stock : '';
    document.getElementById('weight_kg').value = product.weight_kg != null ? product.weight_kg : '';

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
    
    // Save the product first before publishing/unpublishing
    const saveSuccess = await saveProductData();
    if (!saveSuccess) {
        return; // Don't proceed if save failed
    }
    
    // Get the updated product ID in case this was a new product
    const updatedId = document.getElementById('productId').value;
    
    try {
        const response = await fetchWithAdmin(`${API_URL}/products/${updatedId}/${action}`, { method: 'POST' });
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

async function saveProductData() {
    const id = document.getElementById('productId').value;
    
    const priceVal = document.getElementById('price').value;
    const stockVal = document.getElementById('stock').value;
    const weightVal = document.getElementById('weight_kg').value;

    const categoryVal = document.getElementById('category').value.trim();

    const product = {
        name: document.getElementById('name').value,
        sku: document.getElementById('sku').value,
        description: document.getElementById('description').value,
        category: categoryVal || 'Misc',
        price: priceVal !== '' ? parseFloat(priceVal) : null,
        stock: stockVal !== '' ? parseInt(stockVal, 10) : null,
        weight_kg: weightVal !== '' ? parseFloat(weightVal) : null,
    };

    const method = id ? 'PUT' : 'POST';
    const url = id ? `${API_URL}/products/${id}` : `${API_URL}/products`;

    try {
        const response = await fetchWithAdmin(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(product)
        });

        if (response.ok) {
            const savedProduct = await response.json();
            // Update the productId in case this was a new product
            if (!id) {
                document.getElementById('productId').value = savedProduct.id;
            }
            populateCategoryDatalist();
            loadAdminProducts();
            loadProducts();
            return true;
        } else {
            const err = await response.json();
            alert(err.detail || "Error saving product");
            return false;
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Failed to save product");
        return false;
    }
}

async function saveProduct(e) {
    e.preventDefault();
    const success = await saveProductData();
    if (success) {
        closeModal('productModal');
    }
}

async function deleteProduct(id) {
    if (!confirm("Are you sure you want to delete this product?")) return;
    
    try {
        const response = await fetchWithAdmin(`${API_URL}/products/${id}`, {
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

// ── Categories Management ────────────────────────────────────────────────────
async function populateCategoryDatalist() {
    try {
        const res = await fetch(`${API_URL}/categories`);
        if (res.ok) {
            const categories = await res.json();
            const datalist = document.getElementById('category-list');
            datalist.innerHTML = '';
            categories.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c.name;
                datalist.appendChild(opt);
            });
        }
    } catch (err) {
        console.error("Error fetching categories for list:", err);
    }
}

async function loadAdminCategories() {
    try {
        const res = await fetch(`${API_URL}/categories`);
        if (res.ok) {
            const categories = await res.json();
            const tbody = document.getElementById('admin-category-list');
            tbody.innerHTML = '';
            categories.forEach(c => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${c.id}</td>
                    <td><strong>${c.name}</strong></td>
                    <td>
                        <button class="btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;" onclick="editCategory(${c.id}, '${c.name.replace(/'/g, "\\'")}')">Rename</button>
                        <button class="btn-danger" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;" onclick="deleteCategory(${c.id})">Delete</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (err) {
        console.error("Error loading categories:", err);
    }
}

async function submitCategoryForm(e) {
    e.preventDefault();
    const nameInput = document.getElementById('newCategoryName');
    const name = nameInput.value.trim();
    if (!name) return;

    try {
        const res = await fetchWithAdmin(`${API_URL}/categories`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        });
        if (res.ok) {
            nameInput.value = '';
            loadAdminCategories();
            populateCategoryDatalist();
        } else {
            const err = await res.json();
            alert(err.detail || "Error creating category");
        }
    } catch (err) {
        console.error(err);
    }
}

async function editCategory(id, currentName) {
    const newName = prompt("Rename category:", currentName);
    if (!newName || !newName.trim() || newName.trim() === currentName) return;

    try {
        const res = await fetchWithAdmin(`${API_URL}/categories/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: newName.trim() })
        });
        if (res.ok) {
            loadAdminCategories();
            loadAdminProducts();
            populateCategoryDatalist();
        } else {
            const err = await res.json();
            alert(err.detail || "Error updating category");
        }
    } catch (err) {
        console.error(err);
    }
}

async function deleteCategory(id) {
    if (!confirm("Are you sure you want to delete this category? All associated products will become uncategorized.")) return;

    try {
        const res = await fetchWithAdmin(`${API_URL}/categories/${id}`, {
            method: 'DELETE'
        });
        if (res.ok) {
            loadAdminCategories();
            loadAdminProducts();
            populateCategoryDatalist();
        } else {
            const err = await res.json();
            alert(err.detail || "Error deleting category");
        }
    } catch (err) {
        console.error(err);
    }
}

