<template>
  <div class="home-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <h1>Welcome to LearnOnline</h1>
        <p class="subtitle">Gamified Vocational Training Platform</p>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="feature-section">
      <el-col :xs="24" :sm="12" :md="8" v-for="feature in features" :key="feature.title">
        <el-card class="feature-card">
          <template #header>
            <div class="card-header">
              <el-icon class="feature-icon">
                <component :is="feature.icon"></component>
              </el-icon>
              <h3>{{ feature.title }}</h3>
            </div>
          </template>
          <p>{{ feature.description }}</p>
          <el-button type="primary" @click="navigateTo(feature.link)">Learn More</el-button>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="cta-section">
      <el-col :span="24">
        <el-card class="cta-card">
          <h2>Ready to Start Learning?</h2>
          <p>Join our community of learners and start your journey today.</p>
          <div class="cta-buttons">
            <el-button type="primary" size="large" @click="$router.push('/register')">Sign Up</el-button>
            <el-button type="success" size="large" @click="$router.push('/login')">Login</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import { 
  Reading, 
  Trophy, 
  User, 
  Connection, 
  ChatDotRound, 
  DataAnalysis 
} from '@element-plus/icons-vue'

export default defineComponent({
  name: 'HomeView',
  components: {
    Reading,
    Trophy,
    User,
    Connection,
    ChatDotRound,
    DataAnalysis
  },
  setup() {
    const features = [
      {
        title: 'Interactive Learning',
        description: 'Engage with interactive content and assessments designed to enhance your learning experience.',
        icon: 'Reading',
        link: '/courses'
      },
      {
        title: 'Gamified Experience',
        description: 'Earn points, badges, and level up as you progress through your learning journey.',
        icon: 'Trophy',
        link: '/achievements'
      },
      {
        title: 'Personalized Learning',
        description: 'Follow your own learning path with content tailored to your needs and preferences.',
        icon: 'User',
        link: '/profile'
      },
      {
        title: 'Community Learning',
        description: 'Connect with peers, mentors, and industry professionals in a collaborative environment.',
        icon: 'Connection',
        link: '/community'
      },
      {
        title: 'Real-time Feedback',
        description: 'Receive immediate feedback on your progress and performance to guide your learning.',
        icon: 'ChatDotRound',
        link: '/feedback'
      },
      {
        title: 'Progress Tracking',
        description: 'Monitor your learning journey with detailed analytics and progress reports.',
        icon: 'DataAnalysis',
        link: '/progress'
      }
    ]

    const navigateTo = (link) => {
      // Check if user is logged in
      const isLoggedIn = localStorage.getItem('token')
      if (!isLoggedIn && link !== '/courses') {
        // Redirect to login if not logged in
        this.$router.push('/login')
      } else {
        this.$router.push(link)
      }
    }

    return {
      features,
      navigateTo
    }
  }
})
</script>

<style scoped>
.home-container {
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

.feature-section {
  margin-bottom: 40px;
}

.feature-card {
  height: 100%;
  margin-bottom: 20px;
  transition: transform 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.feature-icon {
  font-size: 24px;
  color: #409EFF;
}

.cta-section {
  margin-top: 40px;
}

.cta-card {
  text-align: center;
  padding: 30px;
}

.cta-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 20px;
}

@media (max-width: 768px) {
  .cta-buttons {
    flex-direction: column;
    gap: 10px;
  }
}
</style> 