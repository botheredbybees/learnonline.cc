<template>
  <div class="introductory-quest-container">
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="5" animated />
    </div>
    
    <div v-else-if="!quest" class="empty-state">
      <el-empty description="No introductory quest found">
        <template #image>
          <img src="@/assets/quest-not-found.svg" alt="Quest not found" class="empty-image" />
        </template>
        <el-button type="primary" @click="$router.push('/')">
          Return Home
        </el-button>
      </el-empty>
    </div>
    
    <div v-else class="quest-content">
      <div class="quest-header">
        <h1>{{ quest.title }}</h1>
        <div class="quest-meta">
          <el-tag type="info">Introductory Quest</el-tag>
          <span class="quest-xp">{{ quest.experience_points }} XP</span>
        </div>
        <p class="quest-description">{{ quest.description }}</p>
      </div>
      
      <el-divider content-position="center">Quest Progress</el-divider>
      
      <div class="quest-progress">
        <el-progress 
          :percentage="progressPercentage"
          :format="progressFormat"
          :stroke-width="18" 
          :color="progressColor">
        </el-progress>
      </div>
      
      <div class="quest-units">
        <h2>Units in this Quest</h2>
        <el-timeline>
          <el-timeline-item 
            v-for="unit in questUnits" 
            :key="unit.unit_id"
            :color="getUnitColor(unit)"
            :timestamp="getUnitStatus(unit)">
            <div class="unit-item" @click="startUnit(unit)">
              <h3>{{ getUnitTitle(unit.unit_id) || 'Loading...' }}</h3>
              <div class="unit-actions">
                <el-button 
                  type="primary" 
                  size="small"
                  :disabled="isUnitLocked(unit)">
                  <el-icon>
                    <component :is="getUnitButtonIcon(unit)"></component>
                  </el-icon>
                  {{ getUnitButtonText(unit) }}
                </el-button>
              </div>
            </div>
          </el-timeline-item>
        </el-timeline>
      </div>
      
      <!-- Completion Dialog - Shown when all units are completed -->
      <el-dialog
        v-model="completionDialogVisible"
        title="Congratulations!"
        width="500px">
        <div class="completion-dialog-content">
          <div class="completion-icon">
            <el-icon size="48"><circle-check-filled /></el-icon>
          </div>
          <h2>You've completed the introductory quest!</h2>
          <p>You've earned {{ quest.experience_points }} experience points.</p>
          
          <div v-if="!isLoggedIn" class="guest-call-to-action">
            <p>To save your progress and unlock more features:</p>
            <div class="register-buttons">
              <el-button type="primary" @click="goToRegister">Create Account</el-button>
              <el-button @click="goToLogin">Login</el-button>
            </div>
            <div class="guest-benefits">
              <h4>By creating an account, you'll:</h4>
              <ul>
                <li>Save your progress across devices</li>
                <li>Unlock player level features</li>
                <li>Access more training content</li>
                <li>Track your learning journey</li>
              </ul>
            </div>
          </div>
          
          <div v-else class="logged-in-completion">
            <p>Your progress has been saved and your level has been updated.</p>
            <el-button type="primary" @click="goToQuests">Explore More Quests</el-button>
          </div>
        </div>
      </el-dialog>
      
      <!-- Unit Study Dialog -->
      <el-dialog
        v-model="unitDialogVisible"
        :title="currentUnitTitle"
        fullscreen>
        <div class="unit-dialog-content">
          <!-- Unit content would go here -->
          <div class="unit-content">
            <div v-if="currentUnitContent.loading" class="unit-loading">
              <el-skeleton :rows="10" animated />
            </div>
            <div v-else>
              <!-- Simulated unit content for this example -->
              <div class="unit-section">
                <h3>Introduction</h3>
                <p>This is the introductory content for this unit.</p>
              </div>
              
              <div class="unit-section">
                <h3>Learning Objectives</h3>
                <ul>
                  <li>Objective 1</li>
                  <li>Objective 2</li>
                  <li>Objective 3</li>
                </ul>
              </div>
              
              <div class="unit-section">
                <h3>Content</h3>
                <p>This would be the main content of the unit...</p>
              </div>
              
              <!-- Unit quiz/assessment -->
              <div class="unit-assessment">
                <h3>Quick Assessment</h3>
                <el-form :model="assessmentForm">
                  <el-form-item label="Question 1: What is the main purpose of this platform?">
                    <el-radio-group v-model="assessmentForm.q1">
                      <el-radio label="1">Social networking</el-radio>
                      <el-radio label="2">Online learning</el-radio>
                      <el-radio label="3">Video streaming</el-radio>
                    </el-radio-group>
                  </el-form-item>
                  
                  <el-form-item label="Question 2: What level do you start at on this platform?">
                    <el-radio-group v-model="assessmentForm.q2">
                      <el-radio label="1">Player</el-radio>
                      <el-radio label="2">Mentor</el-radio>
                      <el-radio label="3">Guest</el-radio>
                    </el-radio-group>
                  </el-form-item>
                </el-form>
              </div>
            </div>
          </div>
          
          <div class="unit-dialog-footer">
            <el-button @click="unitDialogVisible = false">Close</el-button>
            <el-button type="primary" @click="completeCurrentUnit">Mark as Complete</el-button>
          </div>
        </div>
      </el-dialog>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, reactive } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useStore } from 'vuex';
import { ElMessage } from 'element-plus';
import { CircleCheckFilled, VideoPlay, Refresh, Right } from '@element-plus/icons-vue';
import { saveGuestProgress, getGuestProgress } from '@/utils/guestUtils';

export default {
  name: 'IntroductoryQuest',
  components: {
    CircleCheckFilled,
    VideoPlay,
    Refresh,
    Right
  },
  setup() {
    const router = useRouter();
    const route = useRoute();
    const store = useStore();
    
    // State
    const loading = ref(true);
    const quest = ref(null);
    const questUnits = ref([]);
    const unitDetails = ref({});
    const unitProgress = ref({});
    const completionDialogVisible = ref(false);
    const unitDialogVisible = ref(false);
    const currentUnitId = ref(null);
    const currentUnitContent = ref({ loading: true });
    const assessmentForm = reactive({
      q1: '',
      q2: ''
    });
    
    // Computed properties
    const isLoggedIn = computed(() => store.state.auth.isLoggedIn);
    
    const progressPercentage = computed(() => {
      if (!questUnits.value.length) return 0;
      
      const completed = questUnits.value.filter(unit => 
        unitProgress.value[unit.unit_id] && unitProgress.value[unit.unit_id].completed
      ).length;
      
      return Math.round((completed / questUnits.value.length) * 100);
    });
    
    const progressFormat = () => {
      if (!questUnits.value.length) return '0/0';
      
      const completed = questUnits.value.filter(unit => 
        unitProgress.value[unit.unit_id] && unitProgress.value[unit.unit_id].completed
      ).length;
      
      return `${completed}/${questUnits.value.length}`;
    };
    
    const progressColor = computed(() => {
      const percentage = progressPercentage.value;
      if (percentage < 30) return '#909399';
      if (percentage < 70) return '#e6a23c';
      return '#67c23a';
    });
    
    const currentUnitTitle = computed(() => {
      if (!currentUnitId.value) return '';
      return getUnitTitle(currentUnitId.value) || 'Unit';
    });
    
    // Methods
    const fetchQuest = async () => {
      loading.value = true;
      
      try {
        const questId = route.params.id;
        let response;
        
        // Try public endpoint first for guest users
        response = await fetch(`/api/public/quests/${questId}`);
        
        if (!response.ok && isLoggedIn.value) {
          // If logged in and public quest not found, try the authenticated endpoint
          response = await fetch(`/api/quests/${questId}`, {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
          });
        }
        
        if (!response.ok) {
          throw new Error('Quest not found');
        }
        
        const data = await response.json();
        quest.value = data;
        questUnits.value = data.units.sort((a, b) => a.sequence_number - b.sequence_number);
        
        // Fetch unit details
        await fetchUnitDetails();
        
        // Get existing progress
        await loadProgress();
        
        // Check if quest is complete
        checkQuestCompletion();
      } catch (error) {
        console.error('Error fetching quest:', error);
        ElMessage.error('Failed to load quest');
      } finally {
        loading.value = false;
      }
    };
    
    const fetchUnitDetails = async () => {
      if (!questUnits.value.length) return;
      
      try {
        const unitIds = questUnits.value.map(u => u.unit_id).join(',');
        const response = await fetch(`/api/units?ids=${unitIds}`);
        
        if (!response.ok) {
          throw new Error('Failed to fetch unit details');
        }
        
        const units = await response.json();
        units.forEach(unit => {
          unitDetails.value[unit.id] = unit;
        });
      } catch (error) {
        console.error('Error fetching unit details:', error);
      }
    };
    
    const loadProgress = async () => {
      if (isLoggedIn.value) {
        await loadUserProgress();
      } else {
        await loadGuestProgress();
      }
    };
    
    const loadUserProgress = async () => {
      try {
        const questId = route.params.id;
        const response = await fetch(`/api/user-quest-progress/${questId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          unitProgress.value = data.progress_data || {};
        }
      } catch (error) {
        console.error('Error loading user progress:', error);
      }
    };
    
    const loadGuestProgress = async () => {
      try {
        const progress = await getGuestProgress();
        
        if (progress && progress.quest_id === route.params.id) {
          unitProgress.value = progress.unit_progress || {};
        } else {
          unitProgress.value = {};
          questUnits.value.forEach(unit => {
            unitProgress.value[unit.unit_id] = { started: false, completed: false };
          });
        }
      } catch (error) {
        console.error('Error loading guest progress:', error);
      }
    };
    
    const saveProgress = async () => {
      if (isLoggedIn.value) {
        await saveUserProgress();
      } else {
        await saveGuestProgress(quest.value.id, unitProgress.value);
      }
      
      checkQuestCompletion();
    };
    
    const saveUserProgress = async () => {
      try {
        const questId = route.params.id;
        await fetch('/api/user-quest-progress', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            quest_id: questId,
            progress_data: unitProgress.value
          })
        });
      } catch (error) {
        console.error('Error saving user progress:', error);
      }
    };
    
    const getUnitTitle = (unitId) => {
      return unitDetails.value[unitId]?.title || `Unit ${unitId}`;
    };
    
    const getUnitStatus = (unit) => {
      const progress = unitProgress.value[unit.unit_id];
      
      if (!progress || !progress.started) {
        return 'Not Started';
      }
      
      if (progress.completed) {
        return 'Completed';
      }
      
      return 'In Progress';
    };
    
    const getUnitColor = (unit) => {
      const progress = unitProgress.value[unit.unit_id];
      
      if (!progress || !progress.started) {
        return '#909399'; // Grey
      }
      
      if (progress.completed) {
        return '#67c23a'; // Green
      }
      
      return '#e6a23c'; // Orange
    };
    
    const getUnitButtonText = (unit) => {
      const progress = unitProgress.value[unit.unit_id];
      
      if (!progress || !progress.started) {
        return 'Start';
      }
      
      if (progress.completed) {
        return 'Review';
      }
      
      return 'Continue';
    };
    
    const getUnitButtonIcon = (unit) => {
      const progress = unitProgress.value[unit.unit_id];
      
      if (!progress || !progress.started) {
        return 'VideoPlay';
      }
      
      if (progress.completed) {
        return 'Refresh';
      }
      
      return 'Right';
    };
    
    const isUnitLocked = (unit) => {
      // First unit is always unlocked
      if (unit.sequence_number === 1) return false;
      
      // For other units, check if previous unit is completed
      const prevUnitId = getPreviousUnitId(unit);
      if (!prevUnitId) return false;
      
      const prevProgress = unitProgress.value[prevUnitId];
      return !(prevProgress && prevProgress.completed);
    };
    
    const getPreviousUnitId = (unit) => {
      const prevUnit = questUnits.value.find(u => u.sequence_number === unit.sequence_number - 1);
      return prevUnit ? prevUnit.unit_id : null;
    };
    
    const startUnit = (unit) => {
      if (isUnitLocked(unit)) {
        ElMessage.warning('Complete the previous unit first');
        return;
      }
      
      currentUnitId.value = unit.unit_id;
      
      // Mark as started
      if (!unitProgress.value[unit.unit_id]) {
        unitProgress.value[unit.unit_id] = {};
      }
      unitProgress.value[unit.unit_id].started = true;
      
      // Save progress
      saveProgress();
      
      // Simulate loading unit content
      currentUnitContent.value = { loading: true };
      unitDialogVisible.value = true;
      
      // Simulate content loaded after delay
      setTimeout(() => {
        currentUnitContent.value = { 
          loading: false,
          // Here you would normally fetch the real unit content 
        };
      }, 1000);
    };
    
    const completeCurrentUnit = async () => {
      // Simple validation
      if (!assessmentForm.q1 || !assessmentForm.q2) {
        ElMessage.warning('Please answer all questions');
        return;
      }
      
      // Mark as completed
      unitProgress.value[currentUnitId.value].completed = true;
      
      // Save progress
      await saveProgress();
      
      // Close dialog
      unitDialogVisible.value = false;
      
      // Show success message
      ElMessage.success('Unit completed!');
      
      // Check quest completion
      checkQuestCompletion();
    };
    
    const checkQuestCompletion = () => {
      if (!questUnits.value.length) return;
      
      const allCompleted = questUnits.value.every(unit => 
        unitProgress.value[unit.unit_id] && unitProgress.value[unit.unit_id].completed
      );
      
      if (allCompleted) {
        // Add completion flag
        unitProgress.value.completed = true;
        
        // Save complete status
        saveProgress();
        
        // Show completion dialog
        completionDialogVisible.value = true;
      }
    };
    
    const goToRegister = () => {
      // Store the quest completion in sessionStorage
      sessionStorage.setItem('completedIntroQuest', quest.value.id);
      router.push('/register?from=quest');
    };
    
    const goToLogin = () => {
      // Store the quest completion in sessionStorage
      sessionStorage.setItem('completedIntroQuest', quest.value.id);
      router.push('/login?from=quest');
    };
    
    const goToQuests = () => {
      router.push('/quests');
    };
    
    onMounted(() => {
      fetchQuest();
    });
    
    return {
      loading,
      quest,
      questUnits,
      unitProgress,
      progressPercentage,
      progressFormat,
      progressColor,
      completionDialogVisible,
      unitDialogVisible,
      currentUnitId,
      currentUnitTitle,
      currentUnitContent,
      assessmentForm,
      isLoggedIn,
      getUnitTitle,
      getUnitStatus,
      getUnitColor,
      getUnitButtonText,
      getUnitButtonIcon,
      isUnitLocked,
      startUnit,
      completeCurrentUnit,
      goToRegister,
      goToLogin,
      goToQuests
    };
  }
};
</script>

<style scoped>
.introductory-quest-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.loading-container {
  padding: 40px 0;
}

.empty-state {
  padding: 60px 0;
  text-align: center;
}

.empty-image {
  width: 200px;
  height: 200px;
}

.quest-header {
  margin-bottom: 30px;
}

.quest-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 10px 0;
}

.quest-xp {
  font-weight: bold;
  color: #409EFF;
}

.quest-description {
  margin-top: 15px;
  font-size: 16px;
  color: #606266;
}

.quest-progress {
  margin: 30px 0;
}

.quest-units {
  margin-top: 40px;
}

.unit-item {
  cursor: pointer;
  padding: 10px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.unit-item:hover {
  background-color: #f5f7fa;
}

.unit-actions {
  margin-top: 10px;
}

.completion-dialog-content {
  text-align: center;
}

.completion-icon {
  color: #67c23a;
  margin-bottom: 20px;
}

.guest-call-to-action {
  margin-top: 20px;
  padding: 20px;
  background-color: #f0f9eb;
  border-radius: 4px;
}

.register-buttons {
  margin: 20px 0;
}

.guest-benefits {
  text-align: left;
  margin-top: 20px;
}

.unit-dialog-content {
  min-height: 500px;
  display: flex;
  flex-direction: column;
}

.unit-content {
  flex-grow: 1;
  padding: 0 20px;
}

.unit-section {
  margin-bottom: 30px;
}

.unit-assessment {
  margin-top: 40px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.unit-dialog-footer {
  padding: 20px;
  text-align: right;
  border-top: 1px solid #dcdfe6;
}
</style>
