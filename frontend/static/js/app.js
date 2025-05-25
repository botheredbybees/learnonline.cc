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
            case '/achievements':
                this.loadAchievements();
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

    async loadAchievements() {
        const html = `
            <div class="container">
                <div class="row">
                    <div class="col-12">
                        <h2><i class="fas fa-trophy text-warning"></i> Achievements & Gamification</h2>
                        <p class="lead">Track your progress, earn points, and unlock achievements!</p>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-4 mb-4">
                        <div class="card">
                            <div class="card-header bg-primary text-white">
                                <h5 class="mb-0"><i class="fas fa-star"></i> Your Progress</h5>
                            </div>
                            <div class="card-body" id="user-progress">
                                <div class="text-center">
                                    <div class="spinner-border" role="status">
                                        <span class="visually-hidden">Loading...</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-8 mb-4">
                        <div class="card">
                            <div class="card-header bg-success text-white">
                                <h5 class="mb-0"><i class="fas fa-medal"></i> Available Achievements</h5>
                            </div>
                            <div class="card-body" id="achievements-list">
                                <div class="text-center">
                                    <div class="spinner-border" role="status">
                                        <span class="visually-hidden">Loading...</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-12">
                        <div class="card">
                            <div class="card-header bg-info text-white">
                                <h5 class="mb-0"><i class="fas fa-ranking-star"></i> Leaderboard</h5>
                            </div>
                            <div class="card-body" id="leaderboard">
                                <div class="text-center">
                                    <div class="spinner-border" role="status">
                                        <span class="visually-hidden">Loading...</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        $('#main-content').html(html);
        
        // Load gamification data
        await this.loadGamificationData();
    },

    async loadGamificationData() {
        try {
            // Load user progress
            if (auth.isAuthenticated()) {
                const userStats = await api.get('/api/gamification/stats');
                this.displayUserProgress(userStats);
            } else {
                $('#user-progress').html(`
                    <div class="text-center">
                        <p class="text-muted">Please <a href="#" data-page="/login">login</a> to view your progress</p>
                    </div>
                `);
            }
            
            // Load achievements
            const achievements = await api.get('/api/gamification/achievements/available');
            this.displayAchievements(achievements.achievements);
            
            // Load leaderboard
            const leaderboard = await api.get('/api/gamification/leaderboard');
            this.displayLeaderboard(leaderboard);
            
        } catch (error) {
            console.error('Error loading gamification data:', error);
            $('#user-progress').html('<div class="alert alert-danger">Error loading progress data</div>');
            $('#achievements-list').html('<div class="alert alert-danger">Error loading achievements</div>');
            $('#leaderboard').html('<div class="alert alert-danger">Error loading leaderboard</div>');
        }
    },

    displayUserProgress(stats) {
        const levelProgress = ((stats.experience_points % 100) / 100) * 100;
        const nextLevelPoints = Math.ceil(stats.experience_points / 100) * 100;
        
        const html = `
            <div class="text-center mb-3">
                <h4 class="text-primary">${stats.experience_points} XP</h4>
                <p class="mb-1">Level ${stats.level}</p>
                <div class="progress mb-2">
                    <div class="progress-bar" role="progressbar" style="width: ${levelProgress}%" 
                         aria-valuenow="${levelProgress}" aria-valuemin="0" aria-valuemax="100">
                        ${Math.round(levelProgress)}%
                    </div>
                </div>
                <small class="text-muted">${nextLevelPoints - stats.experience_points} XP to next level</small>
            </div>
            
            <hr>
            
            <div class="row text-center">
                <div class="col-6">
                    <h6 class="text-success">${stats.achievements_count || 0}</h6>
                    <small class="text-muted">Achievements</small>
                </div>
                <div class="col-6">
                    <h6 class="text-info">${stats.role || 'Guest'}</h6>
                    <small class="text-muted">Role</small>
                </div>
            </div>
        `;
        $('#user-progress').html(html);
    },

    displayAchievements(achievements) {
        if (!achievements || achievements.length === 0) {
            $('#achievements-list').html('<p class="text-muted">No achievements available</p>');
            return;
        }
        
        const html = achievements.map(achievement => `
            <div class="card mb-3">
                <div class="card-body">
                    <div class="row align-items-center">
                        <div class="col-2 text-center">
                            <i class="fas fa-trophy fa-2x text-warning"></i>
                        </div>
                        <div class="col-8">
                            <h6 class="card-title mb-1">${achievement.title}</h6>
                            <p class="card-text text-muted mb-1">${achievement.description}</p>
                            <small class="text-success"><i class="fas fa-star"></i> ${achievement.experience_points} XP</small>
                        </div>
                        <div class="col-2 text-center">
                            ${achievement.unlocked ? 
                                '<span class="badge bg-success">Unlocked</span>' : 
                                '<span class="badge bg-secondary">Locked</span>'
                            }
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
        
        $('#achievements-list').html(html);
    },

    displayLeaderboard(data) {
        if (!data || !data.leaderboard || data.leaderboard.length === 0) {
            $('#leaderboard').html('<p class="text-muted">No leaderboard data available</p>');
            return;
        }
        
        const html = `
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>User</th>
                            <th>Level</th>
                            <th>Experience</th>
                            <th>Role</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.leaderboard.map((user) => `
                            <tr>
                                <td>
                                    <span class="badge ${user.rank <= 3 ? 'bg-warning' : 'bg-secondary'}">
                                        #${user.rank}
                                    </span>
                                </td>
                                <td>${user.first_name} ${user.last_name}</td>
                                <td>${user.level}</td>
                                <td>${user.experience_points} XP</td>
                                <td>
                                    <span class="badge bg-primary">${user.role}</span>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        $('#leaderboard').html(html);
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
