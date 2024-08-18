import {round, shorthandDate} from './misc.js'

export class FitTest {
  constructor(data) {
    this.id = data.id
    this.uniqueInternalModelCode = data.unique_internal_model_code
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

  get userSealCheckPassed() {
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
    if (this.userSealCheckPassed) {
      return 'Passed'
    } else {
      return 'Failed'
    }
  }

  get qualitativeStatus() {
    if (this.qualitative.procedure == "Skipped") {
      return "Skipped"
    }

    if (this.qualitativePassed) {
      return 'Passed'
    } else {
      return 'Failed'
    }
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
