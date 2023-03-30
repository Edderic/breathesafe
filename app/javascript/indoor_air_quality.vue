<template>
  <DrillDownSection
    title='Indoor Air Quality'
    icon='<span style="font-size: 2em;">💨</span>'
    :showStat='false'
  >
    <p>
      Indoor Air Quality, in the case of preventing airborne transmission of
      pathogens such as COVID, can be improved by the following:

      <ul>
        <li>Remove the source</li>
        <li><span class='italic'>Dilute polluted air</span></li>
      </ul>
    </p>

    <h3>Dilute polluted air</h3>
    <p>
      Since the removal of sources of infection doesn't always happen, we also
      consider doing interventions that 1. assume there is someone infectious in the room,
      and 2. <span class='italic'>dilute</span> the non-zero concentration of infectious
      particles in the air. When an infector is present, the air inside a room is
      dirty to some extent and contains infectious pathogens that are kept airborne
      by tiny particles. That concentration is measured in terms of infectiousness
      over time (e.g. quanta per hour). The total dose inhaled is essentially
      concentration times time (e.g.  quanta -- see the Risk Equation section for
          more details about quanta).
    </p>

    <div class='centered column'>
      <div class='centered'>
        <VentIcon :showText='true'/>
        <PacIcon :showText='false' height='5em' width='5em' />
      </div>
      <p class='fig-title'>Ventilation via open windows and Filtration via Corsi-Rosenthal box, a type of DIY portable air-cleaner</p>
    </div>

    <p>
      The more ventilation, filtration, and UV
      (upper-room germicidal UV or far UV) there is in the room, the more the
      infectious particles gets <span class='italic'>diluted</span>, and the
      overall inhaled amount of quanta is lower. Wearing tight-fitted, high
      filtration efficiency N95 and elastomeric respirators also dilute the
      concentration significantly.  See the Masking Reduction Factor
      section for more details about that. However, below, we'll focus more on
      the effects of increasing ventilation, filtration, and UV.
    </p>

    <h3>Unmixed Air</h3>
    <div class='centered column'>
      <Interaction/>
      <p class='fig-title'>Infector and susceptible entered the room. Infector talks to susceptible for a small amount of time. No fans to mix the air.</p>
    </div>

    <p>
    In the above graph, we show the scenario of an infector talking and the susceptible listening
    to the infector for a few minutes.

    The gradient of colors denote concentration, with the green
    colored areas having the lowest concentration of infectious aerosols, and the
    dark red areas having the highest concentration of infectious aerosols.
    When air is not well-mixed, and an infector is present, short-range
    transmission is very likely. In this scenario, an infector talking, singing, or even just
    breathing can produce a jet of aerosols toward the susceptible, and a
    susceptible can inhale a high dose quickly, and develop an infection in the
    process.
    </p>

    <p>Notice the symmetry. The density above the susceptible's head is the
    same as the densitiy below the susceptible's head. This is because aerosols <span class='italic'>float</span>. They are so light that they <span class='italic'>can float for hours.</span></p>

    <h3>Mixed Air (Initially, in a Smaller Room)</h3>
    <div class='centered column'>
      <InteractionWithFan :early='true'/>
      <p class='fig-title'>Infector and susceptible entered the room. Infector talks to susceptible for a small amount of time. A fan running mixes the air, leading to some dilution.</p>
    </div>

    <p>Mixing the air via fans can lower the inhaled dose for the susceptible. The cleaner sections of the initial graph become polluted. However, the most polluted sections become less polluted. If there is a fan placed in between the infector and the susceptible, the jet of aerosols that were going directly to the susceptible (e.g. as the infector breathes in front of the susceptible) become redirected and are more likely to spread through the room. Instead of inhaling high concentrations of the virus in a very short time (in red), the susceptible can breathe in a smaller concentration of the virus. The total dose that a susceptible gets is concentration times time. One way to lower the dose is by lowering the concentration.</p>

    <h3>Mixed Air (Initially, in a Larger Room)</h3>

    <div class='centered column'>
      <InteractionWithFan :early='true' :largerVolume='true'/>
      <p class='fig-title'>Infector and susceptible interacting for a long
      time, with a fan to mix the air, but no ventilation, filtration, or UV.</p>
    </div>

    <p>Mixing the air while in a larger room leads to lower initial concentration for the susceptible. This is because the larger room has more clean air to begin with than a smaller room.</p>


    <h3>Mixed Air (Later)</h3>
    <div class='centered column'>
      <InteractionWithFan :early='false'/>
      <p class='fig-title'>Infector and susceptible interacting for a long
      time, with a fan to mix the air, but no ventilation, filtration, or UV.</p>
    </div>

    <p>As we've seen, mixing the air initially can lead to dilution. However, when there aren't mitigations in place to remove (e.g. ventilation or filtration) or inactivate viruses in the air (e.g. far UV or Upper Room Germicidal UV), high concentrations of particles containing infectious pathogens can build up everywhere.
<span class='italic'>It is worthwhile to note that the larger the room, the longer it takes to reach this state of high concentration</span>.
</p>

    <h3>Mixed Air with Fan and Air Cleaner</h3>

    <div class='centered column'>
      <InteractionWithFan :early='false' :airCleaner='true'/>
      <p class='fig-title'>Infector and susceptible interacting for a long
      time, with a fan to mix the air, AND portable air cleaner</p>
    </div>

    <p>Using a fan to mix the air, and a portable air cleaner to remove contaminants from the air, the concentration that a susceptible inhales is lower than in the context of not having an air cleaner. Similarly, ventilation and UV could reduce the risk of transmission by decreasing the concentration per inhalation.</p>


    <h3>Recap</h3>

    <p>To recap, we learned through the graphs that we can dilute the concentration several ways:
      <ul>
        <li>More mixing decreases effect of short-range transmission.</li>
        <li>Larger rooms are safer than smaller rooms (at least initially).</li>
        <li>Removal of pathogens in the air means there's less to inhale.</li>
      </ul>
</p>

    <h3>NADR and ACH</h3>
    <p>In the earlier section, we gave an intuitive explanation of what's happening using heatmaps. In this section, we'll explain the recapped points in a more mathematical fashion.</p>
    <p>
      Assuming the air is well-mixed (i.e. fans are blowing around air so that
      the concentration of indoor air pollution is evenly distributed across the
      room), the concentration that a susceptible inhales over time is affected by
      two parameters:
      <ul>
        <li>non-infectious air delivery rate (NADR)</li>
        <li>Air Changes per Hour (ACH)</li>
      </ul>
    </p>

    <p>
      NADR is measured in volume per time (e.g. cubic feet per minute). It is increased
      by improving ventilation and supplementing via filtration (with portable
      air cleaners), and UV (upper-room germicidal UV or far UV). <span
      class='italic'>In the long run, the higher the NADR, the lower the dose that
      one gets</span>. As time goes by, the concentration
      approaches some value, which is called the steady-state concentration,
      and NADR affects this value. <span class='italic'>The higher the NADR,
      the lower the steady-state concentration, and vice versa.</span>
    </p>
    <p>
      ACH, on the other hand, is NADR divided by the volume of the room. ACH
      affects how fast the concentration gets to the steady state (i.e. the flattened part of the curve). <span
      class='italic'>The higher the ACH, the faster one reaches the steady state
      concentration.</span>

    </p>

    <LineGraph
      :lines="[baseCase, largerVol, highNADR]"
      :ylim='[0, 0.09]'
      title='Contaminant concentration over time'
      xlabel='Time (min)'
      ylabel='Contaminant concentration (quanta / min)'
      :legendStartOffset='[0.45, 0.55]'
      :roundXTicksTo='0'
    />

    <p>
      If the volume of the room is relatively small and
      NADR is relatively big (i.e. high ACH), then it does not take a lot of time to reach
      steady state. On the other hand, if the volume of the room is relatively
      big and NADR is relatively small (i.e. low ACH), then it takes a while to reach steady state.
      See the graph above to see how having different values of NADR and ACH
      interact to produce concentration curves. We assume that a susceptible
      and infector come in at the same time and stay at the venue, and
      everything else is kept constant. The dose is the area under the concentration
      curve.
      <span class='italic'>
      The smaller that area is, the less likely
        susceptibles will be infected.
      </span>
    </p>


    <h3>NADR & ACH Graphs</h3>
    <p>In the graph above, we compare different concentration curves. The first curve in red, called "base case," involves a certain non-infectious air delivery rate and volume. The curve in green, called "larger vol., same NADR," has the same non-infectious air delivery rate as the base case, but has larger volume -- double that of the base case. Since volume is larger, ACH is decreased, which makes it take longer to hit the steady state concentration -- same as the base case. </p>
    <p>
How is this information useful? Assuming that you have two rooms and the same NADR for both, but one is bigger than the other, and that the infector comes in at the same time as you, a susceptible, and assuming well-mixed air (i.e. fans are blowing air around), the room will initially be safer for a period of time. <span class='italic'>Using larger spaces is good because in the beginning, there is more clean air to begin with that dilutes the dirty air. However, in the long run, the concentration of dirty air is dictated by NADR. Both curves will approach the same steady state, given the same NADR.</span> Here we can see that a decrease in ACH (due to an increase in volume) isn't necessarily a bad thing.
    </p>
    <p>In the graph above, we also display the scenario where NADR is increased (doubled) relative to the base case, but volume is kept the same (in blue). This leads to a situation where the steady state concentration is lower, and it's faster to reach the steady state. Increasing NADR decreases the state state concentration (i.e. safer in the long run), and increases ACH, which means that it's faster to reach steady state.</p>
    <p>In conclusion, we see how NADR and volume interact to decrease the concentration of infectious, pathogenic air.
      <ul>
        <li><span class='italic'>Prefer larger spaces over smaller spaces.</span> Larger spaces are safer than smaller spaces, at least for an initial period. Very large spaces will have low ACH, but that's not necessarily a bad thing with respect to risk.</li>
        <li><span class='italic'>Prefer higher NADR over lower NADR.</span> The higher the NADR, the less risky a venue is. People will be inhaling lower concentrations of dirty air with higher NADR in the long run.</li>
      </ul>
    </p>
  </DrillDownSection>
</template>

<script>
import { useMainStore } from './stores/main_store';
import { useProfileStore } from './stores/profile_store';
import { useEventStores } from './stores/event_stores';
import { useEventStore } from './stores/event_store';
import CircularButton from './circular_button.vue'
import DrillDownSection from './drill_down_section.vue'
import Interaction from './interaction.vue'
import InteractionWithFan from './interaction_with_fan.vue'
import LineGraph from './line_graph.vue'
import RapidTest from './rapid_test.vue'
import PacIcon from './pac_icon.vue'
import VentIcon from './vent_icon.vue'
import { genConcCurve } from './misc'
import { mapWritableState, mapState, mapActions } from 'pinia';

export default {
  name: '',
  components: {
    CircularButton,
    DrillDownSection,
    Interaction,
    InteractionWithFan,
    LineGraph,
    PacIcon,
    RapidTest,
    VentIcon,
  },
  data() {
    return { show: false }
  },
  props: {
  },
  computed: {
    baseCase() {
      let curve = genConcCurve({
        roomUsableVolumeCubicMeters: 10,
        c0: 0,
        generationRate: 1.6,
        cadr: 20,
        cBackground: 0,
        windowLength: 180
      })

      let collection = []
      for (let i = 0; i < curve.length; i++) {
        collection.push([i, curve[i]])
      }

      return { points: collection, color: 'red', legend: 'base case' }
    },
    largerVol() {
      let curve = genConcCurve({
        roomUsableVolumeCubicMeters: 20,
        c0: 0,
        generationRate: 1.6,
        cadr: 20,
        cBackground: 0,
        windowLength: 180
      })

      let collection = []
      for (let i = 0; i < curve.length; i++) {
        collection.push([i, curve[i]])
      }

      return { points: collection, color: 'green', legend: 'larger vol., same NADR (lower ACH)' }
    },
    highNADR() {
      let curve = genConcCurve({
        roomUsableVolumeCubicMeters: 10,
        c0: 0,
        generationRate: 1.6,
        cadr: 40,
        cBackground: 0,
        windowLength: 180
      })

      let collection = []
      for (let i = 0; i < curve.length; i++) {
        collection.push([i, curve[i]])
      }

      return { points: collection, color: 'blue', legend: 'same vol., higher NADR (higher ACH)' }
    },


  },
  async created() {
    // TODO: fire and forget. Make asynchronous.
    // this.debugVentilationCalc()

  },
  data() {
  },
  methods: {



  }

}
</script>

<style scoped>
  .centered {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .row {
    margin: 1em 0;
    display: flex;
    flex-direction: row;
  }


  .explainer {
    max-width: 25em;
    margin: 0 auto;
  }

  .title {
    max-width: 12em;
    margin-left: 1em;
  }
  .italic {
    font-style: italic;
  }

  .showHideButton {
    margin-left: 1em;
    margin-right: 1em;
  }

  th, td {
    border: 1px solid gray;
    padding: 0.25em;
    text-align: center;
  }

  .column {
    display: flex;
    flex-direction: column;
  }

  .fig-title {
    font-style: italic;
  }

</style>
