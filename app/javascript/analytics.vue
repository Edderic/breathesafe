<template>

  <div class='col'>
    <div class='row'>
      <div class='col border-showing left-pane'>
        <router-link :to="`/analytics/${this.$route.params.id}#risk-assessment`" class='link-h1'>
          Risk Assessment
        </router-link>
        <router-link :to="`/analytics/${this.$route.params.id}#overview`" class='link-h1'>
          Overview
        </router-link>
        <router-link :to="`/analytics/${this.$route.params.id}#strengths`" class='link-h2'>
          Strengths
        </router-link>
        <router-link :to="`/analytics/${this.$route.params.id}#room-for-improvement`" class='link-h2'>
          Room for Improvement
        </router-link>
        <router-link :to="`/analytics/${this.$route.params.id}#details`" class='link-h1'>
          Details
        </router-link>
        <router-link :to="`/analytics/${this.$route.params.id}#clean-air-delivery-rate`" class='link-h2'>
          Clean Air Delivery Rate (CADR)
        </router-link>
        <router-link :to="`/analytics/${this.$route.params.id}#air-changes-per-hour`" class='link-h2'>
          Air Changes per Hour (ACH)
        </router-link>
        <router-link :to="`/analytics/${this.$route.params.id}#total-ach`" class='link-h2'>
          Total ACH
        </router-link>
        <router-link :to="`/analytics/${this.$route.params.id}#behaviors`" class='link-h2'>
          Behaviors
        </router-link>
        <router-link :to="`/analytics/${this.$route.params.id}#inhalation`" class='link-h2'>
          Inhalation
        </router-link>
        <router-link :to="`/analytics/${this.$route.params.id}#exhalation`" class='link-h2'>
          Exhalation
        </router-link>

        <router-link :to="`/analytics/${this.$route.params.id}#masking`" class='link-h2'>
          Masking
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
          <h4 class='subsection' v-if='event && event.placeData'>{{event.placeData.formattedAddress}}</h4>
          <h4 class='subsection' v-if='event && event.firstName'>Measurements taken by {{event.firstName}} {{event.lastName}}</h4>
          <h4 class='subsection'>on {{datetimeInWords}}</h4>
          <div class='centered col'>
            <div class='container'>

              <div class='centered col'>
                <div class='centered'>
                  <table>
                  <tr>
                    <th>
                       Mask
                    </th>
                    <td>
                      <select class='centered' @change='selectMask'>
                        <option :value="mask.maskName" v-for='mask in maskInstances'>{{mask.maskName}}</option>
                      </select>
                    </td>
                  </tr>
                  <tr>

                    <td>
                      <select class='centered' @change='selectIntervention'>
                        <option :value="interv.id" v-for='interv in interventions'>{{interv.textString()}}</option>
                      </select>
                    </td>
                  </tr>
                  </table>
                </div>
                <RiskTable
                  :maximumOccupancy='maximumOccupancy'
                  :interventions='interventions'
                  :event='event'
                  :selectedIntervention='selectedIntervention'

                />
              </div>

              <p>

                The assessments below assume that an infector is present and is
                doing the riskiest recorded behaviors. For example, the model assumes that the
                infector is wearing the riskiest mask (i.e. the mask with the worst fit and
                filtration efficiency) and is also doing the riskiest aerosol generation activity
                recorded (e.g. loudly talking).
              </p>

              <br id='overview'>
              <br>
              <br>
              <h3>Overview</h3>


          <br id='strengths'>
          <br>
          <br>
          <h4>Strengths</h4>
          <ul>
            <li v-if="selectedIntervention.computeCleanAirDeliveryRate(systemOfMeasurement) > 1000">

              <span class='italic bold'>
                <router-link :to="`/analytics/${this.$route.params.id}#clean-air-delivery-rate`">
                  Clean Air Delivery Rate (CADR):
                </router-link>
              </span>&nbsp;&nbsp;


              Assuming that the air is well-mixed (i.e. infector's air
              particles are distributed evenly throughout the space (i.e. via fans),
              people are getting

              <ColoredCell
                :colorScheme="colorInterpolationSchemeRoomVolume"
                :maxVal=1
                :value='roundOut(selectedIntervention.computeCleanAirDeliveryRate(systemOfMeasurement), 0)'
                :style='cellCSSMerged'
              />

            {{ measurementUnits.airDeliveryRateMeasurementType }} of clean air.
            </li>

            <li v-if='maskingBarChart.isStrength(0.2)'>
            <span class='italic bold'>
              <router-link :to="`/analytics/${this.$route.params.id}#masking`" class='link-h2'>
                Masking
              </router-link>
            </span>&nbsp;&nbsp;

            <ColoredCell
              :colorScheme="reducedRiskColorScheme"
              :maxVal=1
              :value='roundOut(maskingBarChart.fractionOfSubparMasks(), 2)'
              :style='cellCSSMerged'
            />
            </li>

            <li v-if='exhalationActivityIsStrength'>
              <span class='italic bold'>
                <router-link :to="`/analytics/${this.$route.params.id}#exhalation`">
                  Exhalation activity:
                </router-link>
              </span>&nbsp;&nbsp;


              <span>
              The riskiest aerosol generation activity recorded during this measurement is <ColoredCell
                    :colorScheme="riskiestAerosolGenerationActivityScheme"
                    :maxVal=1
                    :value='aerosolActivityToFactor(riskiestPotentialInfector["aerosolGenerationActivity"])'
                    :text='riskiestPotentialInfector["aerosolGenerationActivity"]'
                    :style="inlineCellCSS"
                />.
              </span>
            </li>

            <li v-if='inhalationActivityIsStrength'>
              <span class='italic bold'>
                <router-link :to="`/analytics/${this.$route.params.id}#inhalation`">
                  Inhalation activity:
                </router-link>
              </span>&nbsp;&nbsp;

              <span>The worst case inhalation activity is <ColoredCell
                    :colorScheme="inhalationActivityScheme"
                    :maxVal=1
                    :value='worstCaseInhalation["inhalationFactor"]'
                    :text='worstCaseInhalation["inhalationActivity"]'
                    :style="inlineCellCSS"
                />.
              </span>
            </li>

            <li v-if='maskingBarChart.isStrength(0.2)'>
            <span class='italic bold'>
              <router-link :to="`/analytics/${this.$route.params.id}#masking`" class='link-h2'>
                Masking
              </router-link>
            </span>&nbsp;&nbsp;
            </li>
          </ul>

          <br id='room-for-improvement'>
          <br>
          <br>
          <h4>Room for Improvement</h4>
          <ul>
            <li v-if="selectedIntervention.computeCleanAirDeliveryRate(systemOfMeasurement) <= 1000">
              <span class='italic bold'>
                <router-link :to="`/analytics/${this.$route.params.id}#clean-air-delivery-rate`">
                  Clean Air Delivery Rate (CADR):
                </router-link>
              </span>&nbsp;&nbsp;

              <ColoredCell
                :colorScheme="colorInterpolationSchemeRoomVolume"
                :maxVal=1
                :value='roundOut(selectedIntervention.computeCleanAirDeliveryRate(systemOfMeasurement), 0)'
                :style='cellCSSMerged'
              /> {{ measurementUnits.airDeliveryRateMeasurementType }} of clean
              air. One can invest in ventilation, filtration, and/or upper-room UV
              technologies to increase the amount of clean air delivered, which
              will dilute the inhaled dose of contaminants such as SARS-CoV-2.
            </li>

            <li v-if='!maskingBarChart.isStrength(0.2)'>
            <span class='italic bold'>
              <router-link :to="`/analytics/${this.$route.params.id}#masking`">
                Masking:
              </router-link>
            </span> &nbsp;&nbsp; <ColoredCell
              :colorScheme="reducedRiskColorScheme"
              :maxVal=1
              :text='roundOut(maskingBarChart.fractionOfSubparMasks() * 100, 2)'
              :value='roundOut(maskingBarChart.fractionOfSubparMasks(), 2)'
              :style='cellCSSMerged'
            /> percent of people were wearing subpar masks. Switching to better-fitting, high filtration efficiency masks such as N95s or elastomeric respirators is a very cost-effective way to decrease risk.
            </li>

            <li v-if='!exhalationActivityIsStrength'>
              <span class='italic bold'>
                <router-link :to="`/analytics/${this.$route.params.id}#exhalation`">
                  Exhalation activity:
                </router-link>
              </span>&nbsp;&nbsp;


              <span>
              The riskiest aerosol generation activity recorded during this measurement was <ColoredCell
                    :colorScheme="riskiestAerosolGenerationActivityScheme"
                    :maxVal=1
                    :value='aerosolActivityToFactor(riskiestPotentialInfector["aerosolGenerationActivity"])'
                    :text='riskiestPotentialInfector["aerosolGenerationActivity"]'
                    :style="inlineCellCSS"
                />.
              </span>
            </li>

            <li v-if='!inhalationActivityIsStrength'>
              <span class='italic bold'>
                <router-link :to="`/analytics/${this.$route.params.id}#inhalation`">
                  Inhalation activity:
                </router-link>
              </span>&nbsp;&nbsp;

              <span>The worst case inhalation activity was <ColoredCell
                    :colorScheme="inhalationActivityScheme"
                    :maxVal=1
                    :value='worstCaseInhalation["inhalationFactor"]'
                    :text='worstCaseInhalation["inhalationActivity"]'
                    :style="inlineCellCSS"
                />.
              </span>
            </li>


          </ul>



          <br id='details'>
          <br>
          <br>
          <h3>Details</h3>


          <br id='clean-air-delivery-rate'>
          <br>
          <br>
          <h4>Clean Air Delivery Rate</h4>

          <div class='container'>
            <div class='centered'>
              <CleanAirDeliveryRateTable
                :measurementUnits='measurementUnits'
                :systemOfMeasurement='systemOfMeasurement'
                :intervention='selectedIntervention'
                :cellCSS='cellCSS'
              />
            </div>
          </div>

          <p>
          To give context of what {{roundOut(totalFlowRate, 1)}} {{
          measurementUnits.airDeliveryRateMeasurementType}} means, that is
          about {{
            roundOut(totalFlowRatePerAirCleanerSuggestion, 1)}} times the amount 1
            <a :href="airCleanerSuggestion.website"> {{
              airCleanerSuggestion['singular']}}
            </a> outputs.
            <span class='bold'>
              Adding {{
              numSuggestedAirCleaners }} {{ airCleanerSuggestion['plural'] }} would
              increase the CADR to

              <ColoredCell
                :colorScheme="colorInterpolationSchemeRoomVolume"
                :maxVal=1
                :value='totalFlowRatePlusExtraPacRounded'
                :style='cellCSSMerged'
              />
                {{ measurementUnits.airDeliveryRateMeasurementType}}, which would
                decrease the probability of infection by a factor of {{
                  roundOut(totalFlowRatePlusExtraPacRounded / totalFlowRate, 1)
                }} (assuming the risk was low to begin with).
            </span>
          </p>

          <p>
          A combination of larger rooms along with high ACH can reduce the risk
          of contracting COVID-19 and other airborne viruses. The product of the two
          gives us the Clean Air Delivery Rate (CADR). The higher it is,
          relative to the production rate of contaminants such as airborne
          viruses like that of COVID-19, the safer the environment.
          </p>

          <br id='air-changes-per-hour'>
          <br>
          <br>
          <h4>Air Changes per Hour (ACH)</h4>
          <p>
            Air Changes per Hour (ACH) tells us how much clean air is generated
            relative to the volume of the room. If a device outputs 5 ACH, that means it
            produces clean air that is 5 times the volume of the room in an hour.  Total
            ACH for a room can be computed by summing up the ACH of different types (e.g.
            ventilation, filtration, upper-room germicidal UV).
          </p>

          <br id='total-ach'>
          <br>
          <br>
          <h4>Total ACH</h4>
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

          <div class='centered'>
          <AchToDuration
            :intervention='selectedIntervention'
          />
          </div>

          <br id='behaviors'>
          <br>
          <br>
          <h3>Behaviors</h3>

          <p>
            Activities that people partake in can affect the probability of
            transmission of COVID and other respiratory viruses. Activities
            where the infector is doing lots of exhalation and vocalization (e.g. loudly
            talking during heavy exercise) could drastically increase the
            risk of transmission. Likewise, doing activities where
            susceptibles are inhaling more air in shorter time increases their risk of
            getting COVID.

          </p>
          <p>

          </p>
          <p>
            Choosing activities where an infector is quiet and at rest, along
            with susceptibles being at rest, could decrease the risk of
            airborne transmission.
          </p>

          <br id='inhalation'>
          <br>
          <br>
          <h4>Inhalation</h4>
          <p> The worst case inhalation activity was <ColoredCell
                              :colorScheme="inhalationActivityScheme"
                              :maxVal=1
                              :value='worstCaseInhalation["inhalationFactor"]'
                              :text='worstCaseInhalation["inhalationActivity"]'
                              :style="inlineCellCSS"
                          />, which corresponds to a factor of
              <ColoredCell
                  :colorScheme="inhalationActivityScheme"
                  :maxVal=1
                  :value='worstCaseInhalation["inhalationFactor"]'
                  :style="inlineCellCSS"
              />. To better contextualize how good this is, let's look at the
              table of inhalation activities and factors:
          </p>

          <div class='centered'>
            <table>
              <tr>
                <th>Inhalation Activity</th>
                <th>Factor</th>
              </tr>
              <tr v-for='(value, key, index) in susceptibleBreathingActivityFactorMappings'>
                <td style='padding: 0.25em 1em;'>{{ ['Sleep or Nap', 'Sedentary / Passive', 'Light Intensity', 'Moderate Intensity', 'High Intensity'][index] }}</td>
                <td style='padding: 0;'>
                  <ColoredCell
                    :colorScheme="inhalationActivityScheme"
                    :maxVal=1
                    :value='inhalationValue(value)'
                    :style="tableColoredCellWithHorizPadding"
                    />
                </td>
              </tr>
            </table>
          </div>
          <p>
          If someone were to go from <ColoredCell
                :colorScheme="inhalationActivityScheme"
                :maxVal=1
                :value='worstCaseInhalation["inhalationFactor"]'
                :text='worstCaseInhalation["inhalationActivity"]'
                :style="inlineCellCSS"
            /> to <ColoredCell
                :colorScheme="inhalationActivityScheme"
                :maxVal=1
                :value='susceptibleBreathingActivityFactorMappings["High Intensity"]["30 to <40"]["mean cubic meters per hour"]'
                text='High intensity'
                :style="inlineCellCSS"
            />, this increases the risk by a factor of <ColoredCell
                :colorScheme="inhalationActivityScheme"
                :maxVal=1
                :value='roundOut(susceptibleBreathingActivityFactorMappings["High Intensity"]["30 to <40"]["mean cubic meters per hour"] / worstCaseInhalation["inhalationFactor"], 1)'
                :style="inlineCellCSS"
            />, assuming that the risk was low to begin with.
          </p>

          <br id='exhalation'>
          <br>
          <br>
          <h4>Exhalation</h4>

              <span>
              The riskiest aerosol generation activity recorded for a person in this measurement is <ColoredCell
                    :colorScheme="riskiestAerosolGenerationActivityScheme"
                    :maxVal=1
                    :value='aerosolActivityToFactor(riskiestPotentialInfector["aerosolGenerationActivity"])'
                    :text='riskiestPotentialInfector["aerosolGenerationActivity"]'
                    :style="inlineCellCSS"
                />. Here's a table to contextualize how good or bad it is. In this model, it essentially maps into a factor, where higher leads to more risk.
              </span>
              <div class='centered'>
                <table>
                  <tr>
                    <th>Infector Activity</th>
                    <th>Factor</th>
                  </tr>
                  <tr v-for='(value, key) in infectorActivities'>
                    <td class='table-td'>{{key}}</td>
                    <td class='table-td'>
                    <ColoredCell
                      :colorScheme="riskiestAerosolGenerationActivityScheme"
                      :maxVal=1
                      :value='value'
                      :style="tableColoredCell"
                    />
                    </td>
                  </tr>
                </table>
              </div>

              <p>
                For example, <ColoredCell
                    :colorScheme="riskiestAerosolGenerationActivityScheme"
                    :maxVal=1
                    :value='aerosolActivityToFactor(riskiestPotentialInfector["aerosolGenerationActivity"])'
                    :text='riskiestPotentialInfector["aerosolGenerationActivity"]'
                    :style="inlineCellCSS"
                /> maps to <ColoredCell
                    :colorScheme="riskiestAerosolGenerationActivityScheme"
                    :maxVal=1
                    :value='aerosolActivityToFactor(riskiestPotentialInfector["aerosolGenerationActivity"])'
                    :style="inlineCellCSS"
                />. On the other hand, <ColoredCell
                    :colorScheme="riskiestAerosolGenerationActivityScheme"
                    :maxVal=1
                    :value='aerosolActivityToFactor("Heavy exercise – Loudly speaking")'
                    text='Heavy Exercise - Loudly Speaking'
                    :style="inlineCellCSS"
                />, maps to <ColoredCell
                    :colorScheme="riskiestAerosolGenerationActivityScheme"
                    :maxVal=1
                    :value='aerosolActivityToFactor("Heavy exercise – Loudly speaking")'
                    :style="inlineCellCSS"
                />. Switching to the latter from the former  essentially
                increases the risk of transmission by a factor of <ColoredCell
                    :colorScheme="riskiestAerosolGenerationActivityScheme"
                    :maxVal=1
                    :value='roundOut(aerosolActivityToFactor("Heavy exercise – Loudly speaking") / aerosolActivityToFactor(riskiestPotentialInfector["aerosolGenerationActivity"]), 1)'
                    :style="inlineCellCSS"
                />, assuming the risk was low to begin with.
              </p>

            </div>

          </div>

          <div class='container'>
          <br id='masking'>
          <br>
          <br>
          <h4>Masking</h4>
          <p>Here is the breakdown of masking prevalance:</p>
          <div class='centered'>
            <HorizontalStackedBar
              :values="maskingBarChart.maskingValues()"
              :colors="maskingBarChart.maskingColors()"
            />
          </div>

          <p>
          To see the effects of masking by yourself vs. when everyone is
          masked, see graph below, which shows the relative amount of particles left when
          a susceptible (x-axis) wears some type of mask and an infector (y-axis) also
          wears some type of mask.

          </p>
          <div class='centered'>
            <table>
              <tr>
                <th></th>
                <th style='padding: 0;' v-for='(value1, key1) in maskFactors'>



                  <svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
                    <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" transform='rotate(-40, 40, 40)' class='tilted-header'>{{key1}}</text>
                  </svg>

                </th>
              </tr>
              <tr v-for='(value1, key1) in maskFactors'>
                <th class='table-td-mask'>{{key1}}</th>
                <td class='table-td-mask' v-for='(value2, key2) in maskFactors'>
                  <ColoredCell
                    :colorScheme="riskColorScheme"
                    :maxVal=1
                    :value='roundOut(value1 * value2, 6)'
                    :style="tableColoredCellMasking"
                  />
                </td>
              </tr>
            </table>
          </div>

          <p>
          For example, when the infector is unmasked (i.e.
              "None"), but the susceptible is wearing a KN95, then 0.15 of infectious
          particles are left over for the susceptible to inhale, which is an 85%
          reduction of particles. If both wore KN95s, then the left over particles is
          0.0225 (i.e. a 98.75% reduction of infectious airborne particles a susceptible
              can inhale).  <span class='bold'>If both wore elastomeric N99 respirators, then
          we get a 10,000-fold reduction!</span> Upgrading to N95 respirators and above
          (i.e. tight-fitting, high filtration efficiency), and having mask mandates
          especially in times of surges, is a very effective and cost-efficient way to
          prevent the spread of COVID-19 and other airborne respiratory viruses.
          </p>
          <p>The riskiest mask recorded for this measurement is <span><ColoredCell
                :colorScheme="riskiestMaskColorScheme"
                :maxVal=1
                :value='riskiestMask["maskPenetrationFactor"]'
                :text='riskiestMask["maskType"]'
                :style="inlineCellCSS"
            /></span>, so susceptibles are assumed to be wearing these (unless specified otherwise in the Interventions section).
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
                    v-if="selectedIntervention"
                    :colorScheme="averageInfectedPeopleInterpolationScheme"
                    :maxVal=1
                    :value='roundOut(infectorProductWithIntervention, 1)'
                    class='color-cell'
                  />
                  <td>x</td>
                  <ColoredCell
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
                    :colorScheme="averageInfectedPeopleInterpolationScheme"
                    :maxVal=1
                    :value='roundOut(infectorProductWithIntervention, 1)'
                    class='color-cell'
                  />
                  <td>=</td>
                  <ColoredCell
                    :colorScheme="averageInfectedPeopleInterpolationScheme"
                    :maxVal=1
                    :value=18.6
                    class='color-cell'
                  />
                  <td>x</td>
                  <ColoredCell
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
import { Intervention } from './interventions.js'
import TotalACHTable from './total_ach_table.vue';
import VentIcon from './vent_icon.vue';
import PacIcon from './pac_icon.vue';
import RiskIcon from './risk_icon.vue';
import { airCleaners } from './air_cleaners.js';
import { datetimeEnglish } from './date.js'
import { getSampleInterventions } from './sample_interventions.js'
import {
  AEROSOL_GENERATION_BOUNDS,
  colorSchemeFall,
  colorPaletteFall,
  assignBoundsToColorScheme,
  riskColorInterpolationScheme,
  infectedPeopleColorBounds,
  convertColorListToCutpoints,
  generateEvenSpacedBounds } from './colors.js';
import AchToDuration from './ach_to_duration.vue'
import {
  findRiskiestMask,
  findRiskiestPotentialInfector,
  riskOfEncounteringInfectious,
  riskIndividualIsNotInfGivenNegRapidTest,
  reducedRisk } from './risk.js';
import { convertVolume, computeAmountOfPortableAirCleanersThatCanFit } from './measurement_units.js';
import { useAnalyticsStore } from './stores/analytics_store'
import { Mask, MASKS, MaskingBarChart } from './masks.js';
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
  susceptibleBreathingActivityToFactor,
  round

} from  './misc';

export default {
  name: 'Analytics',
  components: {
    AchToDuration,
    ColoredCell,
    CleanAirDeliveryRateTable,
    DayHourHeatmap,
    Event,
    HorizontalStackedBar,
    PacIcon,
    RiskIcon,
    RiskTable,
    TotalACHTable,
    VentIcon
  },
  computed: {
    ...mapState(
        useMainStore,
        [
          'currentUser',
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
    cellCSSMerged() {
      let def = {
        'font-weight': 'bold',
        'color': 'white',
        'text-shadow': '1px 1px 2px black',
        'text-align': 'center',
        'display': 'inline-block',
        'padding': '1em'
      }

      return Object.assign(def, this.cellCSS)
    },
    cellCSS() {
      return {
        'padding-top': '1em',
        'padding-bottom': '1em',
      }
    },
    maskInstances() {
      let collection = []
      for (let m of MASKS) {
        collection.push(new Mask(m, this.maximumOccupancy))
      }

      return collection
    },
    interventions() {
      return getSampleInterventions(this.event, this.numPeopleToInvestIn)
    },
    datetimeInWords() {
      return datetimeEnglish(this.startDatetime)
    },
    durationWithIntervention() {
      return 40
    },
    inhalationActivityIsStrength() {
      // highest range for Sedentary / Sedentary passive is 6 to <11
      return this.worstCaseInhalation['inhalationFactor']
        <= susceptibleBreathingActivityToFactor['Sedentary / Passive']['6 to <11'][
          'mean cubic meters per hour'
        ]
    },

    exhalationActivityIsStrength() {
      return this.aerosolActivityToFactor(this.riskiestPotentialInfector["aerosolGenerationActivity"])
        <= this.infectorActivityTypeMapping["Standing – Speaking"]
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
      const numObjects = 6
      const evenSpacedBounds = generateEvenSpacedBounds(minimum, maximum, numObjects)

      const scheme = convertColorListToCutpoints(
        JSON.parse(JSON.stringify(colorPaletteFall)).reverse()
      )

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
    async event() {
      return await this.showAnalysis(this.$route.params.id)
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
    totalFlowRatePerAirCleanerSuggestion() {
      return this.totalFlowRateCubicMetersPerHour / this.airCleanerSuggestion.cubicMetersPerHour
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
  async created() {
    let event = await this.showAnalysis(this.$route.params.id)

    await this.$watch(
      () => this.$route.params,
      (toParams, previousParams) => {
        this.showAnalysis(toParams.id)
      }
    )
  },
  data() {
    return {
      event: {
        activityGroups: [],
        portableAirCleaners: [],
        totalAch: 0.1
      },
      center: {lat: 51.093048, lng: 6.842120},
      ventilationACH: 0.0,
      portableACH: 0.0,
      totalACH: 0.0,
      maskFactors: maskToPenetrationFactor,
      tableColoredCellWithHorizPadding: {
        'color': 'white',
        'font-weight': 'bold',
        'text-shadow': '1px 1px 2px black',
        'padding': '0.5em',
      },
      tableColoredCell: {
        'color': 'white',
        'font-weight': 'bold',
        'text-shadow': '1px 1px 2px black',
        'padding-top': '0.5em',
        'padding-bottom': '0.5em',
      },
      tableColoredCellMasking: {
        'color': 'white',
        'font-weight': 'bold',
        'text-shadow': '1px 1px 2px black',
        'padding-top': '0.5em',
        'padding-bottom': '0.5em',
        'width': '5em',
      },
      infectorActivities: infectorActivityTypes,
      inlineCellCSS: {
        'display': 'inline-block',
        'font-weight': 'bold',
        'color': 'white',
        'text-shadow': '1px 1px 2px black',
        'padding': '1em',
        'margin': '0.5em',
        'text-align': 'center'
      },
      selectedMask: new Mask(MASKS[0], this.maximumOccupancy),
      selectedIntervention: {
        computeCleanAirDeliveryRate() {
          return 0
        },
        computePortableAirCleanerACH() {
          return 0.01
        },
        computeVentilationACH() {
          return 0.01
        },
        computeUVACH() {
          return 0.01
        },
        computeEmissionRate() {
          return 0.01
        },
        computeVentilationDenominator() {
          return 0.01
        },
        computeSusceptibleMask() {
          return {
            'maskPenetrationFactor': 'None'
          }
        },
        computeRiskRounded() {
          return 0
        },
        computeACH() {
          return 0
        },
        findPortableAirCleaners() {
          return {
            'cubic meters per hour': 0,
            'numDevices': 0
          }
        },
        ventilationDenominator() { return 0.01 },
        steadyStateCO2Reading() { return 0.01 },
        ambientCO2Reading() { return 0.01 },
        findPortableAirCleaners() {
          return {
            'numDevices': function() { return 0 },
            'numDeviceFactor': function() { return 0 },
            'singularName': function() { return '' }
          }
        },
        findUVDevices() {
          return {
            'numDevices': function() { return 0 },
            'numDeviceFactor': function() { return 0 }
          }
        },
        implementationCostInYears() {
          return 0
        }
      },
      susceptibleBreathingActivityFactorMappings: susceptibleBreathingActivityToFactor
    }
  },
  methods: {
    ...mapActions(useAnalyticsStore, ['setNumPeopleToInvestIn']),
    ...mapActions(useMainStore, ['setGMapsPlace', 'setFocusTab', 'getCurrentUser']),
    ...mapActions(useEventStore, ['addPortableAirCleaner']),
    ...mapState(useEventStore, ['findActivityGroup', 'findPortableAirCleaningDevice']),
    selectMask(event) {
      let name = event.target.value
      this.selectedMask = new Mask(MASKS.find((m) => m.name == name), this.maximumOccupancy)
      this.selectedIntervention =  new Intervention(this.event, [], this.selectedMask)
    },
    selectIntervention(event) {
      let id = event.target.value
      let intervention = this.interventions.find((interv) => { return interv.id == id })
      this.selectedIntervention = intervention
    },
    inhalationValue(value) {
      if (value && this.worstCaseInhalation["ageGroup"]) {
        return value[this.worstCaseInhalation["ageGroup"]]["mean cubic meters per hour"]
      } else {
        return 0
      }
    },
    async showAnalysis(id) {
      let eventStores = useEventStores()
      const showMeasurementSetStore = useShowMeasurementSetStore()
      let event = await eventStores.findOrLoad(id);
      this.event = event
      showMeasurementSetStore.setMeasurementSet(event)

      return event
    },
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
    border-right: 1px solid black;
    height: 100vh;
    border-top: 0px;
    border-bottom: 0px;
  }

  .right-pane {
    height: auto;
    width: 70%;
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

  .icon-bar {
    position: fixed;
    background-color: white;
  }

  .italic {
    font-style: italic;
  }

  .bold {
    font-weight: bold;
  }

  .table-td-mask {
    padding: 0;
    width: 3em;
  }

  .table-td {
    padding: 0 0.5em;
  }

  .tilted-header {
    font-size: 0.5em;
  }

  th.table-td-mask {
    font-size: 0.5em;
  }
</style>
