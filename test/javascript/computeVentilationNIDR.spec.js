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
      {'co2': 476, 'timestamp': '2023-04-26 08:38:10 UTC'},
      {'co2': 488, 'timestamp': '2023-04-26 08:39:12 UTC'},
      {'co2': 500, 'timestamp': '2023-04-26 08:40:13 UTC'},
      {'co2': 487, 'timestamp': '2023-04-26 08:41:14 UTC'},
      {'co2': 490, 'timestamp': '2023-04-26 08:42:15 UTC'},
      {'co2': 480, 'timestamp': '2023-04-26 08:43:16 UTC'},
      {'co2': 525, 'timestamp': '2023-04-26 08:48:17 UTC'},
      {'co2': 504, 'timestamp': '2023-04-26 08:49:18 UTC'},
      {'co2': 508, 'timestamp': '2023-04-26 08:50:19 UTC'},
      {'co2': 525, 'timestamp': '2023-04-26 08:51:20 UTC'},
      {'co2': 547, 'timestamp': '2023-04-26 08:52:21 UTC'},
      {'co2': 552, 'timestamp': '2023-04-26 08:53:23 UTC'},
      {'co2': 554, 'timestamp': '2023-04-26 08:54:24 UTC'},
      {'co2': 559, 'timestamp': '2023-04-26 08:55:26 UTC'},
      {'co2': 573, 'timestamp': '2023-04-26 08:56:27 UTC'},
      {'co2': 561, 'timestamp': '2023-04-26 08:57:28 UTC'},
      {'co2': 572, 'timestamp': '2023-04-26 08:58:29 UTC'},
      {'co2': 577, 'timestamp': '2023-04-26 08:59:30 UTC'},
      {'co2': 588, 'timestamp': '2023-04-26 09:00:31 UTC'},
      {'co2': 598, 'timestamp': '2023-04-26 09:01:32 UTC'},
      {'co2': 594, 'timestamp': '2023-04-26 09:02:33 UTC'},
      {'co2': 581, 'timestamp': '2023-04-26 09:03:35 UTC'},
      {'co2': 594, 'timestamp': '2023-04-26 09:04:36 UTC'},
      {'co2': 578, 'timestamp': '2023-04-26 09:05:37 UTC'},
      {'co2': 597, 'timestamp': '2023-04-26 09:06:38 UTC'},
      {'co2': 591, 'timestamp': '2023-04-26 09:07:39 UTC'},
      {'co2': 579, 'timestamp': '2023-04-26 09:08:41 UTC'},
      {'co2': 592, 'timestamp': '2023-04-26 09:09:43 UTC'},
      {'co2': 600, 'timestamp': '2023-04-26 09:10:44 UTC'},
      {'co2': 577, 'timestamp': '2023-04-26 09:11:45 UTC'},
      {'co2': 582, 'timestamp': '2023-04-26 09:12:46 UTC'},
      {'co2': 581, 'timestamp': '2023-04-26 09:13:48 UTC'},
      {'co2': 614, 'timestamp': '2023-04-26 09:14:49 UTC'},
      {'co2': 617, 'timestamp': '2023-04-26 09:15:51 UTC'},
      {'co2': 596, 'timestamp': '2023-04-26 09:16:52 UTC'},
      {'co2': 604, 'timestamp': '2023-04-26 09:17:53 UTC'},
      {'co2': 615, 'timestamp': '2023-04-26 09:18:56 UTC'},
      {'co2': 612, 'timestamp': '2023-04-26 09:19:57 UTC'},
      {'co2': 614, 'timestamp': '2023-04-26 09:20:59 UTC'},
      {'co2': 599, 'timestamp': '2023-04-26 09:21:01 UTC'},
      {'co2': 623, 'timestamp': '2023-04-26 09:22:03 UTC'},
      {'co2': 608, 'timestamp': '2023-04-26 09:23:04 UTC'},
      {'co2': 599, 'timestamp': '2023-04-26 09:24:05 UTC'},
      {'co2': 602, 'timestamp': '2023-04-26 09:25:07 UTC'},
    ]

    let ventilationNIDR = computeVentilationNIDR(
      activityGroups,
      normalizedCO2Readings,
      ventilationCO2AmbientPPM,
      roomUsableVolumeCubicMeters,
    )

    // should be about 2052 according to
    // https://ospe-calc.herokuapp.com/Air_Changes_-_Ventilation
    expect(ventilationNIDR['result']['cadr'] > 550).toBe(true);

    expect(ventilationNIDR['result']['cadr'] < 600).toBe(true);
  })

  test('just like test 1 but some data redacted to simulate different sampling rates', () => {
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
    // have some irregularity with sampling with respect to time
    let normalizedCO2Readings = [
      {'co2': 476, 'timestamp': '2023-04-26 08:38:10 UTC'},
      {'co2': 488, 'timestamp': '2023-04-26 08:39:12 UTC'},
      {'co2': 480, 'timestamp': '2023-04-26 08:43:16 UTC'},
      {'co2': 525, 'timestamp': '2023-04-26 08:48:17 UTC'},
      {'co2': 504, 'timestamp': '2023-04-26 08:49:18 UTC'},
      {'co2': 508, 'timestamp': '2023-04-26 08:50:19 UTC'},
      {'co2': 525, 'timestamp': '2023-04-26 08:51:20 UTC'},
      {'co2': 547, 'timestamp': '2023-04-26 08:52:21 UTC'},
      {'co2': 573, 'timestamp': '2023-04-26 08:56:27 UTC'},
      {'co2': 561, 'timestamp': '2023-04-26 08:57:28 UTC'},
      {'co2': 572, 'timestamp': '2023-04-26 08:58:29 UTC'},
      {'co2': 577, 'timestamp': '2023-04-26 08:59:30 UTC'},
      {'co2': 588, 'timestamp': '2023-04-26 09:00:31 UTC'},
      {'co2': 598, 'timestamp': '2023-04-26 09:01:32 UTC'},
      {'co2': 578, 'timestamp': '2023-04-26 09:05:37 UTC'},
      {'co2': 597, 'timestamp': '2023-04-26 09:06:38 UTC'},
      {'co2': 591, 'timestamp': '2023-04-26 09:07:39 UTC'},
      {'co2': 579, 'timestamp': '2023-04-26 09:08:41 UTC'},
      {'co2': 592, 'timestamp': '2023-04-26 09:09:43 UTC'},
      {'co2': 600, 'timestamp': '2023-04-26 09:10:44 UTC'},
      {'co2': 614, 'timestamp': '2023-04-26 09:14:49 UTC'},
      {'co2': 617, 'timestamp': '2023-04-26 09:15:51 UTC'},
      {'co2': 596, 'timestamp': '2023-04-26 09:16:52 UTC'},
      {'co2': 604, 'timestamp': '2023-04-26 09:17:53 UTC'},
      {'co2': 615, 'timestamp': '2023-04-26 09:18:56 UTC'},
      {'co2': 612, 'timestamp': '2023-04-26 09:19:57 UTC'},
      {'co2': 608, 'timestamp': '2023-04-26 09:23:04 UTC'},
      {'co2': 599, 'timestamp': '2023-04-26 09:24:05 UTC'},
      {'co2': 602, 'timestamp': '2023-04-26 09:25:07 UTC'},
    ]

    let ventilationNIDR = computeVentilationNIDR(
      activityGroups,
      normalizedCO2Readings,
      ventilationCO2AmbientPPM,
      roomUsableVolumeCubicMeters,
    )

    // should be about 2052 according to
    // https://ospe-calc.herokuapp.com/Air_Changes_-_Ventilation
    expect(ventilationNIDR['result']['cadr'] > 550).toBe(true);

    expect(ventilationNIDR['result']['cadr'] < 600).toBe(true);
  })
});
