import { convertLengthBasedOnMeasurementType, round } from './misc.js'

export const UPPER_ROOM_GERMICIDAL_UV = [
  {
    'name': 'Upper Room Germicidal UV (Louvered)',
    'singular': 'Upper Room Germicidal UV (Louvered) Fixture',
    'plural': 'Upper Room Germicidal UV (Louvered) Fixtures',
    'initialCostUSD': 500,
    'recurringCostUSD': 50.00,
    'recurringCostDuration': 'year',
    'recurringCostDetails': 'to replace bulbs',
    'heightLowerBoundMeters': 2.4384,
    'mW': 600,
    'website': 'https://www.cdc.gov/coronavirus/2019-ncov/community/ventilation/uvgi.html',
    'type': 'Upper Room Germicidal UV',
  },
  {
    'name': 'Upper Room Germicidal UV (Open)',
    'singular': 'Upper Room Germicidal UV (Open) Fixture',
    'plural': 'Upper Room Germicidal UV (Open) Fixtures',
    'initialCostUSD': 500,
    'recurringCostUSD': 50.00,
    'recurringCostDuration': 'year',
    'recurringCostDetails': 'to replace bulbs',
    'heightLowerBoundMeters': 4.4384,
    'mW': 6250,
    'website': 'https://www.cdc.gov/coronavirus/2019-ncov/community/ventilation/uvgi.html',
    'type': 'Upper Room Germicidal UV',
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
  }

  applicable() {
    return this.event.roomHeightMeters >= this.device.heightLowerBoundMeters
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
    return `${round(this.initialCost(), 2)} for ${this.amountText()} `
  }

  numDevices() {
    if (!this.applicable()) {
      return 0
    }

    const val = this.event.roomLengthMeters * this.event.roomWidthMeters / convertLengthBasedOnMeasurementType(
      500,
      'feet',
      'meters'
    ) * 3

    return round(val, 0)
  }

  recurringCost() {
    return this.device.recurringCostUSD * this.numDevices()
  }

  recurringCostText() {
    return `${this.recurringCost()} every ${this.recurringCostDuration} ${this.recurringCostDetails}. `
  }

  website() {
    return this.ws
  }
}
