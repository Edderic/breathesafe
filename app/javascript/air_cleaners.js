import { cubicFeetPerMinuteTocubicMetersPerHour, convertLengthBasedOnMeasurementType } from './misc.js'

export const airCleaners = [
  {
    'type': 'airCleaner',
    'singular': 'Corsi-Rosenthal box',
    'plural': 'Corsi-Rosenthal boxes',
    'cubicMetersPerHour': cubicFeetPerMinuteTocubicMetersPerHour('cubic feet per minute', 600),
    'areaInSquareMeters': convertLengthBasedOnMeasurementType(20, 'inches', 'meters')
        * convertLengthBasedOnMeasurementType(20, 'inches', 'meters'),
    'initialCostUSD': 65,
    'recurringCostUSD': 50,
    'recurringCostDuration': '6 months',
    'recurringCostDetails': 'to replace filters',
    'website': "https://aghealth.ucdavis.edu/news/corsi-rosenthal-box-diy-box-fan-air-filter-covid-19-and-wildfire-smoke"
  }
]

export class AirCleaner {
  constructor(device, event) {
    this.event = event
    this.initCost = device.initialCostUSD
    this.cubicMetersPerHour = device.cubicMetersPerHour
    this.volumeOfRoomCubicMeters = event.roomUsableVolumeCubicMeters
    this.singular = device.singular
    this.plural = device.plural
    this.recurringCostUSD = device.recurringCostUSD
    this.recurringCostDuration = device.recurringCostDuration
    this.recurringCostDetails = device.recurringCostDetails
    this.ws = device.website
  }

  applicable() {
    return true
  }

  amountText() {
    return `${this.numFixtures()} ${this.plural}`
  }

  computeACH() {
    const ach = this.numFixtures() * this.cubicMetersPerHour / this.volumeOfRoomCubicMeters
    return ach
  }

  numFixtures() {
    return 2
  }

  initialCost() {
    return this.numFixtures() * this.initCost
  }

  initialCostText() {
    return `${this.initialCost()} for ${this.amountText()} `
  }

  isUpperUV() {
    return false
  }

  isMask() {
    return false
  }

  isFiltrationAirCleaner() {
    return true
  }
  recurringCost() {
    return this.numFixtures() * this.recurringCostUSD
  }

  recurringCostText() {
    return `${this.recurringCost()} every ${this.recurringCostDuration} ${this.recurringCostDetails}. `
  }

  website() {
    return this.ws
  }
}
