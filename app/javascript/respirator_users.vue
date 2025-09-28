<template>
  <div class='top-container'>
    <div class='header justify-content-center align-items-center'>
      <div class='flex align-items-center row'>
        <h2 class='tagline'>Respirator Users</h2>
        <CircularButton text="+" @click="newUser"/>
        <CircularButton text="?" @click="showHelp = true"/>
      </div>

      <div class='row justify-content-center'>
        <input id='search' type="text" v-model='search'>
        <SearchIcon height='2em' width='2em'/>
      </div>
    </div>

    <div>
      <RespiratorUsersOverview :search="search" :metricToShow="metricToShow" />
    </div>

    <Popup v-if='showHelp' @onclose='showHelp = false'>
      <div v-if='tabToShow == "Overview"'>
        <h3>Overview Tab Help</h3>
        <p>This page is meant for people who are trying to contribute data to Breathesafe for research.</p>

        <h4>Getting Started:</h4>
        <ul>
          <li><strong>Create a new user:</strong> Click the "+" button to create a new user that you manage. You'll be asked questions about demographics and facial measurements, which help develop the mask recommender algorithm.</li>
        </ul>

        <h4>Using the Table:</h4>
        <ul>
          <li><strong>Click on cells:</strong> Clicking on a particular cell will take you to the associated section for that user (demographics, facial measurements, etc.)</li>
          <li><strong>Recommend button:</strong> Click the "Recommend" button for a particular user to get mask recommendations using their facial measurements</li>
          <li><strong>Missing measurements:</strong> If a user is missing required facial measurements (face width, nose protrusion, or bitragion subnasale arc), you'll see a popup asking you to complete those measurements first</li>
        </ul>
      </div>

      <div v-if='tabToShow == "Facial Measurements"'>
        <h3>Facial Measurements Tab Help</h3>
        <p>This view is meant for quality control purposes.</p>

        <h4>Understanding Z-Scores:</h4>
        <ul>
          <li><strong>What are Z-scores:</strong> Z-scores measure how much of an outlier the given data is (e.g., close to -2 or 2)</li>
          <li><strong>When to be concerned:</strong> If values are close to -2 or 2, there might be a significant measurement error</li>
          <li><strong>Important note:</strong> It's possible that there's actually nothing wrong with the data, but there's also a possibility that the user just measured incorrectly</li>
          <li><strong>Recommendation:</strong> Please re-measure if values are close to -2 or 2</li>
        </ul>

        <h4>Using the View:</h4>
        <ul>
          <li><strong>Switch between views:</strong> Use the "Absolute" and "Z-Score" tabs to see measurements in different formats</li>
          <li><strong>Search:</strong> Use the search box to filter users by name or manager email</li>
        </ul>
      </div>
    </Popup>

    <div v-if='tabToShow == "Facial Measurements"'>
      <div class='container chunk'>
        <ClosableMessage @onclose='messages = []' :messages='messages'/>
        <br>
      </div>

      <div class='main facial-measurements-table-container'>
        <div class='centered'>
          <table v-if='facialMeasurementsData.length > 0' class='facial-measurements-table'>
            <thead>
              <tr>
                <th v-if='currentUser.admin'>Manager Email</th>
                <th>Name</th>
                <th v-for='col in facialMeasurementColumns'>{{columnDisplayNames[col]}}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for='row in filteredFacialMeasurementsData'>
                <td v-if='currentUser.admin'>{{row.manager_email}}</td>
                <td>{{row.full_name}}</td>
                <td v-for='col in facialMeasurementColumns' class='colored-cell'>
                  <ColoredCell
                    :colorScheme="getColorSchemeForColumn(col)"
                    :value='getValueForColumn(row, col)'
                    :text='getDisplayValueForColumn(row, col)'
                    :exception='getExceptionForColumn(row, col)'
                    class='colored-cell'
                  />
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <h3 class='text-align-center' v-show='facialMeasurementsData.length == 0'>
          Loading facial measurements data...
        </h3>
        <h3 class='text-align-center' v-show='facialMeasurementsData.length > 0 && filteredFacialMeasurementsData.length == 0'>
          No facial measurements found matching your search.
        </h3>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Button from './button.vue'
import ClosableMessage from './closable_message.vue'
import CircularButton from './circular_button.vue'
import ColoredCell from './colored_cell.vue'
import Popup from './pop_up.vue'
import { genColorSchemeBounds } from './colors';
import { deepSnakeToCamel, setupCSRF } from './misc.js'
import { userSealCheckColorMapping, riskColorInterpolationScheme } from './colors.js'
import { RespiratorUser } from './respirator_user.js'
import { signIn } from './session.js'
import { mapActions, mapWritableState, mapState } from 'pinia';
import { useProfileStore } from './stores/profile_store';
import { useMainStore } from './stores/main_store';
import SearchIcon from './search_icon.vue'

import TabSet from './tab_set.vue'
import RespiratorUsersOverview from './respirator_users_overview.vue'

export default {
  name: 'RespiratorUsers',
  components: {
    Button,
    CircularButton,
    ClosableMessage,
    ColoredCell,
    Popup,
    SearchIcon,
    TabSet,
    RespiratorUsersOverview
  },
  data() {
    return {
      search: "",
      tabToShow: "Overview",
      metricToShow: "Demographics",
      facialMeasurementView: "Absolute",
      facialMeasurementsData: [],
      showHelp: false
    }
  },
  props: {
  },
  computed: {
    ...mapState(
        useMainStore,
        [
          'currentUser',
          'messages'
        ]
    ),
    ...mapWritableState(
        useMainStore,
        [
          'messages'
        ]
    ),
    ...mapState(
        useProfileStore,
        [
          'profileId',
          'readyToAddFitTestingDataPercentage',
          'nameComplete',
          'genderAndSexComplete',
          'raceEthnicityComplete',
          'facialMeasurementsComplete',
          'loadFacialMeasurements',
        ]
    ),

    ...mapWritableState(
        useProfileStore,
        [
          'firstName',
          'lastName',
          'raceEthnicity',
          'genderAndSex',
        ]
    ),

    evenlySpacedColorScheme() {
      return genColorSchemeBounds(0, 1, 5)
    },
    tabToShowOptions() {
      return [
        { text: 'Demographics' },
        { text: 'Facial measurements' },
        { text: 'Num masks tested' }
      ];
    },
    facialMeasurementViewOptions() {
      return [
        { text: 'Absolute' },
        { text: 'Z-Score' }
      ];
    },
    facialMeasurementColumns() {
      return [
        'face_width',
        'jaw_width',
        'face_depth',
        'face_length',
        'lower_face_length',
        'bitragion_menton_arc',
        'bitragion_subnasale_arc',
        'nasal_root_breadth',
        'nose_protrusion',
        'nose_bridge_height',
        'lip_width',
        'head_circumference',
        'nose_breadth'
      ];
    },
    columnDisplayNames() {
      const names = {
        'face_width': 'Face Width',
        'jaw_width': 'Jaw Width',
        'face_depth': 'Face Depth',
        'face_length': 'Face Length',
        'lower_face_length': 'Lower Face Length',
        'bitragion_menton_arc': 'Bitragion Menton Arc',
        'bitragion_subnasale_arc': 'Bitragion Subnasale Arc',
        'nasal_root_breadth': 'Nasal Root Breadth',
        'nose_protrusion': 'Nose Protrusion',
        'nose_bridge_height': 'Nose Bridge Height',
        'lip_width': 'Lip Width',
        'head_circumference': 'Head Circumference',
        'nose_breadth': 'Nose Breadth'
      };
      return names;
    },
    filteredFacialMeasurementsData() {
      if (this.search === "") {
        return this.facialMeasurementsData;
      } else {
        const lowerSearch = this.search.toLowerCase();
        return this.facialMeasurementsData.filter(row => {
          const name = (row.full_name || '').toLowerCase();
          const managerEmail = (row.manager_email || '').toLowerCase();
          return name.includes(lowerSearch) || managerEmail.includes(lowerSearch);
        });
      }
    }
  },
  async created() {
    console.log('RespiratorUsers component created');
    await this.getCurrentUser()
    console.log('Current user loaded:', this.currentUser);

    if (!this.currentUser) {
      console.log('No current user, redirecting to sign in');
      signIn.call(this)
    } else {
      console.log('Calling handleRoute');
      this.handleRoute()
      // If we're already on the facial measurements tab, load the data
      if (this.tabToShow === 'Facial Measurements') {
        console.log('Tab is Facial Measurements, loading data');
        this.loadFacialMeasurementsData();
      }
    }
  },
  mounted() {
    // Add keyboard event listener for Escape key
    document.addEventListener('keydown', this.handleKeydown);
  },
  beforeUnmount() {
    // Remove keyboard event listener
    document.removeEventListener('keydown', this.handleKeydown);
  },
  watch: {
    '$route': {
      handler() {
        console.log('Route changed, calling handleRoute');
        this.handleRoute();
      },
      immediate: false
    }
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser', 'addMessages']),
    ...mapActions(useProfileStore, ['loadProfile']),
    statusColor(fitTestingPercent) {
      let percentage = parseFloat(fitTestingPercent.split("%")[0])
      let status = 'Passed'
      if (percentage == 0) {
        status = "Failed"
      } else if (percentage > 0 && percentage < 100) {
        status = "Skipped"
      }

      let color = userSealCheckColorMapping[status]
      return `rgb(${color.r}, ${color.g}, ${color.b})`
    },
    backgroundColor(boolean) {
      let color;

      if (boolean) {
        color = userSealCheckColorMapping['Passed']

      } else {
        color = userSealCheckColorMapping['Failed']
      }

      return `rgb(${color.r}, ${color.g}, ${color.b}, 0.5)`
    },
    checkmarkOrCross(boolean) {
      if (boolean) {
        return `&#x2714;`
      } else {
        return "&#x2717;"
      }
    },

    async newUser() {
      setupCSRF();

      let managedUser;
      let respiratorUser;

      await axios.post(
        `/managed_users.json`,
      )
        .then(response => {
          let data = response.data
          if (response.data.managed_user) {
            managedUser = deepSnakeToCamel(response.data.managed_user)

            respiratorUser = new RespiratorUser(
              managedUser
            )

            // The overview component will handle adding the user to its data
            // since it manages its own data fetching

            this.$router.push(
              {
                'name': 'RespiratorUser',
                params: {
                  id: respiratorUser.managedId
                }
              }
            )
          }
        })
        .catch(error => {
          if (error && error.response && error.response.data && error.response.data.messages) {
            this.addMessages(error.response.data.messages)
          } else {
            this.addMessages['Something went wrong.']
          }

        // whatever you want
        })
    },

    displayMetric(event) {
      this.metricToShow = event.target.value
    },
    setTabToShow(option) {
      this.tabToShow = option.name;
      //if (this.tabToShow === 'Facial Measurements') {
      //  this.loadFacialMeasurementsData();
      //}

      // Update URL query parameter to reflect current tab
      //const query = { ...this.$route.query };
      //if (this.tabToShow === 'Overview') {
      //  query.tab = 'overview';
      //} else if (this.tabToShow === 'Facial Measurements') {
      //  query.tab = 'facial_measurements';
      //}

      //this.$router.replace({ query });
    },
    handleRoute() {
      console.log('handleRoute called with:', {
        hash: this.$route.hash,
        query: this.$route.query,
        currentTab: this.tabToShow
      });

      // Handle the facial measurements route
      if (this.$route.hash === '#/respirator_users/facial_measurements') {
        console.log('Setting tab to Facial Measurements from hash');
        this.tabToShow = 'Facial Measurements';
        this.loadFacialMeasurementsData();
      }

      // Handle query parameter for tab selection
      if (this.$route.query.tab) {
        const tab = this.$route.query.tab;
        console.log('Processing query tab:', tab);
        if (tab === 'overview') {
          console.log('Setting tab to Overview');
          this.tabToShow = 'Overview';
        } else if (tab === 'facial_measurements') {
          console.log('Setting tab to Facial Measurements from query');
          this.tabToShow = 'Facial Measurements';
          this.loadFacialMeasurementsData();
        }
      }
    },
    setFacialMeasurementView(option) {
      this.facialMeasurementView = option.name;
    },
    getColorSchemeForColumn(col) {
      // Define color schemes for different measurement ranges
      const schemes = {
        'face_width': genColorSchemeBounds(120, 180, 6),
        'jaw_width': genColorSchemeBounds(120, 170, 6),
        'face_depth': genColorSchemeBounds(100, 150, 6),
        'face_length': genColorSchemeBounds(100, 150, 6),
        'lower_face_length': genColorSchemeBounds(60, 120, 6),
        'bitragion_menton_arc': genColorSchemeBounds(200, 300, 6),
        'bitragion_subnasale_arc': genColorSchemeBounds(200, 300, 6),
        'nasal_root_breadth': genColorSchemeBounds(15, 25, 6),
        'nose_protrusion': genColorSchemeBounds(20, 40, 6),
        'nose_bridge_height': genColorSchemeBounds(15, 30, 6),
        'lip_width': genColorSchemeBounds(40, 60, 6),
        'head_circumference': genColorSchemeBounds(500, 600, 6),
        'nose_breadth': genColorSchemeBounds(25, 40, 6)
      };

      // For z-scores, use a different color scheme
      if (this.facialMeasurementView === 'Z-Score') {
        return genColorSchemeBounds(-2.5, 2.5, 6);
      }

      return schemes[col] || this.evenlySpacedColorScheme;
    },
    getValueForColumn(row, col) {
      if (this.facialMeasurementView === 'Z-Score') {
        const zScoreCol = `${col}_z_score`;
        const value = row[zScoreCol];
        console.log(`Getting z-score for ${col}:`, { zScoreCol, value, type: typeof value });
        return value === null || value === undefined ? null : parseFloat(value);
      } else {
        const value = row[col];
        console.log(`Getting value for ${col}:`, { value, type: typeof value, availableKeys: Object.keys(row) });
        return value === null || value === undefined ? null : parseFloat(value);
      }
    },
    getDisplayValueForColumn(row, col) {
      const value = this.getValueForColumn(row, col);
      console.log(`getDisplayValueForColumn for ${col}:`, { value, isNull: value === null, isUndefined: value === undefined, isNaN: isNaN(value) });

      if (value === null || value === undefined || isNaN(value)) {
        return 'N/A';
      }

      if (this.facialMeasurementView === 'Z-Score') {
        return value.toFixed(2);
      } else {
        return `${value} mm`;
      }
    },
    getExceptionForColumn(row, col) {
      const value = this.getValueForColumn(row, col);
      if (value === null || value === undefined || isNaN(value)) {
        return {
          value: null,
          text: 'N/A',
          color: { r: 128, g: 128, b: 128 }
        };
      }

      // For z-scores, highlight outliers
      if (this.facialMeasurementView === 'Z-Score') {
        if (Math.abs(value) > 2) {
          return {
            value: value,
            text: value.toFixed(2),
            color: { r: 255, g: 0, b: 0 }
          };
        }
      }

      return null;
    },
    handleKeydown(event) {
      if (event.key === 'Escape' && this.showHelp) {
        this.showHelp = false;
      }
    },
    async loadFacialMeasurementsData() {
      try {
        console.log('Loading facial measurements data...');
        const response = await axios.get('/managed_users/facial_measurements.json');
        console.log('Facial measurements response:', response.data);
        this.facialMeasurementsData = response.data.facial_measurements;
        console.log('Facial measurements data loaded:', this.facialMeasurementsData.length, 'rows');

        if (this.facialMeasurementsData.length > 0) {
          console.log('First row columns:', Object.keys(this.facialMeasurementsData[0]));
          console.log('Sample z-score columns:', this.facialMeasurementColumns.map(col => `${col}_z_score`));
          console.log('First row data:', this.facialMeasurementsData[0]);
        }
      } catch (error) {
        console.error('Error loading facial measurements data:', error);
        this.addMessages(['Failed to load facial measurements data.']);
      }
    }
     }
}
</script>

<style scoped>
  .main {
    display: flex;
    flex-direction: column;
  }
  p {
    margin: 1em;
  }

  .colored-cell {
    color: white;
    text-shadow: 1px 1px 2px black;
    padding: 1em;
  }

  .quote {
    font-style: italic;
    margin: 1em;
    margin-left: 2em;
    padding-left: 1em;
    border-left: 5px solid black;
    max-width: 25em;
  }
  .author {
    margin-left: 2em;
  }
  .credentials {
    margin-left: 3em;
  }

  .italic {
    font-style: italic;
  }

  .tagline {
    text-align: center;
    font-weight: bold;
    margin: 0.5em;
  }

  .call-to-actions {
    display: flex;
    flex-direction: column;
    align-items: center;
    height: 14em;
  }
  .call-to-actions a {
    text-decoration: none;
  }
  .header {
    margin-top: 1.5em;
  }

  .main {
    display: grid;
    grid-template-columns: 100%;
    grid-template-rows: auto;
  }

  .centered {
    display: flex;
    justify-content: space-around;
  }

  .missing {
    color: black;
  }
  img {
    width: 30em;
  }
  .top-container {
    height: 100vh;
  }

  .row {
    display: flex;
    flex-direction: row;
  }

  .align-items-center {
    align-items: center;
  }

  .justify-content-center {
    display: flex;
    justify-content: center;
  }

  tbody tr:hover {
    cursor: pointer;
    background-color: rgb(230,230,230);
  }

  thead th {
    background-color: #eee;
    padding: 1em;
  }

  .colored-cell {
    text-align: center;
  }

  .text-align-center {
    text-align: center;
  }

  .empty-sign {
    margin-top: 25em;
  }

  .scrollable {
    overflow-y: auto;
    height: 75vh;
  }

  a {
    color: white;
  }

  .facial-measurements-table-container {
    max-height: 70vh;
    overflow-y: auto;
    position: relative;
  }

  .facial-measurements-table {
    width: 100%;
    border-collapse: collapse;
  }

  .facial-measurements-table thead, .facial-measurements-header {
    position: sticky;
    top: 0;
    z-index: 10;
    background-color: #eee;
  }

  .facial-measurements-table th {
    padding: 1em;
    background-color: #eee;
    border-bottom: 2px solid #ddd;
    font-weight: bold;
  }

  .facial-measurements-table td {
    padding: 0.5em;
    border-bottom: 1px solid #ddd;
  }

  .facial-measurements-table tbody tr:hover {
    background-color: rgb(240, 240, 240);
  }

  #facial-measurements-search {
    width: 75vw;
    padding: 1em;
    margin-bottom: 1em;
  }

  @media(max-width: 700px) {
    img {
      width: 100vw;
    }

    .call-to-actions {
      height: 14em;
    }

    #search {
      width: 75vw;
      padding: 1em;
    }

    .header {
      flex-direction: column;

    }
  }

  label {
    padding-left: 0.5em;
    padding-right: 0.5em;

  }

  .row {
    margin-top: 1em;
    margin-bottom: 1em;
  }

  select {
    padding: 1em;
  }
</style>
