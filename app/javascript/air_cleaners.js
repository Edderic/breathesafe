import { cubicFeetPerMinuteTocubicMetersPerHour, convertLengthBasedOnMeasurementType } from './misc.js'
import { convertVolume, computeAmountOfPortableAirCleanersThatCanFit } from './measurement_units.js';

export const airCleaners = [
  {
    'type': 'airCleaner',
    'singular': 'Corsi-Rosenthal box (Max Speed)',
    'plural': 'Corsi-Rosenthal boxes (Max Speed)',
    'shortName': 'CR boxes',
    'cubicMetersPerHour': cubicFeetPerMinuteTocubicMetersPerHour('cubic feet per minute', 600),
    'areaInSquareMeters': convertLengthBasedOnMeasurementType(20, 'inches', 'meters')
        * convertLengthBasedOnMeasurementType(20, 'inches', 'meters'),
    'initialCostUSD': 65,
    'initialDurationYears': 0.5,  // 6 months to replace filters
    'recurringCostUSD': 50,
    'recurringCostDuration': '6 months',
    'recurringCostDetails': 'to replace filters',
    'recurringCostPerYearUSD': 100,
    'recurringDurationYears': 0.5,  // 6 months to replace filters
    'website': "https://aghealth.ucdavis.edu/news/corsi-rosenthal-box-diy-box-fan-air-filter-covid-19-and-wildfire-smoke",
    'imgLink': "https://www.texairfilters.com/wp-content/uploads/image-12.png"
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
    this.device = device
    this.shortName = this.device.shortName
  }

  applicable() {
    return true
  }

  amountText() {
    return `${this.numDevices()} ${this.shortName}`
  }

  computeACH() {
    const ach = this.numDevices() * this.cubicMetersPerHour / this.volumeOfRoomCubicMeters
    return ach
  }

  computeFiltrationAirCleanerACH() {
    return this.computeACH()
  }

  computeUVACH() {
    return 0
  }

  computeVentilationACH() {
    return 0
  }
  costInYears(years) {
    return this.numDevices() * (this.device.initialCostUSD + years * this.device.recurringCostPerYearUSD)
  }

  numDevices() {
    let amountA = computeAmountOfPortableAirCleanersThatCanFit(
      this.event.roomLengthMeters * this.event.roomWidthMeters,
      this.areaInSquareMeters
    ) - this.event.portableAirCleaners.length

    return amountA
  }

  initialCost() {
    return this.numDevices() * this.initCost
  }

  initialCostText() {
    return `${this.shortName}: $${this.initialCost()} `
  }

  isUpperUV() {
    return false
  }

  isMask() {
    return false
  }

  imgLink() {
    return this.device.imgLink
  }

  isFiltrationAirCleaner() {
    return true
  }
  recurringCost() {
    return this.numDevices() * this.recurringCostUSD
  }

  recurringCostText() {
    return `${this.shortName}: $${this.recurringCost()} / ${this.recurringCostDuration} ${this.recurringCostDetails}. `
  }

  singularName() {
    return this.device.singular;
  }

  website() {
    return this.ws
  }
}
