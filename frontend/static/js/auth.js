const auth = {
    init() {
        this.setupLoginForm();
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
    }
};
