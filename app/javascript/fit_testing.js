import {round, shorthandDate, isNullOrBlank } from './misc.js'
import { deepSnakeToCamel } from './misc.js'

export class FitTest {
  constructor(data) {
    this.id = data.id

    this._fit_test = deepSnakeToCamel(data)
    for(let k in this._fit_test) {
      this[k] = this._fit_test[k]
    }

    this.qualitative = data.results.qualitative;
    this.quantitative = data.results.quantitative;
    this.qualitativeExercises = this.qualitative.exercises
    this.quantitativeExercises = this.quantitative.exercises

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
    return this.quantitative.testing_mode;
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
      return (this.userSealCheck.positive["...how much air movement on your face along the seal of the mask did you feel?"] == 'No air movement') &&
        (this.userSealCheck.positive["...how much pressure build up was there?"] == 'As expected')
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
    let nullCount = 0
    let sizingQuestion = this.userSealCheck['sizing']["What do you think about the sizing of this mask relative to your face?"]

    if ( sizingQuestion == "Too small" || sizingQuestion == 'Too big') {
      return 'Failed'
    }

    if (this.usePositivePressureUserSealCheck) {
      // Fail the sizing question, -> Failed
      // One question failed -> Fail
      // All questions unanswered or blank -> incomplete
      // No questions failed but there is a blank -> incomplete
      // All questions answered and no failure -> pass
      //
      // So we can count the number of blanks
      // Scenario 1: all questions unanswered or blank -> Incomplete
      if (
        (
          (!isNullOrBlank(this.userSealCheck.positive["...how much air movement on your face along the seal of the mask did you feel?"])) &&
          (this.userSealCheck.positive["...how much air movement on your face along the seal of the mask did you feel?"] != 'No air movement')
        ) || (
          !isNullOrBlank(this.userSealCheck.positive["...how much did your glasses fog up?"]) &&
          (
            (this.userSealCheck.positive["...how much did your glasses fog up?"] != 'Not at all') &&
            (this.userSealCheck.positive["...how much did your glasses fog up?"] != 'Not applicable')
          )
        ) || (
          !isNullOrBlank(this.userSealCheck.positive["...how much pressure build up was there?"]) &&
          (this.userSealCheck.positive["...how much pressure build up was there?"] != 'As expected')
        )
      ) {
          return 'Failed'
      } else if (
        isNullOrBlank(this.userSealCheck.positive["...how much air movement on your face along the seal of the mask did you feel?"]) ||
          isNullOrBlank(this.userSealCheck.positive["...how much did your glasses fog up?"]) ||
          isNullOrBlank(this.userSealCheck.positive["...how much pressure build up was there?"])
      ) {
        return 'Incomplete'
      } else {
        return 'Passed'
      }

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
