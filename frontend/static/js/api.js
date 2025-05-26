const api = {
    baseUrl: 'http://localhost:8000',
    
    init() {
        const token = localStorage.getItem('token');
        if (token) {
            this.setToken(token);
        }
        console.log('API initialized with baseUrl:', this.baseUrl);
        return this;
    },
    
    setToken(token) {
        localStorage.setItem('token', token);
        $.ajaxSetup({
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
    },

    getToken() {
        return localStorage.getItem('token');
    },

    getAuthHeaders() {
        const token = this.getToken();
        return token ? { 'Authorization': `Bearer ${token}` } : {};
    },

    clearToken() {
        localStorage.removeItem('token');
        $.ajaxSetup({
            headers: {
                'Authorization': null
            }
        });
    },

    async login(email, password) {
        try {
            const response = await $.ajax({
                url: `${this.baseUrl}/auth/login`,
                method: 'POST',
                contentType: 'application/x-www-form-urlencoded',
                data: {
                    username: email,
                    password: password
                }
            });
            if (response.access_token) {
                this.setToken(response.access_token);
            }
            return response;
        } catch (error) {
            console.error('Login failed:', error);
            throw error;
        }
    },

    async register(userData) {
        try {
            const response = await $.ajax({
                url: `${this.baseUrl}/auth/register`,
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(userData)
            });
            return response;
        } catch (error) {
            console.error('Registration failed:', error);
            throw error;
        }
    },

    async get(endpoint) {
        try {
            const response = await $.ajax({
                url: `${this.baseUrl}${endpoint}`,
                method: 'GET',
                headers: this.getAuthHeaders()
            });
            return response;
        } catch (error) {
            console.error(`GET ${endpoint} failed:`, error);
            throw error;
        }
    },

    async post(endpoint, data) {
        try {
            const response = await $.ajax({
                url: `${this.baseUrl}${endpoint}`,
                method: 'POST',
                contentType: 'application/json',
                headers: this.getAuthHeaders(),
                data: JSON.stringify(data)
            });
            return response;
        } catch (error) {
            console.error(`POST ${endpoint} failed:`, error);
            throw error;
        }
    },

    async put(endpoint, data) {
        try {
            const response = await $.ajax({
                url: `${this.baseUrl}${endpoint}`,
                method: 'PUT',
                contentType: 'application/json',
                headers: this.getAuthHeaders(),
                data: JSON.stringify(data)
            });
            return response;
        } catch (error) {
            console.error(`PUT ${endpoint} failed:`, error);
            throw error;
        }
    },

    async delete(endpoint) {
        try {
            const response = await $.ajax({
                url: `${this.baseUrl}${endpoint}`,
                method: 'DELETE',
                headers: this.getAuthHeaders()
            });
            return response;
        } catch (error) {
            console.error(`DELETE ${endpoint} failed:`, error);
            throw error;
        }
    }
};

// Initialize API
$(document).ready(() => {
    api.init();
});
