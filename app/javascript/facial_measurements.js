export function getFacialMeasurements() {
  return {
    'bitragionSubnasaleArcMm': {
      'eng': "Bitragion subnasale arc (mm)",
      'value': 230,
      'explanation': "The surface distance between the left and right tragion landmarks (cartilaginous flap of the ear) across the subnasale landmark at the bottom of the nose. Please use a tape measure.",
      'image_url': "https://nap.nationalacademies.org/openbook/0309103983/xhtml/images/p20012464g30003.jpg",
      'use_for_recommender': true
    },
    'faceWidthMm': {
      'eng': "Face width (mm)",
      'value': 150,
      'explanation': "The maximum horizontal breadth of the face between the zygomatic arches (cheekbones). Please use a caliper.",
      'image_url': 'https://nap.nationalacademies.org/openbook/0309103983/xhtml/images/p20012464g31003.jpg',
      'use_for_recommender': true
    },
    'noseProtrusionMm': {
      'eng': "Nose protrusion (mm)",
      'value': 29,
      'explanation': "The straight-line distance between the pronasale landmark at the tip of the nose and the subnasale landmark under the nose. Please use a tape measure.",
      'image_url': 'https://nap.nationalacademies.org/openbook/0309103983/xhtml/images/p20012464g33001.jpg',
      'use_for_recommender': true
    },
    'noseBreadthMm': {
      'eng': "Nose breadth (mm)",
      'value': 28,
      'explanation': "The straight-line distance between the right and left alare landmarks on the sides of the nostrils. Please use a caliper.",
      'image_url': 'https://nap.nationalacademies.org/openbook/0309103983/xhtml/images/p20012464g32003.jpg',
      'use_for_recommender': false
    },
    'jawWidthMm': {
      'eng': 'Jaw width (mm)',
      'value': 145,
      'explanation': 'The straight line distance between right and left gonion landmarks on the corners of the jaw. Please use a caliper.',
      'image_url': 'https://nap.nationalacademies.org/openbook/0309103983/xhtml/images/p20012464g30001.jpg',
      'use_for_recommender': false
    },
    'faceLengthMm': {
      'eng': 'Face length (mm)',
      'value': 127,
      'explanation': 'The distance in the midsagittal plane between the menton landmark at the bottom of the chin and the sellion landmark at the deepest point of the nasal root depression. Please use a caliper.',
      'image_url': 'https://nap.nationalacademies.org/openbook/0309103983/xhtml/images/p20012464g31004.jpg',
      'use_for_recommender': false
    },
    'lowerFaceLengthMm': {
      'eng': 'Lower face length (mm)',
      'value': 88.9,
      'explanation': 'The distance between the menton (chin) and subnasale landmark under the nose. Please use a caliper.',
      'image_url': `https://breathesafe.s3.us-east-2.amazonaws.com/images/breathesafe-facial-measurements-examples/lower_face_length.jpg`,
      'use_for_recommender': false
    },
    'nasalRootBreadthMm': {
      'eng': 'Nasal root breadth (mm)',
      'value': 19,
      'explanation': 'The horizontal breadth of the nose at the level of the deepest depression of the root (sellion landmark) and at a depth equal to one-half the distance from the bridge of the nose to the eyes.',
      'image_url': `https://breathesafe.s3.us-east-2.amazonaws.com/images/breathesafe-facial-measurements-examples/nasal_root_breadth.jpg`,
      'use_for_recommender': false
    },
    'noseBridgeHeightMm': {
      'eng': 'Nose Bridge Height (mm)',
      'value': 20,
      'explanation': 'The distance between the tip of the nasal root and the cheek-to-nose-bridge intersection.',
      'image_url': `https://breathesafe.s3.us-east-2.amazonaws.com/images/breathesafe-facial-measurements-examples/nose_bridge_height.jpg`,
      'use_for_recommender': false
    },
    'lipWidthMm': {
      'eng': 'Lip width (mm)',
      'value': 48,
      'explanation': 'The straight-line distance between the left and right chelion landmarks at the corners of the closed mouth',
      'image_url': `https://nap.nationalacademies.org/openbook/0309103983/xhtml/images/p20012464g32001.jpg`,
      'use_for_recommender': false
    },
    'bitragionMentonArcMm': {
      'eng': 'Bitragion menton arc (mm)',
      'value': 255,
      'explanation': 'The surface distance between the left and right tragion landmarks across the anterior point of the chin.',
      'image_url': `https://nap.nationalacademies.org/openbook/0309103983/xhtml/images/p20012464g30004.jpg`,
      'use_for_recommender': false
    },
    'headCircumferenceMm': {
      'eng': 'Head circumference (mm)',
      'value': 550,
      'explanation': 'The maximum circumference of the head just above the ridges of the eyebrows.',
      'image_url': `https://breathesafe.s3.us-east-2.amazonaws.com/images/breathesafe-facial-measurements-examples/head_circumference.jpg`,
      'use_for_recommender': false
    }
  }
}
