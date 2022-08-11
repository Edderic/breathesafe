import {
  findRiskiestPotentialInfector,
  riskOfEncounteringInfectious,
  findRiskiestMask,
  riskIndividualIsNotInfGivenNegRapidTest } from './risk.js';
import {
  computePortableACH,
  computeVentilationACH,
  convertCubicMetersPerHour,
  convertLengthBasedOnMeasurementType,
  cubicFeetPerMinuteTocubicMetersPerHour,
  displayCADR,
  findWorstCaseInhFactor,
  generateUUID,
  maskToPenetrationFactor,
  setupCSRF,
  simplifiedRisk,
  round,

} from  './misc';

function binarySearch(low, high, funcStuff, target, key) {
  /*
   * Parameters:
   *  high: 0 - 1000000
   *  target: 0.99
   */
  if (!key) {
    key = 'amount'
  }
  funcStuff['args'][key] = low
  let lowVal = funcStuff['func'](funcStuff['args'])

  funcStuff['args'][key] = high
  let highVal = funcStuff['func'](funcStuff['args'])

  let middle = low + (high - low) / 2
  funcStuff['args'][key] = low + (high - low) / 2
  let middleVal = funcStuff['func'](funcStuff['args'])

  if (Math.abs(low - high) <= 1) {
    return middle
  }


  // case 1:
  // |                   x         |
  // A                             B
  //
  // case 2:
  // |    |   x
  // A    B

  // case 3:
  //          x  |                 |
  //             A                 B
  // overshoot
  //
  //
  // case 1:
  // |                   x         |
  // A                             B
  if (middleVal < target) {
    return binarySearch(middle, high, funcStuff, target, key)
  }
  else {
    // case 1:
    // |        x                    |
    // A                             B
    return binarySearch(low, middle, funcStuff, target, key)
  }
}

function probability_getting_infected_at_least_once(args) {
  return 1 - (1- args.probability) ** args.amount
}

export class Intervention {
  constructor(event, interventions) {
    this.interventions = interventions
    this.event = event
    this.portableAch = event.portableAch
    this.uvAch = event.uvAch
    this.totalAch = event.totalAch
    this.ventilationAch = event.ventilationAch
    this.roomUsableVolumeCubicMeters = event.roomUsableVolumeCubicMeters
    this.activityGroups = event.activityGroups
    this.riskiestMask = findRiskiestMask(this.activityGroups)
    this.riskiestPotentialInfector = findRiskiestPotentialInfector(this.activityGroups)
    this.riskiestActivityGroup = {
      'numberOfPeople': 1,
      'aerosolGenerationActivity': this.riskiestPotentialInfector['aerosolGenerationActivity'],
      'carbonDioxideGenerationActivity': this.riskiestPotentialInfector['carbonDioxideGenerationActivity'],
      'maskType': this.riskiestMask['maskType']
    }

    this.id = generateUUID()
    this.risk = undefined
    this.numEventsToEnsureInfection = undefined
  }

  computeACH() {
    let total = this.totalAch

    for (let intervention of this.interventions) {
      total += intervention.computeACH()
    }

    return total
  }

  computeRisk(duration) {
    if (!duration) {
      duration = 1
    }

    let totalAch = this.event.totalAch
    if (!totalAch) {
      debugger

    }
    let uvAch = 0
    let ventilationAch = 0
    let portableAch = 0
    let riskiestActivityGroup = JSON.parse(JSON.stringify(this.riskiestActivityGroup))
    // When there are no interventions, default to the maskType of the riskiest potential infector
    let susceptibleMaskPenentrationFactor = maskToPenetrationFactor[riskiestActivityGroup.maskType]

    for (let intervention of this.interventions) {
      if (intervention.isMask()) {
        // susceptible and infector wear the same mask
        riskiestActivityGroup['maskType'] = intervention.maskType
        susceptibleMaskPenentrationFactor = maskToPenetrationFactor[intervention.maskType]
      } else if (intervention.isFiltrationAirCleaner()) {
        portableAch += intervention.computeACH()
      } else if (intervention.isUpperUV()) {
        uvAch += intervention.computeACH()
      }

      totalAch += intervention.computeACH()
    }

    if (!this.riskiestPotentialInfector['aerosolGenerationActivity'])  {
      return 0
    }

    const occupancy = 1
    const flowRate = totalAch * this.roomUsableVolumeCubicMeters
    // TODO: consolidate this information in one place
    const basicInfectionQuanta = 18.6
    const variantMultiplier = 3.3
    const quanta = basicInfectionQuanta * variantMultiplier
    const susceptibleAgeGroup = '30 to <40'

    const susceptibleInhalationFactor = findWorstCaseInhFactor(
      this.activityGroups,
      susceptibleAgeGroup
    )
    const probaRandomSampleOfOneIsInfectious = 1.0

    let result = simplifiedRisk(
      [riskiestActivityGroup],
      occupancy,
      flowRate,
      quanta,
      susceptibleMaskPenentrationFactor,
      susceptibleAgeGroup,
      probaRandomSampleOfOneIsInfectious,
      duration
    )

    return result
  }

  durationToLikelyInfection() {
    if (this.durToLikelyInfection) {
      return this.durToLikelyInfection
    }

    let lowerBound = 0
    let upperBound = 5000000
    let target = 0.99

    this.durToLikelyInfection = binarySearch(
      lowerBound,
      upperBound,
      {
        'func': this.computeInfection.bind(this),
        'args': {}
      },
      target,
      'duration'
    )

    return this.durToLikelyInfection
  }

  computeInfection(args) {
    if (!args.duration) {
      args.duration = 1 // hour
    }

    let totalAch = this.event.totalAch
    if (!totalAch) {
      debugger

    }
    let uvAch = 0
    let ventilationAch = 0
    let portableAch = 0
    let riskiestActivityGroup = JSON.parse(JSON.stringify(this.riskiestActivityGroup))
    // When there are no interventions, default to the maskType of the riskiest potential infector
    let susceptibleMaskPenentrationFactor = maskToPenetrationFactor[riskiestActivityGroup.maskType]

    for (let intervention of this.interventions) {
      if (intervention.isMask()) {
        // susceptible and infector wear the same mask
        riskiestActivityGroup['maskType'] = intervention.maskType
        susceptibleMaskPenentrationFactor = maskToPenetrationFactor[intervention.maskType]
      } else if (intervention.isFiltrationAirCleaner()) {
        portableAch += intervention.computeACH()
      } else if (intervention.isUpperUV()) {
        uvAch += intervention.computeACH()
      }

      totalAch += intervention.computeACH()
    }

    if (!this.riskiestPotentialInfector['aerosolGenerationActivity'])  {
      return 0
    }

    const occupancy = 1
    const flowRate = totalAch * this.roomUsableVolumeCubicMeters
    // TODO: consolidate this information in one place
    const basicInfectionQuanta = 18.6
    const variantMultiplier = 3.3
    const quanta = basicInfectionQuanta * variantMultiplier
    const susceptibleAgeGroup = '30 to <40'

    const susceptibleInhalationFactor = findWorstCaseInhFactor(
      this.activityGroups,
      susceptibleAgeGroup
    )
    const probaRandomSampleOfOneIsInfectious = 1.0

    return simplifiedRisk(
      [riskiestActivityGroup],
      occupancy,
      flowRate,
      quanta,
      susceptibleMaskPenentrationFactor,
      susceptibleAgeGroup,
      probaRandomSampleOfOneIsInfectious,
      args.duration
    )

  }

  numEventsToInfectionWithCertainty() {
    if (this.numEventsToEnsureInfection) {
      return this.numEventsToEnsureInfection
    }

    let lowerBound = 0
    let upperBound = 5000000
    let target = 0.99

    this.numEventsToEnsureInfection = binarySearch(
      lowerBound,
      upperBound,
      {
        'func': probability_getting_infected_at_least_once,
        'args': {
          probability: this.computeRisk()
        }
      },
      target,
    )

    return this.numEventsToEnsureInfection
  }

  numDevices() {
    let count = 0

    for (let intervention of this.interventions) {
      count += intervention.numDevices()
    }

    return count
  }

  costInYears(numYears) {
    let cost = 0

    for (let intervention of this.interventions) {
      cost += intervention.costInYears(numYears)
    }

    return cost
  }

  computeRiskRounded(duration) {
    return round(this.computeRisk(duration), 6)
  }

  amountText() {
    let tmp = ""

    for (let intervention of this.interventions) {
      tmp += `${intervention.amountText()} `
    }

    return tmp
  }

  initialCostText() {
    let tmp = ""

    for (let intervention of this.interventions) {
      tmp += `${intervention.initialCostText()} `
    }

    return tmp
  }

  recurringCostText() {
    let tmp = ""

    for (let intervention of this.interventions) {
      tmp += `${intervention.recurringCostText()} `
    }

    return tmp
  }

  websitesAndText() {
    let tmp = []

    for (let intervention of this.interventions) {
      tmp.push(
        {
          website: intervention.website(),
          text: intervention.amountText(),
          imgLink: intervention.imgLink()
        }
      )
    }

    return tmp
  }
}

