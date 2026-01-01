<template>
  <div class="dashboard-container">
    <h1 class="dashboard-title">Breathesafe Dashboard</h1>

    <div v-if="loading" class="loading">
      <p>Loading dashboard data...</p>
    </div>

    <div v-else-if="error" class="error">
      <p>Error loading dashboard: {{ error }}</p>
    </div>

    <div v-else class="dashboard-content">
      <!-- Masks Section -->
      <section class="dashboard-section">
        <h2 class="section-title">Masks</h2>

        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-value">{{ stats.masks.total }}</div>
            <div class="stat-label">Total Masks</div>
          </div>
        </div>

        <div class="charts-row">
          <div class="chart-container">
            <h3>Filtration Efficiency Data</h3>
            <div class="measurement-explanation">
              <strong>Filtration efficiency data</strong> measures how well the mask material filters particles when properly sealed to the face.
              It comes from two sources: (1) <strong>Aaron Collins (MaskNerd)</strong> sealed masks to his face using both hands and estimated
              filtration efficiency using a PortaCount at normal breathing rates, and (2) <strong>N99 Mode Fit Tests</strong> where other people perform Aaron's procedure and save the data in the
              optional "Normal Breathing (SEALED)" exercise. The data is expressed as <strong>avg_sealed_ff</strong> (average sealed
              fit factor), calculated as the arithmetic mean of 1/(1-filtration_efficiency) across fit tests that have that optional exercise filled in. For example, 98.8% filtration = 83.33 fit factor.
              <strong>Why it matters:</strong> This data helps predict mask protection and is used to estimate N95 fit factor scores (i.e. measurements of leakage) when direct N95 mode
              data isn't available. If your N99 fit factor during regular testing is close to the sealed fit factor, you have a well-fitting mask.
            </div>
            <div class="stacked-bar-wrapper">
              <canvas ref="filtrationChart"></canvas>
            </div>
            <div class="chart-legend">
              <div class="legend-item">
                <span class="legend-color" style="background-color: #4CAF50;"></span>
                <span>With Data: {{ stats.masks.with_filtration_data }}</span>
              </div>
              <div class="legend-item">
                <span class="legend-color" style="background-color: #f44336;"></span>
                <span>Missing Data: {{ stats.masks.missing_filtration_data }}</span>
              </div>
            </div>
          </div>

          <div class="chart-container">
            <h3>Breathability Scores</h3>
            <div class="measurement-explanation">
              <strong>Breathability</strong> measures the breathing resistance of a mask, expressed in pascals (Pa).
              Lower values mean easier breathing. This helps users understand comfort and wearability alongside protection data.
            </div>
            <div class="stacked-bar-wrapper">
              <canvas ref="breathabilityChart"></canvas>
            </div>
            <div class="chart-legend">
              <div class="legend-item">
                <span class="legend-color" style="background-color: #4CAF50;"></span>
                <span>With Scores: {{ stats.masks.with_breathability }}</span>
              </div>
              <div class="legend-item">
                <span class="legend-color" style="background-color: #f44336;"></span>
                <span>Without Scores: {{ stats.masks.without_breathability }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Fit Tests Section -->
      <section class="dashboard-section">
        <h2 class="section-title">Fit Tests</h2>

        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-value">{{ stats.fit_tests.total }}</div>
            <div class="stat-label">Total Fit Tests</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ stats.fit_tests.missing_facial_measurements }}</div>
            <div class="stat-label">Missing Facial Measurements</div>
          </div>
        </div>

        <div class="charts-row">
          <div class="chart-container">
            <h3>Fit Test Types</h3>
            <div class="measurement-explanation">
              <strong>N95 Mode</strong>: Direct N95 quantitative fit testing.
              <strong>N99 Mode</strong>: N99 quantitative fit testing converted to N95 estimates using sealed filtration data.
              <strong>QLFT</strong>: Qualitative fit testing (pass/fail based on taste/smell).
              <strong>User Seal Check</strong>: Self-reported seal check results.
            </div>
            <canvas ref="fitTestTypesChart"></canvas>
            <div class="chart-legend">
              <div class="legend-item">
                <span class="legend-color" style="background-color: #4CAF50;"></span>
                <span>N95 Mode: {{ stats.fit_tests.by_type.n95_mode }}</span>
              </div>
              <div class="legend-item">
                <span class="legend-color" style="background-color: #2196F3;"></span>
                <span>N99 Mode: {{ stats.fit_tests.by_type.n99_mode }}</span>
              </div>
              <div class="legend-item">
                <span class="legend-color" style="background-color: #FF9800;"></span>
                <span>QLFT: {{ stats.fit_tests.by_type.qlft }}</span>
              </div>
              <div class="legend-item">
                <span class="legend-color" style="background-color: #9C27B0;"></span>
                <span>User Seal Check: {{ stats.fit_tests.by_type.user_seal_check }}</span>
              </div>
            </div>
          </div>

          <div class="chart-container">
            <h3>Facial Measurements by Type</h3>
            <div class="measurement-explanation">
              <strong>Traditional measurements</strong> are taken with tape measures and calipers: face_width, face_length,
              bitragion_subnasale_arc, nasal_root_breadth, nose_protrusion, and nose_bridge_height (6 total).
              <strong>ARKit</strong> measurements come from iPhone 3D face scanning.
            </div>
            <div class="sample-size-note">
              Note: Categories are not mutually exclusive. Users may be counted in multiple categories.
            </div>
            <canvas ref="facialMeasurementsChart"></canvas>
            <div class="chart-legend">
              <div class="legend-item">
                <span class="legend-color" style="background-color: #f44336;"></span>
                <span>Incomplete Traditional: {{ stats.fit_tests.facial_measurements.users_with_incomplete_traditional }}</span>
              </div>
              <div class="legend-item">
                <span class="legend-color" style="background-color: #4CAF50;"></span>
                <span>Complete Traditional: {{ stats.fit_tests.facial_measurements.users_with_complete_traditional }}</span>
              </div>
              <div class="legend-item">
                <span class="legend-color" style="background-color: #2196F3;"></span>
                <span>Has ARKit: {{ stats.fit_tests.facial_measurements.users_with_arkit }}</span>
              </div>
              <div class="legend-item">
                <span class="legend-color" style="background-color: #9C27B0;"></span>
                <span>Both Complete: {{ stats.fit_tests.facial_measurements.users_with_both_complete }}</span>
              </div>
              <div class="legend-item">
                <span class="legend-color" style="background-color: #757575;"></span>
                <span>No Measurements: {{ stats.fit_tests.facial_measurements.users_with_no_measurements }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="charts-row">
          <div class="chart-container">
            <h3>Gender & Sex</h3>
            <canvas ref="genderChart"></canvas>
            <div class="chart-stats">
              <p><strong>Total:</strong> {{ stats.fit_tests.demographics.gender_and_sex.reduce((sum, item) => sum + item.fit_tests, 0) }} fit tests</p>
              <p><strong>Unique Users:</strong> {{ stats.fit_tests.demographics.gender_and_sex.reduce((sum, item) => sum + item.unique_users, 0) }}</p>
            </div>
          </div>

          <div class="chart-container">
            <h3>Race & Ethnicity</h3>
            <canvas ref="raceChart"></canvas>
            <div class="chart-stats">
              <p><strong>Total:</strong> {{ stats.fit_tests.demographics.race_ethnicity.reduce((sum, item) => sum + item.fit_tests, 0) }} fit tests</p>
              <p><strong>Unique Users:</strong> {{ stats.fit_tests.demographics.race_ethnicity.reduce((sum, item) => sum + item.unique_users, 0) }}</p>
            </div>
          </div>

          <div class="chart-container">
            <h3>Age Range</h3>
            <canvas ref="ageChart"></canvas>
            <div class="chart-stats">
              <p><strong>Total:</strong> {{ stats.fit_tests.demographics.age.reduce((sum, item) => sum + item.fit_tests, 0) }} fit tests</p>
              <p><strong>Unique Users:</strong> {{ stats.fit_tests.demographics.age.reduce((sum, item) => sum + item.unique_users, 0) }}</p>
            </div>
          </div>
        </div>

        <div class="charts-row">
          <div class="chart-container">
            <h3>Overall Pass Rate</h3>
            <div class="stacked-bar-wrapper">
              <canvas ref="overallPassRateChart"></canvas>
            </div>
            <div class="chart-stats">
              <p><strong>Pass Rate:</strong> {{ stats.fit_tests.pass_rates.overall.pass_rate }}%</p>
              <p><strong>Passed:</strong> {{ stats.fit_tests.pass_rates.overall.passed }} / {{ stats.fit_tests.pass_rates.overall.total }}</p>
            </div>
          </div>
        </div>

        <!-- Pass Rates by Mask -->
        <div class="chart-container-full">
          <h3>Pass Rates by Mask</h3>

          <!-- Sorting Controls -->
          <div class="sort-controls">
            <div class="sort-group">
              <label for="maskSortBy">Sort by:</label>
              <select id="maskSortBy" v-model="maskSortBy" @change="onSortChange" class="sort-select">
                <option value="pass_rate">Pass Rate</option>
                <option value="sample_size">Sample Size</option>
                <option value="name">Mask Name</option>
              </select>
            </div>

            <div class="sort-group">
              <label for="maskSortOrder">Order:</label>
              <select id="maskSortOrder" v-model="maskSortOrder" @change="onSortChange" class="sort-select">
                <option value="desc">{{ maskSortBy === 'name' ? 'Z-A' : 'High to Low' }}</option>
                <option value="asc">{{ maskSortBy === 'name' ? 'A-Z' : 'Low to High' }}</option>
              </select>
            </div>
          </div>

          <!-- Pagination -->
          <Pagination
            :current-page="maskCurrentPage"
            :per-page="maskPerPage"
            :total-count="totalMasks"
            item-name="masks"
            @page-change="onMaskPageChange"
          />

          <div class="sample-size-note">
            Sample sizes shown in parentheses. Lighter colors indicate smaller sample sizes.
          </div>

          <div class="chart-wrapper">
            <canvas ref="passRateByMaskChart"></canvas>
          </div>
        </div>

        <!-- Pass Rates by Strap Type -->
        <div class="charts-row">
          <div class="chart-container">
            <h3>Pass Rates by Strap Type</h3>
            <div class="sample-size-note">
              Sample sizes in parentheses. Lighter = smaller sample.
            </div>
            <div class="chart-wrapper">
              <canvas ref="passRateByStrapChart"></canvas>
            </div>
          </div>

          <div class="chart-container">
            <h3>Pass Rates by Style</h3>
            <div class="sample-size-note">
              Sample sizes in parentheses. Lighter = smaller sample.
            </div>
            <div class="chart-wrapper">
              <canvas ref="passRateByStyleChart"></canvas>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js';
import Pagination from './pagination.vue';

Chart.register(...registerables);

export default {
  name: 'Dashboard',
  components: {
    Pagination
  },
  data() {
    return {
      stats: null,
      loading: true,
      error: null,
      charts: {},
      // Pagination and sorting for Pass Rates by Mask
      maskCurrentPage: 1,
      maskPerPage: 20,
      maskSortBy: 'pass_rate', // 'pass_rate', 'sample_size', 'name'
      maskSortOrder: 'desc' // 'asc' or 'desc'
    };
  },
  computed: {
    sortedMasks() {
      if (!this.stats?.fit_tests?.pass_rates?.by_mask) return [];

      const masks = [...this.stats.fit_tests.pass_rates.by_mask];

      // Sort based on current sort settings
      masks.sort((a, b) => {
        let compareA, compareB;

        switch (this.maskSortBy) {
          case 'pass_rate':
            compareA = a.pass_rate;
            compareB = b.pass_rate;
            break;
          case 'sample_size':
            compareA = a.total;
            compareB = b.total;
            break;
          case 'name':
            compareA = a.name.toLowerCase();
            compareB = b.name.toLowerCase();
            // For strings, handle ascending/descending differently
            if (this.maskSortOrder === 'asc') {
              return compareA.localeCompare(compareB);
            } else {
              return compareB.localeCompare(compareA);
            }
        }

        // For numbers
        if (this.maskSortOrder === 'asc') {
          return compareA - compareB;
        } else {
          return compareB - compareA;
        }
      });

      return masks;
    },
    paginatedMasks() {
      const start = (this.maskCurrentPage - 1) * this.maskPerPage;
      const end = start + this.maskPerPage;
      return this.sortedMasks.slice(start, end);
    },
    totalMasks() {
      return this.sortedMasks.length;
    }
  },
  mounted() {
    this.loadDashboardData();
  },
  beforeUnmount() {
    // Destroy all charts to prevent memory leaks
    Object.values(this.charts).forEach(chart => {
      if (chart) chart.destroy();
    });
  },
  methods: {
    async loadDashboardData() {
      try {
        this.loading = true;
        this.error = null;

        const response = await fetch('/dashboard/stats', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Debug logging
        console.log('Dashboard stats loaded:', data);
        console.log('Pass rates by mask:', data.fit_tests?.pass_rates?.by_mask);
        console.log('Pass rates by strap:', data.fit_tests?.pass_rates?.by_strap_type);
        console.log('Pass rates by style:', data.fit_tests?.pass_rates?.by_style);

        // Set stats
        this.stats = data;
      } catch (err) {
        this.error = err.message;
        console.error('Error loading dashboard data:', err);
      } finally {
        this.loading = false;

        // Now that loading is false, the v-else block will render
        // Wait for DOM to update, then render charts
        await this.$nextTick();
        console.log('After setting loading=false and nextTick');
        console.log('passRateByMaskChart exists?', !!this.$refs.passRateByMaskChart);

        if (this.stats && !this.error) {
          // Give DOM a bit more time to fully render
          setTimeout(() => {
            console.log('About to render charts');
            console.log('passRateByMaskChart exists now?', !!this.$refs.passRateByMaskChart);
            this.renderCharts();
          }, 100);
        }
      }
    },
    renderCharts() {
      console.log('renderCharts called');
      console.log('Available refs:', Object.keys(this.$refs));
      console.log('filtrationChart ref:', this.$refs.filtrationChart);
      console.log('passRateByMaskChart ref:', this.$refs.passRateByMaskChart);

      this.renderFiltrationChart();
      this.renderBreathabilityChart();
      this.renderFitTestTypesChart();
      this.renderFacialMeasurementsChart();
      this.renderGenderChart();
      this.renderRaceChart();
      this.renderAgeChart();
      this.renderOverallPassRateChart();
      this.renderPassRateByMaskChart();
      this.renderPassRateByStrapChart();
      this.renderPassRateByStyleChart();
    },
    renderFiltrationChart() {
      const ctx = this.$refs.filtrationChart;
      if (!ctx) return;

      const withData = this.stats.masks.with_filtration_data;
      const missingData = this.stats.masks.missing_filtration_data;
      const total = this.stats.masks.total;

      this.charts.filtration = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['Filtration Efficiency'],
          datasets: [{
            label: 'With Data',
            data: [withData],
            backgroundColor: '#4CAF50',
            borderWidth: 1,
            borderColor: '#fff'
          }, {
            label: 'Missing Data',
            data: [missingData],
            backgroundColor: '#f44336',
            borderWidth: 1,
            borderColor: '#fff'
          }]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              stacked: true,
              beginAtZero: true,
              max: total
            },
            y: {
              stacked: true,
              display: false
            }
          },
          plugins: {
            legend: {
              display: true,
              position: 'bottom'
            },
            tooltip: {
              callbacks: {
                label: (context) => {
                  const label = context.dataset.label || '';
                  const value = context.parsed.x;
                  const percentage = ((value / total) * 100).toFixed(1);
                  return `${label}: ${value} (${percentage}%)`;
                }
              }
            }
          }
        },
        plugins: [{
          id: 'dataLabels',
          afterDatasetsDraw: (chart) => {
            const ctx = chart.ctx;
            chart.data.datasets.forEach((dataset, datasetIndex) => {
              const meta = chart.getDatasetMeta(datasetIndex);
              meta.data.forEach((bar, index) => {
                const value = dataset.data[index];
                if (value === 0) return;

                const percentage = ((value / total) * 100).toFixed(1);
                const label = `${value} (${percentage}%)`;

                ctx.fillStyle = '#fff';
                ctx.font = 'bold 14px Arial';
                ctx.textBaseline = 'middle';

                // Measure label width
                const labelWidth = ctx.measureText(label).width;

                // For stacked horizontal bars:
                // bar.base is the starting x position (left edge of this segment)
                // bar.x is the ending x position (right edge of this segment)
                const leftEdge = bar.base;
                const rightEdge = bar.x;
                const segmentWidth = rightEdge - leftEdge;

                const padding = 10;
                let x;

                // Position label to stay within its color segment
                if (labelWidth + (padding * 2) < segmentWidth) {
                  // Label fits, center it in the segment
                  x = leftEdge + (segmentWidth / 2);
                } else {
                  // Label is tight, position from left with padding
                  x = leftEdge + (labelWidth / 2) + padding;
                }

                // Ensure label doesn't exceed right edge of segment
                const labelRightEdge = x + (labelWidth / 2);
                if (labelRightEdge > rightEdge - padding) {
                  x = rightEdge - (labelWidth / 2) - padding;
                }

                // Ensure label doesn't go before left edge of segment
                const labelLeftEdge = x - (labelWidth / 2);
                if (labelLeftEdge < leftEdge + padding) {
                  x = leftEdge + (labelWidth / 2) + padding;
                }

                ctx.textAlign = 'center';
                const y = bar.y;

                ctx.fillText(label, x, y);
              });
            });
          }
        }]
      });
    },
    renderBreathabilityChart() {
      const ctx = this.$refs.breathabilityChart;
      if (!ctx) return;

      const withScores = this.stats.masks.with_breathability;
      const withoutScores = this.stats.masks.without_breathability;
      const total = this.stats.masks.total;

      this.charts.breathability = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['Breathability'],
          datasets: [{
            label: 'With Scores',
            data: [withScores],
            backgroundColor: '#4CAF50',
            borderWidth: 1,
            borderColor: '#fff'
          }, {
            label: 'Without Scores',
            data: [withoutScores],
            backgroundColor: '#f44336',
            borderWidth: 1,
            borderColor: '#fff'
          }]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              stacked: true,
              beginAtZero: true,
              max: total
            },
            y: {
              stacked: true,
              display: false
            }
          },
          plugins: {
            legend: {
              display: true,
              position: 'bottom'
            },
            tooltip: {
              callbacks: {
                label: (context) => {
                  const label = context.dataset.label || '';
                  const value = context.parsed.x;
                  const percentage = ((value / total) * 100).toFixed(1);
                  return `${label}: ${value} (${percentage}%)`;
                }
              }
            }
          }
        },
        plugins: [{
          id: 'dataLabels',
          afterDatasetsDraw: (chart) => {
            const ctx = chart.ctx;
            chart.data.datasets.forEach((dataset, datasetIndex) => {
              const meta = chart.getDatasetMeta(datasetIndex);
              meta.data.forEach((bar, index) => {
                const value = dataset.data[index];
                if (value === 0) return;

                const percentage = ((value / total) * 100).toFixed(1);
                const label = `${value} (${percentage}%)`;

                ctx.fillStyle = '#fff';
                ctx.font = 'bold 14px Arial';
                ctx.textBaseline = 'middle';

                // Measure label width
                const labelWidth = ctx.measureText(label).width;

                // For stacked horizontal bars:
                // bar.base is the starting x position (left edge of this segment)
                // bar.x is the ending x position (right edge of this segment)
                const leftEdge = bar.base;
                const rightEdge = bar.x;
                const segmentWidth = rightEdge - leftEdge;

                const padding = 10;
                let x;

                // Position label to stay within its color segment
                if (labelWidth + (padding * 2) < segmentWidth) {
                  // Label fits, center it in the segment
                  x = leftEdge + (segmentWidth / 2);
                } else {
                  // Label is tight, position from left with padding
                  x = leftEdge + (labelWidth / 2) + padding;
                }

                // Ensure label doesn't exceed right edge of segment
                const labelRightEdge = x + (labelWidth / 2);
                if (labelRightEdge > rightEdge - padding) {
                  x = rightEdge - (labelWidth / 2) - padding;
                }

                // Ensure label doesn't go before left edge of segment
                const labelLeftEdge = x - (labelWidth / 2);
                if (labelLeftEdge < leftEdge + padding) {
                  x = leftEdge + (labelWidth / 2) + padding;
                }

                ctx.textAlign = 'center';
                const y = bar.y;

                ctx.fillText(label, x, y);
              });
            });
          }
        }]
      });
    },
    renderFitTestTypesChart() {
      const ctx = this.$refs.fitTestTypesChart;
      if (!ctx) return;

      const total = this.stats.fit_tests.by_type.n95_mode +
                    this.stats.fit_tests.by_type.n99_mode +
                    this.stats.fit_tests.by_type.qlft +
                    this.stats.fit_tests.by_type.user_seal_check;

      this.charts.fitTestTypes = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['N95\nMode', 'N99\nMode', 'QLFT', 'User Seal\nCheck'],
          datasets: [{
            label: 'Fit Tests',
            data: [
              this.stats.fit_tests.by_type.n95_mode,
              this.stats.fit_tests.by_type.n99_mode,
              this.stats.fit_tests.by_type.qlft,
              this.stats.fit_tests.by_type.user_seal_check
            ],
            backgroundColor: ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0'],
            borderWidth: 1,
            borderColor: '#fff'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 1
              }
            }
          },
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              callbacks: {
                afterLabel: (context) => {
                  const value = context.parsed.y;
                  const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                  return `${percentage}% of fit tests with facial measurements`;
                }
              }
            }
          }
        }
      });
    },
    renderFacialMeasurementsChart() {
      const ctx = this.$refs.facialMeasurementsChart;
      if (!ctx) return;

      this.charts.facialMeasurements = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['Incomplete\nTraditional', 'Complete\nTraditional', 'Has\nARKit', 'Both\nComplete', 'No\nMeasurements'],
          datasets: [{
            label: 'Users',
            data: [
              this.stats.fit_tests.facial_measurements.users_with_incomplete_traditional,
              this.stats.fit_tests.facial_measurements.users_with_complete_traditional,
              this.stats.fit_tests.facial_measurements.users_with_arkit,
              this.stats.fit_tests.facial_measurements.users_with_both_complete,
              this.stats.fit_tests.facial_measurements.users_with_no_measurements
            ],
            backgroundColor: ['#f44336', '#4CAF50', '#2196F3', '#9C27B0', '#757575'],
            borderWidth: 1,
            borderColor: '#fff'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 1
              }
            }
          },
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              callbacks: {
                afterLabel: (context) => {
                  const labels = [
                    'Has 1-5 traditional measurements or none',
                    'Has all 6 traditional measurements',
                    'Has ARKit data (regardless of traditional)',
                    'Has all 6 traditional AND ARKit',
                    'Has neither traditional nor ARKit'
                  ];
                  return labels[context.dataIndex];
                }
              }
            }
          }
        }
      });
    },
    renderGenderChart() {
      const ctx = this.$refs.genderChart;
      if (!ctx) return;

      const data = this.stats.fit_tests.demographics.gender_and_sex;
      const labels = data.map(item => item.name);
      const fitTests = data.map(item => item.fit_tests);
      const uniqueUsers = data.map(item => item.unique_users);

      // Generate colors
      const colors = this.generateColors(data.length);

      this.charts.gender = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Fit Tests',
            data: fitTests,
            backgroundColor: colors.map(c => c + 'CC'),
            borderWidth: 1,
            borderColor: '#fff'
          }, {
            label: 'Unique Users',
            data: uniqueUsers,
            backgroundColor: colors.map(c => c + '80'),
            borderWidth: 1,
            borderColor: '#fff'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 1
              }
            }
          },
          plugins: {
            legend: {
              display: true,
              position: 'bottom'
            },
            tooltip: {
              callbacks: {
                afterLabel: (context) => {
                  const dataIndex = context.dataIndex;
                  const item = data[dataIndex];
                  return `Fit Tests: ${item.fit_tests}\nUnique Users: ${item.unique_users}`;
                }
              }
            }
          }
        }
      });
    },
    renderRaceChart() {
      const ctx = this.$refs.raceChart;
      if (!ctx) return;

      const data = this.stats.fit_tests.demographics.race_ethnicity;
      const labels = data.map(item => item.name);
      const fitTests = data.map(item => item.fit_tests);
      const uniqueUsers = data.map(item => item.unique_users);

      // Generate colors
      const colors = this.generateColors(data.length);

      this.charts.race = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Fit Tests',
            data: fitTests,
            backgroundColor: colors.map(c => c + 'CC'),
            borderWidth: 1,
            borderColor: '#fff'
          }, {
            label: 'Unique Users',
            data: uniqueUsers,
            backgroundColor: colors.map(c => c + '80'),
            borderWidth: 1,
            borderColor: '#fff'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 1
              }
            }
          },
          plugins: {
            legend: {
              display: true,
              position: 'bottom'
            },
            tooltip: {
              callbacks: {
                afterLabel: (context) => {
                  const dataIndex = context.dataIndex;
                  const item = data[dataIndex];
                  return `Fit Tests: ${item.fit_tests}\nUnique Users: ${item.unique_users}`;
                }
              }
            }
          }
        }
      });
    },
    renderAgeChart() {
      const ctx = this.$refs.ageChart;
      if (!ctx) return;

      const data = this.stats.fit_tests.demographics.age;
      const labels = data.map(item => item.name);
      const fitTests = data.map(item => item.fit_tests);
      const uniqueUsers = data.map(item => item.unique_users);

      // Generate colors
      const colors = this.generateColors(data.length);

      this.charts.age = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Fit Tests',
            data: fitTests,
            backgroundColor: colors.map(c => c + 'CC'),
            borderWidth: 1,
            borderColor: '#fff'
          }, {
            label: 'Unique Users',
            data: uniqueUsers,
            backgroundColor: colors.map(c => c + '80'),
            borderWidth: 1,
            borderColor: '#fff'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 1
              }
            }
          },
          plugins: {
            legend: {
              display: true,
              position: 'bottom'
            },
            tooltip: {
              callbacks: {
                afterLabel: (context) => {
                  const dataIndex = context.dataIndex;
                  const item = data[dataIndex];
                  return `Fit Tests: ${item.fit_tests}\nUnique Users: ${item.unique_users}`;
                }
              }
            }
          }
        }
      });
    },
    renderOverallPassRateChart() {
      const ctx = this.$refs.overallPassRateChart;
      if (!ctx) return;

      const passed = this.stats.fit_tests.pass_rates.overall.passed;
      const failed = this.stats.fit_tests.pass_rates.overall.total - passed;
      const total = this.stats.fit_tests.pass_rates.overall.total;

      this.charts.overallPassRate = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['Overall Pass Rate'],
          datasets: [{
            label: 'Passed',
            data: [passed],
            backgroundColor: '#4CAF50',
            borderWidth: 1,
            borderColor: '#fff'
          }, {
            label: 'Failed',
            data: [failed],
            backgroundColor: '#f44336',
            borderWidth: 1,
            borderColor: '#fff'
          }]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              stacked: true,
              beginAtZero: true,
              max: total
            },
            y: {
              stacked: true,
              display: false
            }
          },
          plugins: {
            legend: {
              display: true,
              position: 'bottom'
            },
            tooltip: {
              callbacks: {
                label: (context) => {
                  const label = context.dataset.label || '';
                  const value = context.parsed.x;
                  const percentage = ((value / total) * 100).toFixed(1);
                  return `${label}: ${value} (${percentage}%)`;
                }
              }
            }
          }
        },
        plugins: [{
          id: 'dataLabels',
          afterDatasetsDraw: (chart) => {
            const ctx = chart.ctx;
            chart.data.datasets.forEach((dataset, datasetIndex) => {
              const meta = chart.getDatasetMeta(datasetIndex);
              meta.data.forEach((bar, index) => {
                const value = dataset.data[index];
                if (value === 0) return;

                const percentage = ((value / total) * 100).toFixed(1);
                const label = `${value} (${percentage}%)`;

                ctx.fillStyle = '#fff';
                ctx.font = 'bold 14px Arial';
                ctx.textBaseline = 'middle';

                // Measure label width
                const labelWidth = ctx.measureText(label).width;

                // For stacked horizontal bars:
                // bar.base is the starting x position (left edge of this segment)
                // bar.x is the ending x position (right edge of this segment)
                const leftEdge = bar.base;
                const rightEdge = bar.x;
                const segmentWidth = rightEdge - leftEdge;

                const padding = 10;
                let x;

                // Position label to stay within its color segment
                if (labelWidth + (padding * 2) < segmentWidth) {
                  // Label fits, center it in the segment
                  x = leftEdge + (segmentWidth / 2);
                } else {
                  // Label is tight, position from left with padding
                  x = leftEdge + (labelWidth / 2) + padding;
                }

                // Ensure label doesn't exceed right edge of segment
                const labelRightEdge = x + (labelWidth / 2);
                if (labelRightEdge > rightEdge - padding) {
                  x = rightEdge - (labelWidth / 2) - padding;
                }

                // Ensure label doesn't go before left edge of segment
                const labelLeftEdge = x - (labelWidth / 2);
                if (labelLeftEdge < leftEdge + padding) {
                  x = leftEdge + (labelWidth / 2) + padding;
                }

                ctx.textAlign = 'center';
                const y = bar.y;

                ctx.fillText(label, x, y);
              });
            });
          }
        }]
      });
    },
    renderPassRateByMaskChart() {
      const ctx = this.$refs.passRateByMaskChart;
      if (!ctx) {
        console.error('passRateByMaskChart canvas ref not found');
        return;
      }

      const masks = this.paginatedMasks;

      if (masks.length === 0) {
        console.warn('No mask pass rate data available');
        return;
      }

      console.log('Rendering pass rate by mask chart with', masks.length, 'masks');

      // Color bars based on sample size - lighter for smaller samples
      const colors = masks.map(m => this.getColorBySampleSize(m.total, '#2196F3'));

      // Destroy existing chart if it exists
      if (this.charts.passRateByMask) {
        this.charts.passRateByMask.destroy();
      }

      this.charts.passRateByMask = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: masks.map(m => this.truncateLabel(m.name, 40)),
          datasets: [{
            label: 'Pass Rate (%)',
            data: masks.map(m => m.pass_rate),
            backgroundColor: colors,
            borderWidth: 1,
            borderColor: colors.map(c => this.darkenColor(c, 0.2))
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              max: 100,
              ticks: {
                callback: function(value) {
                  return value + '%';
                }
              }
            },
            x: {
              ticks: {
                autoSkip: false,
                maxRotation: 60,
                minRotation: 40
              }
            }
          },
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              callbacks: {
                label: (context) => {
                  const mask = masks[context.dataIndex];
                  return [
                    `Pass Rate: ${mask.pass_rate}%`,
                    `Passed: ${mask.passed}/${mask.total}`,
                    `Sample Size: ${mask.total}`
                  ];
                }
              }
            },
            datalabels: {
              anchor: 'end',
              align: 'end',
              formatter: (value, context) => {
                const mask = masks[context.dataIndex];
                return `(${mask.total})`;
              },
              color: '#555',
              font: {
                size: 11,
                weight: 'bold'
              }
            }
          }
        },
        plugins: [this.createDataLabelsPlugin(masks)]
      });

      console.log('Pass rate by mask chart rendered successfully');
    },
    renderPassRateByStrapChart() {
      const ctx = this.$refs.passRateByStrapChart;
      if (!ctx) {
        console.error('passRateByStrapChart canvas ref not found');
        return;
      }

      const strapData = this.stats.fit_tests.pass_rates.by_strap_type || [];

      if (strapData.length === 0) {
        console.warn('No strap type pass rate data available');
        return;
      }

      console.log('Rendering pass rate by strap chart with', strapData.length, 'strap types');

      // Color bars based on sample size - lighter for smaller samples
      const colors = strapData.map(s => this.getColorBySampleSize(s.total, '#FF9800'));

      this.charts.passRateByStrap = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: strapData.map(s => s.name || 'Unknown'),
          datasets: [{
            label: 'Pass Rate (%)',
            data: strapData.map(s => s.pass_rate),
            backgroundColor: colors,
            borderWidth: 1,
            borderColor: colors.map(c => this.darkenColor(c, 0.2))
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              max: 100,
              ticks: {
                callback: function(value) {
                  return value + '%';
                }
              }
            }
          },
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              callbacks: {
                label: (context) => {
                  const strap = strapData[context.dataIndex];
                  return [
                    `Pass Rate: ${strap.pass_rate}%`,
                    `Passed: ${strap.passed}/${strap.total}`,
                    `Sample Size: ${strap.total}`
                  ];
                }
              }
            }
          }
        },
        plugins: [this.createDataLabelsPlugin(strapData)]
      });

      console.log('Pass rate by strap chart rendered successfully');
    },
    renderPassRateByStyleChart() {
      const ctx = this.$refs.passRateByStyleChart;
      if (!ctx) {
        console.error('passRateByStyleChart canvas ref not found');
        return;
      }

      const styleData = this.stats.fit_tests.pass_rates.by_style || [];

      if (styleData.length === 0) {
        console.warn('No style pass rate data available');
        return;
      }

      console.log('Rendering pass rate by style chart with', styleData.length, 'styles');

      // Color bars based on sample size - lighter for smaller samples
      const colors = styleData.map(s => this.getColorBySampleSize(s.total, '#9C27B0'));

      this.charts.passRateByStyle = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: styleData.map(s => s.name || 'Unknown'),
          datasets: [{
            label: 'Pass Rate (%)',
            data: styleData.map(s => s.pass_rate),
            backgroundColor: colors,
            borderWidth: 1,
            borderColor: colors.map(c => this.darkenColor(c, 0.2))
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              max: 100,
              ticks: {
                callback: function(value) {
                  return value + '%';
                }
              }
            }
          },
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              callbacks: {
                label: (context) => {
                  const style = styleData[context.dataIndex];
                  return [
                    `Pass Rate: ${style.pass_rate}%`,
                    `Passed: ${style.passed}/${style.total}`,
                    `Sample Size: ${style.total}`
                  ];
                }
              }
            }
          }
        },
        plugins: [this.createDataLabelsPlugin(styleData)]
      });

      console.log('Pass rate by style chart rendered successfully');
    },
    onMaskPageChange(page) {
      this.maskCurrentPage = page;
      // Re-render the mask chart with new page data
      this.$nextTick(() => {
        this.renderPassRateByMaskChart();
      });
    },
    onSortChange() {
      // Reset to first page when sort changes
      this.maskCurrentPage = 1;
      // Re-render the mask chart with new sort
      this.$nextTick(() => {
        this.renderPassRateByMaskChart();
      });
    },
    truncateLabel(label, maxLength) {
      if (!label) return 'Unknown';
      return label.length > maxLength ? label.substring(0, maxLength) + '...' : label;
    },
    getColorBySampleSize(sampleSize, baseColor) {
      // Use lighter colors for smaller sample sizes
      // Thresholds: n < 10 (very light), n < 30 (light), n < 50 (medium), n >= 50 (full color)
      if (sampleSize < 10) {
        return this.lightenColor(baseColor, 0.6); // Very light
      } else if (sampleSize < 30) {
        return this.lightenColor(baseColor, 0.4); // Light
      } else if (sampleSize < 50) {
        return this.lightenColor(baseColor, 0.2); // Medium
      } else {
        return baseColor; // Full color
      }
    },
    generateColors(count) {
      // Generate a diverse set of colors for demographic charts
      const baseColors = [
        '#4CAF50', // Green
        '#2196F3', // Blue
        '#FF9800', // Orange
        '#9C27B0', // Purple
        '#F44336', // Red
        '#00BCD4', // Cyan
        '#FFC107', // Amber
        '#E91E63', // Pink
        '#3F51B5', // Indigo
        '#8BC34A', // Light Green
        '#FF5722', // Deep Orange
        '#673AB7', // Deep Purple
      ];

      // If we need more colors than we have, cycle through them
      const colors = [];
      for (let i = 0; i < count; i++) {
        colors.push(baseColors[i % baseColors.length]);
      }
      return colors;
    },
    lightenColor(color, amount) {
      // Convert hex to RGB
      const hex = color.replace('#', '');
      const r = parseInt(hex.substring(0, 2), 16);
      const g = parseInt(hex.substring(2, 4), 16);
      const b = parseInt(hex.substring(4, 6), 16);

      // Lighten by moving towards white
      const newR = Math.round(r + (255 - r) * amount);
      const newG = Math.round(g + (255 - g) * amount);
      const newB = Math.round(b + (255 - b) * amount);

      // Convert back to hex
      return `#${newR.toString(16).padStart(2, '0')}${newG.toString(16).padStart(2, '0')}${newB.toString(16).padStart(2, '0')}`;
    },
    darkenColor(color, amount) {
      // Convert hex to RGB
      const hex = color.replace('#', '');
      const r = parseInt(hex.substring(0, 2), 16);
      const g = parseInt(hex.substring(2, 4), 16);
      const b = parseInt(hex.substring(4, 6), 16);

      // Darken by moving towards black
      const newR = Math.round(r * (1 - amount));
      const newG = Math.round(g * (1 - amount));
      const newB = Math.round(b * (1 - amount));

      // Convert back to hex
      return `#${newR.toString(16).padStart(2, '0')}${newG.toString(16).padStart(2, '0')}${newB.toString(16).padStart(2, '0')}`;
    },
    createDataLabelsPlugin(data) {
      // Custom plugin to draw sample size labels at the end of bars
      return {
        id: 'sampleSizeLabels',
        afterDatasetsDraw: (chart) => {
          const ctx = chart.ctx;

          chart.data.datasets.forEach((dataset, datasetIndex) => {
            const meta = chart.getDatasetMeta(datasetIndex);

            meta.data.forEach((bar, index) => {
              const item = data[index];
              const sampleSize = `(${item.total})`;

              // Set font
              ctx.font = 'bold 11px Arial';
              ctx.fillStyle = '#555';
              ctx.textAlign = 'left';
              ctx.textBaseline = 'middle';

              // Calculate position
              let x, y;

              if (chart.config.options.indexAxis === 'y') {
                // Horizontal bar chart
                x = bar.x + 5; // 5px padding from end of bar
                y = bar.y;
              } else {
                // Vertical bar chart
                x = bar.x;
                y = bar.y - 5; // 5px above bar
                ctx.textAlign = 'center';
              }

              // Draw the label
              ctx.fillText(sampleSize, x, y);
            });
          });
        }
      };
    }
  }
};
</script>

<style scoped>
.dashboard-container {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.dashboard-title {
  font-size: 2.5rem;
  color: #333;
  margin-bottom: 2rem;
  text-align: center;
}

.loading, .error {
  text-align: center;
  padding: 3rem;
  font-size: 1.2rem;
}

.error {
  color: #f44336;
}

.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 3rem;
}

.dashboard-section {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.section-title {
  font-size: 2rem;
  color: #2196F3;
  margin-bottom: 1.5rem;
  border-bottom: 3px solid #2196F3;
  padding-bottom: 0.5rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.stat-value {
  font-size: 3rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 1rem;
  opacity: 0.9;
}

.charts-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.chart-container {
  background: #f9f9f9;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.chart-container-full {
  background: #f9f9f9;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  margin-bottom: 2rem;
}

.chart-container h3,
.chart-container-full h3 {
  font-size: 1.3rem;
  color: #555;
  margin-bottom: 1rem;
  text-align: center;
}

.chart-wrapper {
  position: relative;
  height: 400px;
  width: 100%;
}

.chart-wrapper canvas {
  max-height: 400px;
}

.stacked-bar-wrapper {
  position: relative;
  height: 80px;
  width: 100%;
  margin: 1rem 0;
}

.stacked-bar-wrapper canvas {
  max-height: 80px;
}

.chart-legend {
  margin-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.legend-color {
  width: 20px;
  height: 20px;
  border-radius: 4px;
}

.chart-stats {
  margin-top: 1rem;
  text-align: center;
  font-size: 1rem;
  color: #555;
}

.chart-stats p {
  margin: 0.5rem 0;
}

.sample-size-note {
  font-size: 0.85rem;
  color: #666;
  font-style: italic;
  margin-bottom: 0.5rem;
  text-align: center;
}

.measurement-explanation {
  font-size: 0.9rem;
  color: #555;
  background-color: #f0f7ff;
  padding: 0.75rem;
  border-radius: 4px;
  border-left: 4px solid #2196F3;
  margin-bottom: 0.75rem;
  line-height: 1.5;
}

.measurement-explanation strong {
  color: #1976D2;
}

.sort-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 2rem;
  margin: 1rem 0;
  padding: 1rem;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.sort-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sort-group label {
  font-weight: 600;
  color: #555;
  font-size: 0.9rem;
}

.sort-select {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  color: #333;
  font-size: 0.9rem;
  cursor: pointer;
  transition: border-color 0.2s;
}

.sort-select:hover {
  border-color: #2196F3;
}

.sort-select:focus {
  outline: none;
  border-color: #2196F3;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.1);
}

@media (max-width: 768px) {
  .dashboard-container {
    padding: 1rem;
  }

  .dashboard-title {
    font-size: 2rem;
  }

  .section-title {
    font-size: 1.5rem;
  }

  .charts-row {
    grid-template-columns: 1fr;
  }

  .stat-value {
    font-size: 2rem;
  }

  .sort-controls {
    flex-direction: column;
    gap: 1rem;
  }

  .sort-group {
    width: 100%;
    justify-content: space-between;
  }

  .sort-select {
    flex: 1;
    max-width: 200px;
  }
}
</style>
