export class RespiratorUser {
  constructor(user) {
    this.user = user
    this.profileId = user.profileId

    for (const [key, value] of Object.entries(user)) {
      this[key] = value
    }
  }

  get fullName() {
    return this.firstName + ' ' + this.lastName;
  }

  get raceEthnicityComplete() {
    return !!this.user.raceEthnicity
  }

  get genderAndSexComplete() {
    return !!this.user.genderAndSex
  }

  get facialMeasurementsComplete() {
    return !!this.user.facialMeasurementId
  }

  get nameComplete() {
    return (!!this.firstName || !!this.lastName) && (this.firstName != "Edit")
    && (this.lastName != "Me")
  }

  get readyToAddFitTestingDataPercentage() {
    let numerator = this.nameComplete
      + this.raceEthnicityComplete
      + this.genderAndSexComplete
      + this.facialMeasurementsComplete

    let rounded = Math.round(
      numerator / 4 * 100
    )

    return `${rounded}%`
  }

};
