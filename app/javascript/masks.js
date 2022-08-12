import { round } from './misc.js'

export const MASKS = [
  {
    'name': 'Elastomeric Mask (Flo Mask Pro w/ Pro Filter)',
    'shortName': 'Flo Mask Pro',
    'filtrationEfficiency': 0.99,
    'initialCostUSD': 90,
    'initialDurationYears': 0.144, // 5 Pro filters = 5 weeks, 5 Everyday = 2.5 weeks = 7.5 weeks. 7.5 weeks / 52 weeks = 0.144 years,
    'recurringCostUSD': 60,
    'recurringCostDuration': 'year',
    'recurringCostDetails': 'for Pro filters',
    'recurringCostPerYearUSD': 60,
    'rucurringDurationYears': 1,
    'website': 'https://flomask.com/collections/flo-mask-for-adults',
    'type': 'tight-fitting, elastomeric',
    'filtrationType': 'Elastomeric N99',
    'interventionType': 'mask',
    'imgLink': "https://cdn.shopify.com/s/files/1/0405/0154/3079/products/RB0A6673_28402bc4-206b-4a64-92f7-e591c70a1e64_900x.jpg?v=1647932779"
  },

  {
    'name': 'Surgical Mask',
    'shortName': 'Surgical Mask',
    'filtrationEfficiency': 0.5,
    'initialCostUSD': 30,
    'initialDurationYears': 1, // Assuming 1 mask / week
    'recurringCostUSD': 30,
    'recurringCostDuration': 'year',
    'recurringDurationYears': 1,
    'recurringCostDetails': 'for a pack of 50 surgical masks',
    'recurringCostPerYearUSD': 30,
    'website': 'https://www.armbrustusa.com/collections/medical-face-masks-made-in-austin-tx/products/usa-made-surgical-masks-1',
    'type': 'leaky, surgical mask',
    'filtrationType': 'Cloth / Surgical',
    'interventionType': 'mask',
    'imgLink': 'https://cdn.shopify.com/s/files/1/0384/4145/1653/products/Single-Mask-Front-Denim-USA-Made-Surgical-Masks-sw_700x.jpg?v=1618508031'
  },
  {
    'name': 'N95 Mask (3M Aura)',
    'shortName': '3M Aura',
    'filtrationEfficiency': 0.95,
    'initialCostUSD': 30,
    'initialDurationYears': 2 / 5, // Assuming 1 mask / week
    'recurringCostUSD': 30,
    'recurringCostDuration': '20 weeks',
    'recurringCostDetails': 'for a pack of 20',
    'recurringDurationYears': 2 / 5, // Assuming 1 mask / week
    'recurringCostPerYearUSD': 30 * 5 / 2,
    'website': 'https://www.projectn95.org/products/3m-company-n95-respirator-mask-9205-aura',
    'type': 'disposable N95 mask',
    'filtrationType': 'N95 - unfitted',
    'interventionType': 'mask',
    'imgLink': 'https://m.media-amazon.com/images/I/51IBeI2RK+L._AC_UL640_FMwebp_QL65_.jpg'
  },
  {
    'name': 'Elastomeric Mask (GVS Elipse P100)',
    'shortName': 'GVS Elipse P100',
    'filtrationEfficiency': 0.9997,
    'initialCostUSD': 26,
    'initialDurationYears': 0.5, // Every 6 months
    'recurringCostUSD': 12,
    'recurringCostDuration': '6 months',
    'recurringCostDetails': 'for filters',
    'recurringDurationYears': 2, // Every 6 months
    'recurringCostPerYearUSD': 24,
    'website': 'https://www.gvs.com/en/catalog/elipse-p100-with-source-control-niosh-respirator',
    'type': 'tight-fitting, P100 mask',
    'filtrationType': 'Elastomeric P100',
    'interventionType': 'mask',
    'imgLink': "https://m.media-amazon.com/images/I/817OKYFIPDS._SX522_.jpg"
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
    this.device = mask
    this.shortName = mask.shortName
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

  computeFiltrationAirCleanerACH() {
    return 0
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
    return this.numDev
  }

  filtrationEfficiency() {
    return this.mask.filtrationEfficiency
  }

  initialCost() {
    return round(this.initialCostUSD * this.numDevices(), 2)
  }

  initialCostText() {
    return `${this.shortName}: $${this.initialCost()}.`
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

  imgLink() {
    return this.device.imgLink
  }

  recurringCost() {
    return this.recurringCostUSD * this.numDevices()
  }

  recurringCostText() {
    return `${this.shortName}: $${this.recurringCost()} / ${this.recurringCostDuration} ${this.recurringCostDetails}. `
  }

  website() {
    return this.mask.website
  }
}
