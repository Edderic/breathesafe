import { findRiskiestPotentialInfector, riskOfEncounteringInfectious, riskIndividualIsNotInfGivenNegRapidTest } from './risk.js';
import {
  computePortableACH,
  computeVentilationACH,
  convertCubicMetersPerHour,
  convertLengthBasedOnMeasurementType,
  cubicFeetPerMinuteTocubicMetersPerHour,
  displayCADR,
  findWorstCaseInhFactor,
  maskToPenetrationFactor,
  setupCSRF,
  simplifiedRisk,
  round,

} from  './misc';

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
    this.riskiestPotentialInfector = findRiskiestPotentialInfector(this.activityGroups)
    this.riskiestActivityGroup = {
      'numberOfPeople': 1,
      'aerosolGenerationActivity': this.riskiestPotentialInfector['aerosolGenerationActivity'],
      'carbonDioxideGenerationActivity': this.riskiestPotentialInfector['carbonDioxideGenerationActivity'],
      'maskType': this.riskiestPotentialInfector['maskType']
    }
  }

  computeRisk() {

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
    const duration = 1 // hour

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

  numDevices() {
    let count = 0

    for (let intervention of this.interventions) {
      count += intervention.numDevices()
    }

    return count
  }

  computeRiskRounded() {
    return round(this.computeRisk(), 6)
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
          text: intervention.amountText()
        }
      )
    }

    return tmp
  }
}

