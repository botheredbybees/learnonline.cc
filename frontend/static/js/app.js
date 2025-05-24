const app = {
    init() {
        // Initialize modules
        api.init();
        auth.init();
        
        // Setup navigation events
        this.setupNavigation();
        
        // Update navigation visibility
        this.updateNavigation();
        
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
            case '/units':
                this.loadUnits();
                break;
            default:
                this.loadNotFound();
        }
    },

    // Page loading methods
    loadHome() {
        const html = `
            <div class="container">
                <div class="row">
                    <div class="col-12 text-center">
                        <h1 class="display-4 mb-4">Welcome to LearnOnline.cc</h1>
                        <p class="lead mb-5">Gamified Vocational Training Platform</p>
                        
                        <div class="row justify-content-center">
                            <div class="col-md-4 mb-4">
                                <div class="card h-100">
                                    <div class="card-body text-center">
                                        <i class="fas fa-graduation-cap fa-3x text-primary mb-3"></i>
                                        <h5 class="card-title">Training Units</h5>
                                        <p class="card-text">Explore AQTF training units, qualifications, and skill sets</p>
                                        <a href="#" class="btn btn-primary" data-page="/units">Browse Units</a>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4 mb-4">
                                <div class="card h-100">
                                    <div class="card-body text-center">
                                        <i class="fas fa-trophy fa-3x text-success mb-3"></i>
                                        <h5 class="card-title">Achievements</h5>
                                        <p class="card-text">Track your progress and earn badges</p>
                                        <a href="#" class="btn btn-success" data-page="/achievements">View Achievements</a>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4 mb-4">
                                <div class="card h-100">
                                    <div class="card-body text-center">
                                        <i class="fas fa-users fa-3x text-info mb-3"></i>
                                        <h5 class="card-title">Community</h5>
                                        <p class="card-text">Connect with other learners and mentors</p>
                                        <a href="#" class="btn btn-info" data-page="/community">Join Community</a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        $('#main-content').html(html);
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

    loadUnits() {
        if (typeof units !== 'undefined') {
            units.loadUnitsExplorer();
        } else {
            $('#main-content').html('<div class="alert alert-danger">Units module not loaded</div>');
        }
    },

    loadNotFound() {
        $('#main-content').html('<h1>Page Not Found</h1>');
    },

    updateNavigation() {
        const isAuthenticated = auth.isAuthenticated();
        const isAdmin = auth.hasRole('admin');

        // Show/hide navigation items based on authentication status
        if (isAuthenticated) {
            $('#nav-login').hide();
            $('#nav-logout').show();
            
            if (isAdmin) {
                $('#nav-admin').show();
            } else {
                $('#nav-admin').hide();
            }
        } else {
            $('#nav-login').show();
            $('#nav-logout').hide();
            $('#nav-admin').hide();
        }
    }
};

// Initialize app when DOM is ready
$(document).ready(() => {
    app.init();
});
