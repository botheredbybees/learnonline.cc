const api = {
    baseUrl: '/api',
    
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
    }
};

// Initialize API
$(document).ready(() => {
    api.init();
});
