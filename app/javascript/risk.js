export function riskOfEncounteringInfectious(probaInfectious, numPeople) {
  /*
   * Parameters:
   *   probaInfectious: Float
   *     The rate of currently infectious in the community
   *
   *   numPeople: Number
   *     The number of people to encounter
   *
   * Returns: Float
   */
  return 1 - (1 - probaInfectious)  ** numPeople;
}


export function riskIndividualIsNotInfGivenNegRapidTest(
  testSpecificity,
  testSensitivity,
  priorIndivInfectious
) {
  /*
   * https://twitter.com/michaelmina_lab/status/1438032854907301893/photo/1
   *
   * Parameters:
   *   testSpecificity: Float
   *     Probability that the test will give a negative result, when the
   *     individual is not infectious
   *
   *   testSensitivity: Float
   *     Probability that the test will give a positive result, when the
   *     individual is infectious
   *
   *   priorIndivInfectious: Float
   *     Probability that an andividual is infectious
   *
   * Returns: Float
   */
  const priorNotInfectious = 1 - priorIndivInfectious
  const specNotInf = testSpecificity * (priorNotInfectious)
  const falseNegativeRate = 1 - testSensitivity

  return specNotInf / (
    specNotInf + falseNegativeRate  * priorIndivInfectious
  );
}

