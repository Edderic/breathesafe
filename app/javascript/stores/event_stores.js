import { defineStore } from 'pinia'
import { Intervention } from '../interventions.js';
import { Mask, MASKS } from '../masks.js'
import { useMainStore } from './main_store'
import { useProfileStore } from './profile_store'
import { usePrevalenceStore } from './prevalence_store'
import axios from 'axios'
import { computeRiskWithVariableOccupancy, deepSnakeToCamel, setupCSRF, round, filterEvents } from  '../misc'


// useStore could be anything like useUser, useCart
// the first argument is a unique id of the store across your application
export const useEventStores = defineStore('events', {
  state: () => ({
    location: { lat: 0, lng: 0},
    displayables: [],
    durationHours: 1,
    events: [],
    masks: [],
    selectedMask: new Mask(MASKS[0], 1, 1),
    display: 'map',
    filterForDraft: false,
    placeTypePicked: '',
    placeTypeCounts: {},
    search: '',
    sort: '',
    sortHow: ''
  }),
  getters: {

  },
  actions: {
    setDraft(val) {
      this.filterForDraft = val
    },
    setDisplayables() {
      let collection = []
      if (!this.search) {
        this.search = ''
      }
      const lowercasedSearch = this.search.toLowerCase()

      for (let event of this.events) {

        // If a private reading
        // ... placeData.types would be an empty object
        if (event.placeData.types.length == 0) {
          // add for now
          collection.push(event)
        } else {
          for (let placeType of event.placeData.types) {
            if (
              (this.filterForDraft && event.status == 'draft' || !this.filterForDraft) &&
              (!lowercasedSearch || event.roomName.toLowerCase().match(lowercasedSearch) )
              && ((placeType == this.placeTypePicked) || !this.placeTypePicked)
            ) {
              collection.push(event)
              break
            }
          }
        }
      }

      if (this.sort == 'risk-infector' && this.sortHow == 'ascending') {
        collection.sort((a, b) => a.risk - b.risk)
      } else if (this.sort == 'risk-infector' && this.sortHow == 'descending') {
        collection.sort((a, b) => b.risk - a.risk)
      } else if (this.sort == 'distance' && this.sortHow == 'ascending') {
        collection.sort((a, b) => a.distance - b.distance)
      } else if (this.sort == 'distance' && this.sortHow == 'descending') {
        collection.sort((a, b) => b.distance - a.distance)
      }

      this.displayables = collection
    },
    updateSearch(event) {
      this.search = event.target.value
    },
    pickPlaceType(placeType) {
      this.placeTypePicked = placeType
    },
    countPlaceTypes(data) {
      this.placeTypeCounts = {}

      for (let d of data) {
        let countable = false

        if (!d.placeData || !d.placeData.types) {
          continue

        }

        for (let placeType of d.placeData.types) {
          if (!this.placeTypeCounts[placeType]) {
             this.placeTypeCounts[placeType] = 0
          }

          this.placeTypeCounts[placeType] += 1

          break
        }
      }
    },
    setDisplay(arg) {
      if (this.display == arg) {
        this.display = 'map'
      } else {
        this.display = arg
      }
    },
    addEvent(event) {
      let camelized = deepSnakeToCamel([event])
      const mainStore = useMainStore()

      this.setDistance(mainStore, camelized)
      this.events.push(camelized[0])
      this.displayables = this.events
    },
    setDistance(mainStore, events) {
      let milesPerEuclidean = 0.8 / 0.012414

      for (let event of events) {
        let x = (mainStore.whereabouts.lat - event.placeData.center.lat)**2
        let y = (mainStore.whereabouts.lng - event.placeData.center.lng)**2

        event.distance = round(Math.sqrt(x + y) * milesPerEuclidean, 1)
      }
    },
    loadMasks() {
      // Load masks
      let masks = []
      for (let mask of MASKS) {
        masks.push(new Mask(mask, 1, 1))
        masks.push(new Mask(mask, 1, 2))
      }

      this.masks = masks
    },
    async load() {
      setupCSRF()

      const mainStore = useMainStore()
      const profileStore = useProfileStore()

      await profileStore.loadProfile()
      let success = true

      await axios.get('/events')
        .then(response => {
          console.log(response)
          if (response.status == 200) {
            let camelized = deepSnakeToCamel(response.data.events)
            this.countPlaceTypes(camelized)
            this.setDistance(mainStore, camelized)
            this.events = camelized
            this.setDisplayables()
          }

          // whatever you want
        })
        .catch(error => {
          console.log(error)
          success = false
          // whatever you want
        })

      this.loadMasks()
    },

    async findOrLoad(id) {
      // TODO: maybe create a Rails route to find a specific analytics to load?
      await this.load()
      const mainStore = useMainStore()



      let event = this.events.find((ev) => { return ev.id == parseInt(id) })

      return event
    },

    susceptibleMask(selectedMask) {
      if (selectedMask.numWays == 2) {
        return new Mask(selectedMask.mask, 1)
      } else {
        return new Mask(MASKS[0], 1)
      }
    },
    infectorMask(selectedMask) {
      return new Mask(selectedMask.mask, 1)
    },
    computeRiskAll(selectedMask) {
      /*
       * Parameters:
       *
       *   selectedMask: Mask object
       *
       */

      // numWays: Number
      //   Whether or not the mask is applied one way or both ways.
      //   1 is for 1-way masking
      //   2 is for 2-way masking.
      //     i.e. Assumes everyone will be wearing the selectedMask
      let numWays = 1;
      if (selectedMask) {
        numWays = selectedMask.numWays
      }
      else {
        numWays = 1
      }

      // TODO: make this a query parameter using router

      for (let event of this.events) {
        let intervention = new Intervention(
          event,
          [
          ],
          this.infectorMask(selectedMask),
          this.susceptibleMask(selectedMask),
          1,
          1
        )

        if (intervention.status == 'complete') {
          event['risk'] = intervention.computeRisk(this.durationHours)
        }
      }
    },
  }
});
