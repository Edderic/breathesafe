import { cubicFeetPerMinuteTocubicMetersPerHour, convertLengthBasedOnMeasurementType } from './misc.js'
import { convertVolume, computeAmountOfPortableAirCleanersThatCanFit } from './measurement_units.js';

export const airCleaners = [
  {
    'type': 'airCleaner',
    'singular': 'None',
    'plural': 'None',
    'shortName': 'None',
    'cubicMetersPerHour': cubicFeetPerMinuteTocubicMetersPerHour('cubic feet per minute', 0),
    'areaInSquareMeters': convertLengthBasedOnMeasurementType(20, 'inches', 'meters')
        * convertLengthBasedOnMeasurementType(20, 'inches', 'meters'),
    'initialCostUSD': 0,
    'initialDurationYears': 0,  // 6 months to replace filters
    'recurringCostUSD': 0,
    'recurringCostDuration': '6 months',
    'recurringCostDetails': 'to replace filters',
    'recurringCostPerYearUSD': 0,
    'recurringDurationYears': 0,  // 6 months to replace filters
    'website': "",
    'imgLink': "https://t3.ftcdn.net/jpg/02/15/15/46/360_F_215154625_hJg9QkfWH9Cu6LCTUc8TiuV6jQSI0C5X.jpg"
  },
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
    'website': "https://cleanaircrew.org/box-fan-filters/",
    'imgLink': "https://www.texairfilters.com/wp-content/uploads/image-12.png"
  }
]

export class AirCleaner {
  constructor(device, event, amount) {
    this.amount = amount
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
    return this.numDevices() * (this.device.initialCostUSD + years * this.device.recurringCostUSD)
  }

  name() {
    return this.singular
  }
  numDevices() {
    return this.amount
  }

  initialCost() {
    return this.numDevices() * this.initCost
  }

  initialCostText() {
    return `$${this.initialCost()} `
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
    return `$${this.device.recurringCostUSD * this.numDevices()} ${this.recurringCostDetails}. `
  }

  singularName() {
    return this.device.singular;
  }

  website() {
    return this.ws
  }
}
