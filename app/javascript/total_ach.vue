<template>
  <div class='item' id='section-total-ach'>
    <br id='total-ach'>
    <br>
    <br>
    <h2>Total ACH</h2>
    <div class='centered'>
      <TotalACHTable
        :measurementUnits='measurementUnits'
        :systemOfMeasurement='systemOfMeasurement'
        :totalFlowRate='totalFlowRate'
        :roomUsableVolume='roomUsableVolume'
        :portableAch='selectedIntervention.computePortableAirCleanerACH()'
        :ventilationAch='selectedIntervention.computeVentilationACH()'
        :uvAch='selectedIntervention.computeUVACH()'
        :cellCSS='cellCSS'
        />
    </div>

    <p>
      Air Changes per Hour (ACH) tells us how much clean air is generated
      relative to the volume of the room. If a device outputs 5 ACH, that means it
      produces clean air that is 5 times the volume of the room in an hour.  Total
      ACH for a room can be computed by summing up the ACH of different types (e.g.
      ventilation, filtration, upper-room germicidal UV).
    </p>

  </div>

</template>

<script>
import TotalACHTable from './total_ach_table.vue'
export default {
  name: 'TotalACH',
  components: {
    TotalACHTable
  },
  data() {
    return {}
  },
  props: {
    measurementUnits: Object,
    systemOfMeasurement: String,
    totalFlowRate: Number,
    roomUsableVolume: Number,
    selectedIntervention: Object,
    cellCSS: Object
  },
  computed: {

  }, methods: {
  }

}
</script>

<style scoped>
</style>
