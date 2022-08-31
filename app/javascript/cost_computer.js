class RandomPerson {
  /*
   * Meant to be instantiated hourly to simulate random people coming into a
   * store, for example
   */
  constructor(risk) {
    this.risk = risk
  }

  isInfectious(dateIndex) {
    return Math.random() < this.risk
  }

  isAbsent(dateIndex, day, hourIndex) {
    return false
  }

  isNotPresent(dateIndex, day, hourIndex) {
    return false
  }

  lostWages() {
    return 0
  }
  updateAbsenceHoursCount(dateIndex, day, hourIndex) {
    // do nothing
  }
}

class Employee {
  /*
   * Parameters
   *   interventions:
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
  constructor(interventions, numDaysInEpoch, schedule, hourlyRate) {
    this.infectedCountDays = 0

    this.infectionList = []
    this.absenceList = []

    for (let i = 0; i < numDaysInEpoch; i++) {
      this.infectionList.push(0)
      this.absenceList.push(0)
    }

    this.numDaysInEpoch = numDaysInEpoch


    this.interventions = interventions
    this.workHoursPerDay = workHoursPerDay
    this.schedule = schedule

    this.absenceHoursCount = 0
    this.hasBeenInfected = 0
    this.cost = 0

    // how many days someone can be infectious
    this.maxInfectiousDays = 8
    this.numDaysAbsent = 5
    this.hourlyRate = hourlyRate

    this.risk = this.interventions.computeRisk(1)

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
    if (
      !this.isWorkingHours(day, hourIndex)
      || this.isAbsent(dateIndex, day, hourIndex)
    ) {
      return true
    }
  }

  isWorkingHours(day, hourIndex) {
    return !!this.schedule[day][hourIndex]
  }

  lostWages() {
    /*
     * Meant to be called after one simulation.
     */

    return this.absenceHoursCount * this.hourlyRate
  }

  sampleInfection(people, dateIndex, day, hourIndex) {
    // TODO: build in scenario where one can get sick?
    if (!this.hasBeenInfected && !this.isInfectious(dateIndex)
        &&!this.isNotPresent(dateIndex, day, hourIndex)) {

      for (let otherEmployee in people) {
        if (otherEmployee.isInfectious(dateIndex)
          && !otherEmployee.isNotPresent(dateIndex, day, hourIndex)
        ) {

          if (Math.random() < this.risk) {
            const latencyDays = 2
            const absenceStartDays = 4

            for (let i = latencyDays; i < this.maxInfectiousDays + latencyDays; i++) {
              try {
                this.infectionList[dateIndex + i] = 1
              } catch {
                return
                // do nothing. Handle the index out of bounds error.
              }
            }

            // Update absence list
            for (let i = absenceStartDays; i < absenceStartDays + this.numDaysAbsent; i++) {
              try {
                this.absenceList[dateIndex + i] = 1
              } catch {
                return
                // do nothing. Handle the index out of bounds error.
              }
            }
          }
        }
      }
    }
  }

  updateAbsenceHoursCount(dateIndex, day, hourIndex) {
    /*
     * If absent, update absence hours count by 1
     */
    if (this.isAbsent(dateIndex, day, hourIndex)) {
      this.absenceHoursCount += 1
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
  constructor(interventions, dayHourOccupancy, employees, prevalence, numDaysInEpoch, maxOccupancy) {
    this.employees = employees
    this.maxOccupancy = maxOccupancy
    this.interventions = interventions
    this.dayHourOccupancy = dayHourOccupancy
    this.prevalence = prevalence
    if (!numDaysInEpoch) {
      this.numDaysInEpoch = 120
    } else {
      this.numDaysInEpoch = numDaysInEpoch
    }

    this.hourlyRisk = this.interventions.computeRisk(1)
  }

  compute() {
    // Loop through time, day, dateIndex
    //   For each person present, see if there are any people infectious in the last hour.
    //   If so, sample to figure out if the person in question got infected.
    //
    for (let i = 0; i < this.numDaysInEpoch; i++) {
      let day = this.getDay(i)

      // loop through hours
      for (let h = 0; i < 24; i++) {
        let availablePeople = []

        // build the customer list
        const numberOfCustomers = getNumberOfCustomers(day, h)
        let customers = buildRandomCustomers(numberOfCustomers)

        for (let p = 0; p < this.employees.length; p++) {

          // combine customers and employees
          let otherPeople = this.getPeopleOtherThan(p).concat(customers)
          person.sampleInfection(otherPeople, i, day, h)

          person.updateAbsenceHoursCount(i, day, h)
        }
      }

    }
  }

  getNumberOfCustomers(day, hour) {
    /*
     * Use the occupancy data.
     *
     */
    let occupancy = this.dayHourOccupancy[day][hour] * maxOccupancy

    let workingEmployees = []

    for (let e in this.employees) {
      if (!e.isNotPresent()) {
        workingEmployees.push(e)
      }
    }

    return Math.ceil(occupancy - workingEmployees.length)
  }

  buildRandomCustomers(numberOfCustomers) {
    let customers = []

    for (let j = 0; j < numberOfCustomers; j++) {
      customers.push(new RandomPerson(this.hourlyRisk))
    }

    return customers
  }

  getPeopleOtherThan(otherEmployee) {
    let collection = []

    for (let p in this.people) {
      if (p != otherEmployee) {
        collection.push(p)
      }
    }

    return collection
  }

  getDay(dateIndex) {
    let dayIndex = dateIndex % 7
    return ["Sundays", "Mondays", "Tuesdays", "Wednesdays", "Thursdays", "Fridays", "Saturdays"][dayIndex]
  }
}
