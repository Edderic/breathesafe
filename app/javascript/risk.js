import { cubicFeetPerMinuteTocubicMetersPerHour, infectorActivityTypes } from './misc.js'

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

export function findRiskiestPotentialInfector(activityGroups) {
  let maxExhalationFactor = 0;
  let maxExhalationActivity;
  let carbonDioxideGenerationActivity;
  let maskType;
  let tmp_val = 0;

  for (let activityGroup of activityGroups) {
    tmp_val = infectorActivityTypes[activityGroup['aerosolGenerationActivity']]

    if (tmp_val > maxExhalationFactor) {
      maxExhalationActivity = activityGroup['aerosolGenerationActivity']
      maxExhalationFactor = tmp_val
      carbonDioxideGenerationActivity = activityGroup['carbonDioxideGenerationActivity']
      maskType = activityGroup['maskType']
    }
  }

  return {
    'aerosolGenerationActivityFactor': maxExhalationFactor,
    'aerosolGenerationActivity': maxExhalationActivity,
    'carbonDioxideGenerationActivity': carbonDioxideGenerationActivity,
    'maskType': maskType
  }
}

export function reducedRisk(from, to) {
  return (from - to) / from
}

