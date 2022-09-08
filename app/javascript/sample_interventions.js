import { AirCleaner, airCleaners } from './air_cleaners.js'
import { Intervention } from './interventions.js'
import { Mask, MASKS } from './masks.js'
import { UpperRoomGermicidalUV, UPPER_ROOM_GERMICIDAL_UV } from './upper_room_germicidal_uv.js'

export function getSampleInterventions(event, numPeopleToInvestIn) {
  if (!numPeopleToInvestIn) {
    numPeopleToInvestIn = 1
  }

  return [
    new Intervention(
      event,
      [
        new AirCleaner(airCleaners[0], event)
      ],
      new Mask(MASKS[0], numPeopleToInvestIn),
      new Mask(MASKS[0], numPeopleToInvestIn)
    ),
    new Intervention(
      event,
      [
        new UpperRoomGermicidalUV(UPPER_ROOM_GERMICIDAL_UV[0], event)
      ],
      new Mask(MASKS[0], numPeopleToInvestIn),
      new Mask(MASKS[0], numPeopleToInvestIn)
    ),
    new Intervention(
      event,
      [
        new UpperRoomGermicidalUV(UPPER_ROOM_GERMICIDAL_UV[1], event)
      ],
      new Mask(MASKS[0], numPeopleToInvestIn),
      new Mask(MASKS[0], numPeopleToInvestIn)
    ),
    new Intervention(
      event,
      [
        new UpperRoomGermicidalUV(UPPER_ROOM_GERMICIDAL_UV[2], event)
      ],
      new Mask(MASKS[0], numPeopleToInvestIn),
      new Mask(MASKS[0], numPeopleToInvestIn)
    ),
    new Intervention(
      event,
      [
      ],
      new Mask(MASKS[0], numPeopleToInvestIn),
      new Mask(MASKS[0], numPeopleToInvestIn)
    ),
    new Intervention(
      event,
      [
      ],
      new Mask(MASKS[1], numPeopleToInvestIn)
    ),
    new Intervention(
      event,
      [
      ],
      new Mask(MASKS[2], numPeopleToInvestIn)
    ),
    new Intervention(
      event,
      [
      ],
      new Mask(MASKS[3], numPeopleToInvestIn)
    ),
    new Intervention(
      event,
      [
      ],
      new Mask(MASKS[4], numPeopleToInvestIn)
    ),
    new Intervention(
      event,
      [
        new AirCleaner(airCleaners[0], event)
      ],
      new Mask(MASKS[0], numPeopleToInvestIn),
    ),
    new Intervention(
      event,
      [
        new AirCleaner(airCleaners[0], event)
      ],

      new Mask(MASKS[2], numPeopleToInvestIn),
    ),
    new Intervention(
      event,
      [
        new UpperRoomGermicidalUV(UPPER_ROOM_GERMICIDAL_UV[0], event)
      ],

      new Mask(MASKS[2], numPeopleToInvestIn),
    ),
    new Intervention(
      event,
      [
        new UpperRoomGermicidalUV(UPPER_ROOM_GERMICIDAL_UV[0], event),
        new AirCleaner(airCleaners[0], event)
      ],

      new Mask(MASKS[2], numPeopleToInvestIn),
    ),
  ]
}
