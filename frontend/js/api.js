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

    getToken() {
        return localStorage.getItem('token');
    },

    clearToken() {
        localStorage.removeItem('token');
        $.ajaxSetup({
            headers: {}
        });
    },

    getAuthHeaders() {
        const token = this.getToken();
        return token ? { 'Authorization': `Bearer ${token}` } : {};
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
    },

    async getCurrentUser() {
        try {
            const response = await $.ajax({
                url: `${this.baseUrl}/api/auth/me`,
                method: 'GET',
                headers: this.getAuthHeaders()
            });
            return response;
        } catch (error) {
            console.error('Failed to get current user:', error);
            throw error;
        }
    },

    async getAvailableTrainingPackages() {
        try {
            const response = await $.ajax({
                url: `${this.baseUrl}/api/training-packages/available`,
                method: 'GET',
                headers: this.getAuthHeaders()
            });
            return response;
        } catch (error) {
            console.error('Failed to get available training packages:', error);
            throw error;
        }
    },

    async bulkDownloadTrainingPackages(packageCodes) {
        try {
            const response = await $.ajax({
                url: `${this.baseUrl}/api/training-packages/bulk-download`,
                method: 'POST',
                headers: this.getAuthHeaders(),
                data: JSON.stringify(packageCodes),
                contentType: 'application/json'
            });
            return response;
        } catch (error) {
            console.error('Failed to start bulk download:', error);
            throw error;
        }
    },

    async getAvailableUnits() {
        try {
            const response = await $.ajax({
                url: `${this.baseUrl}/api/units/available`,
                method: 'GET',
                headers: this.getAuthHeaders()
            });
            return response;
        } catch (error) {
            console.error('Failed to get available units:', error);
            throw error;
        }
    },

    async bulkDownloadUnits(unitCodes) {
        try {
            const response = await $.ajax({
                url: `${this.baseUrl}/api/units/bulk-download`,
                method: 'POST',
                headers: this.getAuthHeaders(),
                data: JSON.stringify(unitCodes),
                contentType: 'application/json'
            });
            return response;
        } catch (error) {
            console.error('Failed to start bulk download:', error);
            throw error;
        }
    },

    async getDownloadStatus(jobId) {
        try {
            const response = await $.ajax({
                url: `${this.baseUrl}/api/training-packages/download-status/${jobId}`,
                method: 'GET',
                headers: this.getAuthHeaders()
            });
            return response;
        } catch (error) {
            console.error('Failed to get download status:', error);
            throw error;
        }
    }
};
