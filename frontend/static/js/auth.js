const auth = {
    currentUser: null,

    init() {
        this.setupLoginForm();
        this.loadCurrentUser();
        return this;
    },

    setupLoginForm() {
        $('#loginForm').on('submit', async (e) => {
            e.preventDefault();
            const email = $('#email').val();
            const password = $('#password').val();
            
            try {
                const response = await api.login(email, password);
                if (response.access_token) {
                    await this.loadCurrentUser();
                    if (response.is_admin) {
                        window.location.href = '/admin';
                    } else {
                        window.location.href = '/';
                    }
                }
            } catch (error) {
                alert('Login failed. Please check your credentials.');
            }
        });
    },

    async loadCurrentUser() {
        const token = api.getToken();
        if (!token) {
            this.currentUser = null;
            if (typeof app !== 'undefined') {
                app.updateNavigation();
            }
            return;
        }

        try {
            const response = await $.ajax({
                url: `${api.baseUrl}/auth/me`,
                method: 'GET',
                headers: api.getAuthHeaders()
            });
            this.currentUser = response;
            if (typeof app !== 'undefined') {
                app.updateNavigation();
            }
        } catch (error) {
            console.error('Failed to load current user:', error);
            this.currentUser = null;
            if (typeof app !== 'undefined') {
                app.updateNavigation();
            }
        }
    },

    hasRole(roleName) {
        if (!this.currentUser || !this.currentUser.role) {
            return false;
        }
        return this.currentUser.role.name === roleName;
    },

    isAuthenticated() {
        return !!api.getToken() && !!this.currentUser;
    },

    logout() {
        api.clearToken();
        this.currentUser = null;
        window.location.href = '/login';
    }
};
