import { defineStore } from 'pinia'

// useStore could be anything like useUser, useCart
// the first argument is a unique id of the store across your application
export const useEventStore = defineStore('events', {
  state: () => ({
    roomName: "",
    roomLength: "",
    roomHeight: "",
    roomWidth: "",
    duration: "",
    numberOfPeople: '',
    carbonDioxideSteadyState: '',
    carbonDioxideAmbient: '420',
    carbonDioxideMeasurementDevice: '',
    lengthMeasurementType: 'feet',
    airDeliveryRateMeasurementType: 'cubic feet per minute',
    airDeliveryRate: "",
    singlePassFiltrationEfficiency: "",
    percentOfPeopleWithElastomerics: "",
    percentOfPeopleWithN95s: "",
    percentOfPeopleWithClothSurgicalMasks: "",
    percentOfPeopleWithNoMasks: "",
    eventPrivacy: 'public',
    infectorActivityTypeMapping: {
      "Unknown": 'NA',
      "Resting – Oral breathing": 1,
      "Resting – Speaking": 4.7,
      "Resting – Loudly speaking": 30.3,
      "Standing – Oral breathing": 1.2,
      "Standing – Speaking": 5.7,
      "Standing – Loudly speaking": 32.6,
      "Light exercise – Oral breathing": 2.8,
      "Light exercise – Speaking": 13.2,
      "Light exercise – Loudly speaking": 85,
      "Heavy exercise – Oral breathing": 6.8,
      "Heavy exercise – Speaking": 31.6,
      "Heavy exercise – Loudly speaking": 204,
    },
    infectorActivity: "Unknown",
    susceptibleActivities: [
      "Unknown",
      "Sleep or Nap",
      "Sedentary / Passive",
      "Light Intensity",
      "Moderate Intensity",
      "High Intensity",
    ],
    susceptibleActivity: "Unknown",
    susceptibleAgeGroup: "Unknown",
    susceptibleAgeGroups: [
      "Unknown",
      "Birth to <1",
      "1 to <2",
      "2 to <3",
      "3 to <6",
      "6 to <11",
      "11 to <16",
      "16 to <21",
      "21 to <31",
      "31 to <41",
      "41 to <51",
      "51 to <61",
      "61 to <71",
      "71 to <81",
      ">= 81",
    ],
  }),
  actions: {
    save() {
    }
  }
});
