<template>
  <div class='col border-showing scrollable'>
    <div class='container'>
      <h3 class='subsection'>Analysis & Recommendations for {{this.roomName}}</h3>
      <div class='centered col'>
        <div class='container'>
          <h4>Introduction</h4>
          <p>
            While vaccines prevent deaths and hospitalizations to a great degree, they by themselves are not so great at
            <a href="https://www.nejm.org/doi/full/10.1056/NEJMoa2119451">
            preventing symptomatic infections
            </a>
            and
            <a href="https://www.nature.com/articles/d41586-022-01453-0#:~:text=The%20researchers%20found%20that%20vaccination,found%20much%20higher%20protection%20rates."
            >
            long COVID
            </a>.
            As of August 2022, it is estimated that
            <a
            href="https://www.npr.org/2022/07/31/1114375163/long-covid-longhaulers-disability-labor-ada"
            >
            4 million employees in the U.S. are out of work due to long-COVID.
            </a>

            Decreasing the risk of transmission will decrease the
            likelihood of contracting COVID, and therefore,
            <a href="https://www.science.org/content/article/what-causes-long-covid-three-leading-theories"
            >
            long-COVID</a>.

            Doing so will also make spaces become more
            accessible to
            <a href="https://www.theatlantic.com/health/archive/2022/02/covid-pandemic-immunocompromised-risk-vaccines/622094/"
            >the millions of immunocompromised people in the U.S.</a>
            We need a "vaccines-plus" strategy, not just a "vaccines-only" strategy, using non-pharmaceutical interventions such as cleaning the air, masking, and rapid testing.

            Investing in infrastructure to clean the air will make the spaces
            we inhabit <a href="https://www.science.org/doi/10.1126/science.abd9149">be
            more resilient not just to COVID-19, but also to other respiratory viruses</a>.
          </p>
          <p>In the interventions section below, there are many proven ways to decrease the risk of contracting COVID-19 and other airborne viruses. One would be able to see the interventions to clean the air. I introduce a metric for cost benefit </p>
          <h4>Modeling</h4>

          <p>The model used here is a variant of
          <a href="https://pubs.acs.org/doi/full/10.1021/acs.est.1c06531">
          Peng et.al.'s Practical Indicators for Risk of Airborne Transmission in Shared Indoor Environments and Their Application to COVID-19 Outbreaks
          </a>. We assume that an infector is present as it allows us to test the resiliency of environmental
            and behavioral interventions in decreasing the risk
            of transmission of respiratory viruses.
          </p>
          <p>
          Put simply, the risk of transmission is proportional to the generation rate of
          infectious aerosols from infector(s) and is inversely related to the removal rate of said
          aerosols. The faster the generation rate of infectious aerosols from infectors,
          the higher the risk. On the other hand, the faster the rate of air cleaning in
          the air, the lower the risk.
          </p>
          <h4>Risky behaviors and environments</h4>
          <p>Actions that increase risk:
            <ul>
              <li>
              infector not wearing a mask with high filtration efficiency. N95
              and Elastomeric masks block a lot more particles of aerosols that contain the
              virus than cloth and surgical.
              </li>
              <li>
              aerosol activity. Singing produces more aerosols than talking,
              which in turn produces more aerosols than oral breathing.
              </li>
              <li>
              exercise. Exercise encourages more exhalation. If there's an
              infector doing exercise, they will generate more respiratory particles in the
              air more so than someone who is at rest.
              </li>
              <li>inherent infectiousness of the virus. Alpha &lt; Delta &lt; Omicron. </li>
            </ul>

          </p>
          <h4>Safer behaviors and environments</h4>
            <p>
            In contrast, cleaning the air efficiently and quickly lowers the
            probability of infection. Air is cleaner when:

            <ul>
              <li>
              air is filtered through masking.
              If an infector is wearing a tight-fitting mask with a high
              filtration efficiency (e.g. N95 and Elastomeric masks), then there are less
              infectious particles in the air for susceptibles to breathe in.
              Likewise, if susceptibles are wearing such masks, they can significantly reduce
              their inhalation dose.
               </li>
              <li>
              HEPA or MERV 13 filtration with powerful fans are used. Portable
              air cleaning technologies like the DIY Corsi-Rosenthal box or commercial ones
              with comparable or higher clean air delivery rates (CADR) could quickly remove
              particles from the air that contain the virus.
              </li>
              <li>
              ventilation is increased. Increasing the amount of air exchanged
              from outside to inside (e.g. by opening windows) discourages build up of
              infectious aerosols in a room.
              </li>
              <li>
              Irradiation technologies are put in place to deactivate the virus while
              in the air (e.g. Upper-room UV).
              </li>
              <li>
              susceptibles inhale more slowly (e.g. through resting instead of
              doing heavy exercise while an infector is present). The less breaths a
              susceptible takes, the less infectious dose one can receive.
              </li>
            </ul>
          </p>

          <p>
              We assume that the air is well-mixed (i.e. COVID particles are
              spread evenly throughout the space) and that people are far apart
              (6 ft or more). If people are far apart, then they are less likely to breathe
              in a jet of aerosols from an infector, and increases the effectiveness of
              the environment (e.g. air cleaning through ventilation, filtration, deactivation).
              <span class='bold'>
                If this assumption does not hold in practice for this space, then the estimates of risk can be thought of as lower-bound risks.
              </span>
          </p>
          <p>

            The assessments below assume that an infector is present and is
            doing the riskiest recorded behaviors. For example, the model assumes that the
            infector is wearing the riskiest mask (i.e. the mask with the worst fit and
            filtration efficiency) and is also doing the riskiest aerosol generation activity
            recorded (e.g. loudly talking).
          </p>

          <h4>Risk Assessment</h4>
          <div class='centered'>
            <table>
              <tr>
                <th></th>
                <th>1 hour</th>
                <th>8 hours</th>
                <th>40 hours</th>
                <th>80 hours</th>
              </tr>

              <tr>
                <th>Risk</th>
                <ColoredCell
                    v-if="nullIntervention"
                    :colorScheme="riskColorScheme"
                    :maxVal=1
                    :value='nullIntervention.computeRiskRounded()'
                    :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em'}"
                />
                <ColoredCell
                    v-if="nullIntervention"
                    :colorScheme="riskColorScheme"
                    :maxVal=1
                    :value='roundOut(1 - (1-nullIntervention.computeRiskRounded())**8, 6)'
                    :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em'}"
                />
                <ColoredCell
                    v-if="nullIntervention"
                    :colorScheme="riskColorScheme"
                    :maxVal=1
                    :value='roundOut(1 - (1-nullIntervention.computeRiskRounded())**40, 6)'
                    :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em'}"
                />
                <ColoredCell
                    v-if="nullIntervention"
                    :colorScheme="riskColorScheme"
                    :maxVal=1
                    :value='roundOut(1 - (1-nullIntervention.computeRiskRounded())**80, 6)'
                    :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em'}"
                />
              </tr>
              <tr>
                <th>Average # of Susceptibles Infected under Max Occupancy</th>
                <ColoredCell
                    v-if="nullIntervention"
                    :colorScheme="averageInfectedPeopleInterpolationScheme"
                    :maxVal=1
                    :text='roundOut(this.maximumOccupancy * nullIntervention.computeRiskRounded(), 1)'
                    :value='this.maximumOccupancy * nullIntervention.computeRiskRounded()'
                    :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em'}"
                />
                <ColoredCell
                    v-if="nullIntervention"
                    :colorScheme="averageInfectedPeopleInterpolationScheme"
                    :maxVal=1
                    :value='roundOut(this.maximumOccupancy* (1 - (1-nullIntervention.computeRiskRounded())**8), 1)'
                    :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em'}"
                />
                <ColoredCell
                    v-if="nullIntervention"
                    :colorScheme="averageInfectedPeopleInterpolationScheme"
                    :maxVal=1
                    :value='roundOut(this.maximumOccupancy* (1 - (1-nullIntervention.computeRiskRounded())**40), 1)'
                    :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em'}"
                />
                <ColoredCell
                    v-if="nullIntervention"
                    :colorScheme="averageInfectedPeopleInterpolationScheme"
                    :maxVal=1
                    :value='roundOut(this.maximumOccupancy* (1 - (1-nullIntervention.computeRiskRounded())**80), 1)'
                    :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em'}"
                />
              </tr>
            </table>
          </div>

          <p>
            <span>
              In 1 hour, a susceptible's risk is <ColoredCell
                  v-if="nullIntervention"
                  :colorScheme="riskColorScheme"
                  :maxVal=1
                  :value='nullIntervention.computeRiskRounded()'
                  :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em'}"
              />
            </span>, and if we repeat this many times under this assumption,
            <span>
            we should find on average that
                <ColoredCell
                    v-if="nullIntervention"
                    :colorScheme="averageInfectedPeopleInterpolationScheme"
                    :maxVal=1
                    :text='roundOut(this.maximumOccupancy * nullIntervention.computeRiskRounded(), 1)'
                    :value='this.maximumOccupancy * nullIntervention.computeRiskRounded()'
                    :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em'}"
                />
            </span> susceptibles would get infected.
            <span> In 8 hours of exposure, the risk jumps to <ColoredCell
                    v-if="nullIntervention"
                    :colorScheme="riskColorScheme"
                    :maxVal=1
                    :value='roundOut(1 - (1-nullIntervention.computeRiskRounded())**8, 6)'
                    :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em'}"
                />
            </span>. Assuming max occupancy (with the same susceptibles staying throughout),
            <span>
                <ColoredCell
                    v-if="nullIntervention"
                    :colorScheme="averageInfectedPeopleInterpolationScheme"
                    :maxVal=1
                    :text='roundOut(this.maximumOccupancy * (1 - (1-nullIntervention.computeRiskRounded())**8), 1)'
                    :value='this.maximumOccupancy * nullIntervention.computeRiskRounded()'
                    :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em'}"
                />
            </span> susceptibles would get infected, on average.
            <span>
              It would be very surprising if in <ColoredCell
                    v-if="nullIntervention"
                    :colorScheme="riskColorScheme"
                    :maxVal=1
                    :value='roundOut(nullIntervention.durationToLikelyInfection(), 1)'
                    :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em'}"
                /> hours of exposure, a susceptible doesn't get infected (99% probability).
            </span>
          </p>

          <h4>Behaviors</h4>

          <p>
            <span>
            The riskiest aerosol generation activity is <ColoredCell
                  :colorScheme="riskiestAerosolGenerationActivityScheme"
                  :maxVal=1
                  :value='aerosolActivityToFactor(riskiestPotentialInfector["aerosolGenerationActivity"])'
                  :text='riskiestPotentialInfector["aerosolGenerationActivity"]'
                  :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em' }"
              /> so we assume that the infector in the risk calculations above is doing this.
            </span>


            <span>The worst case inhalation activity is <ColoredCell
                  :colorScheme="inhalationActivityScheme"
                  :maxVal=1
                  :value='worstCaseInhalation["inhalationFactor"]'
                  :text='worstCaseInhalation["inhalationActivity"]'
                  :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em' }"
              /> so we assume that susceptibles in the risk calculations above are doing this.
            </span>

            Choosing activities where an infector is quiet and at rest, along
            with susceptibles being at rest, could decrease the risk of
            airborne transmission.
          </p>
        </div>

      </div>

      <div class='container'>
        <h4>Masking</h4>
        <div class='centered'>
          <HorizontalStackedBar
            :values="maskingValues"
            :colors="maskingColors"
          />
        </div>

        <p>The riskiest mask recorded for this measurement is <span><ColoredCell
              :colorScheme="riskiestMaskColorScheme"
              :maxVal=1
              :value='riskiestMask["maskPenetrationFactor"]'
              :text='riskiestMask["maskType"]'
              :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em' }"
          /></span>, so susceptibles are assumed to be wearing these (unless specified otherwise in the Interventions section).
         </p>

        <h4>Clean Air Delivery Rate</h4>

        <p>
          Air Changes per Hour (ACH) tells us how much clean air is generated
          relative to the volume of the room. If a device outputs 5 ACH, that means it
          produces clean air that is 5 times the volume of the room in an hour.  Total
          ACH for a room can be computed by summing up the ACH of different types (e.g.
          ventilation, filtration, upper-room germicidal UV).
        </p>
      </div>


      <div class='container'>
        <div class='centered'>
          <table>
            <tr>
              <th class='col centered'>
                <span>Total ACH</span>
                <span class='font-light'>(1 / h)</span>
              </th>
              <th></th>
              <th class='col centered'>
                <span>Ventilation ACH</span>
                <span class='font-light'>(1 / h)</span>
              </th>
              <th></th>
              <th class='col centered'>
                <span>Portable ACH</span>
                <span class='font-light'>(1 / h)</span>
              </th>
            </tr>
            <tr>
              <ColoredCell
                :colorScheme="colorInterpolationSchemeTotalAch"
                :maxVal=1
                :value='totalAchRounded'
                :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '2em' }"
              />
              <td>=</td>
              <ColoredCell
                :colorScheme="colorInterpolationSchemeTotalAch"
                :maxVal=1
                :value='ventilationAchRounded'
                :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '2em' }"
              />
              <td>+</td>
              <ColoredCell
                :colorScheme="colorInterpolationSchemeTotalAch"
                :maxVal=1
                :value='portableAchRounded'
                :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '2em' }"
              />
            </tr>
          </table>
        </div>
      </div>

      <div class='centered'>
        <table>
          <tr>
            <th class='col centered'>
              <span>Clean Air Delivery Rate</span>
              <span class='font-light'>({{this.measurementUnits.airDeliveryRateMeasurementTypeShort}})</span>
            </th>
            <th></th>
            <th class='col centered'>
              <span>Unoccupied Room Volume</span>
              <span class='font-light'>({{this.measurementUnits.cubicLengthShort}})</span>
            </th>
            <th></th>
            <th class='col centered'>
              <span>Total ACH</span>
              <span class='font-light'>(1 / h)</span>
            </th>
            <th v-if="systemOfMeasurement == 'imperial'"></th>
            <th class='col centered' v-if="systemOfMeasurement == 'imperial'">
              <span></span>
              <span class='font-light'>(min / h)</span>
            </th>
          </tr>
          <tr>
            <ColoredCell
              :colorScheme="colorInterpolationSchemeRoomVolume"
              :maxVal=1
              :value='totalFlowRateRounded'
              :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '2em' }"
            />
            <td>=</td>
            <ColoredCell
              :colorScheme="colorInterpolationSchemeRoomVolume"
              :maxVal=1
              :value='roomUsableVolumeRounded'
              :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '2em' }"
            />
            <td>x</td>
            <ColoredCell
              :colorScheme="colorInterpolationSchemeTotalAch"
              :maxVal=1
              :value='totalAchRounded'
              :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '2em' }"
            />
            <td v-if="systemOfMeasurement == 'imperial'">/</td>
            <ColoredCell
              v-if="systemOfMeasurement == 'imperial'"
              :colorScheme="colorInterpolationSchemeTotalAch"
              :maxVal=1
              :value='60'
              :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '2em', 'background-color': 'grey'}"
            />
          </tr>
        </table>
      </div>

      <div class='container'>
        <p>
        A combination of larger rooms along with high ACH can reduce the risk
        of contracting COVID-19 and other airborne viruses. The product of the two
        gives us the Clean Air Delivery Rate (CADR). The higher, the safer the
        environment.
        </p>

        <p>
          <span>If everyone in the room wore {{this.maskSuggestion['type']}} masks such as the <a :href="maskSuggestion['website']">{{ this.maskSuggestion['name']}}</a> on top of {{ this.numSuggestedAirCleaners }} {{ this.airCleanerSuggestion.plural }} for air cleaning, long-range transmission risk goes down </span> to
          <ColoredCell
            :colorScheme="riskColorScheme"
            :maxVal=1
            :value='riskTransmissionOfUnmaskedInfectorToUnmaskedSusceptibleWithSuggestedAirCleanersAndMasks'
            :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em', 'display': 'inline-block' }"
          />. The cost of <a :href="maskSuggestion['website']">{{ this.maskSuggestion['name']}}</a> is ${{ this.maskSuggestion['initialCostUSD']}} per person, with a recurring cost of ${{ this.maskSuggestion['recurringCostUSD']}} every {{ this.maskSuggestion['recurringCostDuration']}} per person.
        </p>

        <h4>Interventions</h4>
        <div class='container centered'>
          <label>Number of people to invest in (e.g. employees)</label>
          <input :value='numPeopleToInvestIn' @change='setNumPeople'>
        </div>

        <table>
          <tr>
            <th>Investments</th>
            <th>1-hour Risk</th>
            <th>8-hour Risk</th>
            <th>40-hour Risk</th>
            <th>Initial Cost</th>
            <th>Recurring Cost</th>
            <th>Total Cost in 10 years</th>
            <th>Benefit / Cost in 10 years</th>
          </tr>
          <tr v-for='intervention in interventions'>
            <td v-if='intervention.numDevices() > 0'>
                <div v-for='obj in intervention.websitesAndText()' class='col centered container'>
                  <img :src="obj.imgLink">
                  <a :href="obj.website" >{{obj.text}}</a>
                </div>
            </td>

            <ColoredCell
                v-if='intervention.numDevices() > 0'
                :colorScheme="riskColorScheme"
                :maxVal=1
                :value='intervention.computeRiskRounded(1)'
                :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em' }"
            />

            <ColoredCell
                v-if='intervention.numDevices() > 0'
                :colorScheme="riskColorScheme"
                :maxVal=1
                :value='intervention.computeRiskRounded(8)'
                :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em' }"
            />

            <ColoredCell
                v-if='intervention.numDevices() > 0'
                :colorScheme="riskColorScheme"
                :maxVal=1
                :value='intervention.computeRiskRounded(40)'
                :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em' }"
            />
            <td v-if='intervention.numDevices() > 0' >~${{ intervention.initialCostText() }}</td>
            <td v-if='intervention.numDevices() > 0' >~${{ intervention.recurringCostText() }}</td>
            <td v-if='intervention.numDevices() > 0' >~${{ intervention.costInYears(10) }}</td>
            <td v-if='intervention.numDevices() > 0' >
              {{ roundOut((intervention.numEventsToInfectionWithCertainty()) / intervention.costInYears(10), 2 )}}
            </td>
          </tr>
        </table>

        <h4>Rapid Testing</h4>

        <p>
          <span>If, at max occupancy, everyone did rapid testing beforehand, and all got negative results, the probability that at least one person is infectious drops down to
              <ColoredCell
                :colorScheme="riskColorScheme"
                :maxVal=1
                :value='riskEncounteringInfectiousAllNegRapid'
                :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em', 'display': 'inline-block' }"
              />.
          </span>
        </p>
      </div>

    </div>

    <div class='container'>
      <label class='subsection'>Occupancy</label>

      <div class='container'>
      <span>Assuming a COVID infectious prevalence rate of {{this.riskOfOneRounded}}, and that the room is at max occupancy ~{{maximumOccupancy}}, the probability of having at least one infector in the room is
          <ColoredCell
            :colorScheme="riskColorScheme"
            :maxVal=1
            :value='maxOccupancyEncounterRisk'
            :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em', 'display': 'inline-block' }"
          />.
      </span>
      </div>

      <div class='container col centered' v-if="heatmapShowable">
        <h4 :style="{'margin-bottom': 0}">Popular Times at {{this.roomName}}</h4>
        <DayHourHeatmap
          :dayHours="occupancy.parsed"
        />
      </div>
    </div>

  </div>
</template>

<script>
// Have a VueX store that maintains state across components
import axios from 'axios';
import ColoredCell from './colored_cell.vue';
import DayHourHeatmap from './day_hour_heatmap.vue';
import HorizontalStackedBar from './horizontal_stacked_bar.vue';
import { airCleaners } from './air_cleaners.js';
import BarGraph from './bar_graph.vue';
import {
  AEROSOL_GENERATION_BOUNDS,
  colorSchemeFall,
  colorPaletteFall,
  assignBoundsToColorScheme,
  riskColorInterpolationScheme,
  infectedPeopleColorBounds,
  convertColorListToCutpoints,
  generateEvenSpacedBounds } from './colors.js';
import {
  findRiskiestMask,
  findRiskiestPotentialInfector,
  riskOfEncounteringInfectious,
  riskIndividualIsNotInfGivenNegRapidTest,
  reducedRisk } from './risk.js';
 import { convertVolume, computeAmountOfPortableAirCleanersThatCanFit } from './measurement_units.js';
import { useAnalyticsStore } from './stores/analytics_store'
import { MASKS } from './masks.js';
import { useEventStore } from './stores/event_store';
import { useEventStores } from './stores/event_stores';
import { useMainStore } from './stores/main_store';
import { useShowMeasurementSetStore } from './stores/show_measurement_set_store';
import { useProfileStore } from './stores/profile_store';
import { usePrevalenceStore } from './stores/prevalence_store';
import { mapWritableState, mapState, mapActions } from 'pinia';
import {
  computePortableACH,
  computeVentilationACH,
  convertCubicMetersPerHour,
  convertLengthBasedOnMeasurementType,
  cubicFeetPerMinuteTocubicMetersPerHour,
  displayCADR,
  findWorstCaseInhFactor,
  infectorActivityTypes,
  maskToPenetrationFactor,
  setupCSRF,
  simplifiedRisk,
  round,

} from  './misc';

export default {
  name: 'App',
  components: {
    BarGraph,
    ColoredCell,
    DayHourHeatmap,
    Event,
    HorizontalStackedBar
  },
  computed: {
    ...mapState(
        useMainStore,
        [
          'currentUser',
        ]
    ),
    ...mapState(
        useAnalyticsStore,
        [
          'interventions',
          'nullIntervention'
        ]
    ),
    ...mapWritableState(
        useMainStore,
        [
          'focusTab',
        ]
    ),
    ...mapState(
        usePrevalenceStore,
        [
          'riskOfOne',
        ]
    ),
    ...mapState(
        useProfileStore,
        [
          'lengthMeasurementType',
          'airDeliveryRateMeasurementType',
          'carbonDioxideMonitors',
          'measurementUnits',
          'systemOfMeasurement'
        ]
    ),
    ...mapWritableState(
      useAnalyticsStore,
      [
        'numPeopleToInvestIn'
      ]
    ),
    ...mapWritableState(
        useShowMeasurementSetStore,
        [
          'roomName',
          'activityGroups',
          'ageGroups',
          'carbonDioxideActivities',
          'ventilationCo2AmbientPpm',
          'ventilationCo2MeasurementDeviceModel',
          'ventilationCo2MeasurementDeviceName',
          'ventilationCo2MeasurementDeviceSerial',
          'ventilationCo2SteadyStatePpm',
          'duration',
          'private',
          'formatted_address',
          'infectorActivity',
          'infectorActivityTypeMapping',
          'maskTypes',
          'numberOfPeople',
          'occupancy',
          'maximumOccupancy',
          'placeData',
          'portableAirCleaners',
          'rapidTestResult',
          'rapidTestResults',
          'roomHeightMeters',
          'roomLengthMeters',
          'roomWidthMeters',
          'roomUsableVolumeFactor',
          'roomUsableVolumeCubicMeters',
          'singlePassFiltrationEfficiency',
          'startDatetime',
          'susceptibleActivities',
          'susceptibleActivity',
          'susceptibleAgeGroups',
          'ventilationNotes',
          'ventilationAch',
          'portableAch',
          'totalAch'
        ]
    ),
    inhalationActivityScheme() {
      colorPaletteFall
      const minimum = 0.258
      const maximum = 3
      const numObjects = 6
      const evenSpacedBounds = generateEvenSpacedBounds(minimum, maximum, numObjects)

      const scheme = convertColorListToCutpoints(
        JSON.parse(JSON.stringify(colorPaletteFall)).reverse()
      )

      return assignBoundsToColorScheme(scheme, evenSpacedBounds)
    },
    maskingValues() {
      let key;
      let color;

      let dict = {}
      for (let p in maskToPenetrationFactor) {
        dict[p] = 0
      }

      for (let ag of this.activityGroups) {
        dict[ag.maskType] += parseFloat(ag.numberOfPeople)
      }

      return dict
    },
    maskingColors() {
      let index = 0
      let key = 'lowerColor'
      let colors = []
      let color;

      for (let colorPair of colorSchemeFall) {
        color = colorPair[key]

        colors.push(
          `rgb(${color.r}, ${color.g}, ${color.b})`
        )
      }


      color = colorSchemeFall[colorSchemeFall.length - 1]['upperColor']
      colors.push(`rgb(${color.r}, ${color.g}, ${color.b})`)

      return colors
    },
    reducedRiskColorScheme() {
      const minimum = 0
      const maximum = 1
      const numObjects = 2
      const evenSpacedBounds = generateEvenSpacedBounds(minimum, maximum, numObjects)

      const scheme = convertColorListToCutpoints(
        [colorPaletteFall[3], colorPaletteFall[4], colorPaletteFall[5]]
      )
      // const reducedRiskColorBounds = infectedPeopleColorBounds.reverse()

      return assignBoundsToColorScheme(scheme, evenSpacedBounds)
    },
    reducedRiskOfUnmaskedVsUnmaskedButWithSuggestedAirCleaners() {
      const result = (
        this.riskTransmissionOfUnmaskedInfectorToUnmaskedSusceptible
        - this.riskTransmissionOfUnmaskedInfectorToUnmaskedSusceptibleWithSuggestedAirCleaners
      ) / this.riskTransmissionOfUnmaskedInfectorToUnmaskedSusceptible

      return result
    },
    reducedRiskOfUnmaskedVsUnmaskedButWithSuggestedAirCleanersAndMasks() {
      const result = (
        this.riskTransmissionOfUnmaskedInfectorToUnmaskedSusceptible
        - this.riskTransmissionOfUnmaskedInfectorToUnmaskedSusceptibleWithSuggestedAirCleanersAndMasks
      ) / this.riskTransmissionOfUnmaskedInfectorToUnmaskedSusceptible

      return result
    },
    reducedRiskOfUnmaskedVsUnmaskedButWithSuggestedAirCleanersAndMasksText() {
      return `${round(this.reducedRiskOfUnmaskedVsUnmaskedButWithSuggestedAirCleanersAndMasks * 100, 4)}%`
    },
    reducedRiskOfUnmaskedVsUnmaskedButWithSuggestedAirCleanersText() {
      return `${round(this.reducedRiskOfUnmaskedVsUnmaskedButWithSuggestedAirCleaners * 100, 1)}%`
    },

    absoluteReducedRiskOfUnmaskedVsUnmaskedButWithSuggestedAirCleaners() {
      const result = (
        this.riskTransmissionOfUnmaskedInfectorToUnmaskedSusceptible
        - this.riskTransmissionOfUnmaskedInfectorToUnmaskedSusceptibleWithSuggestedAirCleaners
      )

      return round(result, 6)
    },
    absoluteReducedRiskOfUnmaskedVsUnmaskedButWithSuggestedAirCleanersAndMasks() {
      const result = (
        this.riskTransmissionOfUnmaskedInfectorToUnmaskedSusceptible
        - this.riskTransmissionOfUnmaskedInfectorToUnmaskedSusceptibleWithSuggestedAirCleanersAndMasks
      )

      return round(result, 6)
    },
    riskiestPotentialInfector() {
      return findRiskiestPotentialInfector(this.activityGroups)
    },
    riskiestMask() {
      return findRiskiestMask(this.activityGroups)
    },
    riskiestAerosolGenerationActivityScheme() {
      const copy = [
        colorPaletteFall[4],
        colorPaletteFall[3],
        colorPaletteFall[2],
        colorPaletteFall[1],
        colorPaletteFall[0]]
          const cutPoints = convertColorListToCutpoints(copy)
      return assignBoundsToColorScheme(cutPoints, AEROSOL_GENERATION_BOUNDS)
    },
    riskiestMaskColorScheme() {
      const copy = JSON.parse(JSON.stringify(colorPaletteFall))
      const cutPoints = convertColorListToCutpoints(copy)
      return assignBoundsToColorScheme(cutPoints, infectedPeopleColorBounds)
    },
    worstCaseInhalation() {
      return findWorstCaseInhFactor(this.activityGroups)
    },
    riskTransmissionOfUnmaskedInfectorToUnmaskedSusceptible() {
      const riskiestActivityGroup = {
        'numberOfPeople': 1,
        'aerosolGenerationActivity': this.riskiestPotentialInfector['aerosolGenerationActivity'],
        'carbonDioxideGenerationActivity': this.riskiestPotentialInfector['carbonDioxideGenerationActivity'],
        'maskType': 'None'
      }

      if (!this.riskiestPotentialInfector['aerosolGenerationActivity'])  {
        return 0
      }

      // 1 infector
      const occupancy = 1
      const probaRandomSampleOfOneIsInfectious = 1.0

      const flowRate = this.totalFlowRateCubicMetersPerHour

      // TODO: consolidate this information in one place
      const basicInfectionQuanta = 18.6
      const variantMultiplier = 3.3
      const quanta = basicInfectionQuanta * variantMultiplier
      const susceptibleAgeGroup = '30 to <40'
      const susceptibleMaskPenentrationFactor = 1
      const susceptibleInhalationFactor = findWorstCaseInhFactor(
        this.activityGroups,
        susceptibleAgeGroup
      )
      const duration = 1 // hour

      return round(simplifiedRisk(
        [riskiestActivityGroup],
        occupancy,
        flowRate,
        quanta,
        susceptibleMaskPenentrationFactor,
        susceptibleAgeGroup,
        probaRandomSampleOfOneIsInfectious,
        duration
      ), 6)
    },
    averageTransmissionOfUnmaskedInfectorToUnmaskedSusceptible() {
      return round(this.maximumOccupancy * this.riskTransmissionOfUnmaskedInfectorToUnmaskedSusceptible, 1)
    },
    averageTransmissionOfUnmaskedInfectorToUnmaskedSusceptibleWithSuggestedAirCleaners() {
      return round(this.maximumOccupancy * this.riskTransmissionOfUnmaskedInfectorToUnmaskedSusceptibleWithSuggestedAirCleaners, 1)
    },
    riskTransmissionOfUnmaskedInfectorToUnmaskedSusceptibleWithSuggestedAirCleaners() {
      const riskiestActivityGroup = {
        'numberOfPeople': 1,
        'aerosolGenerationActivity': this.riskiestPotentialInfector['aerosolGenerationActivity'],
        'carbonDioxideGenerationActivity': this.riskiestPotentialInfector['carbonDioxideGenerationActivity'],
        'maskType': 'None'
      }

      if (!this.riskiestPotentialInfector['aerosolGenerationActivity'])  {
        return 0
      }

      const occupancy = 1
      const flowRate = this.totalFlowRateCubicMetersPerHour + this.numSuggestedAirCleaners * this.airCleanerSuggestion.cubicMetersPerHour

      // TODO: consolidate this information in one place
      const basicInfectionQuanta = 18.6
      const variantMultiplier = 3.3
      const quanta = basicInfectionQuanta * variantMultiplier
      const susceptibleAgeGroup = '30 to <40'
      const susceptibleMaskPenentrationFactor = 1
      const susceptibleInhalationFactor = findWorstCaseInhFactor(
        this.activityGroups,
        susceptibleAgeGroup
      )
      const probaRandomSampleOfOneIsInfectious = 1.0
      const duration = 1 // hour

      return round(simplifiedRisk(
        [riskiestActivityGroup],
        occupancy,
        flowRate,
        quanta,
        susceptibleMaskPenentrationFactor,
        susceptibleAgeGroup,
        probaRandomSampleOfOneIsInfectious,
        duration
      ), 6)
    },
    riskTransmissionOfUnmaskedInfectorToUnmaskedSusceptibleWithSuggestedAirCleanersAndMasks() {
      const riskiestActivityGroup = {
        'numberOfPeople': 1,
        'aerosolGenerationActivity': this.riskiestPotentialInfector['aerosolGenerationActivity'],
        'carbonDioxideGenerationActivity': this.riskiestPotentialInfector['carbonDioxideGenerationActivity'],
        'maskType': this.maskSuggestion['filtrationType']
      }

      if (!this.riskiestPotentialInfector['aerosolGenerationActivity'])  {
        return 0
      }

      const occupancy = 1
      const flowRate = this.totalFlowRateCubicMetersPerHour + this.numSuggestedAirCleaners * this.airCleanerSuggestion.cubicMetersPerHour

      // TODO: consolidate this information in one place
      const basicInfectionQuanta = 18.6
      const variantMultiplier = 3.3
      const quanta = basicInfectionQuanta * variantMultiplier
      const susceptibleAgeGroup = '30 to <40'
      const susceptibleMaskPenentrationFactor = maskToPenetrationFactor[
        this.maskSuggestion['filtrationType']
      ]

      const susceptibleInhalationFactor = findWorstCaseInhFactor(
        this.activityGroups,
        susceptibleAgeGroup
      )
      const probaRandomSampleOfOneIsInfectious = 1.0
      const duration = 1 // hour

      return round(simplifiedRisk(
        [riskiestActivityGroup],
        occupancy,
        flowRate,
        quanta,
        susceptibleMaskPenentrationFactor,
        susceptibleAgeGroup,
        probaRandomSampleOfOneIsInfectious,
        duration
      ), 6)
    },
    riskEncounteringInfectiousAllNegRapid() {
      const testSpecificity = 0.999
      const testSensitivity = 0.97

      const value =  1 - riskIndividualIsNotInfGivenNegRapidTest(
          testSpecificity,
          testSensitivity,
          this.riskOfOne
        ) ** this.maximumOccupancy
      return round(value, 6)
    },
    riskEncounteringInfectiousAllNegRapid() {
      const testSpecificity = 0.999
      const testSensitivity = 0.97

      const value =  1 - riskIndividualIsNotInfGivenNegRapidTest(
          testSpecificity,
          testSensitivity,
          this.riskOfOne
        ) ** this.maximumOccupancy
      return round(value, 6)
    },
    heatmapShowable() {
      return !!this.occupancy.parsed['Mondays']
    },
    riskOfOneRounded() {
      return round(this.riskOfOne, 6)
    },
    maxOccupancyEncounterRisk() {
      return round(riskOfEncounteringInfectious(this.riskOfOne, this.maximumOccupancy), 6)
    },
    riskColorScheme() {
      return riskColorInterpolationScheme
    },
    averageInfectedPeopleInterpolationScheme() {
      const copy = JSON.parse(JSON.stringify(riskColorInterpolationScheme))
      return assignBoundsToColorScheme(copy, infectedPeopleColorBounds)
    },
    colorInterpolationSchemeTotalAch() {
      return [
        {
          'lowerBound': 0,
          'upperBound': 2,
          'upperColor': {
            name: 'red',
            r: 219,
            g: 21,
            b: 0
          },
          'lowerColor': {
            name: 'darkRed',
            r: 174,
            g: 17,
            b: 0
          },
        },
        {
          'lowerBound': 2,
          'upperBound': 4,
          'upperColor': {
            name: 'orangeRed',
            r: 240,
            g: 90,
            b: 0
          },
          'lowerColor': {
            name: 'red',
            r: 219,
            g: 21,
            b: 0
          },
        },
        {
          'lowerBound': 4,
          'upperBound': 8,
          'upperColor': {
            name: 'yellow',
            r: 255,
            g: 233,
            b: 56
          },
          'lowerColor': {
            name: 'orangeRed',
            r: 240,
            g: 90,
            b: 0
          },
        },
        {
          'lowerBound': 8,
          'upperBound': 16,
          'lowerColor': {
            name: 'yellow',
            r: 255,
            g: 233,
            b: 56
          },
          'upperColor': {
            name: 'green',
            r: 87,
            g: 195,
            b: 40
          },
        },
        {
          'lowerBound': 16,
          'upperBound': 100,
          'lowerColor': {
            name: 'green',
            r: 87,
            g: 195,
            b: 40
          },
          'upperColor': {
            name: 'dark green',
            r: 11,
            g: 161,
            b: 3
          },
        },
      ]
    },
    cutoffsVolume() {
      let factor = 500 // cubic meters per hour
      let collection = []

      if (this.measurementUnits['airDeliveryRateMeasurementType'] == 'cubic feet per minute') {
        factor = factor / 60 * 35.3147 // cubic feet per minute
      }
      for (let i = 0; i < colorSchemeFall.length; i++) {
        collection.push(
          {
            'lowerBound': (i) * factor,
            'upperBound': (i + 1) * factor,
          }
        )
      }

      return collection
    },
    colorInterpolationSchemeRoomVolume() {
      return assignBoundsToColorScheme(colorSchemeFall, this.cutoffsVolume)
    },
    numSuggestedAirCleaners() {
      return computeAmountOfPortableAirCleanersThatCanFit(
        this.roomLengthMeters * this.roomWidthMeters,
        this.airCleanerSuggestion.areaInSquareMeters
      )
    },
    maskSuggestion() {
      return MASKS[0]
    },
    roomUsableVolumeRounded() {

      const profileStore = useProfileStore()
      return round(
        convertVolume(
          this.roomUsableVolumeCubicMeters,
          'meters',
          profileStore.measurementUnits.lengthMeasurementType
        ),
        1
      )
    },
    totalFlowRateCubicMetersPerHour() {
      return this.roomUsableVolumeCubicMeters * this.totalAch
    },
    totalFlowRate() {
      return displayCADR(this.systemOfMeasurement, this.totalFlowRateCubicMetersPerHour)
    },
    totalFlowRateRounded() {
      return round(this.totalFlowRate, 1)
    },
    airCleanerSuggestion() {
      return airCleaners.find((ac) => ac.singular == 'Corsi-Rosenthal box')
    },
    totalFlowRatePlusExtraPacRounded() {
      // TODO: could pull from risk.js airCleaners instead

      const newCADRcubicMetersPerHour = this.totalFlowRateCubicMetersPerHour + this.airCleanerSuggestion.cubicMetersPerHour * this.numSuggestedAirCleaners

      return round(displayCADR(this.systemOfMeasurement, newCADRcubicMetersPerHour), 1)
    },
    portableAchRounded() {
      return round(this.portableAch, 1)
    },
    totalAchRounded() {
      return round(this.totalAch, 1)
    },
    ventilationAchRounded() {
      return round(this.ventilationAch, 1)
    }
  },
  async created() {
  },
  data() {
    return {
      center: {lat: 51.093048, lng: 6.842120},
      ventilationACH: 0.0,
      portableACH: 0.0,
      totalACH: 0.0,
    }
  },
  methods: {
    ...mapActions(useAnalyticsStore, ['reload', 'setNumPeopleToInvestIn']),
    ...mapActions(useMainStore, ['setGMapsPlace', 'setFocusTab', 'getCurrentUser']),
    ...mapActions(useEventStore, ['addPortableAirCleaner']),
    ...mapState(useEventStore, ['findActivityGroup', 'findPortableAirCleaningDevice']),
    aerosolActivityToFactor(key) {
      return infectorActivityTypes[key]
    },
    reduceRisk(before, after) {
      return reducedRisk(before, after)
    },
    roundOut(someValue, numRound) {
      return round(someValue, numRound)
    },
    roundOutRisk(riskA, riskB) {
      return `${round(reducedRisk(riskA, riskB) * 100, 4)}%`
    },
    setNumPeople(event) {
      this.setNumPeopleToInvestIn(parseInt(event.target.value))
      this.reload()
    }
  }
}

</script>

<style scoped>
  .main {
    display: flex;
    flex-direction: row;
  }
  .container {
    margin: 1em;
  }
  label {
    padding: 1em;
  }
  .subsection {
    text-align: center;
    font-weight: bold;
    margin-left: 1em;
  }

  .wide {
    display: flex;
    flex-direction: row;
  }

  .row {
    display: flex;
    flex-direction: column;
  }

  .textarea-label {
    padding-top: 0;
  }

  textarea {
    width: 30em;
  }

  .border-showing {
    border: 1px solid grey;
  }

  .centered {
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .wider-input {
    width: 30em;
  }

  button {
    padding: 1em 3em;
  }

  table {
    text-align: center;
    padding: 2em;
  }

  .scrollable {
    overflow-y: scroll;
    height: 72em;
  }

  .col {
    display: flex;
    flex-direction: column;
  }

  .margined {
    margin: 2em;
  }

  th {
    padding: 1em;
  }

  .font-light {
    font-weight: 400;
  }

  td {
    padding: 1em;
  }

  span {
    line-height: 2em;
  }

  .highlight {
    font-style: italic;
    font-weight: bold;
  }

  img {
    width: 4em;
  }

  p {
    line-height: 2em;
  }

  li {
    line-height: 2em;
  }

  .bold {
    font-weight: bold;
  }
</style>
