<template>
  <div class="courses-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <h1>Available Courses</h1>
        <p class="subtitle">Browse and enroll in courses to start your learning journey</p>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="filter-section">
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-input
          v-model="searchQuery"
          placeholder="Search courses..."
          prefix-icon="el-icon-search"
          clearable
          @input="handleSearch"
        />
      </el-col>
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-select
          v-model="selectedCategory"
          placeholder="Filter by category"
          clearable
          @change="handleFilter"
        >
          <el-option
            v-for="category in categories"
            :key="category.value"
            :label="category.label"
            :value="category.value"
          />
        </el-select>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-select
          v-model="selectedLevel"
          placeholder="Filter by level"
          clearable
          @change="handleFilter"
        >
          <el-option
            v-for="level in levels"
            :key="level.value"
            :label="level.label"
            :value="level.value"
          />
        </el-select>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-select
          v-model="sortBy"
          placeholder="Sort by"
          @change="handleSort"
        >
          <el-option label="Newest" value="newest" />
          <el-option label="Popular" value="popular" />
          <el-option label="Rating" value="rating" />
          <el-option label="Name (A-Z)" value="name_asc" />
          <el-option label="Name (Z-A)" value="name_desc" />
        </el-select>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="courses-section">
      <el-col 
        v-for="course in filteredCourses" 
        :key="course.id" 
        :xs="24" 
        :sm="12" 
        :md="8" 
        :lg="6"
      >
        <el-card class="course-card" :body-style="{ padding: '0px' }">
          <img :src="course.image" class="course-image" />
          <div class="course-content">
            <h3>{{ course.title }}</h3>
            <p class="course-description">{{ course.description }}</p>
            <div class="course-meta">
              <el-tag size="small" :type="getCategoryType(course.category)">
                {{ course.category }}
              </el-tag>
              <el-tag size="small" type="info">{{ course.level }}</el-tag>
            </div>
            <div class="course-stats">
              <span>
                <el-icon><User /></el-icon>
                {{ course.enrolled }} enrolled
              </span>
              <span>
                <el-icon><Star /></el-icon>
                {{ course.rating }} ({{ course.reviews }} reviews)
              </span>
            </div>
            <div class="course-footer">
              <el-button 
                type="primary" 
                @click="viewCourse(course.id)"
              >
                View Course
              </el-button>
              <el-button 
                v-if="!course.enrolled" 
                type="success" 
                @click="enrollInCourse(course.id)"
              >
                Enroll
              </el-button>
              <el-button 
                v-else 
                type="info" 
                @click="continueCourse(course.id)"
              >
                Continue
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row v-if="filteredCourses.length === 0" class="no-results">
      <el-col :span="24">
        <el-empty description="No courses found matching your criteria" />
      </el-col>
    </el-row>

    <el-row v-if="hasMorePages" class="pagination-section">
      <el-col :span="24">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="totalCourses"
          layout="prev, pager, next"
          @current-change="handlePageChange"
        />
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { defineComponent, ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Star } from '@element-plus/icons-vue'

export default defineComponent({
  name: 'CoursesView',
  components: {
    User,
    Star
  },
  setup() {
    const store = useStore()
    const router = useRouter()
    
    // State
    const courses = ref([])
    const searchQuery = ref('')
    const selectedCategory = ref('')
    const selectedLevel = ref('')
    const sortBy = ref('newest')
    const currentPage = ref(1)
    const pageSize = ref(12)
    const totalCourses = ref(0)
    
    // Categories and levels
    const categories = [
      { label: 'Business', value: 'business' },
      { label: 'Technology', value: 'technology' },
      { label: 'Health', value: 'health' },
      { label: 'Education', value: 'education' },
      { label: 'Arts', value: 'arts' }
    ]
    
    const levels = [
      { label: 'Beginner', value: 'beginner' },
      { label: 'Intermediate', value: 'intermediate' },
      { label: 'Advanced', value: 'advanced' }
    ]
    
    // Computed
    const filteredCourses = computed(() => {
      let result = [...courses.value]
      
      // Apply search filter
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        result = result.filter(course => 
          course.title.toLowerCase().includes(query) || 
          course.description.toLowerCase().includes(query)
        )
      }
      
      // Apply category filter
      if (selectedCategory.value) {
        result = result.filter(course => course.category === selectedCategory.value)
      }
      
      // Apply level filter
      if (selectedLevel.value) {
        result = result.filter(course => course.level === selectedLevel.value)
      }
      
      // Apply sorting
      switch (sortBy.value) {
        case 'newest':
          result.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
          break
        case 'popular':
          result.sort((a, b) => b.enrolled - a.enrolled)
          break
        case 'rating':
          result.sort((a, b) => b.rating - a.rating)
          break
        case 'name_asc':
          result.sort((a, b) => a.title.localeCompare(b.title))
          break
        case 'name_desc':
          result.sort((a, b) => b.title.localeCompare(a.title))
          break
      }
      
      return result
    })
    
    const hasMorePages = computed(() => {
      return totalCourses.value > pageSize.value
    })
    
    // Methods
    const fetchCourses = async () => {
      try {
        const response = await store.dispatch('courses/fetchCourses', {
          page: currentPage.value,
          pageSize: pageSize.value,
          category: selectedCategory.value,
          level: selectedLevel.value,
          search: searchQuery.value,
          sort: sortBy.value
        })
        
        courses.value = response.courses
        totalCourses.value = response.total
      } catch (error) {
        console.error('Error fetching courses:', error)
        ElMessage.error('Failed to load courses')
      }
    }
    
    const handleSearch = () => {
      currentPage.value = 1
      fetchCourses()
    }
    
    const handleFilter = () => {
      currentPage.value = 1
      fetchCourses()
    }
    
    const handleSort = () => {
      fetchCourses()
    }
    
    const handlePageChange = (page) => {
      currentPage.value = page
      fetchCourses()
    }
    
    const viewCourse = (courseId) => {
      router.push(`/courses/${courseId}`)
    }
    
    const enrollInCourse = async (courseId) => {
      try {
        await store.dispatch('courses/enrollInCourse', courseId)
        ElMessage.success('Successfully enrolled in course')
        router.push(`/courses/${courseId}`)
      } catch (error) {
        console.error('Error enrolling in course:', error)
        ElMessage.error('Failed to enroll in course')
      }
    }
    
    const continueCourse = (courseId) => {
      router.push(`/courses/${courseId}/learn`)
    }
    
    const getCategoryType = (category) => {
      const types = {
        business: 'success',
        technology: 'primary',
        health: 'danger',
        education: 'warning',
        arts: 'info'
      }
      return types[category] || 'info'
    }
    
    // Lifecycle hooks
    onMounted(() => {
      fetchCourses()
    })
    
    return {
      courses,
      searchQuery,
      selectedCategory,
      selectedLevel,
      sortBy,
      currentPage,
      pageSize,
      totalCourses,
      categories,
      levels,
      filteredCourses,
      hasMorePages,
      handleSearch,
      handleFilter,
      handleSort,
      handlePageChange,
      viewCourse,
      enrollInCourse,
      continueCourse,
      getCategoryType
    }
  }
})
</script>

<style scoped>
.courses-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  font-size: 2.5em;
  color: #409EFF;
  text-align: center;
  margin-bottom: 10px;
}

.subtitle {
  font-size: 1.2em;
  color: #606266;
  text-align: center;
  margin-bottom: 40px;
}

.filter-section {
  margin-bottom: 30px;
}

.filter-section .el-col {
  margin-bottom: 15px;
}

.courses-section {
  margin-bottom: 30px;
}

.course-card {
  height: 100%;
  margin-bottom: 20px;
  transition: transform 0.3s;
}

.course-card:hover {
  transform: translateY(-5px);
}

.course-image {
  width: 100%;
  height: 160px;
  object-fit: cover;
}

.course-content {
  padding: 15px;
}

.course-content h3 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 1.2em;
  color: #303133;
}

.course-description {
  color: #606266;
  font-size: 0.9em;
  margin-bottom: 15px;
  height: 40px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.course-meta {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.course-stats {
  display: flex;
  justify-content: space-between;
  color: #909399;
  font-size: 0.9em;
  margin-bottom: 15px;
}

.course-stats span {
  display: flex;
  align-items: center;
  gap: 5px;
}

.course-footer {
  display: flex;
  justify-content: space-between;
}

.no-results {
  margin: 40px 0;
}

.pagination-section {
  margin-top: 30px;
  display: flex;
  justify-content: center;
}

@media (max-width: 768px) {
  .courses-container {
    padding: 10px;
  }
  
  .course-footer {
    flex-direction: column;
    gap: 10px;
  }
  
  .course-footer .el-button {
    width: 100%;
  }
}
</style> 