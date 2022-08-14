import { convertLengthBasedOnMeasurementType, round } from './misc.js'

export const UPPER_ROOM_GERMICIDAL_UV = [
  {
    'name': 'Upper Room Germicidal UV (600mW, Louvered)',
    'singular': 'Upper Room Germicidal UV Fixture (600mW, Louvered)',
    'plural': 'Upper Room Germicidal UV Fixtures (600mW, Louvered)',
    'shortName': 'Upper Room UV (600mW)',
    'initialCostUSD': 500,
    'initialDurationYears': 1,
    'recurringCostUSD': 50.00,
    'recurringCostDuration': 'year',
    'recurringCostDetails': 'to replace bulbs',
    'recurringCostPerYearUSD': 50,
    'recurringDurationYears': 1,
    'heightLowerBoundMeters': 2.4384,
    'numDeviceFactor': 1,
    'mW': 600,
    'website': 'https://www.cdc.gov/coronavirus/2019-ncov/community/ventilation/uvgi.html',
    'type': 'Upper Room Germicidal UV',
    'imgLink': 'https://uvresources.com/wp-content/uploads/2020/06/UVR-GLO150-Hero-Side-Angle-1.jpg'
  },
  {
    'name': 'Upper Room Germicidal UV (600mW, Louvered)',
    'singular': 'Upper Room Germicidal UV Fixture (600mW, Louvered)',
    'plural': 'Upper Room Germicidal UV Fixtures (600mW, Louvered)',
    'shortName': 'Upper Room UV (600mW)',
    'initialCostUSD': 500,
    'initialDurationYears': 1,
    'recurringCostUSD': 50.00,
    'recurringCostDuration': 'year',
    'recurringCostDetails': 'to replace bulbs',
    'recurringDurationYears': 1,
    'recurringCostPerYearUSD': 50,
    'heightLowerBoundMeters': 2.4384,
    'numDeviceFactor': 3,
    'mW': 600,
    'website': 'https://www.cdc.gov/coronavirus/2019-ncov/community/ventilation/uvgi.html',
    'type': 'Upper Room Germicidal UV',
    'imgLink': 'https://uvresources.com/wp-content/uploads/2020/06/UVR-GLO150-Hero-Side-Angle-1.jpg'
  },
  {
    'name': 'Upper Room Germicidal UV (6.25W, Open)',
    'singular': 'Upper Room Germicidal UV Fixture (6.25W, Open)',
    'plural': 'Upper Room Germicidal UV Fixtures (6.25W, Open)',
    'shortName': 'Upper Room UV (6.25W)',
    'initialCostUSD': 500,
    'initialDurationYears': 1,
    'recurringCostUSD': 50.00,
    'recurringCostPerYearUSD': 50.00,
    'recurringCostDuration': 'year',
    'recurringCostDetails': 'to replace bulbs',
    'recurringDurationYears': 1,
    'heightLowerBoundMeters': 4.4384,
    'numDeviceFactor': 1.5,
    'mW': 6250,
    'website': 'https://www.cdc.gov/coronavirus/2019-ncov/community/ventilation/uvgi.html',
    'type': 'Upper Room Germicidal UV',
    'imgLink': 'https://www.esmagazine.com/ext/resources/2022/02/17/UV-Resources-GLO-2900-OF-UR-UVC-Fixture_angle-04-1-scaled.jpg?1645111471'
  },
]

export class UpperRoomGermicidalUV {
  constructor(device, event) {
    this.device = device
    this.singular = device.singular
    this.plural = device.plural
    this.mW = this.device.mW
    this.event = event
    this.volumeOfRoomCubicMeters = event.roomUsableVolumeCubicMeters
    this.initialCostUSD = device.initialCostUSD
    this.recurringCostUSD = device.recurringCostUSD
    this.recurringCostDetails = device.recurringCostDetails
    this.ws = device.website
    this.shortName = device.shortName
  }

  applicable() {
    return (this.event.roomHeightMeters >= this.device.heightLowerBoundMeters)
  }

  costInYears(years) {
    return this.numDevices() * (this.device.initialCostUSD + years * this.device.recurringCostPerYearUSD)
  }

  computeVentilationACH() {
    return 0
  }

  computeFiltrationAirCleanerACH() {
    return 0
  }

  computeUVACH() {
    return this.computeACH()
  }

  isUpperUV() {
    return true
  }

  isMask() {
    return false
  }

  isFiltrationAirCleaner() {
    return false
  }

  amountText() {
    return `${this.numDevices()} ${this.plural}`
  }

  computeACH() {
    return 2 * this.numDevices() * this.mW / this.volumeOfRoomCubicMeters
  }

  initialCost() {
    return this.device.initialCostUSD * this.numDevices()
  }

  initialCostText() {
    return `${this.shortName}: $${round(this.initialCost(), 2)} `
  }

  imgLink() {
    return this.device.imgLink
  }

  numDevices() {
    if (!this.applicable()) {
      return 0
    }

    let once = convertLengthBasedOnMeasurementType(
      500,
      'feet',
      'meters'
    )
    const val = this.event.roomLengthMeters * this.event.roomWidthMeters /
      convertLengthBasedOnMeasurementType(
        once,
        'feet',
        'meters'
      ) * this.device.numDeviceFactor

    return round(val, 0)
  }

  numDeviceFactor() {
    return this.device.numDeviceFactor
  }

  recurringCost() {
    return this.device.recurringCostUSD * this.numDevices()
  }

  recurringCostText() {
    return `${this.shortName}: $${this.recurringCost()} every ${this.device.recurringCostDuration} ${this.device.recurringCostDetails}. `
  }

  website() {
    return this.ws
  }
}
