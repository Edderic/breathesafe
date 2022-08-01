import {convertLengthBasedOnMeasurementType} from './misc.js'

export function computeAmountOfPortableAirCleanersThatCanFit(
  areaOfRoom,
  areaOfOneAirCleaner
) {
  let numAirCleaners = 0
  while (areaOfOneAirCleaner * numAirCleaners / areaOfRoom < 0.005) {
    numAirCleaners += 1
  }

  return numAirCleaners
}

export function convertVolume(vol, from, to) {
  let f;
  let t;
  if (from == 'cubic feet' && to == 'cubic meters') {
    f = 'feet'
    t = 'meters'
  } else if (from == 'cubic meters' && to == 'cubic feet') {
    f = 'meters'
    t = 'feet'
  } else if (from == to) {
    return vol
  }

  return convertLengthBasedOnMeasurementType(
    convertLengthBasedOnMeasurementType(
      convertLengthBasedOnMeasurementType(
        vol,
        from,
        to
      ),
      from,
      to
    ),
    from,
    to
  )
}
