import axios from 'axios';
import { defineStore } from 'pinia'
import { MASKS, Mask  } from '../masks.js'
import { generateUUID, hourToIndex, round } from '../misc.js'
import { airCleaners, AirCleaner } from '../air_cleaners.js'
import { UpperRoomGermicidalUV, UPPER_ROOM_GERMICIDAL_UV } from '../upper_room_germicidal_uv.js'
import { Intervention } from '../interventions.js'
import { useShowMeasurementSetStore } from './show_measurement_set_store';
import { useEventStores } from './event_stores';
import { getSampleInterventions } from '../sample_interventions.js'
import { ProbaInfectious } from '../proba_infectious.js';


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
    defaultNumSusceptibles: 30,
    numPeopleToInvestIn: 5,
    numPACs: 1,
    possibleInfectorGroups: [
      // for Rapid tests:
      // https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8863328/ uses 100% for specificity
      //
      // https://covid19-sciencetable.ca/sciencebrief/use-of-rapid-antigen-tests-during-the-omicron-wave/#:~:text=In%20light%20of%20the%20results,and%20a%20specificity%20of%2099.5%25.
      // says 99.5% for specificity, 60% for sensitivity
      //
      // https://www.bmj.com/content/378/bmj-2022-071215 says only 97% for specificity, 80% for FlowFlex
      {
        numPeople: 1,
        identifier: generateUUID(),
        evidence: [
          {
            name: 'PCR',
            result: '?',
            sensitivity: 0.95,
            specificity: 0.999,
          },
          // https://www.bmj.com/content/378/bmj-2022-071215
          {
            name: 'Rapid Test',
            result: '?',
            sensitivity: 0.80,
            specificity: 0.998,
          },
          {
            name: 'Has Symptoms',
            result: '?',
            sensitivity: 0.75,
            specificity: 0.95,
          },
        ]
      }
    ],

    priorProbabilityOfInfectiousness: 0.01,
    selectedInfMask: MASKS[0],
    selectedSuscMask: MASKS[0],
    selectedAirCleanerObj: airCleaners[0],
    selectedHour: 1,
    selectedInterventionType: 'Prevalence',
    event: {
      activityGroups: [],
      totalAch: 0.1,
      roomUsableVolumeCubicMeters: 1
    }
  }),
  getters: {
    numSusceptibles() {
      let count = 0

      for (let possibleInfectorGroup of this.possibleInfectorGroups) {
        count += parseInt(possibleInfectorGroup.numPeople)
      }

      return count - 1
    },
    probabilityOneInfectorIsPresent() {
      let values = []
      let calculator = new ProbaInfectious(this.priorProbabilityOfInfectiousness)

      let product = 1

      for (let possibleInfectorGroup of this.possibleInfectorGroups) {
        product *= (1 - calculator.compute(possibleInfectorGroup.evidence)) ** possibleInfectorGroup.numPeople
      }
      return 1 - product
    },
    nullIntervention() {
      return new Intervention(
          this.event,
          [],
          new Mask(MASKS[0], 1),
          new Mask(MASKS[0], this.numSusceptibles),
      )
    },
    selectedSusceptibleMask() {
      return new Mask(this.selectedSuscMask, this.numSusceptibles)
    },
    selectedInfectorMask() {
      return new Mask(this.selectedInfMask, this.numInfectors)
    },
    selectedIntervention() {
      return new Intervention(
          this.event,
          [this.selectedAirCleaner],
          this.selectedInfectorMask,
          this.selectedSusceptibleMask,
          this.numInfectors,
          this.numSusceptibles
      )
    },
    implementationCost() {
      return round(this.selectedIntervention.implementationCostInYears(1), -2)
    },
    implementationCostText() {
      return `$${this.implementationCost}`
    },
    numInfected() {
      return round(this.numSusceptibles * this.risk, 2) || 0
    },
    peopleCost() {
      return round(this.numInfected * this.wage * this.numDaysOff * this.numHoursPerDay, 2)
    },
    averageNumTimesAnInfectorShowsUpPerYear() {
      return 4
    },
    yearlyPeopleCost() {
      return round(
        this.averageNumTimesAnInfectorShowsUpPerYear
        * this.numInfected
        * this.wage
        * this.numDaysOff
        * this.numHoursPerDay, -2)
    },
    peopleCostText() { return `$${this.peopleCost}` },
    yearlyPeopleCostText() { return `$${this.yearlyPeopleCost}` },
    totalCost() {
      return round(
        this.selectedIntervention.implementationCostInYears(1)
        + this.yearlyPeopleCost,
        -2
      )
    },
    totalCostText() {
      return `$${this.totalCost}`
    },
    selectedAirCleaner() {
      return new AirCleaner(this.selectedAirCleanerObj, this.event, this.numPACs)
    },
    risk() {
      return this.selectedIntervention.computeRiskRounded(this.selectedHour, this.numInfectors) * this.probabilityOneInfectorIsPresent
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
    addPossibleInfectorGroup() {
      this.possibleInfectorGroups.push(
        {
          numPeople: 1,
          identifier: generateUUID(),
          evidence: [
            {
              name: 'PCR',
              result: '?',
              sensitivity: 0.95,
              specificity: 0.999,
            },
            {
              name: 'Rapid',
              result: '?',
              sensitivity: 0.8,
              specificity: 0.999,
            },
            {
              name: 'Symptoms',
              result: '?',
              sensitivity: 0.75,
              specificity: 0.95,
            },
          ]
        }
      )
    },
    setInfectorGroups(query) {
      //
      for (const [key, value] of Object.entries(query)) {
        let split = key.split('-')
        if (split.length == 2) {
          let index = parseInt(split[1])

          while (index + 1 > this.possibleInfectorGroups.length) {
            this.addPossibleInfectorGroup()
          }

          if (split[0] == 'numPeople') {
            this.possibleInfectorGroups[index][split[0]] = value
          } else {
            let evidence = this.possibleInfectorGroups[index].evidence.find(
              (e) => {return e.name == split[0]}
            )
            evidence['result'] = value

          }
        }
      }
    },
    removePossibleInfectorGroup(identifier) {
      for (let i = 0; i < this.possibleInfectorGroups.length; i++) {
        if (this.possibleInfectorGroups[i].identifier == identifier) {
          this.possibleInfectorGroups.splice(i, 1)
          break
        }
      }
    },
    async showAnalysis(id) {
      let eventStores = useEventStores()
      const showMeasurementSetStore = useShowMeasurementSetStore()
      let event = await eventStores.findOrLoad(id);
      this.event = event
      showMeasurementSetStore.setMeasurementSet(event)

      this.defaultNumSusceptibles = this.event.maximumOccupancy - this.numInfectors

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
    selectInterventionType(str) {
      this.selectedInterventionType = str
    },
    setNumPeopleToInvestIn(num) {
      this.numPeopleToInvestIn = num
    },
    setNumSusceptibles(value) {
      this.numSusceptibles = parseInt(value) || this.defaultNumSusceptibles
    },
    setNumInfectors(value) {
      this.numInfectors = parseInt(value) || 1
    },
    setNumPACs(value) {
      this.numPACs = parseInt(value) || 1
    },
    selectSusceptibleMask(name) {
      // TODO: have some occupancy variable in the data that can be set to maximum occupancy as the default
      if (!name) {
        this.selectedSuscMask = MASKS[0]
      } else {
        this.selectedSuscMask = MASKS.find((m) => m.name == name)
      }
    },
    selectInfectorMask(name) {
      if (!name) {
        this.selectedInfMask = MASKS[0]
      } else {
        this.selectedInfMask = MASKS.find((m) => m.name == name)
      }
    },
    setDuration(hour) {
      if (!hour) {
        this.selectedHour = 1
      } else {
        this.selectedHour = parseFloat(hour)
      }
    },
    selectAirCleaner(name) {
      if (!name) {
        this.selectedAirCleanerObj = airCleaners[0]
      } else {
        this.selectedAirCleanerObj = airCleaners.find((m) => m.singular == name)
      }
    },
  }
});
