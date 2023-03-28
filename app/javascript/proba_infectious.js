export class ProbaInfectious {
  constructor() {
    /*
     * {
     *   infectiousness: 0.05
     * }
     */


  }

  /*
   * Compute the posterior probability of infectiousness given:
   *
   *  - Rapid Test result
   *  - Has symptoms
   * Parameters:
   *    evidence: Array[Object]
   *      Example:
   *         [
   *           {
   *             evidenceName: 'Rapid Test',
   *             result: '+',
   *             sensitivity: 0.9,
   *             specificity: 0.99,
   *           },

   *           {
   *             evidenceName: 'PCR',
   *             result: '+',
   *             sensitivity: 0.95,
   *             specificity: 0.99
   *           },

   *           {
   *             evidenceName: 'Symptoms',
   *             result: '+',
   *             sensitivity: 0.75,
   *             specificity: 0.25
   *           }
   *         ]
   *
   */
  compute(outcome, evidence, cpts) {
    // TODO: filter for evidence

    let factors = []
    for (let cpt of cpts) {
      factors.push(cpt.toFactor())
    }

    let numerator = factors[0]
    for (let i = 1; i < factors.length; i++) {
      numerator = numerator.prod(factors[i])
    }

    let evidenceKeys = []
    for (let k of evidence) {
      evidenceKeys.push(k)
    }

    let varsToSumOutNumerator = []

    for (let k in numerator.arrayOfObj[0]) {
      if (!evidenceKeys.includes(k) && !['value', outcome].includes(k)) {
        varsToSumOutNumerator.push(k)
      }
    }

    let num = numerator.sum(varsToSumOutNumerator)


    let varsToSumOutDenominator = JSON.parse(JSON.stringify(varsToSumOutNumerator))

    varsToSumOutDenominator.push(outcome)

    let den = numerator.sum(varsToSumOutDenominator)

    return num.div(den).filter({ has_covid: 'true'})
  }
}
