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
   *    evidence: Object
   *      Example:
   *           {
   *             rapid: '+'
   *           },

   *           {
   *             pcr: '?',
   *           },

   *           {
   *             symptomatic: '-'
   *           }
   *
   *
   */
  compute(outcome, evidence, cpts) {
    // TODO: filter for evidence

    let evidenceWithoutUnknowns = {}

    for (let k in evidence) {
      if (evidence[k] != '?') {
        evidenceWithoutUnknowns[k] = evidence[k]
      }
    }

    let factors = []
    for (let cpt of cpts) {
      factors.push(cpt.toFactor())
    }

    let numerator = factors[0]
    for (let i = 1; i < factors.length; i++) {
      numerator = numerator.prod(factors[i])
    }

    let evidenceKeys = []
    for (let k in evidenceWithoutUnknowns) {
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

    let filter = JSON.parse(JSON.stringify(evidenceWithoutUnknowns))

    filter['has_covid'] = 'true'

    return num.div(den).filter(filter)
  }
}
