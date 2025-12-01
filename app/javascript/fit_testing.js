import {round, shorthandDate, isNullOrBlank } from './misc.js'
import { deepSnakeToCamel } from './misc.js'

export class FitTest {
  constructor(data) {
    this.id = data.id

    this._fit_test = deepSnakeToCamel(data)
    for(let k in this._fit_test) {
      this[k] = this._fit_test[k]
    }

    // Handle cases where results might be null/undefined or qualitative/quantitative might not exist
    this.qualitative = data.results?.qualitative || {};
    this.quantitative = data.results?.quantitative || {};
    this.qualitativeExercises = this.qualitative?.exercises || []
    this.quantitativeExercises = this.quantitative?.exercises || []

    this.comfortQuestions = {
      "How comfortable is the position of the mask on the nose?": {
        'passingAnswers': ['Comfortable']
      },
      "Is there adequate room for eye protection?": {
        'passingAnswers': ['Adequate', 'Not applicable']
      },
      "Is there enough room to talk?": {
        'passingAnswers': ['Enough']
      },
      "How comfortable is the position of the mask on face and cheeks?": {
        'passingAnswers': ['Comfortable']
      },
    }
  }

  get quantitativeTestingMode() {
    return this.quantitative?.testing_mode;
  }

  get shortHandCreatedAt() {
    return shorthandDate(this.createdAt)
  }

  get usePositivePressureUserSealCheck() {
    return !this.hasExhalationValve
  }

  get userSealCheckPressureType() {
    if (this.usePositivePressureUserSealCheck) {
      return 'positive'
    } else {
      'negative'
    }
  }

  get userSealCheckPassed() {
    if (this.userSealCheck['sizing']["What do you think about the sizing of this mask relative to your face?"] != "Somewhere in-between too small and too big") {
      // Either too big or too small
      return false
    }

    if (this.usePositivePressureUserSealCheck) {
      const airMovement = this.userSealCheck.positive["...how much air movement on your face along the seal of the mask did you feel?"]
      return airMovement == 'No air movement' || airMovement == 'Some air movement'
    } else {
      return (this.userSealCheck['negative']['...how much air passed between your face and the mask?'] == 'Unnoticeable')
    }
  }

  get comfortStatus() {
    let collector = true
    for (const [ question, value ] of Object.entries(this.comfortQuestions)) {
      if (isNullOrBlank(this.comfort[question])) {
        return 'Incomplete'
      }
      collector = collector && value['passingAnswers'].includes(this.comfort[question])
    }

    if (collector) {
      return 'Passed'
    } else {
      return 'Failed'
    }
  }

  get userSealCheckStatus() {
    const sizingQuestionKey = "What do you think about the sizing of this mask relative to your face?"
    const sizing = this.userSealCheck['sizing'] && this.userSealCheck['sizing'][sizingQuestionKey]

    if (sizing == "Too small" || sizing == 'Too big') {
      return 'Failed'
    }

    if (this.usePositivePressureUserSealCheck) {
      // Use the same logic as UserSealCheckService
      const airMovementQuestion = "...how much air movement on your face along the seal of the mask did you feel?"

      const airMovement = this.userSealCheck.positive && this.userSealCheck.positive[airMovementQuestion]

      // Check if questions are missing
      if (isNullOrBlank(sizing) || isNullOrBlank(airMovement)) {
        return 'Incomplete'
      }

      // Fail if "A lot of air movement" is selected
      if (airMovement == 'A lot of air movement') {
        return 'Failed'
      }

      // Pass if "Somewhere in-between too small and too big" AND ("Some air movement" OR "No air movement")
      if (sizing == "Somewhere in-between too small and too big") {
        if (airMovement == 'Some air movement' || airMovement == 'No air movement') {
          return 'Passed'
        }
      }

      // If we get here, the combination doesn't match our pass criteria
      return 'Incomplete'

    } else {
      // use negative pressure

      for (const [key, value] of Object.entries(this.userSealCheck.negative)) {
        if (value != 'Unnoticeable') {
          return 'Failed'
        } else if (value == null) {
          nullCount += 1
        }
      }

      if (nullCount > 0) {
        return 'Incomplete'
      }

      return 'Passed'
    }
  }

  get qualitativeStatus() {
    if (this.qualitative.procedure == "Skipping") {
      return "Skipped"
    }
    // if No failures but some questions are unfilled
    // Incomplete
    if (this.qualitativeFailed) {
      return 'Failed'
    } else if (!this.qualitativeFailed && this.qualitativeHasUnanswered) {
      return 'Incomplete'
    } else {
      return 'Passed'
    }
  }

  get qualitativeHasUnanswered() {
    let counter = 0;
    for(let q of this.qualitativeExercises) {
      if (q.result == null) {
        return true
      }
    }

    return false
  }
  get qualitativeFailed() {
    for(let q of this.qualitativeExercises) {
      if (q.result == 'Fail') {
        return true
      }
    }

    return false
  }

  get qualitativePassed() {
    return !this.qualitativeFailed
  }

  get quantitativeStatusNumeric() {
    if (this.quantitative.procedure == "Skipped") {
      return -1
    }

    // quantify HMFF
    let fitFactorsInverted = 0
    let fitFactorCount = 0
    let sealingExercise = 0

    for (let ex of this.quantitativeExercises) {
      if (ex.name.includes("SEALED")) {
        sealingExercise = 1
        continue
        // skip the SEALED exercise which is for measuring filtration
        // efficiency of the mask.
      }

      if (!!ex.fit_factor) {
        fitFactorCount += 1
      }

      fitFactorsInverted += 1 / ex.fit_factor
    }


    if (this.quantitativeExercises.length - fitFactorCount - sealingExercise > 0) {
      // there are still some exercises that haven't been done. OSHA protocol
      // expects users to finish every single exercise to get the overall HMFF
      return 0
    }

    return round(fitFactorCount / fitFactorsInverted, 1)
  }
  get quantitativeStatus() {
    if (this.quantitative.procedure == "Skipped") {
      return "Skipped"
    }

    // quantify HMFF
    let fitFactorsInverted = 0
    let fitFactorCount = 0
    let sealingExercise = 0

    for (let ex of this.quantitativeExercises) {
      if (ex.name.includes("SEALED")) {
        sealingExercise = 1
        continue
        // skip the SEALED exercise which is for measuring filtration
        // efficiency of the mask.
      }

      if (!!ex.fit_factor) {
        fitFactorCount += 1
      }

      fitFactorsInverted += 1 / ex.fit_factor
    }


    if (this.quantitativeExercises.length - fitFactorCount - sealingExercise > 0) {
      // there are still some exercises that haven't been done. OSHA protocol
      // expects users to finish every single exercise to get the overall HMFF
      return 'Incomplete'
    }

    return `${round(fitFactorCount / fitFactorsInverted, 1)} (${this.quantitativeTestingMode})`
  }
};
