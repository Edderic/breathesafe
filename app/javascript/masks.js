import { round } from './misc.js'

export const MASKS = [
  {
    'name': 'Flo Mask Pro w/ Pro Filter',
    'filtrationEfficiency': 0.99,
    'initialCostUSD': 90,
    'recurringCostUSD': 60,
    'recurringCostDuration': 'year',
    'recurringCostDetails': 'for filters',
    'website': 'https://flomask.com/collections/flo-mask-for-adults',
    'type': 'tight-fitting, elastomeric',
    'filtrationType': 'Elastomeric N99',
    'interventionType': 'mask'
  },

  {
    'name': 'Surgical Mask',
    'filtrationEfficiency': 0.5,
    'initialCostUSD': 30,
    'recurringCostUSD': 30,
    'recurringCostDuration': 'year',
    'recurringCostDetails': 'for a pack of 50',
    'website': 'https://www.armbrustusa.com/collections/medical-face-masks-made-in-austin-tx/products/usa-made-surgical-masks-1',
    'type': 'leaky, surgical mask',
    'filtrationType': 'Cloth / Surgical',
    'interventionType': 'mask'
  },
  {
    'name': 'N95 Mask',
    'filtrationEfficiency': 0.95,
    'initialCostUSD': 30,
    'recurringCostUSD': 30,
    'recurringCostDuration': '20 weeks',
    'recurringCostDetails': 'for a pack of 20',
    'website': 'https://www.projectn95.org/products/3m-company-n95-respirator-mask-9205-aura',
    'type': 'leaky, surgical mask',
    'filtrationType': 'N95 - unfitted',
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
    return `${this.initialCost()} for ${this.maskName}`
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
    return `${this.recurringCost()} every ${this.recurringCostDuration} ${this.recurringCostDetails}. `
  }

  website() {
    return this.mask.website
  }
}
