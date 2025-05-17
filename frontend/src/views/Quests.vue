<template>
  <div class="quests-container">
    <div class="header-section">
      <h1>Learning Quests</h1>
      <!-- Create Quest button only for mentors or admins -->
      <el-button 
        v-if="isMentorOrAdmin"
        type="primary" 
        @click="showCreateDialog">
        Create New Quest
      </el-button>
    </div>
    
    <!-- Quest filters -->
    <div class="filter-section">
      <el-form :inline="true" class="quest-filters">
        <el-form-item label="Type">
          <el-select v-model="filters.questType" clearable placeholder="All Types">
            <el-option label="Mentor Created" value="mentor_created" />
            <el-option label="Qualification Based" value="qualification_based" />
            <el-option label="Skillset Based" value="skillset_based" />
          </el-select>
        </el-form-item>
        <el-form-item label="Created By">
          <el-select v-model="filters.creatorId" clearable placeholder="Anyone">
            <el-option label="My Quests" :value="currentUserId" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="applyFilters">Filter</el-button>
          <el-button @click="resetFilters">Reset</el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <!-- Quests grid -->
    <div v-loading="loading" class="quests-grid">
      <el-empty v-if="quests.length === 0" description="No quests found" />
      
      <el-row :gutter="20">
        <el-col 
          v-for="quest in quests" 
          :key="quest.id" 
          :xs="24" :sm="12" :md="8" :lg="6" 
          class="quest-card-col">
          <el-card 
            class="quest-card" 
            :class="{ 'mentor-created': quest.quest_type === 'mentor_created',
                     'qualification-based': quest.quest_type === 'qualification_based',
                     'skillset-based': quest.quest_type === 'skillset_based' }"
            @click="viewQuestDetails(quest)">
            <div class="quest-header">
              <div class="quest-title">{{ quest.title }}</div>
              <favorite-button 
                :itemId="quest.id" 
                itemType="quest" 
                class="favorite-button" />
            </div>
            <div class="quest-type">
              <el-tag :type="getQuestTypeTag(quest.quest_type)" size="small">
                {{ formatQuestType(quest.quest_type) }}
              </el-tag>
            </div>
            <div class="quest-description">{{ quest.description }}</div>
            <div class="quest-xp">
              <el-tag type="success">{{ quest.experience_points }} XP</el-tag>
            </div>
            <div class="quest-footer">
              <span>Created: {{ formatDate(quest.created_at) }}</span>
              <!-- Edit/Delete buttons only for creator or admin -->
              <div v-if="canEditQuest(quest)" class="quest-actions">
                <el-button 
                  size="small" 
                  type="primary" 
                  @click.stop="editQuest(quest)">
                  Edit
                </el-button>
                <el-button 
                  size="small" 
                  type="danger" 
                  @click.stop="confirmDeleteQuest(quest)">
                  Delete
                </el-button>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- Pagination -->
    <div class="pagination-container">
      <el-pagination
        v-model:currentPage="pagination.current"
        :page-size="pagination.pageSize"
        :total="pagination.total"
        layout="prev, pager, next"
        @current-change="handlePageChange"
      />
    </div>
    
    <!-- Create/Edit Quest Dialog -->
    <el-dialog
      v-model="questDialogVisible"
      :title="isEditing ? 'Edit Quest' : 'Create New Quest'"
      width="60%">
      <el-form :model="questForm" label-width="120px" :rules="questFormRules">
        <el-form-item label="Title" prop="title">
          <el-input v-model="questForm.title" />
        </el-form-item>
        
        <el-form-item label="Description" prop="description">
          <el-input v-model="questForm.description" type="textarea" rows="4" />
        </el-form-item>
        
        <el-form-item label="Quest Type" prop="quest_type">
          <el-select v-model="questForm.quest_type" placeholder="Select Type">
            <el-option label="Mentor Created" value="mentor_created" />
            <el-option label="Qualification Based" value="qualification_based" />
            <el-option label="Skillset Based" value="skillset_based" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="Source ID" v-if="questForm.quest_type !== 'mentor_created'">
          <el-input v-model="questForm.source_id" placeholder="Qualification or Skillset ID" />
        </el-form-item>
        
        <el-form-item label="Experience Points" prop="experience_points">
          <el-input-number v-model="questForm.experience_points" :min="0" />
        </el-form-item>
        
        <el-form-item label="Public" prop="is_public">
          <el-switch v-model="questForm.is_public" />
        </el-form-item>
        
        <el-form-item label="Units" prop="unit_ids">
          <el-select
            v-model="questForm.unit_ids"
            multiple
            filterable
            remote
            reserve-keyword
            placeholder="Select Units"
            :remote-method="searchUnits"
            :loading="unitsLoading">
            <el-option
              v-for="unit in availableUnits"
              :key="unit.id"
              :label="`${unit.code} - ${unit.title}`"
              :value="unit.id">
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="questDialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="saveQuest" :loading="savingQuest">
            {{ isEditing ? 'Update' : 'Create' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- Quest Details Dialog -->
    <el-dialog
      v-if="selectedQuest"
      v-model="questDetailsVisible"
      :title="selectedQuest.title"
      width="70%">
      <div class="quest-detail-header">
        <el-tag :type="getQuestTypeTag(selectedQuest.quest_type)" size="large">
          {{ formatQuestType(selectedQuest.quest_type) }}
        </el-tag>
        <el-tag type="success" size="large">{{ selectedQuest.experience_points }} XP</el-tag>
      </div>
      
      <div class="quest-detail-description">
        {{ selectedQuest.description }}
      </div>
      
      <h3>Units in this Quest</h3>
      <el-table
        v-if="selectedQuest.units && selectedQuest.units.length > 0"
        :data="unitDetails"
        style="width: 100%">
        <el-table-column type="index" width="50" />
        <el-table-column prop="code" label="Code" width="120" />
        <el-table-column prop="title" label="Title" />
        <el-table-column prop="required" label="Required" width="100">
          <template #default="scope">
            <el-tag v-if="scope.row.required" type="success">Required</el-tag>
            <el-tag v-else type="info">Optional</el-tag>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-else description="No units in this quest" />
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="questDetailsVisible = false">Close</el-button>
          <el-button 
            v-if="canEditQuest(selectedQuest)" 
            type="primary" 
            @click="editQuest(selectedQuest)">
            Edit
          </el-button>
          <el-button v-else type="primary" @click="startQuest">
            Start Quest
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import axios from 'axios';
import FavoriteButton from '@/components/FavoriteButton.vue';

export default {
  name: 'QuestsView',
  components: {
    FavoriteButton
  },
  setup() {
    // User state
    const currentUserId = ref('');
    const userLevel = ref('');
    const isMentorOrAdmin = computed(() => {
      return userLevel.value === 'mentor' || isAdmin.value;
    });
    const isAdmin = ref(false);
    
    // Quests data
    const quests = ref([]);
    const loading = ref(false);
    const pagination = reactive({
      current: 1,
      pageSize: 12,
      total: 0
    });
    
    // Filters
    const filters = reactive({
      questType: '',
      creatorId: ''
    });
    
    // Create/Edit Dialog
    const questDialogVisible = ref(false);
    const isEditing = ref(false);
    const questForm = reactive({
      id: '',
      title: '',
      description: '',
      quest_type: 'mentor_created',
      source_id: '',
      experience_points: 100,
      is_public: true,
      unit_ids: []
    });
    const questFormRules = {
      title: [{ required: true, message: 'Please input quest title', trigger: 'blur' }],
      quest_type: [{ required: true, message: 'Please select quest type', trigger: 'change' }],
      unit_ids: [{ type: 'array', required: true, message: 'Please select at least one unit', trigger: 'change' }]
    };
    const savingQuest = ref(false);
    
    // Units for quest creation/editing
    const availableUnits = ref([]);
    const unitsLoading = ref(false);
    
    // Quest details dialog
    const questDetailsVisible = ref(false);
    const selectedQuest = ref(null);
    const unitDetails = ref([]);
    
    // Fetch user info
    const fetchCurrentUser = async () => {
      try {
        const response = await axios.get('/api/users/me');
        currentUserId.value = response.data.id;
        userLevel.value = response.data.level;
        isAdmin.value = response.data.is_admin;
      } catch (error) {
        console.error('Failed to fetch user info', error);
      }
    };
    
    // Fetch quests with filters and pagination
    const fetchQuests = async () => {
      loading.value = true;
      try {
        const params = {
          skip: (pagination.current - 1) * pagination.pageSize,
          limit: pagination.pageSize
        };
        
        if (filters.questType) {
          params.quest_type = filters.questType;
        }
        
        if (filters.creatorId) {
          params.creator_id = filters.creatorId;
        }
        
        const response = await axios.get('/api/quests', { params });
        quests.value = response.data;
        
        // Update total if provided in headers
        if (response.headers['x-total-count']) {
          pagination.total = parseInt(response.headers['x-total-count']);
        }
      } catch (error) {
        ElMessage.error('Failed to load quests');
        console.error(error);
      } finally {
        loading.value = false;
      }
    };
    
    // Handle pagination changes
    const handlePageChange = (page) => {
      pagination.current = page;
      fetchQuests();
    };
    
    // Filter functions
    const applyFilters = () => {
      pagination.current = 1; // Reset to first page
      fetchQuests();
    };
    
    const resetFilters = () => {
      filters.questType = '';
      filters.creatorId = '';
      pagination.current = 1;
      fetchQuests();
    };
    
    // Create/Edit quest functions
    const showCreateDialog = () => {
      isEditing.value = false;
      questForm.id = '';
      questForm.title = '';
      questForm.description = '';
      questForm.quest_type = 'mentor_created';
      questForm.source_id = '';
      questForm.experience_points = 100;
      questForm.is_public = true;
      questForm.unit_ids = [];
      questDialogVisible.value = true;
    };
    
    const editQuest = (quest) => {
      isEditing.value = true;
      questForm.id = quest.id;
      questForm.title = quest.title;
      questForm.description = quest.description;
      questForm.quest_type = quest.quest_type;
      questForm.source_id = quest.source_id || '';
      questForm.experience_points = quest.experience_points;
      questForm.is_public = quest.is_public;
      
      // Fetch quest details to get units
      fetchQuestDetails(quest.id, true);
      
      questDialogVisible.value = true;
      
      // Close details dialog if open
      questDetailsVisible.value = false;
    };
    
    const saveQuest = async () => {
      savingQuest.value = true;
      try {
        // Using the response variable for logging status
        let response;
        
        if (isEditing.value) {
          // Update existing quest
          response = await axios.put(`/api/quests/${questForm.id}`, {
            title: questForm.title,
            description: questForm.description,
            is_public: questForm.is_public,
            experience_points: questForm.experience_points,
            unit_ids: questForm.unit_ids
          });
        } else {
          // Create new quest
          response = await axios.post('/api/quests', {
            title: questForm.title,
            description: questForm.description,
            quest_type: questForm.quest_type,
            source_id: questForm.source_id || null,
            is_public: questForm.is_public,
            experience_points: questForm.experience_points,
            unit_ids: questForm.unit_ids
          });
        }
        
        console.log('Quest operation successful with status:', response.status);
        ElMessage.success(`Quest ${isEditing.value ? 'updated' : 'created'} successfully`);
        questDialogVisible.value = false;
        fetchQuests(); // Refresh quests list
      } catch (error) {
        ElMessage.error(`Failed to ${isEditing.value ? 'update' : 'create'} quest`);
        console.error(error);
      } finally {
        savingQuest.value = false;
      }
    };
    
    // Search units for quest creation/editing
    const searchUnits = async (query) => {
      if (query.length < 2) return;
      
      unitsLoading.value = true;
      try {
        const response = await axios.get('/api/units', {
          params: { search: query, limit: 20 }
        });
        availableUnits.value = response.data;
      } catch (error) {
        console.error('Failed to search units', error);
      } finally {
        unitsLoading.value = false;
      }
    };
    
    // Delete quest
    const confirmDeleteQuest = (quest) => {
      ElMessageBox.confirm(
        'Are you sure you want to delete this quest?',
        'Warning',
        {
          confirmButtonText: 'Yes, Delete',
          cancelButtonText: 'Cancel',
          type: 'warning',
        }
      ).then(() => {
        deleteQuest(quest.id);
      }).catch(() => {
        // User canceled
      });
    };
    
    const deleteQuest = async (questId) => {
      try {
        await axios.delete(`/api/quests/${questId}`);
        ElMessage.success('Quest deleted successfully');
        fetchQuests(); // Refresh quests list
      } catch (error) {
        ElMessage.error('Failed to delete quest');
        console.error(error);
      }
    };
    
    // Quest details view
    const viewQuestDetails = async (quest) => {
      selectedQuest.value = quest;
      await fetchQuestDetails(quest.id);
      questDetailsVisible.value = true;
    };
    
    const fetchQuestDetails = async (questId, forEdit = false) => {
      try {
        const response = await axios.get(`/api/quests/${questId}`);
        
        if (forEdit) {
          // For edit mode, just update unit IDs
          questForm.unit_ids = response.data.units.map(u => u.unit_id);
          
          // Also fetch unit details for display
          await fetchUnitDetails(questForm.unit_ids);
        } else {
          selectedQuest.value = response.data;
          await fetchUnitDetails(response.data.units.map(u => u.unit_id));
        }
      } catch (error) {
        ElMessage.error('Failed to load quest details');
        console.error(error);
      }
    };
    
    // Fetch unit details for displaying in quest details
    const fetchUnitDetails = async (unitIds) => {
      if (!unitIds.length) {
        unitDetails.value = [];
        return;
      }
      
      try {
        const response = await axios.get('/api/units', {
          params: { ids: unitIds.join(',') }
        });
        
        // Match units with quest units to get sequence and required info
        const units = response.data;
        
        if (selectedQuest.value) {
          unitDetails.value = units.map(unit => {
            const questUnit = selectedQuest.value.units.find(u => u.unit_id === unit.id);
            return {
              ...unit,
              sequence: questUnit ? questUnit.sequence_number : 0,
              required: questUnit ? questUnit.is_required : true
            };
          }).sort((a, b) => a.sequence - b.sequence);
        } else {
          unitDetails.value = units;
        }
      } catch (error) {
        console.error('Failed to fetch unit details', error);
      }
    };
    
    // Start a quest (placeholder functionality)
    const startQuest = () => {
      ElMessage.info('Starting quest...');
      // Implement quest start functionality
    };
    
    // Check if user can edit/delete a quest
    const canEditQuest = (quest) => {
      return isAdmin.value || quest.creator_id === currentUserId.value;
    };
    
    // Format quest type for display
    const formatQuestType = (type) => {
      switch (type) {
        case 'mentor_created': return 'Mentor Created';
        case 'qualification_based': return 'Qualification';
        case 'skillset_based': return 'Skill Set';
        default: return type;
      }
    };
    
    // Get tag type for quest type
    const getQuestTypeTag = (type) => {
      switch (type) {
        case 'mentor_created': return 'success';
        case 'qualification_based': return 'primary';
        case 'skillset_based': return 'warning';
        default: return 'info';
      }
    };
    
    // Format date
    const formatDate = (dateString) => {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleDateString();
    };
    
    onMounted(() => {
      fetchCurrentUser();
      fetchQuests();
    });
    
    return {
      quests,
      loading,
      pagination,
      filters,
      questDialogVisible,
      isEditing,
      questForm,
      questFormRules,
      savingQuest,
      availableUnits,
      unitsLoading,
      questDetailsVisible,
      selectedQuest,
      unitDetails,
      currentUserId,
      isMentorOrAdmin,
      handlePageChange,
      applyFilters,
      resetFilters,
      showCreateDialog,
      editQuest,
      saveQuest,
      searchUnits,
      confirmDeleteQuest,
      viewQuestDetails,
      canEditQuest,
      startQuest,
      formatQuestType,
      getQuestTypeTag,
      formatDate
    };
  }
};
</script>

<style scoped>
.quests-container {
  padding: 20px;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filter-section {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.quests-grid {
  margin-bottom: 20px;
}

.quest-card-col {
  margin-bottom: 20px;
}

.quest-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: transform 0.3s;
  overflow: hidden;
}

.quest-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.quest-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.quest-title {
  font-weight: bold;
  font-size: 16px;
  flex: 1;
}

.quest-type {
  margin-bottom: 10px;
}

.quest-description {
  flex-grow: 1;
  margin-bottom: 15px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.quest-xp {
  margin-bottom: 10px;
}

.quest-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #909399;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

/* Quest card colors */
.quest-card.mentor-created {
  border-top: 3px solid #67c23a;
}

.quest-card.qualification-based {
  border-top: 3px solid #409eff;
}

.quest-card.skillset-based {
  border-top: 3px solid #e6a23c;
}

.quest-detail-header {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.quest-detail-description {
  margin-bottom: 20px;
  white-space: pre-line;
}
</style>
