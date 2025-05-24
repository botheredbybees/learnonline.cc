const app = {
    init() {
        // Initialize modules
        api.init();
        auth.init();
        
        // Setup navigation events
        this.setupNavigation();
        
        // Load initial content
        this.loadInitialContent();
    },

    setupNavigation() {
        $(document).on('click', 'a[data-page]', (e) => {
            e.preventDefault();
            const page = $(e.currentTarget).data('page');
            this.loadPage(page);
        });
    },

    loadInitialContent() {
        const path = window.location.pathname;
        this.loadPage(path);
    },

    loadPage(path) {
        $('#main-content').empty();
        
        switch(path) {
            case '/':
                this.loadHome();
                break;
            case '/login':
                this.loadLogin();
                break;
            case '/admin':
                this.loadAdmin();
                break;
            default:
                this.loadNotFound();
        }
    },

    // Page loading methods
    loadHome() {
        $('#main-content').html('<h1>Welcome to LearnOnline</h1>');
    },

    loadLogin() {
        $('#main-content').load('/static/pages/login.html');
    },

    loadAdmin() {
        if (!api.getToken()) {
            window.location.href = '/login';
            return;
        }
        $('#main-content').load('/static/pages/admin.html');
    },

    loadNotFound() {
        $('#main-content').html('<h1>Page Not Found</h1>');
    }
};

// Initialize app when DOM is ready
$(document).ready(() => {
    app.init();
});
