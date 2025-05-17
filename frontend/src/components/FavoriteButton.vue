<template>
  <el-button
    :type="isFavorite ? 'danger' : 'default'"
    :icon="isFavorite ? 'el-icon-star-on' : 'el-icon-star-off'"
    size="small"
    @click="toggleFavorite"
    :loading="loading"
    circle>
  </el-button>
</template>

<script>
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import axios from 'axios';

export default {
  name: 'FavoriteButton',
  props: {
    itemId: {
      type: [String, Number],
      required: true
    },
    itemType: {
      type: String,
      required: true,
      validator: (value) => ['training-package', 'unit', 'quest'].includes(value)
    },
    initialState: {
      type: Boolean,
      default: false
    }
  },
  setup(props, { emit }) {
    const isFavorite = ref(props.initialState);
    const loading = ref(false);
    
    // Determine the API endpoint based on item type
    const getEndpoint = () => {
      switch (props.itemType) {
        case 'training-package':
          return '/api/favorites/training-packages';
        case 'unit':
          return '/api/favorites/units';
        case 'quest':
          return '/api/favorites/quests';
        default:
          return '';
      }
    };
    
    // Toggle favorite status
    const toggleFavorite = async (e) => {
      e.stopPropagation(); // Prevent row click event if this button is in a table row
      
      loading.value = true;
      try {
        const endpoint = getEndpoint();
        
        if (isFavorite.value) {
          // Remove from favorites
          await axios.delete(`${endpoint}/${props.itemId}`);
          isFavorite.value = false;
          ElMessage.success('Removed from favorites');
          emit('remove', props.itemId);
        } else {
          // Add to favorites
          await axios.post(endpoint, { id: props.itemId });
          isFavorite.value = true;
          ElMessage.success('Added to favorites');
          emit('add', props.itemId);
        }
      } catch (error) {
        ElMessage.error('Failed to update favorites');
        console.error(error);
      } finally {
        loading.value = false;
      }
    };
    
    // Check if item is already in favorites
    const checkFavoriteStatus = async () => {
      try {
        const response = await axios.get('/api/favorites');
        
        switch (props.itemType) {
          case 'training-package':
            isFavorite.value = response.data.training_packages.some(
              tp => tp.training_package_id === props.itemId
            );
            break;
          case 'unit':
            isFavorite.value = response.data.units.some(
              unit => unit.unit_id === props.itemId
            );
            break;
          case 'quest':
            isFavorite.value = response.data.quests.some(
              quest => quest.quest_id === props.itemId
            );
            break;
        }
      } catch (error) {
        console.error('Failed to check favorite status', error);
      }
    };
    
    onMounted(() => {
      if (!props.initialState) {
        checkFavoriteStatus();
      }
    });
    
    return {
      isFavorite,
      loading,
      toggleFavorite
    };
  }
};
</script>
