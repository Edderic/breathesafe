import axios from 'axios';
import { defineStore } from 'pinia'
import { MASKS, Mask  } from '../masks.js'
import { hourToIndex, round } from '../misc.js'
import { airCleaners, AirCleaner } from '../air_cleaners.js'
import { UpperRoomGermicidalUV, UPPER_ROOM_GERMICIDAL_UV } from '../upper_room_germicidal_uv.js'
import { Intervention } from '../interventions.js'
import { useShowMeasurementSetStore } from './show_measurement_set_store';
import { useEventStores } from './event_stores';
import { getSampleInterventions } from '../sample_interventions.js'


// TODO: use the last location that the user was in, as the default
// the first argument is a unique id of the store across your application
export const useAnalyticsStore = defineStore('analytics', {
  state: () => ({
    wage: 15,
    numDaysOff: 5,
    numHoursPerDay: 8,
    interventions: [],
    workers: [
      // Takes 10 seconds on macbook pro
      // new Worker('worker.js'),
      // new Worker('worker.js'),
      // new Worker('worker.js'),
      // new Worker('worker.js'),
      // new Worker('worker.js'),
      // new Worker('worker.js'),
      // new Worker('worker.js'),
      // new Worker('worker.js'),
      // new Worker('worker.js'),
      // new Worker('worker.js'),
      // new Worker('worker.js'),
      // new Worker('worker.js'),
      // new Worker('worker.js'),
      // new Worker('worker.js'),
      // new Worker('worker.js'),
      // new Worker('worker.js'),
      // new Worker('worker.js'),
      // new Worker('worker.js'),
      // new Worker('worker.js'),
      // new Worker('worker.js'),
    ],
    numInfectors: 1,
    numSusceptibles: 30,
    numPeopleToInvestIn: 5,
    numPACs: 1,
    selectedIntervention: {
      computeCleanAirDeliveryRate() {
        return 0
      },
      computePortableAirCleanerACH() {
        return 0.01
      },
      computeVentilationACH() {
        return 0.01
      },
      computeUVACH() {
        return 0.01
      },
      computeEmissionRate() {
        return 0.01
      },
      computeVentilationDenominator() {
        return 0.01
      },
      computeSusceptibleMask() {
        return {
          'maskPenetrationFactor': 'None'
        }
      },
      computeRiskRounded() {
        return 0
      },
      computeACH() {
        return 0
      },
      ventilationDenominator() { return 0.01 },
      steadyStateCO2Reading() { return 0.01 },
      ambientCO2Reading() { return 0.01 },
      findPortableAirCleaners() {
        return {
          'amountText': function() { return 'None' },
          'numDevices': function() { return 0 },
          'numDeviceFactor': function() { return 0 },
          'singularName': function() { return '' },
          'isFiltrationAirCleaner': function() { return true },
          'initialCostText': function() { return '' },
          'recurringCostText': function() { return '' },
          'costInYears': function(x) { return 0 },
          'name': function() { return '' }
        }
      },
      findUVDevices() {
        return {
          'numDevices': function() { return 0 },
          'numDeviceFactor': function() { return 0 }
        }
      },
      implementationCostInYears() {
        return 0
      }
    },
    selectedInfectorMask: new Mask(MASKS[0], 1),
    selectedSusceptibleMask: new Mask(MASKS[0], 1),
    selectedAirCleanerObj: airCleaners[0],
    selectedHour: 1,
    event: {}
  }),
  getters: {
    numInfected() {
      return round(this.numSusceptibles * this.risk, 0) || 0
    },
    peopleCost() {
      return this.numInfected * this.wage * this.numDaysOff * this.numHoursPerDay
    },
    selectedAirCleaner() {
      return new AirCleaner(this.selectedAirCleanerObj, this.event, this.numPACs)
    },
    risk() {
      const duration = 1
      return (1 - (1-this.selectedIntervention.computeRiskRounded(duration, this.numInfectors))**this.selectedHour)
    },

    styleProps() {
      return {
          'font-weight': 'bold',
          'color': 'white',
          'text-shadow': '1px 1px 2px black',
          'padding': '1em'
        }
    },
  },
  actions: {
    async showAnalysis(id) {
      let eventStores = useEventStores()
      const showMeasurementSetStore = useShowMeasurementSetStore()
      let event = await eventStores.findOrLoad(id);
      this.event = event
      showMeasurementSetStore.setMeasurementSet(event)

      this.numSusceptibles = this.event.maximumOccupancy - this.numInfectors

      return event
    },
    computeLostWages() {
    },
    generateSchedule(workingDays, workingHours) {
      if (!workingHours) {
        workingHours = [
          '9 AM',
          '10 AM',
          '11 AM',
          '12 PM',
          '1 PM',
          '2 PM',
          '3 PM',
          '4 PM',
          '5 PM',
        ]

        workingDays = [
          'Mondays',
          'Tuesdays',
          "Wednesdays",
          "Thursdays",
          "Fridays",
        ]
      }

      let days = [
        'Sundays',
        'Mondays',
        'Tuesdays',
        "Wednesdays",
        "Thursdays",
        "Fridays",
        'Saturdays'
      ]

      let dict = {}

      for (let d of days) {
        dict[d] = {}

        for (let h in hourToIndex) {
          if (workingDays.indexOf(d) != -1 && workingHours.indexOf(h) != -1) {
            dict[d][h] = 1
          } else {
            dict[d][h] = 0
          }
        }
      }

      return dict
    },
    cost(interventions) {
      const environmentalInterventions = interventions.environmentalInterventions
      const mask1 = interventions.mask1
      const mask2 = interventions.mask2

      const numDaysInEpoch = 120
      const occupancy = this.event.occupancy.parsed
      const hourlyRate = 15.00
      let workingDays = [
        'Mondays',
        'Tuesdays',
        'Wednesdays',
        'Thursdays',
        'Fridays'
      ]

      let workingHours = [
        '9 AM',
        '10 AM',
        '11 AM',
        '12 PM',
        '1 PM',
        '2 PM',
        '3 PM',
        '4 PM'
      ]
      let schedule = this.generateSchedule(workingDays, workingHours)

      const numEmployees = 5

      const prevalence = 0.001

      let totalCost = 0
      // TODO: change the masks based on the selection
      let customerMask = interventions.mask1.mask
      let employeeMask = interventions.mask2.mask
      let costs = []

      let numSims = 5
      let total = []
      let processed = []

      for (let i = 0; i < this.workers.length; i++) {
        total.push(0)
        processed.push(0)
      }

      for (let i = 0; i < this.workers.length; i++) {
        this.workers[i].onmessage = (e) => {
          let dict1 = JSON.parse(e.data)
          processed[i] = 1

          for (let key in dict1) {
            total[i] += dict1[key]
          }

          // If all the workers have finished
          if (processed.reduce(
            (previousValue, currentValue) => previousValue + currentValue,
            0
          ) == this.workers.length) {
            let aveCost = total.reduce(
              (previousValue, currentValue) => previousValue + currentValue,
              0
            ) / (this.workers.length * numSims)

            console.log("aveCost", aveCost);

            return aveCost
          }
        }

        this.workers[i].postMessage(JSON.stringify({
          event: this.event,
          numSims: numSims,
          numEmployees: numEmployees,
          hourlyRate: hourlyRate,
          environmentalInterventions: environmentalInterventions,
          schedule: schedule,
          occupancy: occupancy,
          prevalence: prevalence,
          numDaysInEpoch: numDaysInEpoch,
          customerMask: customerMask,
          employeeMask: employeeMask
        }))
      }
    },
    setNumPeopleToInvestIn(num) {
      this.numPeopleToInvestIn = num
    },
    setNumSusceptibles(event) {
      this.numSusceptibles = parseInt(event.target.value)
      this.selectedSusceptibleMask = new Mask(this.selectedSusceptibleMask.mask, this.numSusceptibles)

      this.selectedIntervention = new Intervention(
          this.event,
          [this.selectedAirCleaner],
          this.selectedInfectorMask,
          this.selectedSusceptibleMask
      )
    },
    setNumInfectors(event) {
      this.numInfectors = parseInt(event.target.value)
    },
    setNumPACs(event) {
      this.numPACs = parseInt(event.target.value)

      this.selectedIntervention = new Intervention(
          this.event,
          [this.selectedAirCleaner],
          this.selectedInfectorMask,
          this.selectedSusceptibleMask
      )
    },
    selectSusceptibleMask(event) {
      let name = event.target.value
      // TODO: have some occupancy variable in the data that can be set to maximum occupancy as the default
      this.selectedSusceptibleMask = new Mask(
        MASKS.find((m) => m.name == name),
        this.numSusceptibles
      )

      this.selectedIntervention = new Intervention(
          this.event,
          [this.selectedAirCleaner],
          this.selectedInfectorMask,
          this.selectedSusceptibleMask
      )
    },
    selectInfectorMask(event) {
      let name = event.target.value
      this.selectedInfectorMask = new Mask(MASKS.find((m) => m.name == name), 1)
      this.selectedIntervention = new Intervention(
          this.event,
          [this.selectedAirCleaner],
          this.selectedInfectorMask,
          this.selectedSusceptibleMask
      )
    },
    selectAirCleaner(event) {
      let name = event.target.value
      this.selectedAirCleanerObj = airCleaners.find((m) => m.singular == name)
      this.selectedIntervention = new Intervention(
          this.event,
          [this.selectedAirCleaner],
          this.selectedInfectorMask,
          this.selectedSusceptibleMask
      )
    },
  }
});
