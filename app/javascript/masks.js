import { round } from './misc.js'

export const MASKS = [
  {
    'name': 'Flo Mask Pro w/ Pro Filter',
    'filtrationEfficiency': 0.99,
    'initialCostUSD': 89.99,
    'recurringCostUSD': 59.99,
    'recurringCostDuration': 'year',
    'recurringCostDetails': 'for filters',
    'website': 'https://flomask.com/collections/flo-mask-for-adults',
    'type': 'tight-fitting, elastomeric',
    'filtrationType': 'Elastomeric N99',
    'interventionType': 'mask'
  }
]

export class Mask {
  constructor(mask, numDevices) {
    this.filtrationType = mask.filtrationType
    this.numDev = numDevices
    this.type = 'mask'
    this.maskType = mask.filtrationType
    this.mask = mask
    this.maskName = mask.name
    this.initialCostUSD = mask.initialCostUSD
    this.recurringCostUSD = mask.recurringCostUSD
    this.recurringCostDetails = mask.recurringCostDetails
    this.recurringCostDuration = mask.recurringCostDuration
  }
  applicable() {
    return true
  }

  amountText() {
    return `${this.maskName} per person. `
  }

  computeACH() {
    return 0
  }

  numDevices() {
    return this.numDev
  }

  filtrationEfficiency() {
    return this.mask.filtrationEfficiency
  }

  initialCost() {
    return round(this.initialCostUSD * this.numDevices(), 2)
  }

  initialCostText() {
    return `${this.initialCost()} for ${this.amountText()}`
  }

  isUpperUV() {
    return false
  }

  isMask() {
    return true
  }

  isFiltrationAirCleaner() {
    return false
  }

  recurringCost() {
    return this.recurringCostUSD * this.numDevices()
  }

  recurringCostText() {
    return `${this.recurringCost()} every ${this.recurringCostDetails}. `
  }

  website() {
    return this.mask.website
  }
}
