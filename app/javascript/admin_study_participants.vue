<template>
  <div class="admin-study-participants">
    <div class="container-fluid">
      <div class="row">
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center mb-4">
            <h1 class="h3 mb-0">Study Participants</h1>
            <div class="d-flex gap-2">
              <button
                @click="refreshData"
                class="btn btn-outline-primary"
                :disabled="loading"
              >
                <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i>
                Refresh
              </button>
            </div>
          </div>

          <!-- Loading State -->
          <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2">Loading study participants...</p>
          </div>

          <!-- Error State -->
          <div v-else-if="error" class="alert alert-danger" role="alert">
            <h4 class="alert-heading">Error Loading Data</h4>
            <p>{{ error }}</p>
            <button @click="loadData" class="btn btn-outline-danger">
              Try Again
            </button>
          </div>

          <!-- Data Table -->
          <div v-else-if="studyParticipants.length > 0" class="card">
            <div class="card-body p-0">
              <div class="table-responsive">
                <table class="table table-hover mb-0">
                  <thead class="table-light">
                    <tr>
                      <th @click="sortBy('participant_uuid')" class="sortable">
                        Participant UUID
                        <i class="fas fa-sort ms-1" :class="getSortIcon('participant_uuid')"></i>
                      </th>
                      <th @click="sortBy('masks_count')" class="sortable">
                        Masks
                        <i class="fas fa-sort ms-1" :class="getSortIcon('masks_count')"></i>
                      </th>
                      <th @click="sortBy('finished_study_datetime')" class="sortable">
                        Finished Study
                        <i class="fas fa-sort ms-1" :class="getSortIcon('finished_study_datetime')"></i>
                      </th>
                      <th>Removal from Study</th>
                      <th>Qualifications</th>
                      <th>Equipment</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="participant in paginatedParticipants" :key="participant.participant_uuid">
                      <td>
                        <code class="text-muted">{{ participant.participant_uuid }}</code>
                      </td>
                      <td class="text-center">
                        <span class="badge bg-primary">{{ participant.masks_count || 0 }}</span>
                      </td>
                      <td>
                        <span v-if="participant.finished_study_datetime">
                          {{ formatDateTime(participant.finished_study_datetime) }}
                        </span>
                        <span v-else class="text-muted">-</span>
                      </td>
                      <td>
                        <div v-if="participant.removal_from_study && Object.keys(participant.removal_from_study).length > 0">
                          <button
                            @click="toggleDetails(participant.participant_uuid, 'removal')"
                            class="btn btn-sm btn-outline-info"
                          >
                            View Details
                          </button>
                        </div>
                        <span v-else class="text-muted">-</span>
                      </td>
                      <td>
                        <div v-if="participant.qualifications && Object.keys(participant.qualifications).length > 0">
                          <button
                            @click="toggleDetails(participant.participant_uuid, 'qualifications')"
                            class="btn btn-sm btn-outline-info"
                          >
                            View Details
                          </button>
                        </div>
                        <span v-else class="text-muted">-</span>
                      </td>
                      <td>
                        <div v-if="participant.equipment && Object.keys(participant.equipment).length > 0">
                          <button
                            @click="toggleDetails(participant.participant_uuid, 'equipment')"
                            class="btn btn-sm btn-outline-info"
                          >
                            View Details
                          </button>
                        </div>
                        <span v-else class="text-muted">-</span>
                      </td>
                      <td @click.stop>
                        <GearButton @click.stop="showActionsPopup(participant)" />
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Pagination -->
            <div v-if="totalPages > 1" class="card-footer">
              <nav aria-label="Study participants pagination">
                <ul class="pagination pagination-sm mb-0 justify-content-center">
                  <li class="page-item" :class="{ disabled: currentPage === 1 }">
                    <button @click="goToPage(1)" class="page-link">First</button>
                  </li>
                  <li class="page-item" :class="{ disabled: currentPage === 1 }">
                    <button @click="goToPage(currentPage - 1)" class="page-link">Previous</button>
                  </li>

                  <li
                    v-for="page in visiblePages"
                    :key="page"
                    class="page-item"
                    :class="{ active: page === currentPage }"
                  >
                    <button @click="goToPage(page)" class="page-link">{{ page }}</button>
                  </li>

                  <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                    <button @click="goToPage(currentPage + 1)" class="page-link">Next</button>
                  </li>
                  <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                    <button @click="goToPage(totalPages)" class="page-link">Last</button>
                  </li>
                </ul>
              </nav>
            </div>
          </div>

          <!-- Empty State -->
          <div v-else class="text-center py-5">
            <i class="fas fa-users fa-3x text-muted mb-3"></i>
            <h4 class="text-muted">No Study Participants Found</h4>
            <p class="text-muted">There are currently no study participants in the system.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Actions Popup -->
    <Popup v-if="showActions" @onclose="closeActionsPopup">
      <div class="actions-popup-content">
        <h4>Participant Actions</h4>
        <div class="mb-3">
          <strong>Participant UUID:</strong>
          <code class="ms-2">{{ selectedParticipantForActions?.participant_uuid }}</code>
        </div>

        <div class="d-flex flex-column gap-2">
          <button
            @click="confirmRemoveFromStudy"
            class="btn btn-danger"
            :disabled="actionInProgress"
          >
            <i class="fas fa-user-times me-2"></i>
            Remove from Study
          </button>

          <button
            @click="confirmFinishStudy"
            class="btn btn-success"
            :disabled="actionInProgress || selectedParticipantForActions?.finished_study_datetime"
          >
            <i class="fas fa-check-circle me-2"></i>
            Finish Study
          </button>
        </div>
      </div>
    </Popup>

    <!-- Confirmation Popup for Remove from Study -->
    <Popup v-if="showRemoveConfirmation" @onclose="closeRemoveConfirmation">
      <div class="confirmation-popup-content">
        <h4>Confirm Removal from Study</h4>
        <p>Are you sure you want to remove this participant from the study?</p>
        <p><strong>UUID:</strong> <code>{{ selectedParticipantForActions?.participant_uuid }}</code></p>

        <div class="mb-3">
          <label for="removal-reason" class="form-label">Reason for removal:</label>
          <textarea
            id="removal-reason"
            v-model="removalReason"
            class="form-control"
            rows="3"
            placeholder="Enter reason..."
          ></textarea>
        </div>

        <div class="d-flex gap-2 justify-content-end">
          <button @click="closeRemoveConfirmation" class="btn btn-secondary">
            Cancel
          </button>
          <button @click="executeRemoveFromStudy" class="btn btn-danger" :disabled="!removalReason.trim()">
            Confirm Remove
          </button>
        </div>
      </div>
    </Popup>

    <!-- Confirmation Popup for Finish Study -->
    <Popup v-if="showFinishConfirmation" @onclose="closeFinishConfirmation">
      <div class="confirmation-popup-content">
        <h4>Confirm Finish Study</h4>
        <p>Are you sure you want to mark this participant's study as finished?</p>
        <p><strong>UUID:</strong> <code>{{ selectedParticipantForActions?.participant_uuid }}</code></p>
        <p class="text-muted">This will set the finished_study_datetime to the current time.</p>

        <div class="d-flex gap-2 justify-content-end">
          <button @click="closeFinishConfirmation" class="btn btn-secondary">
            Cancel
          </button>
          <button @click="executeFinishStudy" class="btn btn-success">
            Confirm Finish
          </button>
        </div>
      </div>
    </Popup>

    <!-- Details Modal -->
    <div
      v-if="showDetailsModal"
      class="modal fade show d-block"
      tabindex="-1"
      role="dialog"
      style="background-color: rgba(0,0,0,0.5)"
    >
      <div class="modal-dialog modal-lg" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              {{ detailsTitle }} - {{ selectedParticipant?.participant_uuid }}
            </h5>
            <button
              @click="closeDetailsModal"
              type="button"
              class="btn-close"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <pre class="bg-light p-3 rounded">{{ JSON.stringify(selectedDetails, null, 2) }}</pre>
          </div>
          <div class="modal-footer">
            <button @click="closeDetailsModal" type="button" class="btn btn-secondary">
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { useMainStore } from './stores/main_store.js';
import { setupCSRF } from './misc.js';
import Popup from './pop_up.vue';
import GearButton from './gear_button.vue';

export default {
  name: 'AdminStudyParticipants',
  components: {
    Popup,
    GearButton
  },
  data() {
    return {
      studyParticipants: [],
      loading: false,
      error: null,
      sortField: 'created_at',
      sortDirection: 'desc',
      currentPage: 1,
      itemsPerPage: 25,
      showDetailsModal: false,
      selectedParticipant: null,
      selectedDetails: null,
      detailsTitle: '',
      showActions: false,
      selectedParticipantForActions: null,
      showRemoveConfirmation: false,
      showFinishConfirmation: false,
      removalReason: '',
      actionInProgress: false
    };
  },
  computed: {
    isAdmin() {
      const mainStore = useMainStore();
      return mainStore.isAdmin;
    },
    sortedParticipants() {
      if (!this.studyParticipants.length) return [];

      return [...this.studyParticipants].sort((a, b) => {
        let aVal = a[this.sortField];
        let bVal = b[this.sortField];

        // Handle null/undefined values
        if (aVal === null || aVal === undefined) aVal = '';
        if (bVal === null || bVal === undefined) bVal = '';

        // Handle date strings
        if (this.sortField.includes('datetime') || this.sortField.includes('created_at')) {
          aVal = new Date(aVal);
          bVal = new Date(bVal);
        }

        if (this.sortDirection === 'asc') {
          return aVal > bVal ? 1 : -1;
        } else {
          return aVal < bVal ? 1 : -1;
        }
      });
    },
    paginatedParticipants() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.sortedParticipants.slice(start, end);
    },
    totalPages() {
      return Math.ceil(this.studyParticipants.length / this.itemsPerPage);
    },
    visiblePages() {
      const pages = [];
      const start = Math.max(1, this.currentPage - 2);
      const end = Math.min(this.totalPages, this.currentPage + 2);

      for (let i = start; i <= end; i++) {
        pages.push(i);
      }
      return pages;
    }
  },
  async mounted() {
    if (!this.isAdmin) {
      this.$router.push('/');
      return;
    }
    await this.loadData();
  },
  methods: {
    async loadData() {
      this.loading = true;
      this.error = null;

      try {
        const response = await axios.get('/admin/study_participants');
        this.studyParticipants = response.data;
      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to load study participants';
        console.error('Error loading study participants:', err);
      } finally {
        this.loading = false;
      }
    },
    async refreshData() {
      await this.loadData();
    },
    sortBy(field) {
      if (this.sortField === field) {
        this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
      } else {
        this.sortField = field;
        this.sortDirection = 'asc';
      }
    },
    getSortIcon(field) {
      if (this.sortField !== field) return '';
      return this.sortDirection === 'asc' ? 'fa-sort-up' : 'fa-sort-down';
    },
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page;
      }
    },
    toggleDetails(participantUuid, type) {
      const participant = this.studyParticipants.find(p => p.participant_uuid === participantUuid);
      if (!participant) return;

      this.selectedParticipant = participant;
      this.selectedDetails = participant[type];
      this.detailsTitle = type.charAt(0).toUpperCase() + type.slice(1).replace('_', ' ');
      this.showDetailsModal = true;
    },
    closeDetailsModal() {
      this.showDetailsModal = false;
      this.selectedParticipant = null;
      this.selectedDetails = null;
      this.detailsTitle = '';
    },
    formatDateTime(dateString) {
      if (!dateString) return '-';
      const date = new Date(dateString);
      return date.toLocaleString();
    },
    showActionsPopup(participant) {
      this.selectedParticipantForActions = participant;
      this.showActions = true;
    },
    closeActionsPopup() {
      this.showActions = false;
      this.selectedParticipantForActions = null;
    },
    confirmRemoveFromStudy() {
      this.showRemoveConfirmation = true;
    },
    closeRemoveConfirmation() {
      this.showRemoveConfirmation = false;
      this.removalReason = '';
    },
    confirmFinishStudy() {
      this.showFinishConfirmation = true;
    },
    closeFinishConfirmation() {
      this.showFinishConfirmation = false;
    },
    async executeRemoveFromStudy() {
      if (!this.removalReason.trim()) {
        alert('Please provide a reason for removal');
        return;
      }

      this.actionInProgress = true;
      setupCSRF();

      try {
        await axios.post('/admin/study_participants/remove_from_study', {
          participant_uuid: this.selectedParticipantForActions.participant_uuid,
          reason: this.removalReason
        });

        // Refresh data
        await this.loadData();

        // Close all popups
        this.closeRemoveConfirmation();
        this.closeActionsPopup();

        alert('Participant successfully removed from study');
      } catch (err) {
        console.error('Error removing participant:', err);
        alert(err.response?.data?.error || 'Failed to remove participant from study');
      } finally {
        this.actionInProgress = false;
      }
    },
    async executeFinishStudy() {
      this.actionInProgress = true;
      setupCSRF();

      try {
        await axios.post('/admin/study_participants/finish_study', {
          participant_uuid: this.selectedParticipantForActions.participant_uuid
        });

        // Refresh data
        await this.loadData();

        // Close all popups
        this.closeFinishConfirmation();
        this.closeActionsPopup();

        alert('Study marked as finished for this participant');
      } catch (err) {
        console.error('Error finishing study:', err);
        alert(err.response?.data?.error || 'Failed to mark study as finished');
      } finally {
        this.actionInProgress = false;
      }
    }
  }
};
</script>

<style scoped>
.sortable {
  cursor: pointer;
  user-select: none;
}

.sortable:hover {
  background-color: #f8f9fa;
}

.table th.sortable {
  position: relative;
}

.table th.sortable i {
  opacity: 0.5;
}

.table th.sortable:hover i {
  opacity: 1;
}

.table th.sortable.active i {
  opacity: 1;
  color: #007bff;
}

.pagination .page-link {
  color: #007bff;
}

.pagination .page-item.active .page-link {
  background-color: #007bff;
  border-color: #007bff;
}

.pagination .page-item.disabled .page-link {
  color: #6c757d;
  background-color: #fff;
  border-color: #dee2e6;
}

.modal.show {
  display: block !important;
}

pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 400px;
  overflow-y: auto;
}

.actions-popup-content,
.confirmation-popup-content {
  padding: 1.5em;
  min-width: 400px;
}

.actions-popup-content h4,
.confirmation-popup-content h4 {
  margin-top: 0;
  margin-bottom: 1em;
}

.actions-popup-content .btn,
.confirmation-popup-content .btn {
  width: 100%;
}

.confirmation-popup-content .btn {
  width: auto;
}
</style>
