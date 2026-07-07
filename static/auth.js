const API_URL = '/api';

function getToken() {
    return localStorage.getItem('auth_token');
}

function isLoggedIn() {
    return !!getToken();
}

function updateNavForAuth() {
    const loggedIn = isLoggedIn();
    document.getElementById('nav-admin').style.display   = loggedIn ? '' : 'none';
    document.getElementById('nav-orders').style.display  = loggedIn ? '' : 'none';
    document.getElementById('nav-signin').style.display  = loggedIn ? 'none' : '';
    document.getElementById('nav-signout').style.display = loggedIn ? '' : 'none';
    
    if (!loggedIn) {
        const active = document.querySelector('section.active-section');
        if (active && active.id !== 'products-section') {
            document.querySelectorAll('section').forEach(s => s.classList.remove('active-section'));
            document.getElementById('products-section').classList.add('active-section');
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            document.getElementById('nav-shop').classList.add('active');
            loadProducts();
        }
    }
}

async function submitLogin(e) {
    e.preventDefault();
    const username = document.getElementById('loginUsername').value.trim();
    const password = document.getElementById('loginPassword').value;
    const errorDiv = document.getElementById('loginError');
    errorDiv.style.display = 'none';

    try {
        const res = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        if (res.ok) {
            const data = await res.json();
            localStorage.setItem('auth_token', data.token);
            closeModal('loginModal');
            document.getElementById('loginForm').reset();
            updateNavForAuth();
        } else {
            errorDiv.textContent = 'Invalid username or password.';
            errorDiv.style.display = 'block';
        }
    } catch {
        errorDiv.textContent = 'Could not reach server. Please try again.';
        errorDiv.style.display = 'block';
    }
}

function logout() {
    localStorage.removeItem('auth_token');
    updateNavForAuth();
}

async function fetchHint() {
    try {
        const res = await fetch(`${API_URL}/auth/hint`);
        if (res.ok) {
            const data = await res.json();
            const hintDiv = document.getElementById('loginHint');
            document.getElementById('loginHintText').textContent =
                `${data.username} / ${data.password}`;
            hintDiv.style.display = 'block';
        }
    } catch { /* ignored outside testing mode */ }
}

async function fetchWithAdmin(url, options = {}) {
    const token = getToken();
    if (!token) {
        openModal('loginModal');
        throw new Error('Not authenticated');
    }
    options.headers = { ...options.headers, 'X-Admin-Key': token };
    const response = await fetch(url, options);
    if (response.status === 401) {
        localStorage.removeItem('auth_token');
        updateNavForAuth();
        openModal('loginModal');
        throw new Error('Session expired. Please sign in again.');
    }
    return response;
}
