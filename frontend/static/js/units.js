/**
 * Units module for displaying and managing training units
 * Equivalent to UnitCard.vue and UnitExplorer.vue components
 */
const units = {
    currentUnits: [],
    currentPage: 1,
    pageSize: 20,
    totalUnits: 0,
    isLoading: false,

    init() {
        console.log('Units module initialized');
        this.setupEventHandlers();
    },

    setupEventHandlers() {
        // Search form submission
        $(document).on('submit', '#unit-search-form', (e) => {
            e.preventDefault();
            this.searchUnits();
        });

        // Pagination clicks
        $(document).on('click', '.unit-pagination .page-link', (e) => {
            e.preventDefault();
            const page = $(e.currentTarget).data('page');
            if (page && page !== this.currentPage) {
                this.currentPage = page;
                this.searchUnits();
            }
        });

        // Unit card clicks
        $(document).on('click', '.unit-card', (e) => {
            const unitId = $(e.currentTarget).data('unit-id');
            if (unitId) {
                this.showUnitDetails(unitId);
            }
        });

        // Sync unit button
        $(document).on('click', '.sync-unit-btn', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const unitCode = $(e.currentTarget).data('unit-code');
            if (unitCode) {
                this.syncUnit(unitCode);
            }
        });
    },

    /**
     * Load the units explorer page
     */
    loadUnitsExplorer() {
        const html = `
            <div class="container-fluid">
                <div class="row">
                    <div class="col-12">
                        <h1 class="mb-4">Training Units Explorer</h1>
                        
                        <!-- Search Form -->
                        <div class="card mb-4">
                            <div class="card-body">
                                <form id="unit-search-form">
                                    <div class="row">
                                        <div class="col-md-6">
                                            <div class="mb-3">
                                                <label for="search-query" class="form-label">Search Units</label>
                                                <input type="text" class="form-control" id="search-query" 
                                                       placeholder="Enter unit code, title, or keywords...">
                                            </div>
                                        </div>
                                        <div class="col-md-4">
                                            <div class="mb-3">
                                                <label for="training-package-filter" class="form-label">Training Package</label>
                                                <input type="text" class="form-control" id="training-package-filter" 
                                                       placeholder="e.g., ICT, BSB, SIT...">
                                            </div>
                                        </div>
                                        <div class="col-md-2">
                                            <div class="mb-3">
                                                <label class="form-label">&nbsp;</label>
                                                <button type="submit" class="btn btn-primary w-100">
                                                    <i class="fas fa-search"></i> Search
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </form>
                            </div>
                        </div>

                        <!-- Loading Indicator -->
                        <div id="units-loading" class="text-center py-4" style="display: none;">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                            <p class="mt-2">Loading units...</p>
                        </div>

                        <!-- Units Grid -->
                        <div id="units-grid" class="row">
                            <!-- Units will be loaded here -->
                        </div>

                        <!-- Pagination -->
                        <nav aria-label="Units pagination" id="units-pagination" style="display: none;">
                            <ul class="pagination justify-content-center">
                                <!-- Pagination will be generated here -->
                            </ul>
                        </nav>
                    </div>
                </div>
            </div>
        `;
        
        $('#main-content').html(html);
        
        // Load initial units
        this.searchUnits();
    },

    /**
     * Search for units based on form inputs
     */
    async searchUnits() {
        if (this.isLoading) return;

        this.isLoading = true;
        this.showLoading(true);

        try {
            const query = $('#search-query').val() || '';
            const trainingPackage = $('#training-package-filter').val() || '';
            
            const params = new URLSearchParams({
                query: query,
                page: this.currentPage,
                page_size: this.pageSize
            });

            if (trainingPackage) {
                params.append('training_package_code', trainingPackage);
            }

            const response = await $.ajax({
                url: `${api.baseUrl}/units/search?${params.toString()}`,
                method: 'GET',
                headers: api.getAuthHeaders()
            });

            this.currentUnits = Array.isArray(response) ? response : [];
            this.displayUnits();
            this.updatePagination();

        } catch (error) {
            console.error('Error searching units:', error);
            this.showError('Failed to search units. Please try again.');
        } finally {
            this.isLoading = false;
            this.showLoading(false);
        }
    },

    /**
     * Display units in the grid
     */
    displayUnits() {
        const grid = $('#units-grid');
        
        if (!this.currentUnits || this.currentUnits.length === 0) {
            grid.html(`
                <div class="col-12">
                    <div class="alert alert-info text-center">
                        <i class="fas fa-info-circle"></i>
                        No units found. Try adjusting your search criteria.
                    </div>
                </div>
            `);
            return;
        }

        const unitsHtml = this.currentUnits.map(unit => this.createUnitCard(unit)).join('');
        grid.html(unitsHtml);
    },

    /**
     * Create a unit card (equivalent to UnitCard.vue)
     */
    createUnitCard(unit) {
        const statusBadge = this.getStatusBadge(unit.status);
        const isAdmin = auth.hasRole('admin');
        
        return `
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="card unit-card h-100" data-unit-id="${unit.id}" style="cursor: pointer;">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h6 class="mb-0 text-primary">${this.escapeHtml(unit.code)}</h6>
                        ${statusBadge}
                    </div>
                    <div class="card-body">
                        <h6 class="card-title">${this.escapeHtml(unit.title)}</h6>
                        <p class="card-text text-muted small">
                            ${unit.description ? this.escapeHtml(unit.description.substring(0, 100)) + '...' : 'No description available'}
                        </p>
                        
                        <div class="mt-3">
                            <small class="text-muted">
                                <i class="fas fa-calendar"></i>
                                ${unit.release_date ? new Date(unit.release_date).toLocaleDateString() : 'No release date'}
                            </small>
                        </div>
                    </div>
                    <div class="card-footer bg-transparent">
                        <div class="d-flex justify-content-between align-items-center">
                            <button class="btn btn-sm btn-outline-primary">
                                <i class="fas fa-eye"></i> View Details
                            </button>
                            ${isAdmin ? `
                                <button class="btn btn-sm btn-outline-secondary sync-unit-btn" 
                                        data-unit-code="${unit.code}" 
                                        title="Sync with TGA">
                                    <i class="fas fa-sync"></i>
                                </button>
                            ` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Get status badge HTML
     */
    getStatusBadge(status) {
        const statusMap = {
            'Current': 'success',
            'Superseded': 'warning',
            'Deleted': 'danger'
        };
        
        const badgeClass = statusMap[status] || 'secondary';
        return `<span class="badge bg-${badgeClass}">${status || 'Unknown'}</span>`;
    },

    /**
     * Show unit details modal
     */
    async showUnitDetails(unitId) {
        try {
            const unit = await $.ajax({
                url: `${api.baseUrl}/units/${unitId}`,
                method: 'GET',
                headers: api.getAuthHeaders()
            });

            const elements = await $.ajax({
                url: `${api.baseUrl}/units/${unitId}/elements-with-pc`,
                method: 'GET',
                headers: api.getAuthHeaders()
            });

            this.displayUnitModal(unit, elements);

        } catch (error) {
            console.error('Error loading unit details:', error);
            this.showError('Failed to load unit details.');
        }
    },

    /**
     * Display unit details in a modal
     */
    displayUnitModal(unit, elementsData) {
        const elements = elementsData.elements || [];
        
        const elementsHtml = elements.map(element => `
            <div class="card mb-3">
                <div class="card-header">
                    <h6 class="mb-0">Element ${element.element_num}: ${this.escapeHtml(element.element_text)}</h6>
                </div>
                <div class="card-body">
                    ${element.performance_criteria && element.performance_criteria.length > 0 ? `
                        <h6>Performance Criteria:</h6>
                        <ul class="list-group list-group-flush">
                            ${element.performance_criteria.map(pc => `
                                <li class="list-group-item">
                                    <strong>${pc.pc_num}:</strong> ${this.escapeHtml(pc.pc_text)}
                                </li>
                            `).join('')}
                        </ul>
                    ` : '<p class="text-muted">No performance criteria available</p>'}
                </div>
            </div>
        `).join('');

        const modalHtml = `
            <div class="modal fade" id="unitDetailsModal" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${this.escapeHtml(unit.code)} - ${this.escapeHtml(unit.title)}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            ${unit.description ? `
                                <div class="mb-4">
                                    <h6>Description:</h6>
                                    <p>${this.escapeHtml(unit.description)}</p>
                                </div>
                            ` : ''}
                            
                            <div class="mb-4">
                                <h6>Unit Information:</h6>
                                <ul class="list-unstyled">
                                    <li><strong>Code:</strong> ${this.escapeHtml(unit.code)}</li>
                                    <li><strong>Status:</strong> ${this.getStatusBadge(unit.status)}</li>
                                    <li><strong>Release Date:</strong> ${unit.release_date ? new Date(unit.release_date).toLocaleDateString() : 'Not specified'}</li>
                                </ul>
                            </div>

                            <div>
                                <h6>Elements and Performance Criteria:</h6>
                                ${elements.length > 0 ? elementsHtml : '<p class="text-muted">No elements available</p>'}
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal and add new one
        $('#unitDetailsModal').remove();
        $('body').append(modalHtml);
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('unitDetailsModal'));
        modal.show();
    },

    /**
     * Sync unit with TGA
     */
    async syncUnit(unitCode) {
        if (!auth.hasRole('admin')) {
            this.showError('Only administrators can sync units.');
            return;
        }

        try {
            const response = await $.ajax({
                url: `${api.baseUrl}/units/${unitCode}/sync`,
                method: 'POST',
                headers: api.getAuthHeaders()
            });

            this.showSuccess(`Unit ${unitCode} sync started successfully.`);
            
            // Refresh the current search after a short delay
            setTimeout(() => {
                this.searchUnits();
            }, 2000);

        } catch (error) {
            console.error('Error syncing unit:', error);
            this.showError(`Failed to sync unit ${unitCode}.`);
        }
    },

    /**
     * Update pagination controls
     */
    updatePagination() {
        const pagination = $('#units-pagination');
        
        if (this.currentUnits.length < this.pageSize) {
            pagination.hide();
            return;
        }

        // Simple pagination - could be enhanced
        const paginationHtml = `
            <li class="page-item ${this.currentPage <= 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${this.currentPage - 1}">Previous</a>
            </li>
            <li class="page-item active">
                <span class="page-link">${this.currentPage}</span>
            </li>
            <li class="page-item">
                <a class="page-link" href="#" data-page="${this.currentPage + 1}">Next</a>
            </li>
        `;
        
        pagination.find('.pagination').html(paginationHtml);
        pagination.show();
    },

    /**
     * Show/hide loading indicator
     */
    showLoading(show) {
        if (show) {
            $('#units-loading').show();
            $('#units-grid').hide();
            $('#units-pagination').hide();
        } else {
            $('#units-loading').hide();
            $('#units-grid').show();
        }
    },

    /**
     * Show error message
     */
    showError(message) {
        const alert = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                <i class="fas fa-exclamation-triangle"></i> ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        $('#main-content').prepend(alert);
    },

    /**
     * Show success message
     */
    showSuccess(message) {
        const alert = `
            <div class="alert alert-success alert-dismissible fade show" role="alert">
                <i class="fas fa-check-circle"></i> ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        $('#main-content').prepend(alert);
    },

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};

// Initialize when DOM is ready
$(document).ready(() => {
    units.init();
});
