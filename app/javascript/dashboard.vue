<template>
  <div class="dashboard-container">
    <h1 class="dashboard-title">BreatheSafe Dashboard</h1>

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
            <canvas ref="filtrationChart"></canvas>
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
            <canvas ref="breathabilityChart"></canvas>
            <div class="chart-legend">
              <div class="legend-item">
                <span class="legend-color" style="background-color: #2196F3;"></span>
                <span>With Scores: {{ stats.masks.with_breathability }}</span>
              </div>
              <div class="legend-item">
                <span class="legend-color" style="background-color: #FF9800;"></span>
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
            <h3>Facial Measurements by Type</h3>
            <canvas ref="facialMeasurementsChart"></canvas>
            <div class="chart-legend">
              <div class="legend-item">
                <span class="legend-color" style="background-color: #9C27B0;"></span>
                <span>Old Set Only: {{ stats.fit_tests.facial_measurements.users_with_old_measurements }}</span>
              </div>
              <div class="legend-item">
                <span class="legend-color" style="background-color: #00BCD4;"></span>
                <span>ARKit Only: {{ stats.fit_tests.facial_measurements.users_with_new_measurements }}</span>
              </div>
              <div class="legend-item">
                <span class="legend-color" style="background-color: #8BC34A;"></span>
                <span>Both: {{ stats.fit_tests.facial_measurements.users_with_both }}</span>
              </div>
            </div>
          </div>

          <div class="chart-container">
            <h3>Overall Pass Rate</h3>
            <canvas ref="overallPassRateChart"></canvas>
            <div class="chart-stats">
              <p><strong>Pass Rate:</strong> {{ stats.fit_tests.pass_rates.overall.pass_rate }}%</p>
              <p><strong>Passed:</strong> {{ stats.fit_tests.pass_rates.overall.passed }} / {{ stats.fit_tests.pass_rates.overall.total }}</p>
            </div>
          </div>
        </div>

        <!-- Pass Rates by Mask -->
        <div class="chart-container-full">
          <h3>Pass Rates by Mask (Top 10)</h3>
          <canvas ref="passRateByMaskChart"></canvas>
        </div>

        <!-- Pass Rates by Strap Type -->
        <div class="charts-row">
          <div class="chart-container">
            <h3>Pass Rates by Strap Type</h3>
            <canvas ref="passRateByStrapChart"></canvas>
          </div>

          <div class="chart-container">
            <h3>Pass Rates by Style</h3>
            <canvas ref="passRateByStyleChart"></canvas>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

export default {
  name: 'Dashboard',
  data() {
    return {
      stats: null,
      loading: true,
      error: null,
      charts: {}
    };
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

        this.stats = await response.json();

        // Wait for next tick to ensure refs are available
        await this.$nextTick();
        this.renderCharts();
      } catch (err) {
        this.error = err.message;
        console.error('Error loading dashboard data:', err);
      } finally {
        this.loading = false;
      }
    },
    renderCharts() {
      this.renderFiltrationChart();
      this.renderBreathabilityChart();
      this.renderFacialMeasurementsChart();
      this.renderOverallPassRateChart();
      this.renderPassRateByMaskChart();
      this.renderPassRateByStrapChart();
      this.renderPassRateByStyleChart();
    },
    renderFiltrationChart() {
      const ctx = this.$refs.filtrationChart;
      if (!ctx) return;

      this.charts.filtration = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['With Data', 'Missing Data'],
          datasets: [{
            data: [
              this.stats.masks.with_filtration_data,
              this.stats.masks.missing_filtration_data
            ],
            backgroundColor: ['#4CAF50', '#f44336'],
            borderWidth: 2,
            borderColor: '#fff'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: {
            legend: {
              display: false
            }
          }
        }
      });
    },
    renderBreathabilityChart() {
      const ctx = this.$refs.breathabilityChart;
      if (!ctx) return;

      this.charts.breathability = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['With Scores', 'Without Scores'],
          datasets: [{
            data: [
              this.stats.masks.with_breathability,
              this.stats.masks.without_breathability
            ],
            backgroundColor: ['#2196F3', '#FF9800'],
            borderWidth: 2,
            borderColor: '#fff'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: {
            legend: {
              display: false
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
          labels: ['Old Set', 'ARKit', 'Both'],
          datasets: [{
            label: 'Users',
            data: [
              this.stats.fit_tests.facial_measurements.users_with_old_measurements,
              this.stats.fit_tests.facial_measurements.users_with_new_measurements,
              this.stats.fit_tests.facial_measurements.users_with_both
            ],
            backgroundColor: ['#9C27B0', '#00BCD4', '#8BC34A'],
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
            }
          }
        }
      });
    },
    renderOverallPassRateChart() {
      const ctx = this.$refs.overallPassRateChart;
      if (!ctx) return;

      const passRate = this.stats.fit_tests.pass_rates.overall.pass_rate;
      const failRate = 100 - passRate;

      this.charts.overallPassRate = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['Passed', 'Failed'],
          datasets: [{
            data: [passRate, failRate],
            backgroundColor: ['#4CAF50', '#f44336'],
            borderWidth: 2,
            borderColor: '#fff'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: {
            legend: {
              display: false
            }
          }
        }
      });
    },
    renderPassRateByMaskChart() {
      const ctx = this.$refs.passRateByMaskChart;
      if (!ctx) return;

      // Take top 10 masks by total tests
      const topMasks = this.stats.fit_tests.pass_rates.by_mask
        .sort((a, b) => b.total - a.total)
        .slice(0, 10);

      this.charts.passRateByMask = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: topMasks.map(m => this.truncateLabel(m.name, 30)),
          datasets: [{
            label: 'Pass Rate (%)',
            data: topMasks.map(m => m.pass_rate),
            backgroundColor: '#2196F3',
            borderWidth: 1,
            borderColor: '#1976D2'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          indexAxis: 'y',
          scales: {
            x: {
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
                  const mask = topMasks[context.dataIndex];
                  return [
                    `Pass Rate: ${mask.pass_rate}%`,
                    `Passed: ${mask.passed}/${mask.total}`
                  ];
                }
              }
            }
          }
        }
      });
    },
    renderPassRateByStrapChart() {
      const ctx = this.$refs.passRateByStrapChart;
      if (!ctx) return;

      const strapData = this.stats.fit_tests.pass_rates.by_strap_type;

      this.charts.passRateByStrap = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: strapData.map(s => s.name || 'Unknown'),
          datasets: [{
            label: 'Pass Rate (%)',
            data: strapData.map(s => s.pass_rate),
            backgroundColor: '#FF9800',
            borderWidth: 1,
            borderColor: '#F57C00'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
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
                    `Passed: ${strap.passed}/${strap.total}`
                  ];
                }
              }
            }
          }
        }
      });
    },
    renderPassRateByStyleChart() {
      const ctx = this.$refs.passRateByStyleChart;
      if (!ctx) return;

      const styleData = this.stats.fit_tests.pass_rates.by_style;

      this.charts.passRateByStyle = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: styleData.map(s => s.name || 'Unknown'),
          datasets: [{
            label: 'Pass Rate (%)',
            data: styleData.map(s => s.pass_rate),
            backgroundColor: '#9C27B0',
            borderWidth: 1,
            borderColor: '#7B1FA2'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
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
                    `Passed: ${style.passed}/${style.total}`
                  ];
                }
              }
            }
          }
        }
      });
    },
    truncateLabel(label, maxLength) {
      if (!label) return 'Unknown';
      return label.length > maxLength ? label.substring(0, maxLength) + '...' : label;
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
}
</style>
