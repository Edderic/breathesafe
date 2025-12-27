<template>
  <div class="event-history-container">
    <div class="header">
      <h2>Event History</h2>
      <p class="mask-name">{{ maskName }}</p>
      <button @click="$emit('close')" class="close-button">✕</button>
    </div>

    <div v-if="loading" class="loading">
      <p>Loading event history...</p>
    </div>

    <div v-else-if="events.length === 0" class="no-events">
      <p>No events found for this mask.</p>
    </div>

    <div v-else class="timeline">
      <div
        v-for="(event, index) in events"
        :key="event.id"
        class="event-item"
      >
        <div class="event-marker"></div>
        <div class="event-content">
          <div class="event-header">
            <span class="event-type">{{ formatEventType(event.event_type) }}</span>
            <span class="event-date">{{ formatDate(event.created_at) }}</span>
          </div>

          <div class="event-user">
            By: {{ event.user.email }}
          </div>

          <div v-if="event.notes" class="event-notes">
            <strong>Notes:</strong> {{ event.notes }}
          </div>

          <div class="event-data">
            <details>
              <summary>View Data</summary>
              <pre>{{ formatEventData(event) }}</pre>
            </details>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'MaskEventHistory',
  props: {
    maskId: {
      type: Number,
      required: true
    },
    maskName: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      events: [],
      loading: true
    }
  },
  async mounted() {
    await this.loadEvents()
  },
  methods: {
    async loadEvents() {
      this.loading = true
      try {
        const response = await axios.get(`/masks/${this.maskId}/events.json`)
        this.events = response.data.events
      } catch (error) {
        console.error('Error loading events:', error)
      } finally {
        this.loading = false
      }
    },
    formatEventType(eventType) {
      return eventType
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ')
    },
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleString()
    },
    formatEventData(event) {
      // Pretty print the event data
      return JSON.stringify(event.data, null, 2)
    }
  }
}
</script>

<style scoped>
.event-history-container {
  background: white;
  border-radius: 8px;
  max-width: 800px;
  max-height: 80vh;
  overflow-y: auto;
  position: relative;
}

.header {
  position: sticky;
  top: 0;
  background: white;
  border-bottom: 2px solid #e0e0e0;
  padding: 1.5rem;
  z-index: 10;
}

.header h2 {
  margin: 0 0 0.5rem 0;
}

.mask-name {
  color: #666;
  font-size: 0.9rem;
  margin: 0;
}

.close-button {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
  padding: 0.5rem;
  line-height: 1;
}

.close-button:hover {
  color: #333;
}

.loading, .no-events {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.timeline {
  padding: 2rem;
  position: relative;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 2.5rem;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #e0e0e0;
}

.event-item {
  position: relative;
  padding-left: 3rem;
  margin-bottom: 2rem;
}

.event-marker {
  position: absolute;
  left: 1.75rem;
  top: 0.5rem;
  width: 1rem;
  height: 1rem;
  border-radius: 50%;
  background: #4CAF50;
  border: 3px solid white;
  box-shadow: 0 0 0 2px #4CAF50;
  z-index: 1;
}

.event-content {
  background: #f9f9f9;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1rem;
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.event-type {
  font-weight: 600;
  color: #333;
  font-size: 1.1rem;
}

.event-date {
  color: #666;
  font-size: 0.9rem;
}

.event-user {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.event-notes {
  background: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 4px;
  padding: 0.75rem;
  margin-top: 0.75rem;
  font-size: 0.9rem;
}

.event-data {
  margin-top: 0.75rem;
}

.event-data details {
  cursor: pointer;
}

.event-data summary {
  color: #4CAF50;
  font-size: 0.9rem;
  padding: 0.5rem;
  background: #f0f0f0;
  border-radius: 4px;
}

.event-data summary:hover {
  background: #e0e0e0;
}

.event-data pre {
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 1rem;
  overflow-x: auto;
  font-size: 0.85rem;
  margin-top: 0.5rem;
}

@media (max-width: 768px) {
  .event-history-container {
    max-width: 100%;
    max-height: 100vh;
    border-radius: 0;
  }

  .timeline {
    padding: 1rem;
  }

  .timeline::before {
    left: 1.5rem;
  }

  .event-item {
    padding-left: 2rem;
  }

  .event-marker {
    left: 0.75rem;
  }
}
</style>
