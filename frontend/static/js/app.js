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
            case '/register':
                this.loadRegister();
                break;
            case '/profile':
                this.loadProfile();
                break;
            case '/dashboard':
                this.loadDashboard();
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
        const html = `
            <div class="container">
                <div class="row justify-content-center">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h4 class="mb-0">Login to LearnOnline.cc</h4>
                            </div>
                            <div class="card-body">
                                <form id="loginForm">
                                    <div class="mb-3">
                                        <label for="email" class="form-label">Email</label>
                                        <input type="email" class="form-control" id="email" required>
                                    </div>
                                    <div class="mb-3">
                                        <label for="password" class="form-label">Password</label>
                                        <input type="password" class="form-control" id="password" required>
                                    </div>
                                    <button type="submit" class="btn btn-primary w-100">Login</button>
                                </form>
                                
                                <hr>
                                <h6>Demo Accounts:</h6>
                                <div class="row">
                                    <div class="col-6">
                                        <button class="btn btn-outline-secondary btn-sm w-100" onclick="app.fillDemoAccount('admin')">Admin Demo</button>
                                    </div>
                                    <div class="col-6">
                                        <button class="btn btn-outline-secondary btn-sm w-100" onclick="app.fillDemoAccount('user')">User Demo</button>
                                    </div>
                                </div>
                                
                                <div class="text-center mt-3">
                                    <p>Don't have an account? <a href="#" data-page="/register">Register here</a></p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        $('#main-content').html(html);
        
        // Setup login form handler
        $('#loginForm').on('submit', async (e) => {
            e.preventDefault();
            const email = $('#email').val();
            const password = $('#password').val();
            
            try {
                const response = await api.login(email, password);
                if (response.access_token) {
                    await auth.loadCurrentUser();
                    if (response.role === 'admin') {
                        this.loadPage('/admin');
                    } else {
                        this.loadPage('/dashboard');
                    }
                }
            } catch (error) {
                alert('Login failed. Please check your credentials.');
            }
        });
    },

    fillDemoAccount(type) {
        if (type === 'admin') {
            $('#email').val('admin@learnonline.cc');
            $('#password').val('admin123');
        } else {
            $('#email').val('user@learnonline.cc');
            $('#password').val('user123');
        }
    },

    loadRegister() {
        const html = `
            <div class="container">
                <div class="row justify-content-center">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h4 class="mb-0">Register for LearnOnline.cc</h4>
                            </div>
                            <div class="card-body">
                                <form id="registerForm">
                                    <div class="mb-3">
                                        <label for="firstName" class="form-label">First Name</label>
                                        <input type="text" class="form-control" id="firstName" required>
                                    </div>
                                    <div class="mb-3">
                                        <label for="lastName" class="form-label">Last Name</label>
                                        <input type="text" class="form-control" id="lastName" required>
                                    </div>
                                    <div class="mb-3">
                                        <label for="regEmail" class="form-label">Email</label>
                                        <input type="email" class="form-control" id="regEmail" required>
                                    </div>
                                    <div class="mb-3">
                                        <label for="regPassword" class="form-label">Password</label>
                                        <input type="password" class="form-control" id="regPassword" required>
                                        <div class="form-text">Password must be at least 8 characters long</div>
                                    </div>
                                    <div class="mb-3">
                                        <label for="confirmPassword" class="form-label">Confirm Password</label>
                                        <input type="password" class="form-control" id="confirmPassword" required>
                                    </div>
                                    <button type="submit" class="btn btn-primary w-100">Register</button>
                                </form>
                                
                                <div class="text-center mt-3">
                                    <p>Already have an account? <a href="#" data-page="/login">Login here</a></p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        $('#main-content').html(html);
        
        // Setup register form handler
        $('#registerForm').on('submit', async (e) => {
            e.preventDefault();
            const password = $('#regPassword').val();
            const confirmPassword = $('#confirmPassword').val();
            
            if (password !== confirmPassword) {
                alert('Passwords do not match');
                return;
            }
            
            if (password.length < 8) {
                alert('Password must be at least 8 characters long');
                return;
            }
            
            try {
                const response = await api.register({
                    first_name: $('#firstName').val(),
                    last_name: $('#lastName').val(),
                    email: $('#regEmail').val(),
                    password: password
                });
                
                alert('Registration successful! Please login.');
                this.loadPage('/login');
            } catch (error) {
                alert('Registration failed. Please try again.');
            }
        });
    },

    loadProfile() {
        if (!auth.isAuthenticated()) {
            this.loadPage('/login');
            return;
        }
        
        const user = auth.currentUser;
        const html = `
            <div class="container">
                <div class="row">
                    <div class="col-md-8">
                        <div class="card">
                            <div class="card-header">
                                <h4 class="mb-0">User Profile</h4>
                            </div>
                            <div class="card-body">
                                <form id="profileForm">
                                    <div class="mb-3">
                                        <label for="profileFirstName" class="form-label">First Name</label>
                                        <input type="text" class="form-control" id="profileFirstName" value="${user.first_name || ''}">
                                    </div>
                                    <div class="mb-3">
                                        <label for="profileLastName" class="form-label">Last Name</label>
                                        <input type="text" class="form-control" id="profileLastName" value="${user.last_name || ''}">
                                    </div>
                                    <div class="mb-3">
                                        <label for="profileEmail" class="form-label">Email</label>
                                        <input type="email" class="form-control" id="profileEmail" value="${user.email}" readonly>
                                    </div>
                                    <button type="submit" class="btn btn-primary">Update Profile</button>
                                </form>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-header">
                                <h5 class="mb-0">Account Info</h5>
                            </div>
                            <div class="card-body">
                                <p><strong>Role:</strong> ${user.role || 'Guest'}</p>
                                <p><strong>Experience:</strong> ${user.experience_points || 0} points</p>
                                <p><strong>Level:</strong> ${user.level || 1}</p>
                                <p><strong>Member since:</strong> ${new Date(user.created_at).toLocaleDateString()}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        $('#main-content').html(html);
    },

    loadDashboard() {
        if (!auth.isAuthenticated()) {
            this.loadPage('/login');
            return;
        }
        
        const user = auth.currentUser;
        const role = user.role || 'guest';
        
        const html = `
            <div class="container">
                <div class="row">
                    <div class="col-12">
                        <h2>Welcome back, ${user.first_name || 'User'}!</h2>
                        <p class="lead">Role: ${role.charAt(0).toUpperCase() + role.slice(1)} | Experience: ${user.experience_points || 0} points</p>
                    </div>
                </div>
                
                <div class="row">
                    ${role === 'admin' ? `
                        <div class="col-md-4 mb-4">
                            <div class="card">
                                <div class="card-body text-center">
                                    <h5 class="card-title">User Management</h5>
                                    <p class="card-text">Manage users and roles</p>
                                    <a href="#" class="btn btn-primary" data-page="/admin">Admin Panel</a>
                                </div>
                            </div>
                        </div>
                    ` : ''}
                    
                    ${role === 'mentor' || role === 'admin' ? `
                        <div class="col-md-4 mb-4">
                            <div class="card">
                                <div class="card-body text-center">
                                    <h5 class="card-title">Content Creation</h5>
                                    <p class="card-text">Create and manage content</p>
                                    <a href="#" class="btn btn-success">Create Content</a>
                                </div>
                            </div>
                        </div>
                    ` : ''}
                    
                    <div class="col-md-4 mb-4">
                        <div class="card">
                            <div class="card-body text-center">
                                <h5 class="card-title">Training Units</h5>
                                <p class="card-text">Browse available training</p>
                                <a href="#" class="btn btn-primary" data-page="/units">Browse Units</a>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-4 mb-4">
                        <div class="card">
                            <div class="card-body text-center">
                                <h5 class="card-title">My Progress</h5>
                                <p class="card-text">Track your learning progress</p>
                                <a href="#" class="btn btn-info">View Progress</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        $('#main-content').html(html);
    },

    loadAdmin() {
        if (!auth.isAuthenticated()) {
            this.loadPage('/login');
            return;
        }
        if (!auth.hasRole('admin')) {
            $('#main-content').html('<div class="alert alert-danger">Access denied. Admin privileges required.</div>');
            return;
        }
        
        const html = `
            <div class="container">
                <h2>Admin Panel</h2>
                <div class="row">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h5>User Management</h5>
                            </div>
                            <div class="card-body">
                                <p>Manage users, roles, and permissions</p>
                                <button class="btn btn-primary">View Users</button>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h5>System Settings</h5>
                            </div>
                            <div class="card-body">
                                <p>Configure system settings</p>
                                <button class="btn btn-secondary">Settings</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        $('#main-content').html(html);
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
            // Hide guest navigation
            $('#nav-login').hide();
            $('#nav-register').hide();
            
            // Show authenticated navigation
            $('#nav-profile').show();
            $('#nav-dashboard').show();
            $('#nav-logout').show();
            
            // Show admin navigation if admin
            if (isAdmin) {
                $('#nav-admin').show();
            } else {
                $('#nav-admin').hide();
            }
        } else {
            // Show guest navigation
            $('#nav-login').show();
            $('#nav-register').show();
            
            // Hide authenticated navigation
            $('#nav-profile').hide();
            $('#nav-dashboard').hide();
            $('#nav-logout').hide();
            $('#nav-admin').hide();
        }
    }
};

// Initialize app when DOM is ready
$(document).ready(() => {
    app.init();
});
