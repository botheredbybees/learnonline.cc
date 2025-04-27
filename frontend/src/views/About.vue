<template>
  <div class="about-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <h1>About LearnOnline</h1>
        <p class="subtitle">Transforming Vocational Education Through Gamification</p>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mission-section">
      <el-col :span="24">
        <el-card class="mission-card">
          <h2>Our Mission</h2>
          <p>
            LearnOnline is dedicated to revolutionizing vocational education by making learning engaging, 
            interactive, and accessible to everyone. We believe that education should be a journey of 
            discovery and growth, not just a means to an end.
          </p>
          <p>
            By integrating gamification elements with nationally recognized training content, we create 
            an immersive learning experience that motivates students to achieve their educational goals 
            while developing practical skills for the workforce.
          </p>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="features-section">
      <el-col :span="24">
        <h2>What Makes Us Different</h2>
      </el-col>
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
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="team-section">
      <el-col :span="24">
        <h2>Our Team</h2>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="member in team" :key="member.name">
        <el-card class="team-card">
          <img :src="member.image" class="team-image" />
          <div class="team-content">
            <h3>{{ member.name }}</h3>
            <p class="team-role">{{ member.role }}</p>
            <p class="team-bio">{{ member.bio }}</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="contact-section">
      <el-col :span="24">
        <el-card class="contact-card">
          <h2>Get in Touch</h2>
          <p>
            Have questions or feedback? We'd love to hear from you. Reach out to us through any of the 
            following channels:
          </p>
          <div class="contact-methods">
            <div class="contact-method">
              <el-icon><Message /></el-icon>
              <span>Email: contact@learnonline.cc</span>
            </div>
            <div class="contact-method">
              <el-icon><Phone /></el-icon>
              <span>Phone: +61 123 456 789</span>
            </div>
            <div class="contact-method">
              <el-icon><Location /></el-icon>
              <span>Address: 123 Learning Street, Education City, Australia</span>
            </div>
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
  DataAnalysis,
  Message,
  Phone,
  Location
} from '@element-plus/icons-vue'

export default defineComponent({
  name: 'AboutView',
  components: {
    Reading,
    Trophy,
    User,
    Connection,
    ChatDotRound,
    DataAnalysis,
    Message,
    Phone,
    Location
  },
  setup() {
    const features = [
      {
        title: 'Nationally Recognized Content',
        description: 'All our courses are aligned with the Australian Quality Training Framework (AQTF), ensuring that your learning is recognized and valued by employers.',
        icon: 'Reading'
      },
      {
        title: 'Gamified Learning Experience',
        description: 'Earn points, badges, and level up as you progress through your courses, making learning fun and engaging.',
        icon: 'Trophy'
      },
      {
        title: 'Personalized Learning Paths',
        description: 'Follow a learning path tailored to your goals, preferences, and skill level, ensuring the most effective learning experience.',
        icon: 'User'
      },
      {
        title: 'Community Learning',
        description: 'Connect with peers, mentors, and industry professionals in a collaborative learning environment.',
        icon: 'Connection'
      },
      {
        title: 'Real-time Feedback',
        description: 'Receive immediate feedback on your progress and performance, helping you identify areas for improvement.',
        icon: 'ChatDotRound'
      },
      {
        title: 'Comprehensive Analytics',
        description: 'Track your learning journey with detailed analytics and progress reports, helping you stay on track.',
        icon: 'DataAnalysis'
      }
    ]

    const team = [
      {
        name: 'John Smith',
        role: 'Founder & CEO',
        bio: 'With over 15 years of experience in education technology, John is passionate about making learning accessible and engaging for everyone.',
        image: '/images/team/john-smith.jpg'
      },
      {
        name: 'Sarah Johnson',
        role: 'Head of Education',
        bio: 'Sarah brings her expertise in curriculum development and instructional design to create effective and engaging learning experiences.',
        image: '/images/team/sarah-johnson.jpg'
      },
      {
        name: 'Michael Chen',
        role: 'Lead Developer',
        bio: 'Michael is responsible for the technical architecture and development of the LearnOnline platform, ensuring a seamless user experience.',
        image: '/images/team/michael-chen.jpg'
      },
      {
        name: 'Emily Davis',
        role: 'Community Manager',
        bio: 'Emily fosters a supportive and collaborative learning community, helping students connect and learn from each other.',
        image: '/images/team/emily-davis.jpg'
      }
    ]

    return {
      features,
      team
    }
  }
})
</script>

<style scoped>
.about-container {
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

h2 {
  font-size: 1.8em;
  color: #303133;
  margin-bottom: 20px;
}

.mission-section {
  margin-bottom: 40px;
}

.mission-card {
  padding: 30px;
}

.mission-card p {
  font-size: 1.1em;
  line-height: 1.6;
  color: #606266;
}

.features-section {
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

.team-section {
  margin-bottom: 40px;
}

.team-card {
  height: 100%;
  margin-bottom: 20px;
  transition: transform 0.3s;
}

.team-card:hover {
  transform: translateY(-5px);
}

.team-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.team-content {
  padding: 15px;
}

.team-content h3 {
  margin-top: 0;
  margin-bottom: 5px;
  font-size: 1.2em;
  color: #303133;
}

.team-role {
  color: #409EFF;
  font-weight: bold;
  margin-bottom: 10px;
}

.team-bio {
  color: #606266;
  font-size: 0.9em;
}

.contact-section {
  margin-bottom: 40px;
}

.contact-card {
  padding: 30px;
}

.contact-methods {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: 20px;
}

.contact-method {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #606266;
}

.contact-method .el-icon {
  color: #409EFF;
  font-size: 20px;
}

@media (max-width: 768px) {
  .about-container {
    padding: 10px;
  }
  
  .mission-card,
  .contact-card {
    padding: 20px;
  }
}
</style> 