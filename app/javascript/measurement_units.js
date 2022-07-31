export function computeAmountOfPortableAirCleanersThatCanFit(
  areaOfRoom,
  areaOfOneAirCleaner
) {
  let numAirCleaners = 0
  while (areaOfOneAirCleaner * numAirCleaners / areaOfRoom < 0.01) {
    numAirCleaners += 1
  }

  return numAirCleaners
}
