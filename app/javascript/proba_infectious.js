export class ProbaInfectious {
  constructor(prior) {
    /*
     * {
     *   infectiousness: 0.05
     * }
     */

    this.prior = prior

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
  compute(evidence) {

    let numerator = this.prior;

    for (let e of evidence) {
      if (e.result == '?') {
        continue
      }
      else if (e.result == '+') {
        // P(+ | inf) * P(inf)
        numerator *= e.sensitivity
      } else {
        // P(- | inf) * P(inf)
        numerator *= (1 - e.sensitivity)
      }
    }

    let other = (1 - this.prior)

    for (let e of evidence) {
      if (e.result == '?') {
        continue
      }
      else if (e.result == '+') {
        // P(+ | not inf) * P(not inf)
        other *= (1 - e.specificity)
      } else {
        // P(- | not inf)
        //
        other *= e.specificity
      }
    }

    let denominator = numerator + other

    return numerator / denominator
  }
}
