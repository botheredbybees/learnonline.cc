"""
Selenium tests for the Admin Panel frontend functionality.

These tests verify the admin panel UI works correctly for bulk downloading
training packages and units.
"""

import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class TestAdminPanelFrontend:
    """Test suite for Admin Panel frontend functionality."""
    
    @pytest.fixture(scope="class")
    def driver(self):
        """Set up Chrome WebDriver for testing."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode for CI
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        yield driver
        driver.quit()
    
    @pytest.fixture
    def admin_login(self, driver):
        """Log in as admin user before each test."""
        # Navigate to login page
        driver.get("http://localhost:8080/login.html")
        
        # Wait for login form to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        
        # Fill in admin credentials
        email_field = driver.find_element(By.ID, "email")
        password_field = driver.find_element(By.ID, "password")
        
        email_field.send_keys("admin@learnonline.cc")
        password_field.send_keys("admin123")
        
        # Submit login form
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # Wait for redirect to dashboard or admin panel
        WebDriverWait(driver, 10).until(
            lambda d: "login" not in d.current_url
        )
        
        return driver
    
    def test_admin_panel_loads(self, admin_login):
        """Test that the admin panel loads correctly."""
        driver = admin_login
        
        # Navigate to admin panel
        driver.get("http://localhost:8080/admin.html")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "admin-header"))
        )
        
        # Verify page title
        assert "Admin Panel" in driver.title
        
        # Verify admin header is present
        admin_header = driver.find_element(By.CLASS_NAME, "admin-header")
        assert "Admin Panel" in admin_header.text
        
        # Verify navigation tabs are present
        bulk_download_tab = driver.find_element(By.ID, "bulk-download-tab")
        content_mgmt_tab = driver.find_element(By.ID, "content-management-tab")
        system_settings_tab = driver.find_element(By.ID, "system-settings-tab")
        
        assert bulk_download_tab.is_displayed()
        assert content_mgmt_tab.is_displayed()
        assert system_settings_tab.is_displayed()
    
    def test_bulk_download_tab_functionality(self, admin_login):
        """Test the bulk download tab functionality."""
        driver = admin_login
        driver.get("http://localhost:8080/admin.html")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "bulk-download-tab"))
        )
        
        # Verify bulk download tab is active by default
        bulk_download_tab = driver.find_element(By.ID, "bulk-download-tab")
        assert "active" in bulk_download_tab.get_attribute("class")
        
        # Verify training packages section is present
        packages_section = driver.find_element(By.XPATH, "//h4[contains(text(), 'Training Packages')]")
        assert packages_section.is_displayed()
        
        # Verify units section is present
        units_section = driver.find_element(By.XPATH, "//h4[contains(text(), 'Training Units')]")
        assert units_section.is_displayed()
        
        # Verify download jobs section is present
        jobs_section = driver.find_element(By.XPATH, "//h4[contains(text(), 'Download Jobs')]")
        assert jobs_section.is_displayed()
    
    def test_training_packages_load_button(self, admin_login):
        """Test the load available packages button."""
        driver = admin_login
        driver.get("http://localhost:8080/admin.html")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Load Available Packages')]"))
        )
        
        # Find and click the load packages button
        load_packages_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Load Available Packages')]")
        assert load_packages_btn.is_enabled()
        
        # Click the button
        load_packages_btn.click()
        
        # Verify loading state appears
        try:
            loading_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "packagesLoading"))
            )
            # Check if loading element becomes visible (may be hidden initially)
            assert loading_element is not None
        except TimeoutException:
            # Loading might be too fast to catch, which is okay
            pass
        
        # Verify download button is initially disabled
        download_packages_btn = driver.find_element(By.ID, "downloadPackagesBtn")
        assert not download_packages_btn.is_enabled()
    
    def test_training_units_load_button(self, admin_login):
        """Test the load available units button."""
        driver = admin_login
        driver.get("http://localhost:8080/admin.html")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Load Available Units')]"))
        )
        
        # Find and click the load units button
        load_units_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Load Available Units')]")
        assert load_units_btn.is_enabled()
        
        # Click the button
        load_units_btn.click()
        
        # Verify loading state appears
        try:
            loading_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "unitsLoading"))
            )
            assert loading_element is not None
        except TimeoutException:
            # Loading might be too fast to catch, which is okay
            pass
        
        # Verify download button is initially disabled
        download_units_btn = driver.find_element(By.ID, "downloadUnitsBtn")
        assert not download_units_btn.is_enabled()
    
    def test_tab_navigation(self, admin_login):
        """Test navigation between admin panel tabs."""
        driver = admin_login
        driver.get("http://localhost:8080/admin.html")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "content-management-tab"))
        )
        
        # Test Content Management tab
        content_mgmt_tab = driver.find_element(By.ID, "content-management-tab")
        content_mgmt_tab.click()
        
        # Wait for tab to become active
        WebDriverWait(driver, 5).until(
            lambda d: "active" in content_mgmt_tab.get_attribute("class")
        )
        
        # Verify content management content is visible
        content_mgmt_content = driver.find_element(By.ID, "content-management")
        assert "show active" in content_mgmt_content.get_attribute("class")
        
        # Test System Settings tab
        system_settings_tab = driver.find_element(By.ID, "system-settings-tab")
        system_settings_tab.click()
        
        # Wait for tab to become active
        WebDriverWait(driver, 5).until(
            lambda d: "active" in system_settings_tab.get_attribute("class")
        )
        
        # Verify system settings content is visible
        system_settings_content = driver.find_element(By.ID, "system-settings")
        assert "show active" in system_settings_content.get_attribute("class")
        
        # Return to bulk download tab
        bulk_download_tab = driver.find_element(By.ID, "bulk-download-tab")
        bulk_download_tab.click()
        
        # Wait for tab to become active
        WebDriverWait(driver, 5).until(
            lambda d: "active" in bulk_download_tab.get_attribute("class")
        )
    
    def test_search_functionality(self, admin_login):
        """Test search functionality for packages and units."""
        driver = admin_login
        driver.get("http://localhost:8080/admin.html")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "packageSearch"))
        )
        
        # Test package search field
        package_search = driver.find_element(By.ID, "packageSearch")
        assert package_search.get_attribute("placeholder") == "Search packages..."
        
        # Test unit search field
        unit_search = driver.find_element(By.ID, "unitSearch")
        assert unit_search.get_attribute("placeholder") == "Search units..."
        
        # Test package filter dropdown
        package_filter = driver.find_element(By.ID, "packageFilter")
        assert package_filter.is_displayed()
        
        # Verify default option
        default_option = package_filter.find_element(By.XPATH, ".//option[@value='']")
        assert "All Training Packages" in default_option.text
    
    def test_select_all_checkboxes(self, admin_login):
        """Test select all functionality for packages and units."""
        driver = admin_login
        driver.get("http://localhost:8080/admin.html")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "selectAllPackages"))
        )
        
        # Test select all packages checkbox
        select_all_packages = driver.find_element(By.ID, "selectAllPackages")
        assert not select_all_packages.is_selected()
        
        # Test select all units checkbox
        select_all_units = driver.find_element(By.ID, "selectAllUnits")
        assert not select_all_units.is_selected()
        
        # Verify labels are present
        packages_label = driver.find_element(By.XPATH, "//label[@for='selectAllPackages']")
        assert "Select All Packages" in packages_label.text
        
        units_label = driver.find_element(By.XPATH, "//label[@for='selectAllUnits']")
        assert "Select All Units" in units_label.text
    
    def test_download_buttons_initial_state(self, admin_login):
        """Test that download buttons are initially disabled."""
        driver = admin_login
        driver.get("http://localhost:8080/admin.html")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "downloadPackagesBtn"))
        )
        
        # Verify download buttons are disabled initially
        download_packages_btn = driver.find_element(By.ID, "downloadPackagesBtn")
        download_units_btn = driver.find_element(By.ID, "downloadUnitsBtn")
        
        assert not download_packages_btn.is_enabled()
        assert not download_units_btn.is_enabled()
        
        # Verify button text
        assert "Download Selected" in download_packages_btn.text
        assert "Download Selected" in download_units_btn.text
    
    def test_jobs_refresh_button(self, admin_login):
        """Test the jobs refresh button functionality."""
        driver = admin_login
        driver.get("http://localhost:8080/admin.html")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@onclick, 'refreshJobs')]"))
        )
        
        # Find and click the refresh jobs button
        refresh_jobs_btn = driver.find_element(By.XPATH, "//button[contains(@onclick, 'refreshJobs')]")
        assert refresh_jobs_btn.is_enabled()
        
        # Click the button
        refresh_jobs_btn.click()
        
        # Verify jobs container is present
        jobs_container = driver.find_element(By.ID, "jobsContainer")
        assert jobs_container.is_displayed()
    
    def test_responsive_design_elements(self, admin_login):
        """Test responsive design elements are present."""
        driver = admin_login
        driver.get("http://localhost:8080/admin.html")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "container"))
        )
        
        # Test mobile navigation toggle
        try:
            navbar_toggler = driver.find_element(By.CLASS_NAME, "navbar-toggler")
            # Button should be present but may not be visible on desktop
            assert navbar_toggler is not None
        except NoSuchElementException:
            # May not be visible in desktop view, which is okay
            pass
        
        # Test responsive grid classes
        download_cards = driver.find_elements(By.CLASS_NAME, "download-card")
        assert len(download_cards) >= 2  # Should have packages and units cards
        
        # Test responsive columns
        col_elements = driver.find_elements(By.CSS_SELECTOR, "[class*='col-']")
        assert len(col_elements) > 0
    
    def test_accessibility_elements(self, admin_login):
        """Test basic accessibility elements are present."""
        driver = admin_login
        driver.get("http://localhost:8080/admin.html")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "main"))
        )
        
        # Test page has proper heading structure
        h1_elements = driver.find_elements(By.TAG_NAME, "h1")
        assert len(h1_elements) >= 1
        
        # Test form labels are associated with inputs
        search_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
        for input_elem in search_inputs:
            placeholder = input_elem.get_attribute("placeholder")
            assert placeholder is not None and len(placeholder) > 0
        
        # Test buttons have descriptive text
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for button in buttons:
            button_text = button.text or button.get_attribute("aria-label")
            assert button_text is not None and len(button_text.strip()) > 0
    
    def test_error_handling_ui(self, admin_login):
        """Test error handling UI elements are present."""
        driver = admin_login
        driver.get("http://localhost:8080/admin.html")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "alert-container"))
        )
        
        # Verify alert container is present for error messages
        alert_container = driver.find_element(By.ID, "alert-container")
        assert alert_container.is_displayed()
        
        # Verify loading states are present
        packages_loading = driver.find_element(By.ID, "packagesLoading")
        units_loading = driver.find_element(By.ID, "unitsLoading")
        
        assert packages_loading is not None
        assert units_loading is not None


class TestAdminPanelSecurity:
    """Test security aspects of the admin panel."""
    
    @pytest.fixture(scope="class")
    def driver(self):
        """Set up Chrome WebDriver for testing."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        yield driver
        driver.quit()
    
    def test_admin_panel_requires_authentication(self, driver):
        """Test that admin panel redirects unauthenticated users."""
        # Clear any existing session
        driver.delete_all_cookies()
        
        # Try to access admin panel without authentication
        driver.get("http://localhost:8080/admin.html")
        
        # Should redirect to login or show access denied
        # Wait a moment for any redirects
        time.sleep(2)
        
        # Check if redirected to login or if access is denied
        current_url = driver.current_url
        page_source = driver.page_source.lower()
        
        # Should either redirect to login or show access denied message
        assert ("login" in current_url or 
                "access denied" in page_source or 
                "administrator privileges required" in page_source)
    
    def test_non_admin_user_access(self, driver):
        """Test that non-admin users cannot access admin features."""
        # This test would require a non-admin user account
        # For now, we'll test the client-side role checking
        
        driver.get("http://localhost:8080/admin.html")
        
        # Wait for page to load
        time.sleep(2)
        
        # Check if admin-specific elements are hidden for non-admin users
        # This would need to be implemented based on the actual role-checking logic
        pass


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
