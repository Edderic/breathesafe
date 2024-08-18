import {round, shorthandDate} from './misc.js'

export class FitTest {
  constructor(data) {
    this.id = data.id
    this.uniqueInternalModelCode = data.unique_internal_model_code
    this.hasExhalationValve = data.has_exhalation_valve
    this.imageUrls = data.image_urls
    this.createdAt = data.created_at
    this.updatedAt = data.updated_at
    this.userSealCheck = data.user_seal_check;
    this.qualitative = data.results.qualitative;
    this.quantitative = data.results.quantitative;
    this.comfort = data.comfort
    this.qualitativeExercises = this.qualitative.exercises
    this.quantitativeExercises = this.quantitative.exercises
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
    if (this.usePositivePressureUserSealCheck) {
      return (this.userSealCheck.positive["...how much air movement on your face along the seal of the mask did you feel?"] == 'No air movement') &&
        (
          (
            this.userSealCheck.positive["...how much did your glasses fog up?"] == 'Not applicable'
          ) ||
          (
            this.userSealCheck.positive["...how much did your glasses fog up?"] == 'Not at all'
          )
        ) &&
        (this.userSealCheck.positive["...how much pressure build up was there?"] == 'As expected')
    } else {
      return (this.userSealCheck['negative']['...how much air passed between your face and the mask?'] == 'Unnoticeable')
    }
  }

  get comfortStatus() {
    if (
      (this.comfort["How comfortable is the position of the mask on the nose?"] == 'Comfortable') &&
      (
        (this.comfort["Is there adequate room for eye protection?"] == 'Adequate') ||
        (this.comfort["Is there adequate room for eye protection?"] == 'Not applicable')
      ) &&
      (
        this.comfort["Is there enough room to talk?"] == 'Enough'
      ) && (
        this.comfort["How comfortable is the position of the mask on face and cheeks?"] == 'Comfortable'
      )
    ) {
      return 'Passed'
    } else {
      return 'Failed'
    }
  }

  get userSealCheckStatus() {
    let nullCount = 0

    if (this.usePositivePressureUserSealCheck) {
      if (
        (
          (this.userSealCheck.positive["...how much air movement on your face along the seal of the mask did you feel?"] != null) &&
          (this.userSealCheck.positive["...how much air movement on your face along the seal of the mask did you feel?"] != 'No air movement')
        ) || (
          (this.userSealCheck.positive["...how much did your glasses fog up?"] != null) &&
          (
            (this.userSealCheck.positive["...how much did your glasses fog up?"] != 'Not at all') &&
            (this.userSealCheck.positive["...how much did your glasses fog up?"] != 'Not applicable')
          )
        ) || (
          (this.userSealCheck.positive["...how much pressure build up was there?"] != null) &&
          (this.userSealCheck.positive["...how much pressure build up was there?"] != 'As expected')
        )
      ) {
        return 'Failed'
      }
      // otherwise lets check for  missing values
      for (const [key, value] of Object.entries(this.userSealCheck.positive)) {
        if (value == null) {
          nullCount += 1
        }
      }

      if (nullCount > 0) {
        return 'Incomplete'
      }

      return 'Passed'
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
      return 'Complete'
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

  get quantitativeStatus() {
    if (this.quantitative.procedure == "Skipped") {
      return "Skipped"
    }

    // quantify HMFF
    let fitFactorsInverted = 0
    let fitFactorCount = 0

    for (let ex of this.quantitativeExercises) {
      if (!!ex.fit_factor) {
        fitFactorCount += 1
      }

      fitFactorsInverted += 1 / ex.fit_factor
    }

    return `${round(fitFactorCount / fitFactorsInverted, 1)} HMFF`
  }
};
