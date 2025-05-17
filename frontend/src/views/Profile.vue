<template>
  <div class="profile-container">
    <el-row :gutter="20">
      <!-- User Info Card -->
      <el-col :span="8">
        <div class="profile-card">
          <div class="profile-header">
            <div class="avatar-container">
              <el-avatar :size="100">{{ userInitials }}</el-avatar>
            </div>
            <h2>{{ user.username }}</h2>
            <p class="user-email">{{ user.email }}</p>
          </div>
          
          <div class="profile-details">
            <div class="user-level">
              <h3>Level: <span class="level-tag">{{ user.level }}</span></h3>
              <el-progress 
                :percentage="levelProgress" 
                :format="formatLevelProgress"
                :color="getLevelColor"
                :stroke-width="15">
              </el-progress>
            </div>
            
            <div class="user-stats">
              <div class="stat-item">
                <div class="stat-value">{{ user.experience_points || 0 }}</div>
                <div class="stat-label">Experience Points</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ completedUnitsCount }}</div>
                <div class="stat-label">Units Completed</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ completedQuestsCount }}</div>
                <div class="stat-label">Quests Completed</div>
              </div>
            </div>
            
            <div class="user-info">
              <div class="info-item">
                <div class="info-label">Name:</div>
                <div class="info-value">{{ user.full_name || 'Not set' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">Member since:</div>
                <div class="info-value">{{ formatDate(user.created_at) }}</div>
              </div>
            </div>
          </div>
        </div>
      </el-col>
      
      <!-- Main Content Area -->
      <el-col :span="16">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="Favorites" name="favorites">
            <user-favorites />
          </el-tab-pane>
          <el-tab-pane label="Progress" name="progress">
            <h3>Your Learning Progress</h3>
            <div v-if="loading" class="loading-container">
              <el-skeleton :rows="5" animated />
            </div>
            <div v-else>
              <el-empty v-if="!hasProgress" description="No learning progress yet">
                <el-button type="primary" @click="$router.push('/quests')">
                  Start a Quest
                </el-button>
              </el-empty>
              <div v-else class="progress-content">
                <!-- Progress content goes here -->
              </div>
            </div>
          </el-tab-pane>
          <el-tab-pane label="Account Settings" name="settings">
            <h3>Account Settings</h3>
            <el-form 
              ref="userForm" 
              :model="userForm" 
              :rules="userFormRules"
              label-width="120px">
              <el-form-item label="Username" prop="username">
                <el-input v-model="userForm.username" />
              </el-form-item>
              <el-form-item label="Email" prop="email">
                <el-input v-model="userForm.email" />
              </el-form-item>
              <el-form-item label="Full Name" prop="full_name">
                <el-input v-model="userForm.full_name" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="updateProfile" :loading="updating">
                  Update Profile
                </el-button>
              </el-form-item>
            </el-form>
            
            <el-divider />
            
            <h3>Change Password</h3>
            <el-form 
              ref="passwordForm" 
              :model="passwordForm" 
              :rules="passwordRules"
              label-width="180px">
              <el-form-item label="Current Password" prop="current_password">
                <el-input 
                  v-model="passwordForm.current_password" 
                  type="password" 
                  show-password />
              </el-form-item>
              <el-form-item label="New Password" prop="new_password">
                <el-input 
                  v-model="passwordForm.new_password" 
                  type="password"
                  show-password />
              </el-form-item>
              <el-form-item label="Confirm New Password" prop="confirm_password">
                <el-input 
                  v-model="passwordForm.confirm_password" 
                  type="password"
                  show-password />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="changePassword" :loading="changingPassword">
                  Change Password
                </el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>
        </el-tabs>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { useStore } from 'vuex';
import axios from 'axios';
import UserFavorites from '@/components/UserFavorites.vue';

export default {
  name: 'ProfileView',
  components: {
    UserFavorites
  },
  setup() {
    const store = useStore();
    
    // User data
    const user = ref({});
    const loading = ref(true);
    const activeTab = ref('favorites');
    
    // Form data
    const userForm = reactive({
      username: '',
      email: '',
      full_name: ''
    });
    
    const passwordForm = reactive({
      current_password: '',
      new_password: '',
      confirm_password: ''
    });
    
    const userFormRules = {
      username: [{ required: true, message: 'Please input username', trigger: 'blur' }],
      email: [
        { required: true, message: 'Please input email', trigger: 'blur' },
        { type: 'email', message: 'Please input valid email', trigger: 'blur' }
      ]
    };
    
    const passwordRules = {
      current_password: [
        { required: true, message: 'Please input current password', trigger: 'blur' }
      ],
      new_password: [
        { required: true, message: 'Please input new password', trigger: 'blur' },
        { min: 8, message: 'Password must be at least 8 characters', trigger: 'blur' }
      ],
      confirm_password: [
        { required: true, message: 'Please confirm password', trigger: 'blur' },
        {
          validator: (rule, value, callback) => {
            if (value !== passwordForm.new_password) {
              callback(new Error('Passwords do not match!'));
            } else {
              callback();
            }
          },
          trigger: 'blur'
        }
      ]
    };
    
    // UI state
    const updating = ref(false);
    const changingPassword = ref(false);
    
    // Progress data (placeholder)
    const completedUnitsCount = ref(0);
    const completedQuestsCount = ref(0);
    const hasProgress = computed(() => completedUnitsCount.value > 0 || completedQuestsCount.value > 0);
    
    // Computed properties
    const userInitials = computed(() => {
      if (!user.value.username) return '';
      return user.value.username.substring(0, 2).toUpperCase();
    });
    
    const levelProgress = computed(() => {
      if (!user.value.experience_points) return 0;
      
      const points = user.value.experience_points;
      let percentage = 0;
      
      if (user.value.level === 'guest') {
        // 0-100 points for guest
        percentage = Math.min(points / 100 * 100, 100);
      } else if (user.value.level === 'player') {
        // 101-1000 points for player
        const playerPoints = points - 101;
        const playerTotal = 1000 - 101;
        percentage = Math.min(playerPoints / playerTotal * 100, 100);
      } else if (user.value.level === 'mentor') {
        // 1001+ points for mentor
        percentage = 100; 
      }
      
      return Math.round(percentage);
    });
    
    const getLevelColor = computed(() => {
      switch(user.value.level) {
        case 'mentor': return '#67c23a';
        case 'player': return '#e6a23c';
        case 'guest': return '#909399';
        default: return '#409eff';
      }
    });
    
    // Format level progress text
    const formatLevelProgress = (percentage) => {
      if (!user.value.experience_points) return '';
      
      const points = user.value.experience_points;
      
      if (user.value.level === 'guest') {
        const remainingForPlayer = 101 - points;
        return `${points}/100 points (${remainingForPlayer} to Player)`;
      } else if (user.value.level === 'player') {
        const remainingForMentor = 1001 - points;
        return `${points}/1000 points (${remainingForMentor} to Mentor)`;
      } else if (user.value.level === 'mentor') {
        return `${points} points (Mentor)`;
      }
      
      return `${points} points`;
    };
    
    // Fetch user data
    const fetchUserData = async () => {
      loading.value = true;
      try {
        const response = await axios.get('/api/users/me');
        user.value = response.data;
        
        // Update form with user data
        userForm.username = user.value.username || '';
        userForm.email = user.value.email || '';
        userForm.full_name = user.value.full_name || '';
        
        // Fetch user progress (placeholder)
        fetchUserProgress();
      } catch (error) {
        ElMessage.error('Failed to load user data');
        console.error(error);
      } finally {
        loading.value = false;
      }
    };
    
    // Fetch user progress (placeholder function)
    const fetchUserProgress = async () => {
      // In a real application, this would fetch actual progress data
      completedUnitsCount.value = Math.floor(Math.random() * 10);
      completedQuestsCount.value = Math.floor(Math.random() * 5);
    };
    
    // Update profile
    const updateProfile = async () => {
      updating.value = true;
      try {
        const response = await axios.put(`/api/users/${user.value.id}`, {
          username: userForm.username,
          email: userForm.email,
          full_name: userForm.full_name
        });
        
        // Update local user data
        user.value = response.data;
        
        // Update store
        store.commit('auth/setUser', response.data);
        
        ElMessage.success('Profile updated successfully');
      } catch (error) {
        ElMessage.error('Failed to update profile');
        console.error(error);
      } finally {
        updating.value = false;
      }
    };
    
    // Change password (placeholder function)
    const changePassword = async () => {
      changingPassword.value = true;
      try {
        // In a real application, this would call an actual API endpoint
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Clear password form
        passwordForm.current_password = '';
        passwordForm.new_password = '';
        passwordForm.confirm_password = '';
        
        ElMessage.success('Password changed successfully');
      } catch (error) {
        ElMessage.error('Failed to change password');
        console.error(error);
      } finally {
        changingPassword.value = false;
      }
    };
    
    // Format date
    const formatDate = (dateString) => {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleDateString();
    };
    
    onMounted(() => {
      fetchUserData();
    });
    
    return {
      user,
      loading,
      activeTab,
      userForm,
      userFormRules,
      passwordForm,
      passwordRules,
      updating,
      changingPassword,
      completedUnitsCount,
      completedQuestsCount,
      hasProgress,
      userInitials,
      levelProgress,
      getLevelColor,
      formatLevelProgress,
      updateProfile,
      changePassword,
      formatDate
    };
  }
};
</script>

<style scoped>
.profile-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.profile-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
  height: 100%;
}

.profile-header {
  padding: 20px;
  text-align: center;
  background-color: #f5f7fa;
}

.avatar-container {
  margin: 0 auto 15px;
}

.user-email {
  color: #909399;
  margin-top: 5px;
}

.profile-details {
  padding: 20px;
}

.user-level {
  margin-bottom: 20px;
}

.level-tag {
  text-transform: capitalize;
  font-weight: normal;
}

.user-stats {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

.user-info {
  border-top: 1px solid #ebeef5;
  padding-top: 20px;
}

.info-item {
  display: flex;
  margin-bottom: 10px;
}

.info-label {
  font-weight: bold;
  width: 120px;
}

.info-value {
  flex: 1;
}

.loading-container {
  padding: 20px 0;
}
</style>
