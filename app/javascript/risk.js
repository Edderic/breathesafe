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
