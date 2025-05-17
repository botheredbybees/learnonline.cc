<template>
  <div class="admin-container">
    <h1>Admin Dashboard</h1>
    
    <el-tabs v-model="activeTab">
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
              <el-form-item>
                <el-button type="success" :loading="isProcessingElements" @click="processUnitElements">
                  Process Unit Elements
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
    const activeTab = ref('training-packages');
    const trainingPackages = ref([]);
    const trainingPackagesLoading = ref(false);
    const tasks = ref([]);
    const tasksLoading = ref(false);
    const isLoading = ref(false);
    const isProcessingElements = ref(false);
    const tpCodesInput = ref('');
    const taskDetailsVisible = ref(false);
    const selectedTask = ref(null);

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

    // Fetch admin tasks
    const fetchTasks = async () => {
      tasksLoading.value = true;
      try {
        const response = await axios.get('/api/admin/tasks');
        tasks.value = response.data.tasks;
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
        
        const response = await axios.post('/api/admin/sync-training-packages', { 
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
        const response = await axios.post('/api/admin/process-unit-elements');
        
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
      fetchTrainingPackages();
      fetchTasks();
    });

    return {
      activeTab,
      trainingPackages,
      trainingPackagesLoading,
      tasks,
      tasksLoading,
      isLoading,
      isProcessingElements,
      tpCodesInput,
      taskDetailsVisible,
      selectedTask,
      fetchTrainingPackages,
      fetchTasks,
      syncTrainingPackages,
      processUnitElements,
      formatDate,
      formatDateTime,
      getStatusTagType,
      viewTaskDetails
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

pre {
  background-color: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
  font-family: monospace;
}
</style>
