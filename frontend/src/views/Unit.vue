<template>
  <div class="unit-viewer">
    <h1>Unit: {{ unit?.code }}</h1>
    <h2>{{ unit?.title }}</h2>
    
    <div v-if="unit">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Code">{{ unit.code }}</el-descriptions-item>
        <el-descriptions-item label="Status">{{ unit.status }}</el-descriptions-item>
        <el-descriptions-item label="Release Date">{{ formatDate(unit.release_date) }}</el-descriptions-item>
        <el-descriptions-item label="Training Package">{{ unit.tp_code }} - {{ unit.tp_title }}</el-descriptions-item>
      </el-descriptions>
      
      <div class="section" v-if="unit.description">
        <h3>Description</h3>
        <p>{{ unit.description }}</p>
      </div>
      
      <div class="section" v-if="unit.elements && unit.elements.length > 0">
        <h3>Elements and Performance Criteria</h3>
        
        <el-collapse>
          <el-collapse-item 
            v-for="element in unit.elements" 
            :key="element.id"
            :title="`Element ${element.element_num}: ${element.element_text}`"
            :name="element.id">
            <div class="performance-criteria">
              <p v-if="!element.performance_criteria || element.performance_criteria.length === 0" class="no-items">
                No performance criteria available
              </p>
              <el-table 
                v-else
                :data="element.performance_criteria" 
                style="width: 100%"
                :show-header="false"
                size="small">
                <el-table-column width="80">
                  <template #default="scope">
                    <strong>{{ scope.row.pc_num }}</strong>
                  </template>
                </el-table-column>
                <el-table-column>
                  <template #default="scope">
                    {{ scope.row.pc_text }}
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
      
      <div class="section" v-else>
        <p class="no-items">No elements available for this unit.</p>
      </div>
    </div>
    
    <div v-else class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import axios from 'axios';

export default {
  name: 'UnitView',
  setup() {
    const route = useRoute();
    const unit = ref(null);
    const loading = ref(true);

    const fetchUnit = async () => {
      try {
        const unitId = route.params.id;
        const response = await axios.get(`/api/units/${unitId}`);
        unit.value = response.data;
      } catch (error) {
        ElMessage.error('Failed to load unit');
        console.error(error);
      } finally {
        loading.value = false;
      }
    };

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleDateString();
    };

    onMounted(() => {
      fetchUnit();
    });

    return {
      unit,
      loading,
      formatDate
    };
  }
};
</script>

<style scoped>
.unit-viewer {
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
}

.section {
  margin-top: 24px;
  margin-bottom: 24px;
}

.performance-criteria {
  padding: 8px;
}

.no-items {
  color: #909399;
  font-style: italic;
}

.loading-container {
  padding: 20px;
}
</style>
