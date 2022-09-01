import axios from 'axios';
import { defineStore } from 'pinia'
import { MASKS, Mask  } from '../masks.js'
import { hourToIndex } from '../misc.js'
import { airCleaners, AirCleaner } from '../air_cleaners.js'
import { UpperRoomGermicidalUV, UPPER_ROOM_GERMICIDAL_UV } from '../upper_room_germicidal_uv.js'
import { Intervention } from '../interventions.js'
import { useShowMeasurementSetStore } from './show_measurement_set_store';
import { getSampleInterventions } from '../sample_interventions.js'
import { CostComputer, Employee } from '../cost_computer.js'


// TODO: use the last location that the user was in, as the default
// the first argument is a unique id of the store across your application
export const useAnalyticsStore = defineStore('analytics', {
  state: () => ({
    nullIntervention: new Intervention({
      activityGroups: [],
      totalAch: 0.1
    }, []),
    interventions: [],
    selectedIntervention: new Intervention({
      activityGroups: [],
      totalAch: 0.1
    }, []),
    numPeopleToInvestIn: 5,
    event: "",
  }),
  actions: {
    load(event) {
      this.event = event
      this.reload()
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
    cost(environmentalInterventions) {
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

      let mask1 = new Mask(MASKS[3], 1)
      const numEmployees = 5

      const prevalence = 0.001

      let totalCost = 0
      let numExperiments = 100
      let customerMask = new Mask(MASKS[3], 1)
      let costs = []

      for (let i = 0; i< numExperiments; i++) {
        let employees = []

        for (let i = 0; i < numEmployees; i++) {
          employees.push(
            new Employee(
              mask1,
              numDaysInEpoch,
              schedule,
              hourlyRate
            )
          )
        }
        const computer = new CostComputer(
          this.event,
          environmentalInterventions,
          occupancy,
          employees,
          prevalence,
          numDaysInEpoch,
          customerMask
        )

        computer.compute()
        let lostWages = computer.getLostWages()
        costs.push(lostWages)
        totalCost += lostWages
      }

      let aveCost = totalCost / numExperiments

      console.log("aveCost", aveCost);
      console.log("costs", costs);

      return aveCost
    },
    selectIntervention(id) {
      let intervention = this.interventions.find((interv) => { return interv.id == id })
      this.selectedIntervention = intervention
      for (let interv of this.interventions) {
        if (intervention.id == interv.id) {
          interv.select()
        } else {
          interv.unselect()
        }
      }
      console.log("this.cost(intervention)", this.cost(intervention.environmentalInterventions));
    },
    setNumPeopleToInvestIn(num) {
      this.numPeopleToInvestIn = num
    },
    reload() {
      this.nullIntervention = new Intervention(this.event, [])

      // TODO: find the number of people that could upgrade to a mask
      let interventions = getSampleInterventions(this.event, this.numPeopleToInvestIn)

      this.interventions = interventions.sort(
          function(a, b) {
            return (
              (b.numEventsToInfectionWithCertainty()) / b.costInYears(10) -
              (a.numEventsToInfectionWithCertainty()) / a.costInYears(10)
            )
          }.bind(this)
      )
    }
  }
});
