export class RespiratorUser {
  constructor(user) {
    this.user = user
    this.profileId = user.profileId
    let toAssign = ['firstName', 'lastName', 'raceEthnicity', 'genderAndSex', 'userId', 'managedId'];
    for (let x of toAssign) {
      this[x] = user[x]
    }

  }

  get raceEthnicityComplete() {
    return !!this.user.raceEthnicity
  }

  get genderAndSexComplete() {
    return !!this.user.genderAndSex
  }

  get facialMeasurementsComplete() {
    return !!this.user.facialMeasurementsId
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
