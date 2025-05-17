<template>
  <div class="favorites-container">
    <div class="section-title">
      <h2>My Favorites</h2>
    </div>
    
    <el-tabs v-model="activeTab">
      <!-- Training Packages Tab -->
      <el-tab-pane label="Training Packages" name="training-packages">
        <div v-if="loadingTrainingPackages" class="loading-state">
          <el-skeleton :rows="3" animated />
        </div>
        
        <div v-else-if="favoriteTrainingPackages.length === 0" class="empty-state">
          <el-empty description="No favorite training packages yet">
            <el-button type="primary" @click="$router.push('/training-packages')">
              Browse Training Packages
            </el-button>
          </el-empty>
        </div>
        
        <el-table
          v-else
          :data="favoriteTrainingPackages"
          style="width: 100%"
          @row-click="viewTrainingPackage">
          <el-table-column prop="code" label="Code" width="120" />
          <el-table-column prop="title" label="Title" />
          <el-table-column prop="status" label="Status" width="120" />
          <el-table-column label="Actions" width="150" align="center">
            <template #default="scope">
              <el-button
                size="small"
                type="danger"
                @click.stop="removeFavoriteTrainingPackage(scope.row.id)">
                Remove
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      
      <!-- Units Tab -->
      <el-tab-pane label="Units" name="units">
        <div v-if="loadingUnits" class="loading-state">
          <el-skeleton :rows="3" animated />
        </div>
        
        <div v-else-if="favoriteUnits.length === 0" class="empty-state">
          <el-empty description="No favorite units yet">
            <el-button type="primary" @click="$router.push('/units')">
              Browse Units
            </el-button>
          </el-empty>
        </div>
        
        <el-table
          v-else
          :data="favoriteUnits"
          style="width: 100%"
          @row-click="viewUnit">
          <el-table-column prop="code" label="Code" width="120" />
          <el-table-column prop="title" label="Title" />
          <el-table-column label="Training Package" width="150">
            <template #default="scope">
              {{ scope.row.training_package_code }}
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="150" align="center">
            <template #default="scope">
              <el-button
                size="small"
                type="danger"
                @click.stop="removeFavoriteUnit(scope.row.id)">
                Remove
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      
      <!-- Quests Tab -->
      <el-tab-pane label="Quests" name="quests">
        <div v-if="loadingQuests" class="loading-state">
          <el-skeleton :rows="3" animated />
        </div>
        
        <div v-else-if="favoriteQuests.length === 0" class="empty-state">
          <el-empty description="No favorite quests yet">
            <el-button type="primary" @click="$router.push('/quests')">
              Browse Quests
            </el-button>
          </el-empty>
        </div>
        
        <el-table
          v-else
          :data="favoriteQuests"
          style="width: 100%"
          @row-click="viewQuest">
          <el-table-column prop="title" label="Title" />
          <el-table-column prop="quest_type" label="Type" width="150">
            <template #default="scope">
              <el-tag :type="getQuestTypeTag(scope.row.quest_type)">
                {{ formatQuestType(scope.row.quest_type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="experience_points" label="XP" width="80" />
          <el-table-column label="Actions" width="150" align="center">
            <template #default="scope">
              <el-button
                size="small"
                type="danger"
                @click.stop="removeFavoriteQuest(scope.row.id)">
                Remove
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import axios from 'axios';

export default {
  name: 'UserFavorites',
  setup() {
    const activeTab = ref('training-packages');
    
    // Training Packages
    const favoriteTrainingPackages = ref([]);
    const loadingTrainingPackages = ref(true);
    
    // Units
    const favoriteUnits = ref([]);
    const loadingUnits = ref(true);
    
    // Quests
    const favoriteQuests = ref([]);
    const loadingQuests = ref(true);
    
    // Fetch all favorites
    const fetchFavorites = async () => {
      try {
        loadingTrainingPackages.value = true;
        loadingUnits.value = true;
        loadingQuests.value = true;
        
        const response = await axios.get('/api/favorites');
        
        // Process favorite training packages
        const trainingPackageIds = response.data.training_packages.map(tp => tp.training_package_id);
        if (trainingPackageIds.length > 0) {
          await fetchTrainingPackageDetails(trainingPackageIds);
        } else {
          favoriteTrainingPackages.value = [];
        }
        
        // Process favorite units
        const unitIds = response.data.units.map(unit => unit.unit_id);
        if (unitIds.length > 0) {
          await fetchUnitDetails(unitIds);
        } else {
          favoriteUnits.value = [];
        }
        
        // Process favorite quests
        const questIds = response.data.quests.map(quest => quest.quest_id);
        if (questIds.length > 0) {
          await fetchQuestDetails(questIds);
        } else {
          favoriteQuests.value = [];
        }
      } catch (error) {
        ElMessage.error('Failed to load favorites');
        console.error(error);
      } finally {
        loadingTrainingPackages.value = false;
        loadingUnits.value = false;
        loadingQuests.value = false;
      }
    };
    
    // Fetch training package details
    const fetchTrainingPackageDetails = async (ids) => {
      try {
        const response = await axios.get('/api/admin/training-packages', {
          params: { ids: ids.join(',') }
        });
        favoriteTrainingPackages.value = response.data.training_packages || [];
      } catch (error) {
        console.error('Failed to fetch training package details', error);
        favoriteTrainingPackages.value = [];
      }
    };
    
    // Fetch unit details
    const fetchUnitDetails = async (ids) => {
      try {
        const response = await axios.get('/api/units', {
          params: { ids: ids.join(',') }
        });
        favoriteUnits.value = response.data || [];
      } catch (error) {
        console.error('Failed to fetch unit details', error);
        favoriteUnits.value = [];
      }
    };
    
    // Fetch quest details
    const fetchQuestDetails = async (ids) => {
      try {
        // Note: This depends on your API implementation. You might need to fetch quests individually
        const quests = [];
        for (const id of ids) {
          const response = await axios.get(`/api/quests/${id}`);
          quests.push(response.data);
        }
        favoriteQuests.value = quests;
      } catch (error) {
        console.error('Failed to fetch quest details', error);
        favoriteQuests.value = [];
      }
    };
    
    // Remove a training package from favorites
    const removeFavoriteTrainingPackage = async (id) => {
      try {
        await axios.delete(`/api/favorites/training-packages/${id}`);
        ElMessage.success('Removed from favorites');
        favoriteTrainingPackages.value = favoriteTrainingPackages.value.filter(tp => tp.id !== id);
      } catch (error) {
        ElMessage.error('Failed to remove from favorites');
        console.error(error);
      }
    };
    
    // Remove a unit from favorites
    const removeFavoriteUnit = async (id) => {
      try {
        await axios.delete(`/api/favorites/units/${id}`);
        ElMessage.success('Removed from favorites');
        favoriteUnits.value = favoriteUnits.value.filter(unit => unit.id !== id);
      } catch (error) {
        ElMessage.error('Failed to remove from favorites');
        console.error(error);
      }
    };
    
    // Remove a quest from favorites
    const removeFavoriteQuest = async (id) => {
      try {
        await axios.delete(`/api/favorites/quests/${id}`);
        ElMessage.success('Removed from favorites');
        favoriteQuests.value = favoriteQuests.value.filter(quest => quest.id !== id);
      } catch (error) {
        ElMessage.error('Failed to remove from favorites');
        console.error(error);
      }
    };
    
    // Navigate to training package details
    const viewTrainingPackage = (row) => {
      // Implement navigation to training package detail page
      // e.g., router.push(`/training-packages/${row.id}`);
    };
    
    // Navigate to unit details
    const viewUnit = (row) => {
      // Implement navigation to unit detail page
      // e.g., router.push(`/units/${row.id}`);
    };
    
    // Navigate to quest details
    const viewQuest = (row) => {
      // Implement navigation to quest detail page
      // e.g., router.push(`/quests/${row.id}`);
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
    
    // Load data on component mount
    onMounted(() => {
      fetchFavorites();
    });
    
    return {
      activeTab,
      favoriteTrainingPackages,
      favoriteUnits,
      favoriteQuests,
      loadingTrainingPackages,
      loadingUnits,
      loadingQuests,
      removeFavoriteTrainingPackage,
      removeFavoriteUnit,
      removeFavoriteQuest,
      viewTrainingPackage,
      viewUnit,
      viewQuest,
      formatQuestType,
      getQuestTypeTag
    };
  }
};
</script>

<style scoped>
.favorites-container {
  padding: 20px;
}

.section-title {
  margin-bottom: 20px;
}

.loading-state {
  padding: 20px;
}

.empty-state {
  padding: 40px 0;
  text-align: center;
}
</style>
