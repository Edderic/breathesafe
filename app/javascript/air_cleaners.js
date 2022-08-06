import { cubicFeetPerMinuteTocubicMetersPerHour, convertLengthBasedOnMeasurementType } from './misc.js'
import { convertVolume, computeAmountOfPortableAirCleanersThatCanFit } from './measurement_units.js';

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
    this.areaInSquareMeters = device.areaInSquareMeters
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
    let amountA = computeAmountOfPortableAirCleanersThatCanFit(
      this.event.roomLengthMeters * this.event.roomWidthMeters,
      this.areaInSquareMeters
    )

    // find the amount of portable ACH. Only recommend up to 100 more
    const remainingAch = 100 - this.event.portableAch

    let amountB = this.volumeOfRoomCubicMeters * remainingAch / this.cubicMetersPerHour

    let amountC = 100 - this.event.portableAirCleaners.length

    return Math.min(amountA, amountB, amountC)
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
