const auth = {
    currentUser: null,

    init() {
        this.loadCurrentUser();
        return this;
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
            
            // If token is invalid (401), clear it
            if (error.status === 401) {
                console.log('Token invalid, clearing storage');
                api.clearToken();
            }
            
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
        return this.currentUser.role === roleName;
    },

    isAuthenticated() {
        return !!api.getToken() && !!this.currentUser;
    },

    logout() {
        api.clearToken();
        this.currentUser = null;
        if (typeof app !== 'undefined') {
            app.updateNavigation();
            app.loadPage('/');
        }
    }
};
