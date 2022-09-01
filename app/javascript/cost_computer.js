import { DAYS, indexToHour, hourToIndex } from './misc.js'
import { Intervention } from './interventions.js'
import { Mask, MASKS } from './masks.js'

export class Employee {
  /*
   * Parameters
   *   mask:
   *     If mask, then at the compute risk stage, check to see if they have a
   *     When assessing the risk of getting infected for a particular employee,
   *       - From random people (e.g. customers),
   *         - check to see what mask they have
   *       - Check to see what mask this employee is wearing
   *
   *     Could also use the computeRiskWithVariableOccupancy?
   *
   *     has methods
   *       - computeRisk(duration)
   *
   *   numDaysInEpoch: Number
   *     The amount of days we're keeping track. In one epoch, a person can
   *     only have 1 infectious period. After that, they are considered immune
   *     for the rest of the epoch. This is to take into account prior immunity
   *     through illness.
   *
   *   schedule: Object
   *     Schedule that has days and hours.
   *
   *     e.g.
   *     {
   *       "Sundays": { 0: 0, 1: 1, ...},
   *       "Mondays": {0: 0, 1: 0, ...},
   *       ...
   *     }
   *
   *     Something we can query e.g. schedule[day][hourIndex]. Value is
   *     boolean. If 1, it is a person's working hours.
   *
   *   hourlyRate: Number
   */
  constructor(mask, numDaysInEpoch, schedule, hourlyRate) {
    this.infectedCountDays = 0

    this.infectionList = []
    this.absenceList = []

    for (let i = 0; i < numDaysInEpoch; i++) {
      this.infectionList.push(0)
      this.absenceList.push(0)
    }

    this.numDaysInEpoch = numDaysInEpoch


    this.mask = mask
    this.schedule = schedule

    this.absenceHoursCount = 0
    this.hasBeenInfected = 0
    this.cost = 0

    // how many days someone can be infectious
    this.maxInfectiousDays = 8
    this.numDaysAbsent = 5
    this.hourlyRate = hourlyRate

  }

  isInfectious(dateIndex) {
    try {
      return !!this.infectionList[dateIndex]
    } catch {
      return false
    }
  }

  isAbsent(dateIndex, day, hourIndex) {
    if (!this.isWorkingHours(day, hourIndex)) {
      return false
    }

    return !!this.absenceList[dateIndex]
  }

  isNotPresent(dateIndex, day, hourIndex) {
    /*
     *
     * Assumptions:
     *  A person once infected, will be 10 days infectious
     *  An individual, on the 3rd day of being infectious, takes leave
     *
     *  Individual
     *  days              0  1  2  3  4  5  6  7  8  9  10 11 12 13
     *  infectious        X  X  I  I  I  I  I  I  I  X  X  X  X  X
     *  absent            N  N  N  N  A  A  A  A  A  N  N  N  N  N
     */
    return !this.isWorkingHours(day, hourIndex)
      || this.isAbsent(dateIndex, day, hourIndex)
  }

  isWorkingHours(day, hourIndex) {
    return !!this.schedule[day][hourIndex]
  }

  lostWages() {
    /*
     * Meant to be called after one simulation.
     */

    let hours = 0

    for (let i = 0; i < this.absenceList.length; i++) {
      if (this.absenceList[i] == 0) {
        continue
      }

      let day = DAYS[i % 7]

      for (let hour in this.schedule[day]) {
        hours += this.schedule[day][hour]
      }
    }

    return hours * this.hourlyRate
  }

  sampleInfection(
    dateIndex,
    day,
    hourIndex,
    infectorPresence,
    infectorMask,
    environmentalInterventions,
    event
  ) {
    /*
     * If none of the employees are exposed
     */
    // TODO: build in scenario where one can get sick?
    if (this.hasBeenInfected || this.isInfectious(dateIndex)
        ||this.isNotPresent(dateIndex, day, hourIndex))
    {
      return
    }

    let risk = new Intervention(
      event, environmentalInterventions, this.mask, infectorMask
    ).computeRisk(1)

    if (Math.random() < risk) {
      // They'll be infectious 2 days from now until some date
      const latencyDays = 2
      const absenceStartDays = 4

      for (let i = latencyDays; i < this.maxInfectiousDays + latencyDays; i++) {
        try {
          this.infectionList[dateIndex + i] = 1
        } catch {
          // do nothing. Handle the index out of bounds error.
        }
      }

      // They'll be absent 4 days from now until some date
      for (let i = absenceStartDays; i < absenceStartDays + this.numDaysAbsent; i++) {
        try {
          this.absenceList[dateIndex + i] = 1
        } catch {
          // do nothing. Handle the index out of bounds error.
        }
      }

      this.hasBeenInfected = 1
    }
  }

}

export class CostComputer {
  /*
   * Assumptions:
   *   Each event is one hour long.
   *   Employees can infect other employees.
   *   Employees can be infected through customers
   *
   *   An individual can only get infected once in an epoch.
   *   An individual is with colleagues for 8 hours a day.
   *
   * Parameters:
   *   dayHourOccupancy: Object
   *     e.g. {
   *       "Sundays": { 0: 0.11, 1: 0.2, 2: 1, ...},
   *       "Mondays": { 0: 0.22, 1: 0.6, 2: 0.65, ...},
   *     }
   *   employees: Array[Object]
   *
   */
  constructor(
    event,
    interventions,
    dayHourOccupancy,
    employees,
    prevalence,
    numDaysInEpoch,
    customerMask
  ) {
    this.event = event
    this.employees = employees
    this.maxOccupancy = event.maximumOccupancy
    this.interventions = interventions
    this.dayHourOccupancy = dayHourOccupancy
    this.prevalence = prevalence
    this.customerMask = customerMask
    if (!numDaysInEpoch) {
      this.numDaysInEpoch = 120
    } else {
      this.numDaysInEpoch = numDaysInEpoch
    }

  }

  compute() {
    // Loop through time, day, dateIndex
    //   For each person present, see if there are any people infectious in the last hour.
    //   If so, sample to figure out if the person in question got infected.
    //
    for (let i = 0; i < this.numDaysInEpoch; i++) {
      let day = this.getDay(i)

      // TODO: Trigger infection event outside of work.
      // Employees can also get infected outside of work.

      // loop through hours
      for (let h in hourToIndex) {
        // TODO: given the number of people here, we can compute the
        // probability that someone is infectious at this hour
        // build the customer list
        const numCustomers = this.getNumberOfCustomers(i, day, h)
        // Why not just compute P(transmission | duration=1h, numCustomers)

        // If we have the number of people we can compute

        let probaCustomerIsInfectious = this.getProbabilityThatSomeoneIsInfectious(
          numCustomers
        )

        for (let p of this.employees) {
          // employees could get exposed to infectious customers
          p.sampleInfection(
            i,
            day,
            h,
            probaCustomerIsInfectious,
            this.customerMask,
            this.interventions,
            this.event
          )

          if (p.isInfectious(i) && !p.isNotPresent(i, day, h)) {

            for (let j of this.employees) {
              j.sampleInfection(
                i,
                day,
                h,
                1, // probability that other employee is infectious
                p.mask,
                this.interventions,
                this.event
              )

            }
          }
        }
      }
    }
  }

  buildCustomers(numCustomers) {
    let list = []
    for (let i = 0; i < numCustomers; i++) {
      list.push()
    }
  }

  getLostWages() {
    let summation = 0
    for (let p of this.employees) {
      summation += p.lostWages()
    }

    return summation
  }

  getProbabilityThatSomeoneIsInfectious(numberOfPeople) {
    return 1 - (1 - this.prevalence)**numberOfPeople
  }

  getNumberOfCustomers(dateIndex, day, hour) {
    /*
     * Use the occupancy data.
     *
     */
    let occ = 0
    if (
      day in this.dayHourOccupancy
      && hour in this.dayHourOccupancy[day]
      && 'occupancyPercent' in this.dayHourOccupancy[day][hour]
    ) {

     occ = parseFloat(this.dayHourOccupancy[day][hour]['occupancyPercent']) / 100
    }

    let occupancy = occ * this.maxOccupancy

    let workingEmployees = []

    for (let e of this.employees) {
      if (!e.isNotPresent(dateIndex, day, hour)) {
        workingEmployees.push(e)
      }
    }

    return Math.max(Math.ceil(occupancy - workingEmployees.length), 0)
  }

  getDay(dateIndex) {
    let dayIndex = dateIndex % 7
    return ["Sundays", "Mondays", "Tuesdays", "Wednesdays", "Thursdays", "Fridays", "Saturdays"][dayIndex]
  }
}
