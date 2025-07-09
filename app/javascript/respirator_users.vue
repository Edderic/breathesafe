<template>
  <div class='top-container'>
    <div class='flex align-items-center justify-content-center row'>
      <h2 class='tagline'>Respirator Users</h2>
      <CircularButton text="+" @click="newUser"/>
    </div>

    <div class='menu row'>
      <TabSet
        :options='tabToShowOptions'
        @update='setTabToShow'
        :tabToShow='tabToShow'
      />
    </div>

    <div v-if='tabToShow == "Overview"'>
      <div class='row justify-content-center'>
        <input id='search' type="text" v-model='search'>
        <SearchIcon height='2em' width='2em'/>
      </div>

      <div class='container chunk'>
        <ClosableMessage @onclose='messages = []' :messages='messages'/>
        <br>
      </div>

      <Popup v-if='missingFacialMeasurementsForRecommender.length > 0' @onclose='missingFacialMeasurementsForRecommender = []'>
        <p>
        User is missing at least one facial measurement needed for mask recommendations:
        <ul>
          <router-link class='missing' :to="linkToUserFacialMeasurement" >
            <li v-for="m in missingFacialMeasurementsForRecommender">{{m}}</li>
          </router-link>
        </ul>

        </p>
      </Popup>

      <div :class='{main: true, scrollable: managedUsers.length == 0}'>
        <div class='centered'>
          <table>
            <thead>
              <tr>
                <th v-if='currentUser.admin'>Manager Email</th>
                <th>Name</th>
                <th>Demographics</th>
                <th>Face Measurements</th>
                <th>Masks that have data</th>
                <th>Recommend</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for='r in displayables' text='Edit'>
                <td v-if='currentUser.admin'>{{r['managerEmail']}}</td>
                <td @click="visit(r.managedId, 'Name')">
                  {{r.firstName}} {{r.lastName}}
                </td>
                <td @click="visit(r.managedId, 'Demographics')" class='colored-cell' >
                  <ColoredCell
                    :colorScheme="evenlySpacedColorScheme"
                    :maxVal=1
                    :value='1 - r.demogPercentComplete / 100'
                    :text='percentage(r.demogPercentComplete)'
                    class='color-cell'
                  />
                </td>
                <td @click="visit(r.managedId, 'Facial Measurements')" class='colored-cell' >
                  <ColoredCell
                    :colorScheme="evenlySpacedColorScheme"
                    :maxVal=1
                    :value='1- r.fmPercentComplete / 100'
                    :text='percentage(r.fmPercentComplete)'
                    class='color-cell'
                  />
                </td>
                <td class='colored-cell' @click='v'>
                  <router-link :to="{name: 'FitTests', query: {'managedId': r.managedId }}">
                    <ColoredCell
                      :colorScheme="evenlySpacedColorScheme"
                      :maxVal=1
                      :value='1 - (r.fitTestingPercentComplete || 0) / 100'
                      :text='percentage(r.fitTestingPercentComplete || 0)'
                      class='color-cell'
                    />
                  </router-link>
                </td>
                <td class='colored-cell' @click='maybeRecommend(r)'>
                    <Button :style='`font-size: 1em; background-color: ${backgroundColorForRecommender(r)}`'>
                      Recommend
                    </Button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <h3 class='text-align-center' v-show='displayables.length == 0' >
          No managed users to show. Use the (+) button above to add users you can add fit test data for.
        </h3>
      </div>
    </div>

    <div v-if='tabToShow == "Facial Measurements"'>
      <div class='container chunk'>
        <ClosableMessage @onclose='messages = []' :messages='messages'/>
        <br>
      </div>

      <div class='menu row'>
        <TabSet
          :options='facialMeasurementViewOptions'
          @update='setFacialMeasurementView'
          :tabToShow='facialMeasurementView'
        />
      </div>

      <div class='main'>
        <div class='centered'>
          <table v-if='facialMeasurementsData.length > 0'>
            <thead>
              <tr>
                <th v-if='currentUser.admin'>Manager Email</th>
                <th>Name</th>
                <th v-for='col in facialMeasurementColumns'>{{columnDisplayNames[col]}}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for='row in facialMeasurementsData'>
                <td v-if='currentUser.admin'>{{row.manager_email}}</td>
                <td>{{row.full_name}}</td>
                <td v-for='col in facialMeasurementColumns' class='colored-cell'>
                  <ColoredCell
                    :colorScheme="getColorSchemeForColumn(col)"
                    :value='getValueForColumn(row, col)'
                    :text='getDisplayValueForColumn(row, col)'
                    :exception='getExceptionForColumn(row, col)'
                    class='color-cell'
                  />
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <h3 class='text-align-center' v-show='facialMeasurementsData.length == 0'>
          Loading facial measurements data...
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
import { deepSnakeToCamel, setupCSRF } from './misc.js'
import { userSealCheckColorMapping, riskColorInterpolationScheme, genColorSchemeBounds } from './colors.js'
import { RespiratorUser } from './respirator_user.js'
import { signIn } from './session.js'
import { facialMeasurementsPresenceColorMapping } from './colors.js'
import { mapActions, mapWritableState, mapState } from 'pinia';
import { useProfileStore } from './stores/profile_store';
import { useMainStore } from './stores/main_store';
import SearchIcon from './search_icon.vue'
import { useManagedUserStore } from './stores/managed_users_store.js'
import TabSet from './tab_set.vue'

export default {
  name: 'RespiratorUsers',
  components: {
    Button,
    CircularButton,
    ClosableMessage,
    ColoredCell,
    Popup,
    SearchIcon,
    TabSet
  },
  data() {
    return {
      facialMeasurementsLength: 0,
      missingFacialMeasurementsForRecommender: [],
      search: "",
      userId: 0,
            tabToShow: "Overview",
      facialMeasurementView: "Absolute",
      facialMeasurementsData: []
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
        useManagedUserStore,
        [
          'managedUsers'
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
    linkToUserFacialMeasurement() {
      return {
        'name': 'RespiratorUser',
        'params': {'id': this.userId},
        'query': {
          'tabToShow': "Facial Measurements"
        }
      }
    },
    displayables() {
      if (this.search == "") {
        return this.managedUsers
      } else {
        let lowerSearch = this.search.toLowerCase()
        return this.managedUsers.filter(
          function(mu) {
            return mu.firstName.toLowerCase().match(lowerSearch)
              || mu.lastName.toLowerCase().match(lowerSearch)

          }
        )
      }
    },
    facialMeasurementsIncomplete() {
      return this.facialMeasurementsLength == 0
    },
    evenlySpacedColorScheme() {
      return genColorSchemeBounds(0, 1, 5)
    },
    tabToShowOptions() {
      return [
        { text: 'Overview' },
        { text: 'Facial Measurements' }
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
    }
  },
  async created() {
    await this.getCurrentUser()

    if (!this.currentUser) {
      signIn.call(this)
    } else {
      this.loadManagedUsers()
    }
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser', 'addMessages']),
    ...mapActions(useProfileStore, ['loadProfile']),
    ...mapActions(useManagedUserStore, ['loadManagedUsers']),
    maybeRecommend(r) {
      let missing = []

      let measurements = {
        'bitragionSubnasaleArc': {
          'eng': 'Bitragion subnasale arc (mm)',
          'mm': 'bitragionSubnasaleArcMm'
        },
        'noseProtrusion': {
          'eng': 'Nose protrusion (mm)',
          'mm': 'noseProtrusionMm'
        },
        'faceWidth' : {
          'eng': 'Face width (mm)',
          'mm': 'faceWidthMm'
        }
      }

      for(let key in measurements) {
        if (!r[key]) {
          missing.push(measurements[key]['eng'])
        }
      }

      if (missing.length > 0) {
        this.missingFacialMeasurementsForRecommender = missing

        this.userId = r.managedId
      } else {

        let query = {}
        for(let key in measurements) {
            query[measurements[key]['mm']] = r[key]
        }

        this.$router.push(
         {
           name: 'Masks',
           query: query
         }
        )
      }
    },
    backgroundColorForRecommender(r) {
      let color;
      if (r.bitragionSubnasaleArc && r.noseProtrusion && r.faceWidth ) {
        color = facialMeasurementsPresenceColorMapping['Complete'];
      } else {
        color = facialMeasurementsPresenceColorMapping['Completely missing'];
      }
      return `rgb(${color.r}, ${color.g}, ${color.b})`
    },
    recommendQuery(r) {
      return {
        bitragionSubnasaleArcMm: r.bitragionSubnasaleArc,
        noseProtrusionMm: r.noseProtrusion,
        faceWidthMm: r.faceWidth,
      }

    },
    percentage(num) {
      return `${num}%`
    },
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

      let managedUsers;
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

            this.managedUsers.push(
              respiratorUser
            )

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
    visit(profileId, tabToShow) {
      this.$router.push({
        name: 'RespiratorUser',
        params: {
          id: profileId
        },
        query: {
          tabToShow: tabToShow
        }
      })
    },
    setTabToShow(option) {
      this.tabToShow = option.name;
      if (this.tabToShow === 'Facial Measurements') {
        this.loadFacialMeasurementsData();
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
        return genColorSchemeBounds(-3, 3, 6);
      }
      
      return schemes[col] || this.evenlySpacedColorScheme;
    },
    getValueForColumn(row, col) {
      if (this.facialMeasurementView === 'Z-Score') {
        const zScoreCol = `${col}_z_score`;
        return row[zScoreCol];
      } else {
        return row[col];
      }
    },
    getDisplayValueForColumn(row, col) {
      const value = this.getValueForColumn(row, col);
      if (value === null || value === undefined) {
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
      if (value === null || value === undefined) {
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
    async loadFacialMeasurementsData() {
      try {
        const response = await axios.get('/managed_users/facial_measurements.json');
        this.facialMeasurementsData = response.data.facial_measurements;
      } catch (error) {
        this.addMessages(['Failed to load facial measurements data.']);
        console.error(error);
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

  th, td {
    padding: 0.5em;
  }

  .colored-cell {
    color: white;
    text-shadow: 1px 1px 2px black;

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
  }

  .row {
    display: flex;
    flex-direction: row;
  }

  .align-items-center {
    align-items: center;
  }

  .justify-content-center {
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

</style>
