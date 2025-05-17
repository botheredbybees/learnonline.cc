<template>
  <div class="admin-container">
    <h1>Admin Dashboard</h1>
    
    <el-tabs v-model="activeTab">
      <el-tab-pane label="Users" name="users">
        <div class="admin-section">
          <h2>User Management</h2>
          
          <div class="filter-section">
            <el-form :inline="true">
              <el-form-item label="Filter by Level">
                <el-select v-model="userLevelFilter" placeholder="Select level" clearable>
                  <el-option label="Guest" value="guest" />
                  <el-option label="Player" value="player" />
                  <el-option label="Mentor" value="mentor" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="fetchUsers">Filter</el-button>
              </el-form-item>
            </el-form>
          </div>
          
          <el-table
            v-loading="usersLoading"
            :data="users"
            stripe
            style="width: 100%">
            <el-table-column prop="username" label="Username" />
            <el-table-column prop="email" label="Email" />
            <el-table-column prop="full_name" label="Full Name" />
            <el-table-column prop="experience_points" label="Experience Points" width="150" sortable />
            <el-table-column label="Level" width="100">
              <template #default="scope">
                <el-tag 
                  :type="getLevelTagType(scope.row.level)"
                  effect="dark">
                  {{ scope.row.level }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="Actions" width="250">
              <template #default="scope">
                <el-button 
                  size="small" 
                  @click="showAwardPointsDialog(scope.row)">
                  Award Points
                </el-button>
                <el-button 
                  size="small" 
                  type="primary"
                  @click="viewUserDetails(scope.row)">
                  Details
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <div class="pagination-container">
            <el-pagination
              v-model:currentPage="usersPagination.current"
              :page-size="usersPagination.pageSize"
              :total="usersPagination.total"
              layout="prev, pager, next"
              @current-change="handleUsersPageChange"
            />
          </div>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="Training Packages" name="training-packages">
        <div class="admin-section">
          <h2>Training Packages</h2>
          
          <div class="actions-panel">
            <el-form @submit.prevent="syncTrainingPackages" :inline="true">
              <el-form-item label="Specific TP Codes (optional)">
                <el-input v-model="tpCodesInput" placeholder="e.g. BSB, TAE, PUA" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" :loading="isLoading" @click="syncTrainingPackages">
                  Sync from TGA
                </el-button>
              </el-form-item>
            </el-form>
          </div>
          
          <div class="action-section">
            <h3>Process Unit Elements</h3>
            <el-form @submit.prevent="processUnitElements" :inline="false">
              <el-form-item label="Unit Code (optional)">
                <el-input v-model="unitCodeInput" placeholder="e.g. PUAAMS101" />
              </el-form-item>
              <el-form-item label="Unit ID (optional)">
                <el-input v-model="unitIdInput" placeholder="Database ID of the unit" />
              </el-form-item>
              <el-form-item>
                <el-checkbox v-model="useLocalFiles">Use local XML files</el-checkbox>
              </el-form-item>
              <el-form-item>
                <el-button type="success" :loading="isProcessingElements" @click="processUnitElements">
                  Process Units
                </el-button>
              </el-form-item>
            </el-form>
          </div>

          <el-table
            v-loading="trainingPackagesLoading"
            :data="trainingPackages"
            stripe
            style="width: 100%">
            <el-table-column prop="code" label="Code" width="100" />
            <el-table-column prop="title" label="Title" />
            <el-table-column prop="status" label="Status" width="120" />
            <el-table-column label="Release Date" width="150">
              <template #default="scope">
                {{ formatDate(scope.row.release_date) }}
              </template>
            </el-table-column>
            <el-table-column label="Last Checked" width="180">
              <template #default="scope">
                {{ formatDateTime(scope.row.last_checked) }}
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="Tasks" name="tasks">
        <div class="admin-section">
          <h2>Background Tasks</h2>
          
          <el-table
            v-loading="tasksLoading"
            :data="tasks"
            stripe
            style="width: 100%">
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="task_type" label="Type" width="150" />
            <el-table-column prop="status" label="Status" width="100">
              <template #default="scope">
                <el-tag :type="getStatusTagType(scope.row.status)">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="Created" width="180">
              <template #default="scope">
                {{ formatDateTime(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="Completed" width="180">
              <template #default="scope">
                {{ formatDateTime(scope.row.completed_at) }}
              </template>
            </el-table-column>
            <el-table-column label="Actions" width="120">
              <template #default="scope">
                <el-button 
                  size="small" 
                  @click="viewTaskDetails(scope.row)"
                  :disabled="!scope.row.result">
                  View Results
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- User Details Dialog -->
    <el-dialog
      v-model="userDetailsVisible"
      title="User Details"
      width="60%">
      <div v-if="selectedUser">
        <el-descriptions title="User Information" :column="2" border>
          <el-descriptions-item label="Username">{{ selectedUser.username }}</el-descriptions-item>
          <el-descriptions-item label="Email">{{ selectedUser.email }}</el-descriptions-item>
          <el-descriptions-item label="Full Name">{{ selectedUser.full_name || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="Admin">
            <el-tag size="small" type="danger" v-if="selectedUser.is_admin">Yes</el-tag>
            <el-tag size="small" type="info" v-else>No</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag size="small" type="success" v-if="!selectedUser.disabled">Active</el-tag>
            <el-tag size="small" type="danger" v-else>Disabled</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Created">{{ formatDateTime(selectedUser.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="Experience Points" :span="2">
            <el-progress 
              :percentage="calculateLevelProgress(selectedUser)" 
              :format="formatLevelProgress"
              :color="getLevelColor(selectedUser.level)"
              :stroke-width="20">
            </el-progress>
          </el-descriptions-item>
          <el-descriptions-item label="Level">
            <el-tag 
              :type="getLevelTagType(selectedUser.level)"
              effect="dark"
              size="large">
              {{ selectedUser.level }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
    
    <!-- Award Points Dialog -->
    <el-dialog
      v-model="awardPointsVisible"
      title="Award Experience Points"
      width="40%">
      <div v-if="selectedUser">
        <p>Awarding points to: <strong>{{ selectedUser.username }}</strong></p>
        <p>Current experience: <strong>{{ selectedUser.experience_points }}</strong> points</p>
        <p>Current level: <strong>{{ selectedUser.level }}</strong></p>
        
        <el-form @submit.prevent="submitAwardPoints">
          <el-form-item label="Points to Award">
            <el-input-number v-model="pointsToAward" :min="1" :step="10"></el-input-number>
          </el-form-item>
          <el-form-item label="Reason">
            <el-input v-model="pointsReason" type="textarea" rows="3"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="submitAwardPoints" :loading="awardingPoints">Award Points</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-dialog>

    <!-- Task Details Dialog -->
    <el-dialog
      v-model="taskDetailsVisible"
      title="Task Details"
      width="70%">
      <div v-if="selectedTask">
        <p><strong>Task ID:</strong> {{ selectedTask.id }}</p>
        <p><strong>Type:</strong> {{ selectedTask.task_type }}</p>
        <p><strong>Status:</strong> {{ selectedTask.status }}</p>
        <p><strong>Created:</strong> {{ formatDateTime(selectedTask.created_at) }}</p>
        <p v-if="selectedTask.completed_at"><strong>Completed:</strong> {{ formatDateTime(selectedTask.completed_at) }}</p>
        
        <h3>Parameters</h3>
        <pre>{{ selectedTask.params }}</pre>
        
        <h3>Results</h3>
        <pre>{{ selectedTask.result }}</pre>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import axios from 'axios';

export default {
  name: 'AdminView',
  setup() {
    // Tabs
    const activeTab = ref('users');
    
    // Users
    const users = ref([]);
    const usersLoading = ref(false);
    const userLevelFilter = ref('');
    const selectedUser = ref(null);
    const userDetailsVisible = ref(false);
    const usersPagination = ref({
      current: 1,
      pageSize: 10,
      total: 0
    });
    
    // Award points
    const awardPointsVisible = ref(false);
    const pointsToAward = ref(10);
    const pointsReason = ref('');
    const awardingPoints = ref(false);
    
    // Training Packages
    const trainingPackages = ref([]);
    const trainingPackagesLoading = ref(false);
    const isLoading = ref(false);
    const tpCodesInput = ref('');
    
    // Tasks
    const tasks = ref([]);
    const tasksLoading = ref(false);
    const selectedTask = ref(null);
    const taskDetailsVisible = ref(false);
    
    // Unit elements processing
    const isProcessingElements = ref(false);
    const unitCodeInput = ref('');
    const unitIdInput = ref('');
    const useLocalFiles = ref(false);

    // Fetch training packages
    const fetchTrainingPackages = async () => {
      trainingPackagesLoading.value = true;
      try {
        const response = await axios.get('/api/admin/training-packages');
        trainingPackages.value = response.data.training_packages;
      } catch (error) {
        ElMessage.error('Failed to load training packages');
        console.error(error);
      } finally {
        trainingPackagesLoading.value = false;
      }
    };

    // Fetch users
    const fetchUsers = async () => {
      usersLoading.value = true;
      try {
        const params = {
          skip: (usersPagination.value.current - 1) * usersPagination.value.pageSize,
          limit: usersPagination.value.pageSize
        };
        
        if (userLevelFilter.value) {
          params.level = userLevelFilter.value;
        }
        
        const response = await axios.get('/api/users', { params });
        users.value = response.data;
        
        // Update pagination total if available
        if (response.headers['x-total-count']) {
          usersPagination.value.total = parseInt(response.headers['x-total-count']);
        }
      } catch (error) {
        ElMessage.error('Failed to load users');
        console.error(error);
      } finally {
        usersLoading.value = false;
      }
    };

    // Handle page change for users
    const handleUsersPageChange = (page) => {
      usersPagination.value.current = page;
      fetchUsers();
    };

    // Show user details
    const viewUserDetails = (user) => {
      selectedUser.value = user;
      userDetailsVisible.value = true;
    };

    // Show award points dialog
    const showAwardPointsDialog = (user) => {
      selectedUser.value = user;
      pointsToAward.value = 10;
      pointsReason.value = '';
      awardPointsVisible.value = true;
    };

    // Submit award points
    const submitAwardPoints = async () => {
      if (!selectedUser.value) return;
      
      awardingPoints.value = true;
      try {
        const response = await axios.post(`/api/users/${selectedUser.value.id}/award-points`, {
          points: pointsToAward.value,
          reason: pointsReason.value || undefined
        });
        
        // Update the user in the list with new values
        const updatedUser = response.data;
        const index = users.value.findIndex(u => u.id === updatedUser.id);
        if (index !== -1) {
          users.value[index] = updatedUser;
        }
        
        // Update selected user
        selectedUser.value = updatedUser;
        
        ElMessage.success(`Awarded ${pointsToAward.value} points to ${updatedUser.username}`);
        awardPointsVisible.value = false;
      } catch (error) {
        ElMessage.error('Failed to award points');
        console.error(error);
      } finally {
        awardingPoints.value = false;
      }
    };

    // Calculate level progress percentage
    const calculateLevelProgress = (user) => {
      if (!user) return 0;
      
      const points = user.experience_points;
      let percentage = 0;
      
      if (user.level === 'guest') {
        // 0-100 points for guest
        percentage = Math.min(points / 100 * 100, 100);
      } else if (user.level === 'player') {
        // 101-1000 points for player
        const playerPoints = points - 101;
        const playerTotal = 1000 - 101;
        percentage = Math.min(playerPoints / playerTotal * 100, 100);
      } else if (user.level === 'mentor') {
        // 1001+ points for mentor
        percentage = 100; 
      }
      
      return Math.round(percentage);
    };

    // Format level progress text
    const formatLevelProgress = (percentage) => {
      if (!selectedUser.value) return '';
      // Use percentage in calculation if needed in the future
      const displayPercentage = percentage > 0 ? percentage : 0;
      return `${selectedUser.value.experience_points} points (${displayPercentage}%)`;
    };

    // Get level tag type
    const getLevelTagType = (level) => {
      switch(level) {
        case 'mentor': return 'success';
        case 'player': return 'warning';
        case 'guest': return 'info';
        default: return 'info';
      }
    };

    // Get level color for progress bar
    const getLevelColor = (level) => {
      switch(level) {
        case 'mentor': return '#67c23a';
        case 'player': return '#e6a23c';
        case 'guest': return '#909399';
        default: return '#409eff';
      }
    };

    // Fetch admin tasks
    const fetchTasks = async () => {
      tasksLoading.value = true;
      try {
        const response = await axios.get('/api/admin/tasks');
        tasks.value = response.data.tasks;
        console.log('Fetched tasks:', response.status);
      } catch (error) {
        ElMessage.error('Failed to load tasks');
        console.error(error);
      } finally {
        tasksLoading.value = false;
      }
    };

    // Sync training packages
    const syncTrainingPackages = async () => {
      isLoading.value = true;
      try {
        // Parse TP codes
        let tpCodes = null;
        if (tpCodesInput.value.trim()) {
          tpCodes = tpCodesInput.value.split(',')
            .map(code => code.trim().toUpperCase())
            .filter(code => code.length > 0);
        }
        
        await axios.post('/api/admin/sync-training-packages', { 
          tp_codes: tpCodes
        });
        
        ElMessage.success('Training package sync started');
        
        // Refresh task list
        fetchTasks();
      } catch (error) {
        ElMessage.error('Failed to start sync');
        console.error(error);
      } finally {
        isLoading.value = false;
      }
    };
    
    // Process unit elements
    const processUnitElements = async () => {
      isProcessingElements.value = true;
      try {
        // Prepare params
        const params = {};
        
        if (unitCodeInput.value) {
          params.unit_code = unitCodeInput.value.trim();
        }
        
        if (unitIdInput.value) {
          const id = parseInt(unitIdInput.value.trim());
          if (!isNaN(id)) {
            params.unit_id = id;
          }
        }
        
        if (useLocalFiles.value) {
          params.use_local_files = true;
        }
        
        await axios.post('/api/admin/process-unit-elements', params);
        console.log('Process started');
        
        ElMessage.success('Unit elements processing started');
        
        // Refresh task list
        fetchTasks();
      } catch (error) {
        ElMessage.error('Failed to start unit elements processing');
        console.error(error);
      } finally {
        isProcessingElements.value = false;
      }
    };

    // View task details
    const viewTaskDetails = (task) => {
      selectedTask.value = task;
      taskDetailsVisible.value = true;
    };

    // Format dates
    const formatDate = (dateString) => {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleDateString();
    };

    const formatDateTime = (dateTimeString) => {
      if (!dateTimeString) return 'N/A';
      const date = new Date(dateTimeString);
      return date.toLocaleString();
    };

    // Get status tag type
    const getStatusTagType = (status) => {
      switch(status) {
        case 'completed': return 'success';
        case 'failed': return 'danger';
        case 'pending': return 'warning';
        default: return 'info';
      }
    };

    // Load data when component mounts
    onMounted(() => {
      fetchUsers();
      fetchTrainingPackages();
      fetchTasks();
    });

    return {
      // Tabs
      activeTab,
      
      // User management
      users,
      usersLoading,
      userLevelFilter,
      selectedUser,
      userDetailsVisible,
      usersPagination,
      fetchUsers,
      handleUsersPageChange,
      viewUserDetails,
      
      // Award points
      awardPointsVisible,
      pointsToAward,
      pointsReason,
      awardingPoints,
      showAwardPointsDialog,
      submitAwardPoints,
      calculateLevelProgress,
      formatLevelProgress,
      getLevelTagType,
      getLevelColor,
      
      // Training packages
      trainingPackages,
      trainingPackagesLoading,
      isLoading,
      tpCodesInput,
      fetchTrainingPackages,
      syncTrainingPackages,
      
      // Tasks
      tasks,
      tasksLoading,
      selectedTask,
      taskDetailsVisible,
      fetchTasks,
      viewTaskDetails,
      getStatusTagType,
      
      // Unit elements
      isProcessingElements,
      unitCodeInput,
      unitIdInput,
      useLocalFiles,
      processUnitElements,
      
      // Utilities
      formatDate,
      formatDateTime
    };
  }
};
</script>

<style scoped>
.admin-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.admin-section {
  margin-bottom: 30px;
}

.actions-panel {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-section {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

pre {
  background-color: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
  font-family: monospace;
}
</style>
