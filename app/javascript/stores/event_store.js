import { defineStore } from 'pinia'
import { useEventStores } from './event_stores.js'
import { cubicFeetPerMinuteTocubicMetersPerHour, feetToMeters, generateUUID } from '../misc'

// useStore could be anything like useUser, useCart
// the first argument is a unique id of the store across your application
export const useEventStore = defineStore('event', {
  state: () => ({
    placeData: {
      'place_id': "",
      'formatted_address': "",
      'center': {
        'lat': 0,
        'lng': 0
      }
    },
    roomName: "",
    roomLength: "",
    roomHeight: "",
    roomWidth: "",
    roomWidthMeters: "",
    roomLengthMeters: "",
    roomHeightMeters: "",
    roomLength: "",
    duration: "",
    ventilationCO2AmbientPPM: 420,
    ventilationCO2SteadyStatePPM: '',
    ventilationCO2MeasurementDeviceName: '',
    ventilationCO2MeasurementDeviceModel: '',
    ventilationCO2MeasurementDeviceSerial: '',
    carbonDioxideMonitors: [],
    systemOfMeasurement: 'imperial',
    lengthMeasurementType: 'feet',
    airDeliveryRate: "",
    singlePassFiltrationEfficiency: "",
    private: 'public',
    activityGroups: [],
    carbonDioxideActivities: {
      "Calisthenics—light effort": 2.8,
      "Calisthenics—moderate effort": 3.8,
      "Calisthenics—vigorous effort": 8.0,
      "Child care": 2.5, // 2 - 3
      "Cleaning, sweeping—moderate effort": 3.8,
      "Custodial work—light": 2.3,
      "Dancing—aerobic, general": 7.3,
      "Dancing—general": 7.8,
      "Health club exercise classes—general": 5.0,
      "Kitchen activity—moderate effort": 3.3,
      "Lying or sitting quietly": 1.0,
      "Sitting reading, writing, typing": 1.3,
      "Sitting at sporting event as spectator": 1.5,
      "Sitting tasks, light effort (e.g, office work)": 1.5,
      "Sitting quietly in religious service": 1.3,
      "Sleeping": 0.95,
      "Standing quietly": 1.3,
      "Standing tasks, light effort (e.g, store clerk, filing)": 3.0,
      "Walking, less than 2 mph, level surface, very slow": 2.0,
      "Walking, 2.8 mph to 3.2 mph, level surface, moderate pace": 3.5,
    },
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
    maskTypes: [
      'None',
      'Cloth / Surgical',
      'N95 - unfitted',
      'N95 - fitted',
      'Elastomeric N95',
      'Elastomeric N99',
      'Elastomeric P100'
    ],
    portableAirCleaners: [],
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
    ageGroups: [
      "Unknown",
      "1 to <3",
      "3 to <6",
      "6 to <11",
      "11 to <16",
      "16 to <21",
      "21 to <30",
      "30 to <40",
      "40 to <50",
      "50 to <60",
      "60 to <70",
      "70 to <80",
      ">= 80",
    ],
    rapidTestResults: [
      "Unknown",
      "Negative",
      "Positive"
    ],
    ventilationNotes: "",
    startDatetime: new Date()
  }),
  getters: {
    findActivityGroup: (state) => {
      return (activityGroupId) => state.activityGroups.find((ag) => ag.id == activityGroupId)
    },
    findPortableAirCleaningDevice: (state) => {
      return (portableAirCleanerId) => state.portableAirCleaners.find((p) => p.id == portableAirCleanerId)
    },
  },
  actions: {
    addPortableAirCleaner() {
      this.portableAirCleaners.unshift({
        'id': generateUUID(),
        'singlePassFiltrationEfficiency': "",
        'airDeliveryRate': "",
        'airDeliveryRateCubicMetersPerHour': "",
      })
    },
    updateRoomDimensionsMeters(measurementUnits) {
      this.roomLengthMeters = convertLengthBasedOnMeasurementType(
        this.roomLength,
        measurementUnits.lengthMeasurementType,
        'meters'
      )
      this.roomWidthMeters = convertLengthBasedOnMeasurementType(
        this.roomWidth,
        measurementUnits.lengthMeasurementType,
        'meters'
      )
      this.roomHeightMeters = convertLengthBasedOnMeasurementType(
        this.roomHeight,
        measurementUnits.lengthMeasurementType,
        'meters'
      )
    },
    setCubicMetersPerHour() {
      for (let portableAirCleaner of this.portableAirCleaners) {
        portableAirCleaner['airDeliveryRateCubicMetersPerHour'] = cubicFeetPerMinuteTocubicMetersPerHour(
          this.airDeliveryRateMeasurementType,
          portableAirCleaner['airDeliveryRate']
        );
      }
    }
  }
});
