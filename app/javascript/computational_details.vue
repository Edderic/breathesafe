<template>
  <DrillDownSection
    title='Computational Details'
    :showStat='false'
  >

    <div class='item-span-wide' id='section-computational-details'>
      <div class='container'>
        <div class='centered'>
          <table>
            <tr>
              <th class='col centered'>
                <span>Risk</span>
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
                :value='this.selectedIntervention.computeRiskRounded(this.selectedHour)'
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
                :value='roundOut(susceptibleProductWithIntervention, 6)'
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
                :value='roundOut(cadr, 1)'
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
                <span>Quanta Generation Rate</span>
                <span class='font-light'>(Quanta / h)</span>
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
                  {{selectedInfectorMask.maskType}}
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
                :value=10
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
                :value='1 - selectedInfectorMask.filtrationEfficiency()'
                :text='roundOut(1 - selectedInfectorMask.filtrationEfficiency(), 6)'
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
                :value='roundOut(susceptibleProductWithIntervention, 6)'
                class='color-cell'
              />

              <td>=</td>
              <ColoredCell
                :colorScheme="riskiestMaskColorScheme"
                :maxVal=1
                :value='1 - selectedSusceptibleMask.filtrationEfficiency()'
                :text='roundOut(1 - selectedSusceptibleMask.filtrationEfficiency(), 6)'
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

        <div class='container' id='section-details-ventilation-ach'>
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
                  :colorScheme="carbonDioxideColorScheme"
                  :maxVal=1
                  :value='roundOut(this.selectedIntervention.steadyStateCO2Reading(numInfectors, numSusceptibles), 0)'
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
                <td v-if='i == 0' >
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeTotalAch"
                    :maxVal=1
                    :value='roundOut(this.selectedIntervention.computeEmissionRate(), 3)'
                    class='color-cell'
                  />
                </td>
                <td v-else></td>

                <td v-if='i == 0'>=</td>
                <td v-else>+</td>

                <td>
                  <ColoredCell
                    :colorScheme="colorInterpolationSchemeTotalAch"
                    :maxVal=1
                    :value='roundOut(co2Rate(activityGroup), 6)'
                    class='color-cell'
                  />
                </td>

                <td>x</td>

                <td>
                <ColoredCell
                  :colorScheme="colorInterpolationSchemeTotalAch"
                  :maxVal=1
                  :value='activityGroup.numberOfPeople'
                  class='color-cell'
                  style='background-color: grey'
                />
                </td>

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

        <div class='container' id='section-details-upper-room-germicidal-uv-ach'>
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
        <h4 >Portable Air Cleaner ACH</h4>

        <div class='container' id='section-details-portable-air-cleaner-ach'>
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
      </div>
    </div>
  </DrillDownSection>
</template>

<script>
import {
  CO2_TO_MET,
  QUANTA,
  computePortableACH,
  computeVentilationACH,
  convertCubicMetersPerHour,
  cubicFeetPerMinuteTocubicMetersPerHour,
  displayCADR,
  findWorstCaseInhFactor,
  getCO2Rate,
  infectorActivityTypes,
  maskToPenetrationFactor,
  setupCSRF,
  simplifiedRisk,
  steadyStateFac,
  susceptibleBreathingActivityToFactor,
  round

} from  './misc';

import {
  AEROSOL_GENERATION_BOUNDS,
  colorSchemeFall,
  colorPaletteFall,
  co2ColorScheme,
  assignBoundsToColorScheme,
  riskColorInterpolationScheme,
  infectedPeopleColorBounds,
  convertColorListToCutpoints,
  generateEvenSpacedBounds } from './colors.js';

import ColoredCell from './colored_cell.vue'
import CircularButton from './circular_button.vue'
import DrillDownSection from './drill_down_section.vue'

export default {
  name: 'ComputationalDetails',
  components: {
    CircularButton,
    ColoredCell,
    DrillDownSection
  },
  data() {
    return {
      show: false
    }
  },
  props: {
    activityGroups: Array,
    numSusceptibles: Number,
    numInfectors: Number,
    roomUsableVolumeCubicMeters: Number,
    roomLengthMeters: Number,
    roomWidthMeters: Number,
    riskColorScheme: Array,
    riskiestPotentialInfector: Object,
    selectedHour: Number,
    selectedInfectorMask: Object,
    selectedIntervention: Object,
    selectedSusceptibleMask: Object,
    aerosolActivityToFactor: Function,
    worstCaseInhalation: Object
  },
  computed: {
    carbonDioxideColorScheme() {
      return co2ColorScheme
    },
    averageInfectedPeopleInterpolationScheme() {
      const copy = JSON.parse(JSON.stringify(riskColorInterpolationScheme))
      return assignBoundsToColorScheme(copy, infectedPeopleColorBounds)
    },
    colorInterpolationSchemeRoomVolumeMetric() {
      return assignBoundsToColorScheme(colorSchemeFall, this.cutoffsMetricVolume)
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
    cadr() {
      return this.computeTotalFlowRate( this.roomUsableVolumeCubicMeters * this.selectedIntervention.computeACH())
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
    intermediateProductWithIntervention() {
      return this.infectorProductWithIntervention * this.susceptibleProductWithIntervention
         * this.selectedHour / this.cadr
    },
    infectorProductWithIntervention() {
      return QUANTA * this.aerosolActivityToFactor(
        this.riskiestPotentialInfector["aerosolGenerationActivity"]
      ) * (1 - this.selectedInfectorMask.filtrationEfficiency())
    },
    riskiestMaskColorScheme() {
      const copy = JSON.parse(JSON.stringify(colorPaletteFall))
      const cutPoints = convertColorListToCutpoints(copy)
      return assignBoundsToColorScheme(cutPoints, infectedPeopleColorBounds)
    },
    susceptibleProductWithIntervention() {
      return (1 - this.selectedSusceptibleMask.filtrationEfficiency())
        * this.worstCaseInhalation["inhalationFactor"]
    },

  }, methods: {
    co2Rate(activityGroup) {
      let blah = getCO2Rate(
        CO2_TO_MET[activityGroup.carbonDioxideGenerationActivity],
        activityGroup["sex"] == "Male",
        activityGroup["ageGroup"]
      )
      return blah
    },
    computeTotalFlowRate(totalFlowRateCubicMetersPerHour) {
      return displayCADR('metric', totalFlowRateCubicMetersPerHour)
    },
    roundOut(someValue, numRound) {
      return round(someValue, numRound)
    },
  }

}
</script>

<style scoped>
  .container {
    margin: 1em;
  }

  .centered {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .col {
    display: flex;
    flex-direction: column;
  }

  .font-light {
    font-weight: 400;
  }

  .color-cell {
    font-weight: bold;
    color: white;
    text-shadow: 1px 1px 2px black;
    padding: 1em;
  }

  td {
    padding: 1em;
  }

  #section-computational-details {
    font-size: 0.5em;
  }

</style>
