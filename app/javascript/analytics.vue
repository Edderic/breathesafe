<template>
  <div class='row'>
    <div class='col border-showing left-pane'>
      <router-link :to="`/analytics/${this.$route.params.id}#risk-assessment`" class='link-h1'>
        Risk Assessment
      </router-link>
      <router-link :to="`/analytics/${this.$route.params.id}#overview`" class='link-h1'>
        Overview
      </router-link>
      <router-link :to="`/analytics/${this.$route.params.id}#introduction`" class='link-h2'>
        Introduction
      </router-link>
      <router-link :to="`/analytics/${this.$route.params.id}#modeling`" class='link-h2'>
        Modeling
      </router-link>
      <router-link :to="`/analytics/${this.$route.params.id}#risky-behaviors-and-environments`" class='link-h2'>
        Risky Behaviors and Environments
      </router-link>
      <router-link :to="`/analytics/${this.$route.params.id}#safer-behaviors-and-environments`" class='link-h2'>
        Safer Behaviors and Environments
      </router-link>
      <router-link :to="`/analytics/${this.$route.params.id}#measurements`" class='link-h1'>
        Measurements
      </router-link>
      <router-link :to="`/analytics/${this.$route.params.id}#behaviors`" class='link-h2'>
        Behaviors
      </router-link>
      <router-link :to="`/analytics/${this.$route.params.id}#masking`" class='link-h2'>
        Masking
      </router-link>
      <router-link :to="`/analytics/${this.$route.params.id}#clean-air-delivery-rate`" class='link-h2'>
        Clean Air Delivery Rate (CADR)
      </router-link>
      <router-link :to="`/analytics/${this.$route.params.id}#interventions`" class='link-h1'>
        Interventions
      </router-link>
      <router-link :to="`/analytics/${this.$route.params.id}#computational-details`" class='link-h1'>
        Computational Details
      </router-link>
      <router-link :to="`/analytics/${this.$route.params.id}#details-ventilation-ach`" class='link-h2'>
        Ventilation ACH
      </router-link>
      <router-link :to="`/analytics/${this.$route.params.id}#details-upper-room-germicidal-uv-ach`" class='link-h2'>
        Upper-Room Germicidal UV ACH
      </router-link>
      <router-link :to="`/analytics/${this.$route.params.id}#details-portable-air-cleaner-ach`" class='link-h2'>
        Portable Air Cleaner ACH
      </router-link>
    </div>

    <div class='col border-showing right-pane'>
      <div class='container'>
        <br id='risk-assessment'>
        <br>
        <br>
        <h3 class='subsection'>Analysis & Recommendations for {{this.roomName}}</h3>
        <div class='centered col'>
          <div class='container'>
            <div class='centered'>
              <RiskTable
                :intervention="nullIntervention"
                :maximumOccupancy='maximumOccupancy'
              />
            </div>

            <p>
              The estimated maximum occupancy for this space is ~{{maximumOccupancy}}. To see how resilient this environment is in preventing outbreaks, let's assume there is one infector in this space.
              <span>
                In 1 hour, a susceptible's risk is <ColoredCell
                    v-if="nullIntervention"
                    :colorScheme="riskColorScheme"
                    :maxVal=1
                    :value='nullIntervention.computeRiskRounded()'
                    :style="inlineCellCSS"
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
                      :style="inlineCellCSS"
                  />
              </span> susceptibles would get infected.
              <span> In 8 hours of exposure, the risk jumps to <ColoredCell
                      v-if="nullIntervention"
                      :colorScheme="riskColorScheme"
                      :maxVal=1
                      :value='roundOut(1 - (1-nullIntervention.computeRiskRounded())**8, 6)'
                      :style="inlineCellCSS"
                  />
              </span>, and
              <span>
                  <ColoredCell
                      v-if="nullIntervention"
                      :colorScheme="averageInfectedPeopleInterpolationScheme"
                      :maxVal=1
                      :text='roundOut(this.maximumOccupancy * (1 - (1-nullIntervention.computeRiskRounded())**8), 1)'
                      :value='this.maximumOccupancy * nullIntervention.computeRiskRounded()'
                      :style="inlineCellCSS"
                  />
              </span> susceptibles would get infected, on average. Likewise,
  <span>
                  <ColoredCell
                      v-if="nullIntervention"
                      :colorScheme="averageInfectedPeopleInterpolationScheme"
                      :maxVal=1
                      :value='roundOut(this.maximumOccupancy* (1 - (1-nullIntervention.computeRiskRounded())**40), 1)'
                      :style="inlineCellCSS"
                  /> and
                  <ColoredCell
                      v-if="nullIntervention"
                      :colorScheme="averageInfectedPeopleInterpolationScheme"
                      :maxVal=1
                      :value='roundOut(this.maximumOccupancy* (1 - (1-nullIntervention.computeRiskRounded())**80), 1)'
                      :style="inlineCellCSS"
                  />, on average, would get infected under 40 and 80 hours of exposure with an infector in this environment. Browse the
  <router-link :to="`/analytics/${this.$route.params.id}#interventions`">
    interventions
  </router-link>
   section to understand what actions you can take to make this environment safer for everyone.</span>
            </p>


            <br id='overview'>
            <br>
            <br>
            <h3>Overview</h3>

            <br id='introduction'>
            <br>
            <br>

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

            <br id='modeling'>
            <br>
            <br>

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
            <br id='risky-behaviors-and-environments'>
            <br>
            <br>
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

            <br id='safer-behaviors-and-environments'>
            <br>
            <br>
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
                infectious aerosols in a room. Outdoors generally have high ventilation rates.
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

            <br id='measurements'>
            <br>
            <br>
            <h3>Measurements</h3>

            <br id='behaviors'>
            <br>
            <br>
            <h4>Behaviors</h4>

            <p>
              <span>
              The riskiest aerosol generation activity is <ColoredCell
                    :colorScheme="riskiestAerosolGenerationActivityScheme"
                    :maxVal=1
                    :value='aerosolActivityToFactor(riskiestPotentialInfector["aerosolGenerationActivity"])'
                    :text='riskiestPotentialInfector["aerosolGenerationActivity"]'
                    :style="inlineCellCSS"
                /> so we assume that the infector in the risk calculations above is doing this.
              </span>


              <span>The worst case inhalation activity is <ColoredCell
                    :colorScheme="inhalationActivityScheme"
                    :maxVal=1
                    :value='worstCaseInhalation["inhalationFactor"]'
                    :text='worstCaseInhalation["inhalationActivity"]'
                    :style="inlineCellCSS"
                /> so we assume that susceptibles in the risk calculations above are doing this.
              </span>

              Choosing activities where an infector is quiet and at rest, along
              with susceptibles being at rest, could decrease the risk of
              airborne transmission.
            </p>
          </div>

        </div>

        <div class='container'>
          <br id='masking'>
          <br>
          <br>
          <h4>Masking</h4>
          <div class='centered'>
            <HorizontalStackedBar
              :values="maskingBarChart.maskingValues()"
              :colors="maskingBarChart.maskingColors()"
            />
          </div>

          <p>The riskiest mask recorded for this measurement is <span><ColoredCell
                :colorScheme="riskiestMaskColorScheme"
                :maxVal=1
                :value='riskiestMask["maskPenetrationFactor"]'
                :text='riskiestMask["maskType"]'
                :style="inlineCellCSS"
            /></span>, so susceptibles are assumed to be wearing these (unless specified otherwise in the Interventions section).
           </p>

          <br id='clean-air-delivery-rate'>
          <br>
          <br>
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
            <CleanAirDeliveryRateTable
              :measurementUnits='measurementUnits'
              :systemOfMeasurement='systemOfMeasurement'
              :intervention='nullIntervention'
              :cellCSS='cellCSS'
            />
          </div>
        </div>

        <div class='centered'>
          <TotalACHTable
            :measurementUnits='measurementUnits'
            :systemOfMeasurement='systemOfMeasurement'
            :totalFlowRate='totalFlowRate'
            :roomUsableVolume='roomUsableVolume'
            :portableAch='nullIntervention.computePortableAirCleanerACH()'
            :ventilationAch='nullIntervention.computeVentilationACH()'
            :uvAch='nullIntervention.computeUVACH()'
            :cellCSS='cellCSS'
            />
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
              :style="inlineCellCSS"
            />. The cost of <a :href="maskSuggestion['website']">{{ this.maskSuggestion['name']}}</a> is ${{ this.maskSuggestion['initialCostUSD']}} per person, with a recurring cost of ${{ this.maskSuggestion['recurringCostUSD']}} every {{ this.maskSuggestion['recurringCostDuration']}} per person.
          </p>

          <br id='interventions'>
          <br>
          <br>

          <h3>Interventions</h3>
          <p>
          An intervention in the list below is either some sort of mask, air cleaning
          device, or a combination of both. The short-term and longer-term
          probabilities of transmission are displayed. Let's consider the 40-hour
          risk. One can interpret it as follows:
          <ol>
            <li>A susceptible is with an infector in this room for 40 hours straight.</li>
            <li>A susceptible has been with an infector in this room for 40
                events total, with each event spanning an hour.
            </li>
            <li>A susceptible has been with an infector in this room for 5
                events total, with each event spanning 8 hours.
           </li>
          </ol>

          The last interpretation is useful for workers who have to work on-site.
          This is the risk of working a 40-hour work week, conditional on an infector
          (asymptomatic or not) being present.
          </p>
          <p>
          The <span class='bold'>Total Cost in 10 years</span> is the estimate which is given by
          <span class='italic'>Initial Cost + Yearly Recurring Cost x 10 years</span>.
          </p>
          <p>
          The <span class='bold'>Benefit / Cost</span> is comprised of the number
          of hours it takes to infect with high certainty (99%), divided by the <span
          class='italic'>Total Cost in 10 years</span>. The higher it is, the more bang
          for the buck.

          One could modify the <span class='bold'>number of people to invest
          in</span> to see how the return of investment changes. Costs of
          interventions that use masks scale with the number of people. On the
          other hand, costs of interventions that only use portable air cleaners
          or upper room germicidal UV don't, and scale more with the volume or
          square footage of the room.

          </p>

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
                <td>
                <ColoredCell
                    v-if="nullIntervention"
                    :colorScheme="riskColorScheme"
                    :maxVal=1
                    :value='nullIntervention.computeRiskRounded()'
                    :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em'}"
                />
                </td>
                <td>
                <ColoredCell
                    v-if="nullIntervention"
                    :colorScheme="riskColorScheme"
                    :maxVal=1
                    :value='roundOut(1 - (1-nullIntervention.computeRiskRounded())**8, 6)'
                    :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em'}"
                />
                </td>
                <td>
                <ColoredCell
                    v-if="nullIntervention"
                    :colorScheme="riskColorScheme"
                    :maxVal=1
                    :value='roundOut(1 - (1-nullIntervention.computeRiskRounded())**40, 6)'
                    :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em'}"
                />
                </td>
                <td>
                <ColoredCell
                    v-if="nullIntervention"
                    :colorScheme="riskColorScheme"
                    :maxVal=1
                    :value='roundOut(1 - (1-nullIntervention.computeRiskRounded())**80, 6)'
                    :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em'}"
                />
                </td>
              </tr>
              <tr>
                <th>Average # of Susceptibles Infected under Max Occupancy</th>
                <td>
                <ColoredCell
                    v-if="nullIntervention"
                    :colorScheme="averageInfectedPeopleInterpolationScheme"
                    :maxVal=1
                    :text='roundOut(this.maximumOccupancy * nullIntervention.computeRiskRounded(), 1)'
                    :value='this.maximumOccupancy * nullIntervention.computeRiskRounded()'
                    :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em'}"
                />
                </td>
                <td>
                <ColoredCell
                    v-if="nullIntervention"
                    :colorScheme="averageInfectedPeopleInterpolationScheme"
                    :maxVal=1
                    :value='roundOut(this.maximumOccupancy* (1 - (1-nullIntervention.computeRiskRounded())**8), 1)'
                    :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em'}"
                />
                </td>
                <td>
                <ColoredCell
                    v-if="nullIntervention"
                    :colorScheme="averageInfectedPeopleInterpolationScheme"
                    :maxVal=1
                    :value='roundOut(this.maximumOccupancy* (1 - (1-nullIntervention.computeRiskRounded())**40), 1)'
                    :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em'}"
                />
                </td>
                <td>
                <ColoredCell
                    v-if="nullIntervention"
                    :colorScheme="averageInfectedPeopleInterpolationScheme"
                    :maxVal=1
                    :value='roundOut(this.maximumOccupancy* (1 - (1-nullIntervention.computeRiskRounded())**80), 1)'
                    :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em'}"
                />
                </td>
              </tr>
            </table>
          </div>

          <div class='container centered'>
            <label class='bold'>Number of people to invest in (e.g. employees)</label>
            <input :value='numPeopleToInvestIn' @change='setNumPeople'>
          </div>

          <div class='scroll-table'>
            <table>
              <tr>
                <th>Investments</th>
                <th>1-hour Risk</th>
                <th>8-hour Risk</th>
                <th>40-hour Risk</th>
                <th>Initial Cost</th>
                <th>Yearly Recurring Cost</th>
                <th>Total Cost in 10 years</th>
                <th>Benefit / Cost</th>
              </tr>
              <tr v-for='intervention in interventions' @click='selectIntervention(intervention.id)' :class='{ clicked: intervention.selected }'>
                <td v-if='intervention.applicable()'>
                    <div v-for='obj in intervention.websitesAndText()' class='col centered container'>
                      <img :src="obj.imgLink">
                      <a :href="obj.website" >{{obj.text}}</a>
                    </div>
                </td>

                <td>
                <ColoredCell
                    v-if='intervention.applicable()'
                    :colorScheme="riskColorScheme"
                    :maxVal=1
                    :value='intervention.computeRiskRounded(1)'
                    class='color-cell'
                />
                </td>

                <td>
                <ColoredCell
                    v-if='intervention.applicable()'
                    :colorScheme="riskColorScheme"
                    :maxVal=1
                    :value='intervention.computeRiskRounded(8)'
                    class='color-cell'
                />
                </td>
                <td>
                <ColoredCell
                    v-if='intervention.applicable()'
                    :colorScheme="riskColorScheme"
                    :maxVal=1
                    :value='intervention.computeRiskRounded(40)'
                    class='color-cell'
                />
                </td>
                <td v-if='intervention.applicable()' >
                  <div v-for='interv in intervention.interventions' class='padded'>
                    {{ interv.initialCostText() }}
                  </div>
                </td>
                <td v-if='intervention.applicable()' >
                  <div v-for='interv in intervention.interventions' class='padded'>
                    {{ interv.recurringCostText() }}
                  </div>
                </td>
                <td v-if='intervention.applicable()' >${{ intervention.costInYears(10) }}</td>
                <td v-if='intervention.applicable()' >
                  {{ roundOut((intervention.numEventsToInfectionWithCertainty()) / intervention.costInYears(10), 2 )}}
                </td>
              </tr>
            </table>
          </div>


          <br id='computational-details'>
          <br>
          <br>
          <h3>Computational Details</h3>
          <p>Click on an intervention to see how risks are calculated.</p>

          <div class='centered'>
            <table>
              <tr>
                <th class='col centered'>
                  <span>Risk in 40 hours</span>
                  <span class='font-light'>(Probability)</span>
                </th>
                <th></th>
                <th class='col centered'>
                </th>
                <th></th>
                <th class='col centered'>
                </th>
                <th></th>
                <th class='col centered'>
                </th>
                <th></th>
                <th class='col centered'>
                  <span>Intermediate Factor</span>
                  <span class='font-light'>(Quanta)</span>
                </th>
              </tr>
              <tr>
                <ColoredCell
                  :colorScheme="riskColorScheme"
                  :maxVal=1
                  :value='this.selectedIntervention.computeRiskRounded(40)'
                  class='color-cell'
                />
                <td>=</td>
                <td class='col centered'>
                  1
                </td>
                <td>-</td>
                <td class='col centered'>
                  1
                </td>
                <td>/</td>
                <td class='col centered'>
                  exp
                </td>
                <td>^</td>
                <ColoredCell
                  :colorScheme="riskColorScheme"
                  :maxVal=1
                  :value='roundOut(intermediateProductWithIntervention, 6)'
                  class='color-cell'
                />
              </tr>
            </table>
          </div>

          <div class='centered'>
            <table>
              <tr>
                <th class='col centered'>
                  <span>Intermediate Factor</span>
                  <span class='font-light'>(Quanta)</span>
                </th>
                <th></th>
                <th class='col centered'>
                  <span>Infector Product</span>
                  <span class='font-light'>(Quanta / h)</span>
                </th>
                <th></th>
                <th class='col centered'>
                  <span>Susceptible Product</span>
                  <span class='font-light'>(m³ / h)</span>
                </th>
                <th></th>
                <th class='col centered'>
                  <span>Duration</span>
                  <span class='font-light'>(h)</span>
                </th>
                <th></th>
                <th class='col centered'>
                  <span>Clean Air Delivery Rate</span>
                  <span class='font-light'>(m³ / h)</span>
                </th>
              </tr>
              <tr>
                <ColoredCell
                  :colorScheme="riskColorScheme"
                  :maxVal=1
                  :value='roundOut(intermediateProductWithIntervention, 6)'
                  class='color-cell'
                />
                <td>=</td>
                <ColoredCell
                  v-if="nullIntervention"
                  :colorScheme="averageInfectedPeopleInterpolationScheme"
                  :maxVal=1
                  :value='roundOut(infectorProductWithIntervention, 1)'
                  class='color-cell'
                />
                <td>x</td>
                <ColoredCell
                  v-if="nullIntervention"
                  :colorScheme="averageInfectedPeopleInterpolationScheme"
                  :maxVal=1
                  :value='roundOut(susceptibleProductWithIntervention, 3)'
                  class='color-cell'
                />
                <td>x</td>
                <td class='col centered'>
                  40
                </td>
                <td>/</td>
                <ColoredCell
                  :colorScheme="colorInterpolationSchemeRoomVolumeMetric"
                  :maxVal=1
                  :value='roundOut(computeTotalFlowRate(roomUsableVolumeCubicMeters *  selectedIntervention.computeACH()), 1)'
                  class='color-cell'
                />
              </tr>
            </table>
          </div>

          <div class='centered'>
            <table>
              <tr>
                <th class='col centered'>
                  <span>Infector Product</span>
                  <span class='font-light'>(Quanta / h)</span>
                </th>
                <th></th>
                <th class='col centered'>
                  <span>Original Strain</span>
                  <span class='font-light'>(Quanta / h)</span>
                </th>
                <th></th>
                <th class='col centered'>
                  <span>Variant Factor</span>
                  <span class='font-light italic'>BA-2</span>
                  <span class='font-light'>(dimension-less)</span>
                </th>
                <th></th>
                <th class='col centered'>
                  <span>Infector Exhalation Factor: </span>
                  <span class='font-light italic'>{{riskiestPotentialInfector["aerosolGenerationActivity"]}}</span>
                  <span class='font-light'>(dimensionless)</span>
                </th>
                <th></th>
                <th class='col centered'>
                  <span>Infector Masking Penetration Factor</span>
                  <span class='font-light italic'>
                    {{selectedIntervention.computeSusceptibleMask()['maskType']}}
                  </span>
                  <span class='font-light'>(dimensionless)</span>
                </th>
              </tr>
              <tr>
                <ColoredCell
                  v-if="nullIntervention"
                  :colorScheme="averageInfectedPeopleInterpolationScheme"
                  :maxVal=1
                  :value='roundOut(infectorProductWithIntervention, 1)'
                  class='color-cell'
                />
                <td>=</td>
                <ColoredCell
                  v-if="nullIntervention"
                  :colorScheme="averageInfectedPeopleInterpolationScheme"
                  :maxVal=1
                  :value=18.6
                  class='color-cell'
                />
                <td>x</td>
                <ColoredCell
                  v-if="nullIntervention"
                  :colorScheme="averageInfectedPeopleInterpolationScheme"
                  :maxVal=1
                  :value=3.3
                  class='color-cell'
                />
                <td>x</td>
                <ColoredCell
                    :colorScheme="riskiestAerosolGenerationActivityScheme"
                    :maxVal=1
                    :value='roundOut(aerosolActivityToFactor(riskiestPotentialInfector["aerosolGenerationActivity"]), 1)'
                  class='color-cell'
                />
                <td>x</td>
                <ColoredCell
                  :colorScheme="riskiestMaskColorScheme"
                  :maxVal=1
                  :value='selectedIntervention.computeSusceptibleMask()["maskPenetrationFactor"]'
                  class='color-cell'
                />
              </tr>
            </table>
          </div>

          <div class='centered'>
            <table>
              <tr>
                <th class='col centered'>
                  <span>Susceptible Product</span>
                  <span class='font-light'>(m³ / h)</span>
                </th>

                <th></th>
                <th class='col centered'>
                  <span>Susceptible Masking Penetration Factor</span>
                  <span class='font-light italic'>
                    {{selectedIntervention.computeSusceptibleMask()['maskType']}}
                  </span>
                  <span class='font-light'>(dimensionless)</span>
                </th>

                <th></th>
                <th class='col centered'>
                  <span>Susceptible Breathing Rate</span>
                  <span class='font-light italic'>
                    {{worstCaseInhalation["inhalationActivity"]}}
                  </span>
                  <span class='font-light'>(m³ / h)</span>
                </th>
              </tr>
              <tr>
                <ColoredCell
                  v-if="nullIntervention"
                  :colorScheme="averageInfectedPeopleInterpolationScheme"
                  :maxVal=1
                  :value='roundOut(susceptibleProductWithIntervention, 3)'
                  class='color-cell'
                />

                <td>=</td>
                <ColoredCell
                  :colorScheme="riskiestMaskColorScheme"
                  :maxVal=1
                  :value='selectedIntervention.computeSusceptibleMask()["maskPenetrationFactor"]'
                  class='color-cell'
                />

                <td>x</td>
                <ColoredCell
                    :colorScheme="inhalationActivityScheme"
                    :maxVal=1
                    :value='worstCaseInhalation["inhalationFactor"]'
                  class='color-cell'
                />
              </tr>

            </table>
          </div>

          <div class='centered'>
            <table>
              <tr>
                <th class='col centered'>
                  <span>Clean Air Delivery Rate</span>
                  <span class='font-light'>(m³ / h)</span>
                </th>
                <th></th>
                <th class='col centered'>
                  <span>Unoccupied Room Volume</span>
                  <span class='font-light'>(m³)</span>
                </th>
                <th></th>
                <th class='col centered'>
                  <span>Total ACH</span>
                  <span class='font-light'>(1 / h)</span>
                </th>
              </tr>
              <tr>
                <ColoredCell
                  :colorScheme="colorInterpolationSchemeRoomVolumeMetric"
                  :maxVal=1
                  :value='roundOut(computeTotalFlowRate(roomUsableVolumeCubicMeters *  selectedIntervention.computeACH()), 1)'
                  class='color-cell'
                />
                <td>=</td>
                <ColoredCell
                  :colorScheme="colorInterpolationSchemeRoomVolumeMetric"
                  :maxVal=1
                  :value='roundOut(roomUsableVolumeCubicMeters, 1)'
                  class='color-cell'
                />
                <td>x</td>
                <ColoredCell
                  :colorScheme="colorInterpolationSchemeTotalAch"
                  :maxVal=1
                  :value='roundOut(selectedIntervention.computeACH(), 1)'
                  class='color-cell'
                />
              </tr>
            </table>
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
                  <th></th>
                  <th class='col centered'>
                    <span>Upper-Room UV ACH</span>
                    <span class='font-light'>(1 / h)</span>
                  </th>
                </tr>
                <tr>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeTotalAch"
                    :maxVal=1
                    :value='roundOut(this.selectedIntervention.computeACH(), 1)'
                    class='color-cell'
                  />
                  <td>=</td>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeTotalAch"
                    :maxVal=1
                    :value='roundOut(this.selectedIntervention.computeVentilationACH(), 1)'
                    class='color-cell'
                  />
                  <td>+</td>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeTotalAch"
                    :maxVal=1
                    :value='roundOut(this.selectedIntervention.computePortableAirCleanerACH(), 1)'
                    class='color-cell'
                  />
                  <td>+</td>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeTotalAch"
                    :maxVal=1
                    :value='roundOut(this.selectedIntervention.computeUVACH(), 1)'
                    class='color-cell'
                  />
                </tr>
              </table>
            </div>
          </div>


          <br id='details-ventilation-ach'>
          <br>
          <br>
          <h4>Ventilation ACH</h4>

          <div class='container'>
            <div class='centered'>
              <table>
                <tr>
                  <th class='col centered'>
                    <span>Ventilation ACH</span>
                    <span class='font-light'>(1 / h)</span>
                  </th>
                  <th></th>
                  <th class='col centered'>
                    <span></span>
                    <span class='font-light'>(m³ x s) / (h x L)</span>
                  </th>
                  <th></th>
                  <th class='col centered'>
                    <span>Total CO2 Emission Rate</span>
                    <span class='font-light'>(L / s)</span>
                  </th>
                  <th></th>
                  <th class='col centered'>
                    <span></span>
                    <span class='font-light'>(ppm)</span>
                  </th>
                  <th></th>
                  <th class='col centered'>
                    <span>Denominator</span>
                    <span class='font-light'>(m³ ppm)</span>
                  </th>
                </tr>
                <tr>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeTotalAch"
                    :maxVal=1
                    :value='roundOut(this.selectedIntervention.computeVentilationACH(), 1)'
                    class='color-cell'
                  />
                  <td>=</td>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeTotalAch"
                    :maxVal=1
                    :value='3.6'
                    class='color-cell'
                    style='background-color: grey;'
                  />
                  <td>x</td>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeTotalAch"
                    :maxVal=1
                    :value='roundOut(this.selectedIntervention.computeEmissionRate(), 3)'
                    class='color-cell'
                  />
                  <td>x</td>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeTotalAch"
                    :maxVal=1
                    :value='1000000'
                    class='color-cell'
                    style='background-color: grey;'
                  />
                  <td>/</td>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeTotalAch"
                    :maxVal=1
                    :value='roundOut(this.selectedIntervention.ventilationDenominator(), 1)'
                    class='color-cell'
                  />
                </tr>
              </table>
            </div>
          </div>

          <div class='container'>
            <div class='centered'>
              <table>
                <tr>
                  <th class='col centered'>
                    <span></span>
                    <span class='font-light'>(m³ x s) / (h x L)</span>
                  </th>
                  <th></th>
                  <th class='col centered'>
                    <span></span>
                    <span class='font-light'>(m³ / L)</span>
                  </th>
                  <th></th>
                  <th class='col centered'>
                    <span></span>
                    <span class='font-light'>(s / h)</span>
                  </th>
                </tr>
                <tr>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeTotalAch"
                    :maxVal=1
                    :value='3.6'
                    class='color-cell'
                    style='background-color: grey;'
                  />
                  <td>=</td>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeTotalAch"
                    :maxVal=1
                    :value='0.001'
                    class='color-cell'
                    style='background-color: grey;'
                  />
                  <td>x</td>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeTotalAch"
                    :maxVal=1
                    :value='3600'
                    class='color-cell'
                    style='background-color: grey;'
                  />
                </tr>
              </table>

            </div>
          </div>

          <div class='container'>
            <div class='centered'>
              <table>
                <tr>
                  <th class='col centered'>
                    <span>Denominator</span>
                    <span class='font-light'>(m³ ppm)</span>
                  </th>
                  <th></th>
                  <th></th>
                  <th class='col centered'>
                    <span>Steady State CO2</span>
                    <span class='font-light'>(ppm)</span>
                  </th>
                  <th></th>
                  <th class='col centered'>
                    <span>Ambient CO2</span>
                    <span class='font-light'>(ppm)</span>
                  </th>
                  <th></th>
                  <th></th>
                  <th class='col centered'>
                    <span>Volume Occupied by Air</span>
                    <span class='font-light'>(m³)</span>
                  </th>
                </tr>
                <tr>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeTotalAch"
                    :maxVal=1
                    :value='roundOut(this.selectedIntervention.ventilationDenominator(), 1)'
                    class='color-cell'
                  />
                  <td>=</td>
                  <td>(</td>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeTotalAch"
                    :maxVal=1
                    :value='roundOut(this.selectedIntervention.steadyStateCO2Reading(), 0)'
                    class='color-cell'
                  />
                  <td>-</td>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeTotalAch"
                    :maxVal=1
                    :value='roundOut(this.selectedIntervention.ambientCO2Reading(), 0)'
                    class='color-cell'
                  />
                  <td>)</td>
                  <td>x</td>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeRoomVolumeMetric"
                    :maxVal=1
                    :value='roundOut(roomUsableVolumeCubicMeters, 1)'
                    class='color-cell'
                  />
                </tr>
              </table>
            </div>
          </div>

          <div class='container'>
            <div class='centered'>
              <table>
                <tr>
                  <th class='col centered'>
                    <span>Total CO2 Emission Rate</span>
                    <span class='font-light'>(L / s)</span>
                  </th>

                  <th></th>

                  <th class='col centered'>
                    <span>Exhalation Activity CO2</span>
                    <span class='font-light'>(L / s)</span>
                  </th>

                  <th></th>

                  <th class='col centered'>
                    <span>Num People</span>
                  </th>

                  <th></th>

                  <th class='col centered'>
                    <span>Activity</span>
                  </th>

                  <th></th>

                  <th class='col centered'>
                    <span>Sex</span>
                  </th>

                  <th></th>

                  <th class='col centered'>
                    <span>Age Group</span>
                  </th>
                </tr>
                <tr v-for='(activityGroup, i) in activityGroups'>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeTotalAch"
                    :maxVal=1
                    :value='roundOut(this.selectedIntervention.computeEmissionRate(), 3)'
                    class='color-cell'
                    v-if='i == 0'
                  />
                  <td v-else></td>

                  <td v-if='i == 0'>=</td>
                  <td v-else>+</td>

                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeTotalAch"
                    :maxVal=1
                    :value='roundOut(co2Rate(activityGroup), 6)'
                    class='color-cell'
                  />

                  <td>x</td>

                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeTotalAch"
                    :maxVal=1
                    :value='activityGroup.numberOfPeople'
                    class='color-cell'
                    style='background-color: grey'
                  />
                  <td></td>

                  <td>{{activityGroup.carbonDioxideGenerationActivity}}</td>

                  <td></td>

                  <td>{{activityGroup.sex}}</td>

                  <td></td>

                  <td>{{activityGroup.ageGroup}}</td>
                </tr>
              </table>
            </div>
          </div>

          <p><span class='bold'>Exhalation Activity CO2</span> values were calculated using regression on data referenced <a href="https://forhealth.org/tools/co2-calculator/">here</a>.</p>


          <br id='details-upper-room-germicidal-uv-ach'>
          <br>
          <br>
          <h4>Upper-Room Germicidal UV ACH</h4>

          <div class='container'>
            <div class='centered'>
              <table>
                <tr>
                  <th class='col centered'>
                    <span>Upper-Room Germicidal UV ACH</span>
                    <span class='font-light'>(1 / h)</span>
                  </th>
                  <th></th>
                  <th></th>
                  <th></th>
                  <th class='col centered'>
                    <span>Number of Devices</span>
                  </th>
                  <th></th>
                  <th class='col centered'>
                    <span>Power</span>
                    <span class='font-light'>(mW)</span>
                  </th>
                  <th></th>
                  <th class='col centered'>
                    <span>Volume Occupied by Air</span>
                    <span class='font-light'>(m³)</span>
                  </th>
                </tr>

                <tr>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeTotalAch"
                    :maxVal=1
                    :value='roundOut(this.selectedIntervention.computeUVACH(), 1)'
                    class='color-cell'
                  />
                  <td>=</td>
                  <td>2</td>
                  <td>x</td>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeTotalAch"
                    :maxVal=1
                    :value='roundOut(this.selectedIntervention.findUVDevices().numDevices(), 0)'
                    class='color-cell'
                  />
                  <td>x</td>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeTotalAch"
                    :maxVal=1
                    :value='roundOut(this.selectedIntervention.findUVDevices().mW, 0)'
                    class='color-cell'
                  />
                  <td>/</td>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeRoomVolumeMetric"
                    :maxVal=1
                    :value='roundOut(roomUsableVolumeCubicMeters, 1)'
                    class='color-cell'
                  />
                </tr>
              </table>
            </div>
          </div>

          <p>
          I got the idea of how to estimate Upper-Room UV ACH from <a href="https://twitter.com/joeyfox85/status/1512230529424371712?s=20&t=Fsswbo2rLsUPZqrsGyI0IQ">Joey Fox</a>.
          To figure out how many fixtures are needed, one can use the
            <a href="To figure out how many fixtures are needed, one can use the">
            CDC's guidelines. See the Installation and Maintenance section for more details:
            </a>
          </p>
          <p class='quote'>A typical room with 500 square feet (ft2) of floor space will generally require two to three UV fixtures.</p>

          <div class='container'>
            <div class='centered'>
              <table>
                <tr>
                  <th class='col centered'>
                    <span>Number of Devices</span>
                  </th>
                  <th></th>
                  <th class='col centered'>
                    <span>Room Length</span>
                    <span class='font-light'>(m)</span>
                  </th>
                  <th></th>
                  <th class='col centered'>
                    <span>Room Width</span>
                    <span class='font-light'>(m)</span>
                  </th>
                  <th></th>
                  <th class='col centered'>
                    <span>Square Meters</span>
                    <span class='font-light'>(m²)</span>
                  </th>
                  <th></th>
                  <th class='col centered'>
                    <span>Factor</span>
                    <span class='font-light'>(dimension-less)</span>
                  </th>
                </tr>

                <tr>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeTotalAch"
                    :maxVal=1
                    :value='roundOut(this.selectedIntervention.findUVDevices().numDevices(), 1)'
                    class='color-cell'
                  />
                  <td>=</td>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeRoomVolumeMetric"
                    :maxVal=1
                    :value='roundOut(this.roomLengthMeters, 0)'
                    class='color-cell'
                  />
                  <td>x</td>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeRoomVolumeMetric"
                    :maxVal=1
                    :value='roundOut(this.roomWidthMeters, 0)'
                    class='color-cell'
                  />
                  <td>/</td>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeRoomVolumeMetric"
                    :maxVal=1
                    :value='46.4515'
                    class='color-cell'
                    style='background-color: grey;'
                  />
                  <td>x</td>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeRoomVolumeMetric"
                    :maxVal=1
                    :value='this.selectedIntervention.findUVDevices().numDeviceFactor()'
                    class='color-cell'
                    style='background-color: grey;'
                  />
                </tr>
              </table>
            </div>
          </div>

          <div class='container'>
            <div class='centered'>
              <table>
                <tr>
                  <th class='col centered'>
                    <span>Square Meters</span>
                    <span class='font-light'>(m²)</span>
                  </th>
                  <th></th>
                  <th class='col centered'>
                    <span>Square Feet</span>
                    <span class='font-light'>(ft²)</span>
                  </th>
                  <th></th>
                  <th class='col centered'>
                    <span></span>
                    <span class='font-light'>(m² / ft²)</span>
                  </th>
                </tr>

                <tr>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeRoomVolumeMetric"
                    :maxVal=1
                    :value='46.4515'
                    class='color-cell'
                    style='background-color: grey;'
                  />
                  <td>=</td>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeRoomVolumeMetric"
                    :maxVal=1
                    :value='500'
                    class='color-cell'
                    style='background-color: grey;'
                  />
                  <td>x</td>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeRoomVolumeMetric"
                    :maxVal=1
                    :value='0.092903'
                    class='color-cell'
                    style='background-color: grey;'
                  />
                </tr>
              </table>
            </div>
          </div>


          <br id='details-portable-air-cleaner-ach'>
          <br>
          <br>
          <h4>Portable Air Cleaner ACH</h4>

          <div class='container'>
            <div class='centered'>
              <table>
                <tr>
                  <th class='col centered'>
                    <span>Portable Air Cleaner ACH</span>
                    <span class='font-light'>(1 / h)</span>
                  </th>
                  <th></th>
                  <th class='col centered'>
                    <span>Number of Devices</span>
                  </th>
                  <th></th>
                  <th class='col centered'>
                    <span>Clean Air Delivery Rate</span>
                    <span class='font-light'>(m³ / h)</span>
                  </th>
                  <th></th>
                  <th class='col centered'>
                    <span>Volume Occupied by Air</span>
                    <span class='font-light'>(m³)</span>
                  </th>
                </tr>

                <tr>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeTotalAch"
                    :maxVal=1
                    :value='roundOut(this.selectedIntervention.computePortableAirCleanerACH(), 1)'
                    class='color-cell'
                  />
                  <td>=</td>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeTotalAch"
                    :maxVal=1
                      :value='roundOut(this.selectedIntervention.findPortableAirCleaners().numDevices(), 0)'
                    class='color-cell'
                  />
                  <td>x</td>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeRoomVolumeMetric"
                    :maxVal=1
                    :value='roundOut(this.selectedIntervention.findPortableAirCleaners().cubicMetersPerHour, 0)'
                    class='color-cell'
                  />
                  <td>/</td>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeRoomVolumeMetric"
                    :maxVal=1
                    :value='roundOut(roomUsableVolumeCubicMeters, 1)'
                    class='color-cell'
                  />
                </tr>
              </table>
            </div>
          </div>

          <div class='container'>
            <div class='centered'>
              <table>
                <tr>
                  <th class='col centered'>
                    <span>Clean Air Delivery Rate</span>
                    <span class='font-light'>(m³ / h)</span>
                  </th>
                  <th></th>
                  <th class='col centered'>
                    <span>Description</span>
                  </th>
                </tr>

                <tr>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeRoomVolumeMetric"
                    :maxVal=1
                    :value='roundOut(this.selectedIntervention.findPortableAirCleaners().cubicMetersPerHour, 0)'
                    class='color-cell'
                  />
                  <td></td>
                  <td>{{selectedIntervention.findPortableAirCleaners().singularName()}}</td>
                </tr>
              </table>
            </div>
          </div>

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
  </div>
</template>

<script>
// Have a VueX store that maintains state across components
import axios from 'axios';
import ColoredCell from './colored_cell.vue';
import CleanAirDeliveryRateTable from './clean_air_delivery_rate_table.vue'
import DayHourHeatmap from './day_hour_heatmap.vue';
import HorizontalStackedBar from './horizontal_stacked_bar.vue';
import RiskTable from './risk_table.vue';
import TotalACHTable from './total_ach_table.vue';
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
import { MASKS, MaskingBarChart } from './masks.js';
import { useEventStore } from './stores/event_store';
import { useEventStores } from './stores/event_stores';
import { useMainStore } from './stores/main_store';
import { useShowMeasurementSetStore } from './stores/show_measurement_set_store';
import { useProfileStore } from './stores/profile_store';
import { usePrevalenceStore } from './stores/prevalence_store';
import { mapWritableState, mapState, mapActions } from 'pinia';
import {
  CO2_TO_MET,
  computePortableACH,
  computeVentilationACH,
  convertCubicMetersPerHour,
  convertLengthBasedOnMeasurementType,
  cubicFeetPerMinuteTocubicMetersPerHour,
  displayCADR,
  findWorstCaseInhFactor,
  getCO2Rate,
  infectorActivityTypes,
  maskToPenetrationFactor,
  setupCSRF,
  simplifiedRisk,
  round,

} from  './misc';

export default {
  name: 'Analytics',
  components: {
    BarGraph,
    ColoredCell,
    CleanAirDeliveryRateTable,
    DayHourHeatmap,
    Event,
    HorizontalStackedBar,
    RiskTable,
    TotalACHTable
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
          'nullIntervention',
          'selectedIntervention'
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
    cellCSS() {
      return {
        'padding-top': '1em',
        'padding-bottom': '1em',
      }
    },
    durationWithIntervention() {
      return 40
    },
    intermediateProductWithIntervention() {
      let cadr = this.computeTotalFlowRate(
        this.roomUsableVolumeCubicMeters *
        this.selectedIntervention.computeACH())

      return this.infectorProductWithIntervention * this.susceptibleProductWithIntervention
         * this.durationWithIntervention / cadr
    },
    infectorProductWithIntervention() {
      return 18.6 * 3.3 * this.aerosolActivityToFactor(
        this.riskiestPotentialInfector["aerosolGenerationActivity"]
      ) * this.selectedIntervention.computeSusceptibleMask()[
        "maskPenetrationFactor"
      ]
    },
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
    maskingBarChart() {
      return new MaskingBarChart(this.activityGroups)
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
    // TODO: delete this
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
    cutoffsMetricVolume() {
      let factor = 500 // cubic meters per hour
      let collection = []

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
    colorInterpolationSchemeRoomVolumeMetric() {
      return assignBoundsToColorScheme(colorSchemeFall, this.cutoffsMetricVolume)
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
    roomUsableVolume() {
      const profileStore = useProfileStore()

      return convertVolume(
        this.roomUsableVolumeCubicMeters,
        'meters',
        profileStore.measurementUnits.lengthMeasurementType
      )
    },
    totalFlowRateCubicMetersPerHour() {
      return this.roomUsableVolumeCubicMeters * this.totalAch
    },
    totalFlowRate() {
      return displayCADR(this.systemOfMeasurement, this.totalFlowRateCubicMetersPerHour)
    },
    airCleanerSuggestion() {
      return airCleaners.find((ac) => ac.singular == 'Corsi-Rosenthal box (Max Speed)')
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
    susceptibleProductWithIntervention() {
      return this.selectedIntervention.computeSusceptibleMask()["maskPenetrationFactor"]
        * this.worstCaseInhalation["inhalationFactor"]
    },
    ventilationAchRounded() {
      return round(this.ventilationAch, 1)
    }
  },
  created() {
    this.showAnalysis(this.$route.params.id)

    this.$watch(
      () => this.$route.params,
      (toParams, previousParams) => {
        this.showAnalysis(toParams.id)
        // react to route changes...
      }
    )
  },
  data() {
    return {
      center: {lat: 51.093048, lng: 6.842120},
      ventilationACH: 0.0,
      portableACH: 0.0,
      totalACH: 0.0,
      inlineCellCSS: {
        'display': 'inline-block',
        'font-weight': 'bold',
        'color': 'white',
        'text-shadow': '1px 1px 2px black',
        'padding': '1em',
        'margin': '0.5em',
        'text-align': 'center'
      }
    }
  },
  methods: {
    ...mapActions(useAnalyticsStore, ['reload', 'setNumPeopleToInvestIn', 'selectIntervention']),
    ...mapActions(useMainStore, ['setGMapsPlace', 'setFocusTab', 'getCurrentUser', 'showAnalysis']),
    ...mapActions(useEventStore, ['addPortableAirCleaner']),
    ...mapState(useEventStore, ['findActivityGroup', 'findPortableAirCleaningDevice']),
    scrollFix(event, hashbang) {
      let element_to_scroll_to = document.getElementById(hashbang);
      element_to_scroll_to.scrollIntoView();
    },
    aerosolActivityToFactor(key) {
      return infectorActivityTypes[key]
    },
    co2Rate(activityGroup) {
      let blah = getCO2Rate(
        CO2_TO_MET[activityGroup.carbonDioxideGenerationActivity],
        activityGroup["sex"] == "Male",
        activityGroup["ageGroup"]
      )
      return blah
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
    },
    computeTotalFlowRateCubicMetersPerHour(totalACH) {
      return this.roomUsableVolumeCubicMeters * totalACH
    },
    computeTotalFlowRate(totalFlowRateCubicMetersPerHour) {
      return displayCADR('metric', totalFlowRateCubicMetersPerHour)
    },
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
    flex-direction: row;
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
    align-items: center;
    justify-content: center;
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

  .scroll-table {
    height: 40em;

    overflow-y: scroll;
  }


  .col {
    display: flex;
    flex-direction: column;
  }

  .margined {
    margin: 2em;
  }

  .padded {
    padding: 1em;
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
  .italic {
    font-style: italic;
  }

  .clicked {
    background-color: #e6e6e6;
  }

  .color-cell {
    font-weight: bold;
    color: white;
    text-shadow: 1px 1px 2px black;
    padding: 1em;
  }

  .quote {
    font-style: italic;
    padding-left: 2em;
  }

  div {
    scroll-behavior: smooth;
  }

  .left-pane {
    width: 20rem;
    height: 50em;
    position: fixed;
    left: 0em;
    border-right: 0px;
    border-top: 0px;
    border-bottom: 0px;
  }

  .right-pane {
    width: 70vw;
    height: auto;
    margin-left: 20rem;
  }

  .link-h1 {
    margin-left: 2em;
    margin-top: 1em;
  }

  .link-h2 {
    margin-left: 3em;
    margin-top: 1em;
  }

  @media (max-width: 840em) {
    .centered {
      overflow-x: auto;
    }
  }

  @media (max-width: 1080px) {

    .left-pane {
      display: none;
      position: unset;
    }

    .right-pane {
      margin-left: 0;
      width: 100vw;
    }
  }

</style>
