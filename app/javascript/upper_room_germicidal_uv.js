export const UPPER_ROOM_GERMICIDAL_UV = [
  {
    'name': 'Upper Room Germicidal UV (Louvered)',
    'singular': 'Upper Room Germicidal UV (Louvered) Fixture',
    'plural': 'Upper Room Germicidal UV (Louvered) Fixtures',
    'initialCostUSD': 1500,
    'recurringCostUSD': 50.00,
    'recurringCostDuration': 'year',
    'recurringCostDetails': 'to replace bulbs',
    'heightLowerBoundMeters': 2.4384,
    'mW': 600,
    'website': 'https://www.cdc.gov/coronavirus/2019-ncov/community/ventilation/uvgi.html',
    'type': 'Upper Room Germicidal UV',
  },
]

export class UpperRoomGermicidalUV {
  constructor(device, heightOfRoomMeters, volumeOfRoomCubicMeters) {
    this.heightOfRoomMeters = heightOfRoomMeters
    this.device = device
    this.singular = device.singular
    this.plural = device.plural
    this.mW = this.device.mW
    this.numFixtures = 4 // TODO: figure this out
    this.volumeOfRoomCubicMeters = volumeOfRoomCubicMeters
    this.initialCostUSD = device.initialCostUSD
    this.recurringCostUSD = device.recurringCostUSD
    this.recurringCostDetails = device.recurringCostDetails
    this.ws = device.website
  }

  applicable() {
    return this.heightOfRoom >= uvObject.heightLowerBoundMeters
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
    return `${this.numFixtures} ${this.plural}`
  }

  computeACH() {
    return this.numFixtures * this.mW / this.volumeOfRoomCubicMeters
  }

  initialCost() {
    return this.initialCostUSD * this.numMasks
  }

  initialCostText() {
    return `${this.initialCost()} for ${this.amountText()} `
  }

  recurringCost() {
    return this.recurringCostUSD * this.numMasks
  }

  recurringCostText() {
    return `${this.recurringCost()} every ${this.recurringCostDetails}. `
  }

  website() {
    return this.ws
  }
}
