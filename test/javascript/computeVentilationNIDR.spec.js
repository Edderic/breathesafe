// inside test/javascript/magicAdd.spec.js
import {computeVentilationNIDR} from 'misc.js'

describe('computeVentilationNIDR', () => {

  test('test 1', () => {
    let ventilationCO2AmbientPPM = 420;
    let roomUsableVolumeCubicMeters = 228.99;

    let activityGroups = [
      {
        id: "360c52db-e0f6-4c71-b790-8e3d7b148ef3",
        ageGroup:"6 to <11",
        maskType:"",
        numberOfPeople:"10",
        aerosolGenerationActivity:"Light exercise - Oral breathing",
        carbonDioxideGenerationActivity:"Sitting reading, writing, typing"
      },
    ]
    let normalizedCO2Readings = [
      {'co2': 497, 'timestamp': '2023-04-26 08:37:07 UTC'},
      {'co2': 457, 'timestamp': '2023-04-26 08:37:08 UTC'},
      {'co2': 472, 'timestamp': '2023-04-26 08:37:09 UTC'},
      {'co2': 476, 'timestamp': '2023-04-26 08:37:10 UTC'},
      {'co2': 471, 'timestamp': '2023-04-26 08:37:11 UTC'},
      {'co2': 488, 'timestamp': '2023-04-26 08:37:12 UTC'},
      {'co2': 500, 'timestamp': '2023-04-26 08:37:13 UTC'},
      {'co2': 487, 'timestamp': '2023-04-26 08:37:14 UTC'},
      {'co2': 490, 'timestamp': '2023-04-26 08:37:15 UTC'},
      {'co2': 480, 'timestamp': '2023-04-26 08:37:16 UTC'},
      {'co2': 525, 'timestamp': '2023-04-26 08:37:17 UTC'},
      {'co2': 504, 'timestamp': '2023-04-26 08:37:18 UTC'},
      {'co2': 508, 'timestamp': '2023-04-26 08:37:19 UTC'},
      {'co2': 525, 'timestamp': '2023-04-26 08:37:20 UTC'},
      {'co2': 547, 'timestamp': '2023-04-26 08:37:21 UTC'},
      {'co2': 523, 'timestamp': '2023-04-26 08:37:22 UTC'},
      {'co2': 552, 'timestamp': '2023-04-26 08:37:23 UTC'},
      {'co2': 554, 'timestamp': '2023-04-26 08:37:24 UTC'},
      {'co2': 568, 'timestamp': '2023-04-26 08:37:25 UTC'},
      {'co2': 559, 'timestamp': '2023-04-26 08:37:26 UTC'},
      {'co2': 573, 'timestamp': '2023-04-26 08:37:27 UTC'},
      {'co2': 561, 'timestamp': '2023-04-26 08:37:28 UTC'},
      {'co2': 572, 'timestamp': '2023-04-26 08:37:29 UTC'},
      {'co2': 577, 'timestamp': '2023-04-26 08:37:30 UTC'},
      {'co2': 588, 'timestamp': '2023-04-26 08:37:31 UTC'},
      {'co2': 598, 'timestamp': '2023-04-26 08:37:32 UTC'},
      {'co2': 594, 'timestamp': '2023-04-26 08:37:33 UTC'},
      {'co2': 585, 'timestamp': '2023-04-26 08:37:34 UTC'},
      {'co2': 581, 'timestamp': '2023-04-26 08:37:35 UTC'},
      {'co2': 594, 'timestamp': '2023-04-26 08:37:36 UTC'},
      {'co2': 578, 'timestamp': '2023-04-26 08:37:37 UTC'},
      {'co2': 597, 'timestamp': '2023-04-26 08:37:38 UTC'},
      {'co2': 591, 'timestamp': '2023-04-26 08:37:39 UTC'},
      {'co2': 594, 'timestamp': '2023-04-26 08:37:40 UTC'},
      {'co2': 579, 'timestamp': '2023-04-26 08:37:41 UTC'},
      {'co2': 592, 'timestamp': '2023-04-26 08:37:42 UTC'},
      {'co2': 592, 'timestamp': '2023-04-26 08:37:43 UTC'},
      {'co2': 600, 'timestamp': '2023-04-26 08:37:44 UTC'},
      {'co2': 577, 'timestamp': '2023-04-26 08:37:45 UTC'},
      {'co2': 582, 'timestamp': '2023-04-26 08:37:46 UTC'},
      {'co2': 584, 'timestamp': '2023-04-26 08:37:47 UTC'},
      {'co2': 581, 'timestamp': '2023-04-26 08:37:48 UTC'},
      {'co2': 614, 'timestamp': '2023-04-26 08:37:49 UTC'},
      {'co2': 588, 'timestamp': '2023-04-26 08:37:50 UTC'},
      {'co2': 617, 'timestamp': '2023-04-26 08:37:51 UTC'},
      {'co2': 596, 'timestamp': '2023-04-26 08:37:52 UTC'},
      {'co2': 604, 'timestamp': '2023-04-26 08:37:53 UTC'},
      {'co2': 602, 'timestamp': '2023-04-26 08:37:54 UTC'},
      {'co2': 601, 'timestamp': '2023-04-26 08:37:55 UTC'},
      {'co2': 615, 'timestamp': '2023-04-26 08:37:56 UTC'},
      {'co2': 612, 'timestamp': '2023-04-26 08:37:57 UTC'},
      {'co2': 611, 'timestamp': '2023-04-26 08:37:58 UTC'},
      {'co2': 614, 'timestamp': '2023-04-26 08:37:59 UTC'},
      {'co2': 609, 'timestamp': '2023-04-26 08:38:00 UTC'},
      {'co2': 599, 'timestamp': '2023-04-26 08:38:01 UTC'},
      {'co2': 605, 'timestamp': '2023-04-26 08:38:02 UTC'},
      {'co2': 623, 'timestamp': '2023-04-26 08:38:03 UTC'},
      {'co2': 608, 'timestamp': '2023-04-26 08:38:04 UTC'},
      {'co2': 599, 'timestamp': '2023-04-26 08:38:05 UTC'},
      {'co2': 619, 'timestamp': '2023-04-26 08:38:06 UTC'},
      {'co2': 602, 'timestamp': '2023-04-26 08:38:07 UTC'},
    ]

    let ventilationNIDR = computeVentilationNIDR(
      activityGroups,
      normalizedCO2Readings,
      ventilationCO2AmbientPPM,
      roomUsableVolumeCubicMeters,
    )

    // should be about 2052 according to
    // https://ospe-calc.herokuapp.com/Air_Changes_-_Ventilation
    console.log(ventilationNIDR)
    expect(ventilationNIDR['result']['cadr'] > 570).toBe(true);

    expect(ventilationNIDR['result']['cadr'] < 670).toBe(true);
  })
});
