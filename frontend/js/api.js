const api = {
    baseUrl: 'http://localhost:8000',
    
    setToken(token) {
        localStorage.setItem('token', token);
        $.ajaxSetup({
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
    },

    init() {
        const token = localStorage.getItem('token');
        if (token) {
            this.setToken(token);
        }
    },

    async login(email, password) {
        try {
            const response = await $.ajax({
                url: `${this.baseUrl}/api/auth/login`,
                method: 'POST',
                contentType: 'application/x-www-form-urlencoded',
                data: {
                    username: email,
                    password: password
                }
            });
            this.setToken(response.access_token);
            return response;
        } catch (error) {
            console.error('Login failed:', error);
            throw error;
        }
    }
};
