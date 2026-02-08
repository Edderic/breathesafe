<template>
  <div class='main-container align-items-center'>

    <!-- Progress Bar for New/Edit Mode -->
    <div class='columns' v-if='newOrEditMode'>
      <MaskProgressBar
        :uniqueInternalModelCode="uniqueInternalModelCode"
        :initialCostUsDollars="initialCostUsDollars"
        :colors="colors"
        :filterType="filterType"
        :style="style"
        :strapType="strapType"
        :hasExhalationValve="hasExhalationValve"
        :imageUrls="imageUrls"
        :whereToBuyUrls="whereToBuyUrls"
        :perimeterMm="perimeterMm"
        :massGrams="massGrams"
        :filtrationEfficiencies="filtrationEfficiencies"
        :breathability="breathability"
        :currentStep="tabToShow"
        @navigate-to-step="navigateToStep"
      />
    </div>

    <div :class="['main', 'main-section', { 'with-sidebar': newOrEditMode }]" >
      <div class='header'>
        <h2 class='tagline'>{{tagline}}</h2>
        <TabSet
          v-if='!newOrEditMode'
          :options='tabToShowOptions'
          :tabToShow='displayTab'
          @update='handleDisplayTabChange'
        />
        <ClosableMessage @onclose='messages = []' :messages='messages'/>
      </div>
    </div>

    <div :class="['main', 'main-section', { 'with-sidebar': newOrEditMode }]" v-show="displayTab == 'Misc. Info'">
      <div :class='{ grid: true, view: showMode, edit: !showMode, triple: columnCount == 3, quad: columnCount == 4}'>
        <table v-if='tabToShow == "Image & Purchasing" || showMode'>
          <tbody>
            <tr>
              <td colspan='3'>
                <CircularButton text="?" @click="showHelp = true" v-if='newOrEditMode'/>
              </td>
            </tr>
            <tr v-show='newOrEditMode' v-for='(imageUrl, index) in imageUrls'>
              <td></td>
              <th>Image URL</th>
              <td>
                <input class='input-list' type="text" :value='imageUrl' @change="update($event, 'imageUrls', index)"
                                          v-show="newOrEditMode" placeholder="e.g. https://examplemask.com/mask1.jpg"
                                                             >
              </td>
            </tr>

            <tr v-for="(imageUrl, index) in imageUrls">
              <td :colspan='3' class='text-align-center'>
                <img class='preview' :src="imageUrl" :alt="maskImageAlt(index)">
              </td>
            </tr>


            <tr v-if='newOrEditMode'>
              <th colspan='2'>Purchasing URLs</th>
              <td >
                <CircularButton text="+" @click="addPurchasingUrl" v-if='newOrEditMode'/>
              </td>
            </tr>
            <tr v-if='whereToBuyUrls.length > 0'>
              <th colspan='2' >Purchasing URL</th>
              <th v-if='userCanEdit && editMode'>Delete</th>
            </tr>
            <tr v-for="(purchasingUrl, index) in whereToBuyUrls" class='text-align-center'>
              <td :colspan='whereToBuyUrlsColspan' >
                <input class='input-list almost-full-width' type="text" :value='purchasingUrl' @change="update($event, 'whereToBuyUrls', index)"
                                                            v-if="newOrEditMode"
                                                            >
                                                            <a :href="purchasingUrl" v-if="!newOrEditMode">{{shortHand(purchasingUrl)}}</a>
              </td>
              <td>
                <CircularButton text="x" @click="deletePurchasingUrl(index)" v-show='newOrEditMode && userCanEdit'/>
              </td>
            </tr>
          </tbody>

        </table>

        <table v-if='tabToShow == "Basic Info" || showMode' class='one-column'>
          <tbody>
            <tr>
              <th>Unique Internal Model Code</th>
              <td>
                <span class='full-width has-minimal-width ' v-show="!newOrEditMode">
                  {{uniqueInternalModelCode }}
                </span>
              </td>
            </tr>
            <tr>
              <th>Initial cost (US Dollars)</th>
                       <ColoredCell
                           v-show='!newOrEditMode'
                           class='risk-score'
                           :colorScheme="costColorScheme"
                           :maxVal=1
                           :value='initialCostUsDollars'
                           :exception='exceptionDollarObject'
                           :text='dollarText(initialCostUsDollars)'
                           :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black',  'border-radius': '100%' }"
                           :title='dollarText(initialCostUsDollars)'
                           />
             </tr>

          </tbody>
          <tbody>

            <tr>
              <th>Colors</th>
              <td colspan='1' class='colors'>

              <span v-for='opt in colorOptions' class='filterCheckbox' >
                <Circle :color='opt' :selected='colors.includes(opt)' :for='`color${opt}`' @click='filterFor("Color", opt)' v-if='newOrEditMode || colors.includes(opt)'/>
              </span>

              </td>
            </tr>

            <tr>
              <th >Filter type</th>
              <td colspan='1' class='text-align-center'>
                <select
                    v-model="filterType"
                    v-show="newOrEditMode"
                    >
                    <option>cloth</option>
                    <option>surgical</option>
                    <option>ASTM Lvl 3</option>
                    <option>ASTM</option>
                    <option>CE</option>
                    <option>E100</option>
                    <option>FFP2 Rated</option>
                    <option>FFP3</option>
                    <option>KF80</option>
                    <option>KF94</option>
                    <option>KN95</option>
                    <option>KN100</option>
                    <option>N95</option>
                    <option>N99</option>
                    <option>N100</option>
                    <option>Non-Rated</option>
                    <option>P95</option>
                    <option>P99</option>
                    <option>P100</option>
                    <option>PM2.5</option>
                </select>

                <span v-show='!newOrEditMode'>{{filterType}}</span>
              </td>
            </tr>
            <tr>
              <th >Style</th>
              <td colspan='1' class='text-align-center'>
                <select
                    v-model="style"
                    v-show="newOrEditMode"
                    >
                    <option>Bifold</option>
                    <option>Bifold &amp; Gasket</option>
                    <option>Boat</option>
                    <option>Cotton + High Filtration Efficiency Material</option>
                    <option>Cup</option>
                    <option>Duckbill</option>
                    <option>Elastomeric</option>
                    <option>Surgical</option>
                    <option>Adhesive</option>
                </select>
                <span v-show='!newOrEditMode'>{{style}}</span>
              </td>
            </tr>

            <tr>
              <th colspan='1'>Strap type</th>
              <td colspan='1' class='text-align-center'>
                <select
                    v-model="strapType"
                    v-show="newOrEditMode"
                    >
                    <option>Earloop</option>
                    <option>Adjustable Earloop</option>
                    <option>Headstrap</option>
                    <option>Adjustable Headstrap</option>
                    <option>Strapless</option>
                </select>
                <span v-show='!newOrEditMode'>{{strapType}}</span>
              </td>
            </tr>

            <tr>
              <th>Has exhalation valve</th>
              <td v-show='!newOrEditMode'>{{hasExhalationValve}}</td>
              <td v-show="newOrEditMode">
                <input type="text" v-model='hasExhalationValve'>
              </td>
            </tr>

          </tbody>
        </table>

        <table v-if='tabToShow == "Basic Info" || showMode' class='desktop'>
          <thead>
             <tr>
               <td colspan='2'>
                <CircularButton text="?" @click="showHelp = true" v-if='newOrEditMode'/>
               </td>
             </tr>
          </thead>
          <tbody>
            <tr>
              <th>Unique Internal Model Code</th>
              <td colspan='1'>
                <input class='full-width has-minimal-width' type="text" v-model='uniqueInternalModelCode' v-if="newOrEditMode" placeholder="e.g. Flo Mask Adults S/M Nose with Pro filter">
                <span class='full-width has-minimal-width ' v-show="!newOrEditMode">
                  {{uniqueInternalModelCode }}
                </span>
              </td>
            </tr>

            <tr>
              <th>Initial cost (US Dollars)</th>
              <td colspan='1' class='text-align-center'>
                <input type="number"
                       v-model='initialCostUsDollars'
                       v-show="newOrEditMode"
                       >

                       <div v-show='!newOrEditMode' class='stat-cell'>
                         <div v-if="statIsMissing('cost')" class='stat-bar-wrapper stat-bar-missing'>
                           <div class='stat-bar-axis'></div>
                           <div class='stat-bar stat-bar-missing-fill'></div>
                           <div class='stat-bar-label'>{{ statMissingText('cost') }}</div>
                         </div>
                         <div v-else class='stat-bar-wrapper'>
                           <div class='stat-bar-axis'></div>
                           <div class='stat-bar' :style="statBarStyle(statPercent('cost'), 'cost')"></div>
                           <div class='stat-bar-label'>{{ statLabel('cost') }}</div>
                           <div v-if="statAxisLabel('cost', 'min')" class='stat-bar-tick stat-bar-tick-left'>{{ statAxisLabel('cost', 'min') }}</div>
                           <div v-if="statAxisLabel('cost', 'max')" class='stat-bar-tick stat-bar-tick-right'>{{ statAxisLabel('cost', 'max') }}</div>
                         </div>
                       </div>
              </td>
            </tr>

            <tr>
              <th>Colors</th>
              <td colspan='1' class='colors'>

              <span v-for='opt in colorOptions' class='filterCheckbox' >
                <Circle :color='opt' :selected='colors.includes(opt)' :for='`color${opt}`' @click='filterFor("Color", opt)' v-if='newOrEditMode || colors.includes(opt)'/>
              </span>

              </td>
            </tr>

            <tr>
              <th >Filter type</th>
              <td colspan='1' class='text-align-center'>
                <select
                    v-model="filterType"
                    v-show="newOrEditMode"
                    >
                    <option>cloth</option>
                    <option>surgical</option>
                    <option>ASTM Lvl 3</option>
                    <option>ASTM</option>
                    <option>CE</option>
                    <option>E100</option>
                    <option>FFP2 Rated</option>
                    <option>FFP3</option>
                    <option>KF80</option>
                    <option>KF94</option>
                    <option>KN95</option>
                    <option>KN100</option>
                    <option>N95</option>
                    <option>N99</option>
                    <option>N100</option>
                    <option>Non-Rated</option>
                    <option>P95</option>
                    <option>P99</option>
                    <option>P100</option>
                    <option>PM2.5</option>
                </select>

                <span v-show='!newOrEditMode'>{{filterType}}</span>
              </td>
            </tr>
            <tr>
              <th >Style</th>
              <td colspan='1' class='text-align-center'>
                <select
                    v-model="style"
                    v-show="newOrEditMode"
                    >
                    <option>Bifold</option>
                    <option>Bifold &amp; Gasket</option>
                    <option>Boat</option>
                    <option>Cotton + High Filtration Efficiency Material</option>
                    <option>Cup</option>
                    <option>Duckbill</option>
                    <option>Elastomeric</option>
                    <option>Surgical</option>
                    <option>Adhesive</option>
                </select>
                <span v-show='!newOrEditMode'>{{style}}</span>
              </td>
            </tr>

            <tr>
              <th colspan='1'>Strap type</th>
              <td colspan='1' class='text-align-center'>
                <select
                    v-model="strapType"
                    v-show="newOrEditMode"
                    >
                    <option>Earloop</option>
                    <option>Adjustable Earloop</option>
                    <option>Headstrap</option>
                    <option>Adjustable Headstrap</option>
                    <option>Strapless</option>
                </select>
                <span v-show='!newOrEditMode'>{{strapType}}</span>
              </td>
            </tr>

            <tr>
              <th>Has exhalation valve</th>
              <td v-show='!newOrEditMode'>{{hasExhalationValve}}</td>
              <td v-show="newOrEditMode">
                <input type="text" v-model='hasExhalationValve'>
              </td>
            </tr>

          </tbody>
        </table>

        <table v-if='tabToShow == "Dimensions"'>
          <thead>
             <tr>
               <th colspan=2><h3>Dimensions</h3></th>
               <td>
                <CircularButton text="?" @click="showHelp = true" v-if='newOrEditMode'/>
               </td>
             </tr>
          </thead>
          <tbody>
            <tr>
              <th>Perimeter (mm)</th>
              <td>
                <input type="number" v-model="perimeterMm" v-show="newOrEditMode">
                <div v-show='!newOrEditMode' class='stat-cell'>
                  <div v-if="statIsMissing('perimeter')" class='stat-bar-wrapper stat-bar-missing'>
                    <div class='stat-bar-axis'></div>
                    <div class='stat-bar stat-bar-missing-fill'></div>
                    <div class='stat-bar-label'>{{ statMissingText('perimeter') }}</div>
                  </div>
                  <div v-else class='stat-bar-wrapper'>
                    <div class='stat-bar-axis'></div>
                    <div class='stat-bar' :style="statBarStyle(statPercent('perimeter'), 'perimeter')"></div>
                    <div class='stat-bar-label'>{{ statLabel('perimeter') }}</div>
                    <div v-if="statAxisLabel('perimeter', 'min')" class='stat-bar-tick stat-bar-tick-left'>{{ statAxisLabel('perimeter', 'min') }}</div>
                    <div v-if="statAxisLabel('perimeter', 'max')" class='stat-bar-tick stat-bar-tick-right'>{{ statAxisLabel('perimeter', 'max') }}</div>
                  </div>
                </div>
              </td>
            </tr>
            <tr>
              <th>Mass (grams)</th>
              <td>
                <input type="number" v-model="massGrams" v-show="newOrEditMode">

                <ColoredCell
                    v-show='!newOrEditMode'
                    class='risk-score'
                    :colorScheme="massColorScheme"
                    :maxVal=1
                    :value='massGrams'
                    :exception='exceptionObjectBlank'
                    :text='massText(massGrams)'
                    :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black',  'border-radius': '100%' }"
                    :title='massText(massGrams)'
                    />
              </td>
            </tr>
          </tbody>
        </table>
        <table v-if='tabToShow == "Filtration & Breathability"'>
          <tbody>
            <tr v-if='newOrEditMode'>
              <th class='text-align-left'>Filtration &amp; Breathability</th>
              <td class='text-align-right'>
                <CircularButton text="+" @click="addFiltEffAndBreathability" v-if='newOrEditMode'/>
              </td>
            </tr>
          </tbody>

          <tbody v-if='newOrEditMode' v-for="(f, index) in filtrationEfficiencies" class='text-align-center'>
            <tr>
              <th>Filtration Efficiency (Percent)</th>
              <td colspan='1'>
                <input type="number" :value='f.filtrationEfficiencyPercent' @change="updateArrayOfObj($event, 'filtrationEfficiencies', index, 'filtrationEfficiencyPercent')"
                       v-show="newOrEditMode"
                       >
              </td>
            </tr>

            <tr>
              <th>Breathability (Pa)</th>
              <td colspan='1'>
                <input type="number" :value='breathability[index].breathabilityPascals' @change="updateArrayOfObj($event, 'breathability', index, 'breathabilityPascals')"
                       v-show="newOrEditMode"
                       >
              </td>
            </tr>

            <tr>
              <th colspan='2'>Source</th>
            </tr>

            <tr>
              <td colspan='2'>
                <input type='text' class='input-list'
                       :value='f.filtrationEfficiencySource'
                       @change="updateArrayOfObj($event, 'filtrationEfficiencies', index, 'filtrationEfficiencySource')"

                       v-show="newOrEditMode"
                       >
              </td>

            </tr>

            <tr>
              <th class='notes' colspan='2'>Notes</th>
            </tr>

            <tr>
              <td colspan='2' v-show='newOrEditMode'>
                <textarea cols="30" rows="10" @change="updateArrayOfObj($event, 'filtrationEfficiencies', index, 'filtrationEfficiencyNotes')"></textarea>
              </td>
            </tr>

            <tr class='text-align-center'>
              <td colspan='2'>
                <CircularButton text="x" @click="deleteArrayOfObj($event, 'filtrationEfficiencies', index)" v-if='newMode || userCanEdit && editMode'/>
              </td>
            </tr>
          </tbody>
        </table>
        <table v-if='showMode'>
          <thead>
             <tr>
               <th colspan=2><h3>Dimensions &amp; Filtration</h3></th>
             </tr>
          </thead>
          <tbody>
            <tr>
              <th>Perimeter (mm)</th>
              <td>
                <div class='stat-cell'>
                  <div v-if="statIsMissing('perimeter')" class='stat-bar-wrapper stat-bar-missing'>
                    <div class='stat-bar-axis'></div>
                    <div class='stat-bar stat-bar-missing-fill'></div>
                    <div class='stat-bar-label'>{{ statMissingText('perimeter') }}</div>
                  </div>
                  <div v-else class='stat-bar-wrapper'>
                    <div class='stat-bar-axis'></div>
                    <div class='stat-bar' :style="statBarStyle(statPercent('perimeter'), 'perimeter')"></div>
                    <div class='stat-bar-label'>{{ statLabel('perimeter') }}</div>
                    <div v-if="statAxisLabel('perimeter', 'min')" class='stat-bar-tick stat-bar-tick-left'>{{ statAxisLabel('perimeter', 'min') }}</div>
                    <div v-if="statAxisLabel('perimeter', 'max')" class='stat-bar-tick stat-bar-tick-right'>{{ statAxisLabel('perimeter', 'max') }}</div>
                  </div>
                </div>
              </td>
            </tr>
            <tr>
              <th>Filtration Factor</th>
              <td>
                <div class='stat-cell'>
                  <div v-if="statIsMissing('filtration')" class='stat-bar-wrapper stat-bar-missing'>
                    <div class='stat-bar-axis'></div>
                    <div class='stat-bar stat-bar-missing-fill'></div>
                    <div class='stat-bar-label'>{{ statMissingText('filtration') }}</div>
                  </div>
                  <div v-else class='stat-bar-wrapper' :style="statBarWrapperStyle('filtration')">
                    <div class='stat-bar-axis'></div>
                    <div class='stat-bar' :style="statBarStyle(statPercent('filtration'), 'filtration')"></div>
                    <div
                      v-if="statNeedsMarker('filtration')"
                      class='stat-bar-marker'
                      :style='statMarkerStyle(statPercent("filtration"), "filtration")'
                    ></div>
                    <div
                      v-if="statNeedsMarker('filtration')"
                      class='stat-bar-cover'
                      :style='statCoverStyle(statPercent("filtration"), "filtration")'
                    ></div>
                    <div class='stat-bar-label'>{{ statLabel('filtration') }}</div>
                    <div v-if="statAxisLabel('filtration', 'min')" class='stat-bar-tick stat-bar-tick-left'>{{ statAxisLabel('filtration', 'min') }}</div>
                    <div v-if="statAxisLabel('filtration', 'max')" class='stat-bar-tick stat-bar-tick-right'>{{ statAxisLabel('filtration', 'max') }}</div>
                  </div>
                </div>
              </td>
            </tr>
            <tr>
              <th>Breathability</th>
              <td>
                <div class='stat-cell'>
                  <div v-if="statIsMissing('breathability')" class='stat-bar-wrapper stat-bar-missing'>
                    <div class='stat-bar-axis'></div>
                    <div class='stat-bar stat-bar-missing-fill'></div>
                    <div class='stat-bar-label'>{{ statMissingText('breathability') }}</div>
                  </div>
                  <div v-else class='stat-bar-wrapper' :style="statBarWrapperStyle('breathability')">
                    <div class='stat-bar-axis'></div>
                    <div class='stat-bar' :style="statBarStyle(statPercent('breathability'), 'breathability')"></div>
                    <div
                      v-if="statNeedsMarker('breathability')"
                      class='stat-bar-marker'
                      :style='statMarkerStyle(statPercent("breathability"), "breathability")'
                    ></div>
                    <div
                      v-if="statNeedsMarker('breathability')"
                      class='stat-bar-cover'
                      :style='statCoverStyle(statPercent("breathability"), "breathability")'
                    ></div>
                    <div class='stat-bar-label'>{{ statLabel('breathability') }}</div>
                    <div v-if="statAxisLabel('breathability', 'min')" class='stat-bar-tick stat-bar-tick-left'>{{ statAxisLabel('breathability', 'min') }}</div>
                    <div v-if="statAxisLabel('breathability', 'max')" class='stat-bar-tick stat-bar-tick-right'>{{ statAxisLabel('breathability', 'max') }}</div>
                  </div>
                </div>
              </td>
            </tr>
            <tr>
              <th>Mass (grams)</th>
              <td>
                <div class='stat-cell'>
                  <div v-if="statIsMissing('mass')" class='stat-bar-wrapper stat-bar-missing'>
                    <div class='stat-bar-axis'></div>
                    <div class='stat-bar stat-bar-missing-fill'></div>
                    <div class='stat-bar-label'>{{ statMissingText('mass') }}</div>
                  </div>
                  <div v-else class='stat-bar-wrapper'>
                    <div class='stat-bar-axis'></div>
                    <div class='stat-bar' :style="statBarStyle(statPercent('mass'), 'mass')"></div>
                    <div class='stat-bar-label'>{{ statLabel('mass') }}</div>
                    <div v-if="statAxisLabel('mass', 'min')" class='stat-bar-tick stat-bar-tick-left'>{{ statAxisLabel('mass', 'min') }}</div>
                    <div v-if="statAxisLabel('mass', 'max')" class='stat-bar-tick stat-bar-tick-right'>{{ statAxisLabel('mass', 'max') }}</div>
                  </div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <br>

      <div class="buttons justify-content-center">
        <Button shadow='true' class='button' text="Edit" @click='switchToEditMode' v-if='showMode && canUpdate'/>
        <Button shadow='true' class='button' text="Delete" @click='deleteMask' v-if='deletable && !showMode && canUpdate'/>
        <Button shadow='true' class='button' text="Cancel" @click='handleCancel' v-if='newOrEditMode && canUpdate'/>
        <Button shadow='true' class='button' text="Save & Continue" @click='saveAndContinue' v-if='newOrEditMode && canUpdate'/>
        <Button shadow='true' class='button' text="Add Fit Testing Data" v-if='showMode' @click='tryAddingFitTest'/>
      </div>

      <br>
      <br>
      <br>

    </div>

    <div :class="['grid', 'bar-charts', 'main-section', { 'with-sidebar': newOrEditMode }]" v-show='showMode &&  displayTab == "Fit Testing"'>
      <div class='card'>
        <h3 class='title'>Counts</h3>
        <HorizontalStackedBar
            :values="basicAggregatesWithFitTestPassCount"
        />
      </div>
      <div class='card'>
        <h3 class='title'>Race &amp; Ethnicity Counts</h3>
        <HorizontalStackedBar
            :values="raceEthnicityAggregates"
        />
      </div>
      <div class='card'>
        <h3 class='title'>Gender Counts</h3>
        <HorizontalStackedBar
            :values="genderSexAggregates"
        />
      </div>
      <div class='card'>
        <h3 class='title'>Age Counts</h3>
        <HorizontalStackedBar
            :values="ageAggregates"
        />
      </div>
    </div>
    <br>
    <br>

  </div>
  <Popup v-if="showHelp && tabToShow == 'Basic Info'" @onclose="this.showHelp = false">
  <h3>Basic Info</h3>
  <table>
    <tr>
      <th>Unique Internal Model code</th>
      <td>This is the name of the mask. For example: Zimi 9541 w/ Headstraps, w/ exhalation valve.</td>
    </tr>
    <tr>
      <th>Colors</th>
      <td>You can select the color(s) of this mask. This can help people find masks that match their outfit. If none of the options match, please email <a mailto="info@breathesafe.xyz">info@breathesafe.xyz</a> and I can add a color for you.</td>
    </tr>
    <tr>
      <th>Strap type</th>
      <td>
        <strong>Earloop</strong> and <strong>Headstrap</strong> options are assumed to be not adjustable. If the mask comes with adjustable ones, you can pick <strong>Adjustable Earloop</strong> and <strong>Adjustable Headstrap</strong> accordingly.
      </td>
    </tr>
  </table>
  </Popup>

  <Popup v-if="showHelp && tabToShow == 'Image & Purchasing'" @onclose="this.showHelp = false">
  <h3>Image & Purchasing</h3>

  <table>
    <tr>
      <th>Image URL</th>
      <td>This link will be used to display the image for the mask.</td>
    </tr>
    <tr>
      <th>Purchasing URLs</th>
      <td>e.g. https://zimiair.com</td>
    </tr>
  </table>
  </Popup>

  <Popup v-if="showHelp && tabToShow == 'Dimensions'" @onclose="this.showHelp = false">
  <h3>Dimensions</h3>

  <h4>Perimeter (mm)</h4>
  <p>This is measuring the distance around the section of the mask that seals to the face. <strong>This is used by the mask recommender algorithm in predicting fit for individuals.</strong> Here is an example for bifolds: </p>

  <div class='align-items-center'>
    <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask_measurements/bifold-highlighted-perimeter.png" alt="bifold mask with the perimeter shown">
  </div>
  <p>So the distance in red times 2 is what I consider the perimeter of the mask. For other types of masks (e.g. boat/trifold, cup, etc.), the same idea can be applied -- take a tape measure, start at some point (e.g. by the crease of the nosewire) and wrap around the edges of the mask that is supposed to seal to the face, until you reach the beginning point.</p>

  <h4>Mass (grams)</h4>
  <p>Useful for people who are looking into elastomeric masks, as they can be heavier than the typical Filtering Facepiece Respirators (FFRs).</p>
  </Popup>
</template>

<script>
import axios from 'axios';
import Button from './button.vue'
import Circle from './circle.vue'
import { assignBoundsToColorScheme, binValue, colorPaletteFall, genColorSchemeBounds, riskColorInterpolationScheme, perimeterColorScheme } from './colors';
import CircularButton from './circular_button.vue'
import ClosableMessage from './closable_message.vue'
import ColoredCell from './colored_cell.vue'
import HorizontalStackedBar from './horizontal_stacked_bar.vue'
import TabSet from './tab_set.vue'
import MaskProgressBar from './mask_progress_bar.vue'
import { deepSnakeToCamel, shortHandHref, round } from './misc.js'
import RecommendPopup from './recommend_popup.vue'
import Popup from './pop_up.vue'
import SurveyQuestion from './survey_question.vue'
import { signIn } from './session.js'
import { getFacialMeasurements } from './facial_measurements.js'
import { mapActions, mapWritableState, mapState } from 'pinia';
import { useProfileStore } from './stores/profile_store';
import { useMainStore } from './stores/main_store';
import { useManagedUserStore } from './stores/managed_users_store';
import ScatterPlot from './scatter_plot.vue'
import { useFacialMeasurementStore } from './stores/facial_measurement_store'

export default {
  name: 'Mask',
  components: {
    Button,
    Circle,
    CircularButton,
    ClosableMessage,
    ColoredCell,
    HorizontalStackedBar,
    MaskProgressBar,
    Popup,
    RecommendPopup,
    ScatterPlot,
    SurveyQuestion,
    TabSet
  },
  data() {
    return {
      showHelp: false,
      noseProtrusionMm: null,
      faceWidthMm: null,
      showPopup: false,
      fitTestsWithFacialMeasurements: [],
      basicAggregates: {},
      basicOptions: [
        'fit_test_count',
        'unique_fit_testers_count',
        'fit_test_pass_count'
      ],
      raceEthnicityAggregates: {},
      raceEthnicityOptions: [
        'american_indian_or_alaskan_native_count',
        'asian_pacific_islander_count',
        'black_african_american_count',
        'hispanic_count',
        'white_caucasian_count',
        'multiple_ethnicity_other_count',
        'prefer_not_to_disclose_race_ethnicity_count'
      ],
      ageAggregates: {},
      ageOptions: [
        'age_between_2_and_4',
        'age_between_4_and_6',
        'age_between_6_and_8',
        'age_between_8_and_10',
        'age_between_10_and_12',
        'age_between_12_and_14',
        'age_between_14_and_18',
        'age_adult',
        'prefer_not_to_disclose_age_count'
      ],
      genderSexAggregates: {},
      genderSexOptions: [
        'cisgender_male_count',
        'cisgender_female_count',
        'mtf_transgender_count',
        'ftm_transgender_count',
        'intersex_count',
        'other_gender_sex_count',
        'prefer_not_to_disclose_gender_sex_count'

      ],
      hasExhalationValve: false,
      exceptionObjectBlank: {
        color: {
          r: '200',
          g: '200',
          b: '200',
        },
        value: '',
        text: '?'
      },
      exceptionObject: {
        color: {
          r: '200',
          g: '200',
          b: '200',
        },
        value: undefined,
        text: '?'
      },
      exceptionDollarObject: {
        color: {
          r: '200',
          g: '200',
          b: '200',
        },
        value: 0,
        text: '?'
      },
      mode: 'New',
      notes: '',
      authorId: 0,
      massGrams: null,
      widthMm: null,
      heightMm: null,
      depthMm: null,
      perimeterMm: null,
      tabToShow: "Basic Info",
      displayTab: "Misc. Info",
      tabToShowOptions: [
        {
          text: "Misc. Info",
        },
        {
          text: "Fit Testing",
        },
      ],
      tabEditOptions: [
        {
          text: "Basic Info",
        },
        {
          text: "Image & Purchasing",
        },
        {
          text: "Dimensions",
        },
        {
          text: "Filtration & Breathability",
        },
      ],
      initialCostUsDollars: 0,
      hasGasket: false,
      id: null,
      uniqueInternalModelCode: '',
      modifications: {},
      color: '',
      colors: [],
      filterType: 'N95',
      filtrationEfficiencies: [],
      breathability: [],
      filterChangeCostUsDollars: 0,
      dataContext: {},
      strapType: 'Headstrap',
      style: '',
      imageUrls: [''],
      authorIds: [],
      whereToBuyUrls: [],
      errorMessages: [],
      fitTestPoints: [
        { x: 155, y: 100, color: '#4CAF50', borderStyle: 'none' },
        { x: 160, y: 150, color: '#2196F3', borderStyle: 'none' },
        { x: 145, y: 80, color: '#FFC107', borderStyle: 'none' },
        { x: 170, y: 200, color: '#9C27B0', borderStyle: 'none' },
        { x: 150, y: 120, color: '#F44336', borderStyle: 'none' }
      ],
    }
  },
  props: {
    colorOptions: {
      default: [
        'White',
        'Black',
        'Blue',
        'Grey',
        'Graphics',
        'Orange',
        'Green',
        'Purple',
        'Pink',
        'Multicolored',
      ],

    }
  },
  computed: {
    ...mapState(
        useMainStore,
        [
          'currentUser',
        ]
    ),
    ...mapState(
        useProfileStore,
        [
          'profileId',
        ]
    ),
    ...mapState(
        useManagedUserStore,
        [
          'managedUsers'
        ]
    ),
    ...mapWritableState(
        useMainStore,
        [
          'messages'
        ]
    ),
    ...mapState(
        useFacialMeasurementStore,
        [
          'bitragionSubnasaleArcMm',
          'faceWidthMm',
          'noseProtrusionMm',
          'facialHairBeardLengthMm'
        ]
    ),
    facialMeasurements() {
      return getFacialMeasurements.bind(this)()
    },
    fitTestPassCount() {
      let count = 0;
      for(let fitTest of this.fitTestsWithFacialMeasurements) {
        if (fitTest['qlftPass']) {
          count += 1
        }
      }
      return count
    },

    basicAggregatesWithFitTestPassCount() {
      let copy = JSON.parse(JSON.stringify(this.basicAggregates))
      copy['fit_test_pass_count'] = this.fitTestPassCount
      return copy
    },
    scatterData1() {
      return this.prepareScatterData('bitragionSubnasaleArc', 'faceWidth')
    },
    scatterData2() {
      return this.prepareScatterData('bitragionSubnasaleArc', 'noseProtrusion')
    },
    scatterData3() {
      return this.prepareScatterData('noseProtrusion', 'faceWidth')
    },
    scatterPlots() {
      return [
        {
          'xLabel': "Bitragion subnasale arc (mm)",
          'title': "Bitragion subnasale arc (mm) vs. Face width (mm)",
          'yLabel': "Face width (mm)",
          'points': this.scatterData1,
          'crossHairPoint': this.crossHairPoint1
        },
        {
          'xLabel': "Bitragion subnasale arc (mm)",
          'title': "Bitragion subnasale arc (mm) vs. Nose protrusion (mm)",
          'yLabel': "Nose protrusion (mm)",
          'points': this.scatterData2,
          'crossHairPoint': this.crossHairPoint2
        },
        {
          'xLabel': "Nose protrusion (mm)",
          'yLabel': 'Face width (mm)',
          'title': "Nose protrusion (mm) vs. Face width (mm)",
          'points': this.scatterData3,
          'crossHairPoint': this.crossHairPoint3
        },
      ]
    },
    crossHairPoint1() {
      const bitragionSubnasaleArc = parseFloat(this.getFacialMeasurement('bitragionSubnasaleArcMm'))
      const faceWidth = parseFloat(this.getFacialMeasurement('faceWidthMm'))

      if (isNaN(bitragionSubnasaleArc) || isNaN(faceWidth)) return null
      return { x: bitragionSubnasaleArc, y: faceWidth }
    },
    crossHairPoint2() {
      const bitragionSubnasaleArc = parseFloat(this.getFacialMeasurement('bitragionSubnasaleArcMm'))
      const noseProtrusion = parseFloat(this.getFacialMeasurement('noseProtrusionMm'))
      if (isNaN(bitragionSubnasaleArc) || isNaN(noseProtrusion)) return null
      return { x: bitragionSubnasaleArc, y: noseProtrusion }
    },
    crossHairPoint3() {
      const noseProtrusion = parseFloat(this.getFacialMeasurement('noseProtrusionMm'))
      const faceWidth = parseFloat(this.getFacialMeasurement('faceWidthMm'))
      if (isNaN(noseProtrusion) || isNaN(faceWidth)) return null
      return { x: noseProtrusion, y: faceWidth }
    },
    columnCount() {
      return 3
    },
    canUpdate() {
      return !!this.currentUser && (this.newMode || (this.authorId == this.currentUser.id) || this.currentUser.admin)
    },
    perimColorScheme() {
      return perimeterColorScheme();
    },

    costColorScheme() {
      const minimum = 0.5
      const maximum = 90 // flo mask
      const numObjects = 6

      return genColorSchemeBounds(minimum, maximum, numObjects)
    },

    widthColorScheme() {
      const minimum = 67
      const maximum = 184
      const numObjects = 6

      return genColorSchemeBounds(minimum, maximum, numObjects)
    },
    depthColorScheme() {
      const minimum = 8
      const maximum = 50
      const numObjects = 6

      return genColorSchemeBounds(minimum, maximum, numObjects)
    },
    heightColorScheme() {
      const minimum = 55
      const maximum = 145
      const numObjects = 6

      return genColorSchemeBounds(minimum, maximum, numObjects)
    },
    massColorScheme() {
      const minimum = 10
      const maximum = 200
      const numObjects = 6

      return genColorSchemeBounds(minimum, maximum, numObjects)
    },
    breathabilityInterpolationScheme() {
      const minimum = 46
      const maximum = 468
      const numObjects = 6

      return genColorSchemeBounds(minimum, maximum, numObjects)
    },
    massGramsScaled() {
      // scale to between 0 and 1
      return this.massGrams / 209
    },
    colorInterpolationScheme() {
      return riskColorInterpolationScheme
    },
    dollarCost() {
      if (this.initialCostUsDollars != 0) {
        return this.initialCostUsDollars / 1000
      }
    },
    riskColorScheme() {
      return riskColorInterpolationScheme
    },
    filtrationEfficienciesRuby() {
      let collection = []
      for(let f of this.filtrationEfficiencies) {
        collection.push({
          'filtration_efficiency_notes': f.filtrationEfficiencyNotes,
          'filtration_efficiency_source': f.filtrationEfficiencySource,
          'filtration_efficiency_percent': f.filtrationEfficiencyPercent
        })

      }

      return collection
    },
    breathabilityRuby() {
      let collection = []
      for(let f of this.breathability) {
        collection.push({
          'breathability_pascals_notes': f.breathabilityPascalsNotes,
          'breathability_pascals_source': f.breathabilityPascalsSource,
          'breathability_pascals': parseFloat(f.breathabilityPascals)
        })

      }

      return collection
    },
    currentUserIsAuthor() {
      return this.authorId == this.currentUser.id
    },
    deletable() {
      return !!this.id && this.userCanEdit
    },
    whereToBuyUrlsColspan() {
      if (this.userCanEdit) {
        return 2
      }
     return 3
    },
    sealColspan() {
      if (this.editMode) {
        return 2
      }
     return 1
    },
    imagePrevColspan() {
      if (this.editMode) {
        return 1
      }
     return 2
    },
    userCanEdit() {
      if (!this.currentUser) {
        return false
      }

      return this.currentUserIsAuthor && this.basicAggregates.fit_test_count == 0
    },
    newMode() {
      return this.$route.name == 'NewMask'
    },
    editMode() {
      return this.$route.name == 'EditMask'
    },
    newOrEditMode() {
      return this.newMode || this.editMode
    },
    showMode() {
      return this.$route.name == 'ShowMask'
    },
    tagline() {
      let displayable = ""

      if (this.showMode) {
        displayable = this.uniqueInternalModelCode
      } else if (this.newMode) {
        displayable = this.mode
      } else {
        displayable = `${this.mode}: ${this.uniqueInternalModelCode}`
      }
      return displayable
    },
    toSave() {
      return {
        colors: this.colors,
        notes: this.notes,
        mass_grams: this.massGrams,
        width_mm: this.widthMm,
        perimeter_mm: this.perimeterMm,
        height_mm: this.heightMm,
        depth_mm: this.depthMm,
        unique_internal_model_code: this.uniqueInternalModelCode,
        modifications: this.modifications,
        filter_type: this.filterType,
        filtration_efficiencies: this.filtrationEfficienciesRuby,
        has_exhalation_valve: this.hasExhalationValve,
        breathability: this.breathabilityRuby,
        filter_change_cost_us_dollars: this.filterChangeCostUsDollars,
        style: this.style,
        image_urls: this.imageUrls,
        where_to_buy_urls: this.whereToBuyUrls,
        author_id: this.currentUser.id,
        initial_cost_us_dollars: this.initialCostUsDollars,
        strap_type: this.strapType
      }
    }
  },
  async created() {
    this.getCurrentUser();

    let toQuery = this.$route.query
    let toName = this.$route.name

    await this.load(toQuery, {}, toName, {})

    this.$watch(
      () => this.$route.fullPath,
      () => {
        this.load(this.$route.query, {}, "", {})
      }
    )

  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser', 'addMessages']),
    ...mapActions(useManagedUserStore, ['loadManagedUsers']),
    ...mapActions(useFacialMeasurementStore, ['getFacialMeasurement', 'updateFacialMeasurements']),
    triggerRouterForFacialMeasurementUpdate(event, key) {
      let newQuery = {}

      newQuery[key] = event.target.value

      let combinedQuery = Object.assign(
        JSON.parse(
          JSON.stringify(this.$route.query)
        ),
        newQuery
      )
      this.$router.push({
        name: 'ShowMask',
        query: combinedQuery
      })
    },
    switchToEditMode() {
      this.$router.push(
        {
          "name": "EditMask",
          'query': {
            "displayTab": this.displayTab
          }
        }
      )
    },
    prepareScatterData(xKey, yKey) {
      return this.fitTestsWithFacialMeasurements.map(point => ({
        x: point[xKey],
        y: point[yKey],
        color: point.qlftPass ? 'rgba(0, 255, 0, 0.7)' : 'rgba(255, 0, 0, 0.7)'
      })).filter(point => point.x != null && point.y != null)
    },

    async load(toQuery, fromQuery) {
      let toName = this.$route.name
      let isMaskPage = (["NewMask", "ShowMask", "EditMask"].includes(toName))
      if (!isMaskPage) {
        return
      }

      await this.getCurrentUser();

      this.updateFacialMeasurements(toQuery)

      if (toQuery == {}) {
        toQuery = this.$route.query
      }

      if (toName == 'NewMask' && this.currentUser) {
        this.mode = 'New'
        this.displayTab = 'Misc. Info'
      } else if (toName == 'NewMask' && !this.currentUser) {
        // visit the URL
        this.$router.push({
          name: 'SignIn',
          query: {
            'attempt-name': 'NewMask'
          }
        })
      } else if (toName == 'ShowMask') {
        this.mode = 'Show'
      } else if (toName == 'EditMask')
        this.mode = 'Edit'

      if (['Edit', 'Show'].includes(this.mode)) {
        this.loadMask()
      }

      if (['Show'].includes(this.mode)) {
        this.loadFitTestsFacialMeasurements()
      }

      if (toQuery['tabToShow'] && isMaskPage) {
        this.tabToShow = toQuery['tabToShow']
      }

      if (toQuery['displayTab'] && isMaskPage) {
        this.displayTab = toQuery['displayTab']
      }
    },
    circleStyling(opt ) {
      if (this.colors.includes(opt)) {
        return "{'border': '2px solid black'}"
      } else {
        return "{'border': '0px solid black'}"
      }
    },
    filterFor(namespace, opt) {
      if (this.colors.includes(opt)) {
        this.colors = this.colors.filter(item => item !== opt)
      } else {
        this.colors.push(opt)
      }
    },
    shortHand(href) {
      return shortHandHref(href)
    },
    filtrationEfficiencyValue(percent) {
      if (percent) {
        return 1 - percent / 100
      }

      return undefined
    },
    dollarText(num) {
      if (num) {
        return `$${num}`
      }

      return '?'
    },
    distanceText(num, unitAbbrev) {
      if (!!unitAbbrev) {
        unitAbbrev = 'mm'
      }
      if (num) {
        return `${round(num, 0)} ${unitAbbrev}`
      }

      return '?'
    },
    massText(num) {
      if (num) {
        return `${num} g`
      }

      return '?'
    },
    breathabilityText(num) {
      if (num) {
        return `${num} pa`
      }

      return "?"
    },
    percentText(num) {
      if (num) {
        return `${num}%`
      }

      return "?"
    },
    formatCurrency(value) {
      if (value === null || value === undefined || isNaN(value)) {
        return 'Missing'
      }

      return `$${Number(value).toFixed(2)}`
    },
    formatValue(value, suffix = '') {
      if (value === null || value === undefined || isNaN(value)) {
        return 'Missing'
      }

      return `${Math.round(value)}${suffix}`
    },
    statPercent(type) {
      if (type === 'filtration') {
        if (this.statIsMissing(type)) {
          return null
        }
        const logValue = Math.log10(this.avgSealedFitFactor)
        return this.clampPercent(logValue / 4)
      }

      if (type === 'breathability') {
        const min = this.dataContext.breathability_min
        const max = this.dataContext.breathability_max
        if (this.statIsMissing(type) || min === null || max === null || min === undefined || max === undefined) {
          return null
        }
        const scaled = this.minMaxScale(this.avgBreathabilityPa, min, max, { zeroRangeValue: 0 })
        return this.clampPercent(1 - scaled)
      }

      if (type === 'perimeter') {
        const min = this.dataContext.perimeter_min
        const max = this.dataContext.perimeter_max
        if (this.statIsMissing(type) || min === null || max === null || min === undefined || max === undefined) {
          return null
        }
        const scaled = this.minMaxScale(this.perimeterMm, min, max, { zeroRangeValue: 1 })
        return this.clampPercent(scaled)
      }

      if (type === 'cost') {
        const min = this.dataContext.initial_cost_min
        const max = this.dataContext.initial_cost_max
        if (this.statIsMissing(type) || min === null || max === null || min === undefined || max === undefined) {
          return null
        }
        const scaled = this.minMaxScale(this.initialCostUsDollars, min, max, { zeroRangeValue: 0 })
        return this.clampPercent(scaled)
      }

      if (type === 'mass') {
        const min = this.dataContext.mass_min
        const max = this.dataContext.mass_max
        if (this.statIsMissing(type) || min === null || max === null || min === undefined || max === undefined) {
          return null
        }
        const scaled = this.minMaxScale(this.massGrams, min, max, { zeroRangeValue: 0 })
        return this.clampPercent(scaled)
      }

      return null
    },
    statLabel(type) {
      if (type === 'filtration') {
        return this.formatValue(this.avgSealedFitFactor)
      }
      if (type === 'breathability') {
        return this.formatValue(this.avgBreathabilityPa, ' pa')
      }
      if (type === 'perimeter') {
        return this.formatValue(this.perimeterMm)
      }
      if (type === 'cost') {
        return this.formatCurrency(this.initialCostUsDollars)
      }
      if (type === 'mass') {
        return this.formatValue(this.massGrams, ' g')
      }
      return 'Missing'
    },
    statBarStyle(percent, type) {
      const clamped = this.clampPercent(percent)
      const width = clamped === null ? '0%' : `${Math.round(clamped * 100)}%`

      if (type === 'filtration' || type === 'breathability') {
        return {
          width: '100%',
          backgroundColor: 'transparent'
        }
      }

      if (type === 'perimeter') {
        return {
          width: width,
          backgroundColor: '#a3a8ad'
        }
      }

      return {
        width: width,
        backgroundColor: this.statRowColors()[type]
      }
    },
    statBarWrapperStyle(type) {
      if (type === 'filtration') {
        return { background: this.filtrationGradient() }
      }
      if (type === 'breathability') {
        const gradient = this.breathabilityGradient()
        if (!gradient) {
          return {}
        }
        return { background: gradient }
      }
      return {}
    },
    statNeedsMarker(type) {
      return ['filtration', 'breathability'].includes(type)
    },
    statMarkerStyle(percent) {
      const clamped = this.clampPercent(percent)
      if (clamped === null) {
        return {}
      }
      const position = Math.round(clamped * 10000) / 100
      return {
        left: `calc(${position}% - 1px)`
      }
    },
    statCoverStyle(percent) {
      const clamped = this.clampPercent(percent)
      if (clamped === null) {
        return {}
      }
      const position = Math.round(clamped * 10000) / 100
      return {
        left: `calc(${position}% + 1px)`,
        backgroundColor: '#f1f1f1'
      }
    },
    filtrationGradient() {
      const red = '#c0392b'
      const yellow = '#f1c40f'
      const green = '#27ae60'
      return `linear-gradient(90deg, ${red} 0%, ${yellow} 33.333%, ${green} 100%)`
    },
    breathabilityGradient() {
      const min = this.dataContext.breathability_min
      const max = this.dataContext.breathability_max
      if (min === null || max === null || min === undefined || max === undefined) {
        return null
      }

      const orderedMin = Math.min(min, max)
      const orderedMax = Math.max(min, max)
      if (orderedMax <= orderedMin) {
        return null
      }

      const p33 = orderedMin + (orderedMax - orderedMin) * 0.3333333333333333
      const red = '#c0392b'
      const yellow = '#f1c40f'
      const green = '#27ae60'
      const scalePosition = (value) => ((value - orderedMin) / (orderedMax - orderedMin)) * 100
      const axisStop33 = scalePosition(p33)
      return `linear-gradient(90deg, ${red} 0%, ${yellow} ${axisStop33}%, ${green} 100%)`
    },
    statRowColors() {
      return {
        filtration: '#c0392b',
        breathability: '#e67e22',
        perimeter: '#16a085',
        cost: 'rgb(188, 163, 255)',
        mass: 'rgb(169, 249, 255)'
      }
    },
    statAxisLabel(type, position) {
      if (type === 'filtration') {
        return position === 'min' ? '10^0' : '10^4'
      }
      if (type === 'breathability') {
        const min = this.dataContext.breathability_min
        const max = this.dataContext.breathability_max
        if (min === null || max === null || min === undefined || max === undefined) {
          return null
        }
        const orderedMin = Math.min(min, max)
        const orderedMax = Math.max(min, max)
        const labelValue = position === 'min' ? orderedMax : orderedMin
        if (labelValue <= 0) {
          return 'Missing'
        }
        return this.formatValue(labelValue, ' pa')
      }
      if (type === 'perimeter') {
        const min = this.dataContext.perimeter_min
        const max = this.dataContext.perimeter_max
        if (min === null || max === null || min === undefined || max === undefined) {
          return null
        }
        return position === 'min' ? this.formatValue(min) : this.formatValue(max)
      }
      if (type === 'cost') {
        const min = this.dataContext.initial_cost_min
        const max = this.dataContext.initial_cost_max
        if (min === null || max === null || min === undefined || max === undefined) {
          return null
        }
        return position === 'min' ? this.formatCurrency(min) : this.formatCurrency(max)
      }
      if (type === 'mass') {
        const min = this.dataContext.mass_min
        const max = this.dataContext.mass_max
        if (min === null || max === null || min === undefined || max === undefined) {
          return null
        }
        return position === 'min' ? this.formatValue(min, ' g') : this.formatValue(max, ' g')
      }
      return null
    },
    statIsMissing(type) {
      if (type === 'filtration') {
        return this.avgSealedFitFactor === null || this.avgSealedFitFactor === undefined || isNaN(this.avgSealedFitFactor) || this.avgSealedFitFactor <= 0
      }
      if (type === 'breathability') {
        return this.avgBreathabilityPa === null || this.avgBreathabilityPa === undefined || isNaN(this.avgBreathabilityPa) || this.avgBreathabilityPa <= 0
      }
      if (type === 'perimeter') {
        return this.perimeterMm === null || this.perimeterMm === undefined || isNaN(this.perimeterMm) || this.perimeterMm <= 0
      }
      if (type === 'cost') {
        return this.initialCostUsDollars === null || this.initialCostUsDollars === undefined || isNaN(this.initialCostUsDollars) || this.initialCostUsDollars <= 0
      }
      if (type === 'mass') {
        return this.massGrams === null || this.massGrams === undefined || isNaN(this.massGrams) || this.massGrams <= 0
      }
      return true
    },
    statMissingText() {
      return 'Missing'
    },
    clampPercent(value) {
      if (value === null || value === undefined || isNaN(value)) {
        return null
      }
      return Math.max(0, Math.min(1, value))
    },
    minMaxScale(value, min, max, { zeroRangeValue }) {
      const range = max - min
      if (range <= 0) {
        return zeroRangeValue
      }
      return (value - min) / range
    },
    maskImageAlt(index) {
      return `Image #${index} for ${this.uniqueInternalModelCode}`
    },
    addFiltEffAndBreathability() {
      this.addFiltrationEfficiency()
      this.addBreathability()
    },
    addFiltrationEfficiency() {
      this.filtrationEfficiencies.push({
        'filtrationEfficiencyPercent': 1,
        'filtrationEfficiencySource': ''
      })

    },
    addBreathability() {
      this.breathability.push({
        'breathabilityPascals': 0,
        'breathabilitySource': ''
      })

    },
    addImageUrl() {
      if (!this.userCanEdit) {
        return
      }
      this.imageUrls.push('')
    },
    addPurchasingUrl() {
      this.whereToBuyUrls.push('')
    },
    deleteImageUrl(index) {
      this.imageUrls.splice(index, 1);
    },
    deletePurchasingUrl(index) {
      this.whereToBuyUrls.splice(index, 1);
    },
    handleCancel() {
      if (this.newMode) {
        this.$router.push(
          {
            name: "Masks"
          }
        )
      } else {
        this.tabToShow = 'Basic Info'
        this.displayTab = 'Misc. Info'
        this.$router.push(
          {
            name: "ShowMask",
            params: { id: this.$route.params.id },
            query: { displayTab: 'Misc. Info', tabToShow: 'Basic Info' }
          }
        )
      }
    },
    newMask() {
      this.$router.push(
        {
          name: "NewMask"
        }
      )

      this.masks.push(
        {
          unique_internal_model_code: '',
          modifications: {},
          type: '',
          image_urls: [''],
          author_id: null,
          where_to_buy_urls: [],
        }
      )
    },
    async tryAddingFitTest() {
      await this.getCurrentUser()

      if (this.currentUser) {
        await this.loadManagedUsers()
        if (this.managedUsers.length == 0) {
          this.messages.push({
            str: "Your account does not have any respirator users yet. Please visit the Respirator Users page by clicking on this message, and add at least one.", to: {
              "name": 'RespiratorUsers'
            }
          })

        }
        else {
          this.$router.push({
            'name': 'NewFitTest',
            'query': {
              maskId: this.id,
              maskCode: this.uniqueInternalModelCode,
            }
          })
        }
      } else {
        this.$router.push({
          'name': 'SignIn',
          'query': {
            'attempt-name': 'ShowMask',
            'params-id': this.id
          }
        })
      }
    },
    runValidations() {
      if (this.imageUrls.length <= 0) {
        this.messages.push({
          str: "Please provide an image URL so one image can be displayed."
        })
      }

      if (!this.uniqueInternalModelCode) {
        this.messages.push({
          str: "Please provide a Unique Internal Model Code"
        })
      }
    },
    async loadFitTestsFacialMeasurements() {
      await axios.get(
        `/facial_measurements_fit_tests/${this.$route.params.id}.json`
      )
        .then(response => {
          let data = response.data
          // whatever you want
          this.fitTestsWithFacialMeasurements = deepSnakeToCamel(data.fit_tests_with_facial_measurements)

        })
        .catch(error => {
          if (error.message) {
            this.addMessages([error.message])
          } else {
            this.addMessages(error.response.data.messages)
          }
        })
    },
    async loadMask() {
      await axios.get(
        `/masks/${this.$route.params.id}.json`
      )
        .then(response => {
          let data = response.data
          // whatever you want
          let mask = deepSnakeToCamel(data.mask)

          for(let k in mask) {
            this[k] = mask[k]
          }

          this.basicAggregates = {}

          for(let k of this.basicOptions) {
            this.basicAggregates[k] = data.mask[k]
          }

          this.raceEthnicityAggregates = {}

          for(let k of this.raceEthnicityOptions) {
            this.raceEthnicityAggregates[k] = data.mask[k]
          }

          this.genderSexAggregates = {}

          for(let k of this.genderSexOptions) {
            this.genderSexAggregates[k] = data.mask[k]
          }

          this.ageAggregates = {}

          for(let k of this.ageOptions) {
            this.ageAggregates[k] = data.mask[k]
          }

          this.dataContext = data.context || {}


        })
        .catch(error => {
          if (error.message) {
            this.addMessages([error.message])
          } else {
            this.addMessages(error.response.data.messages)
          }
        })
    },
    async deleteMask() {
      let answer = window.confirm("Are you sure you want to delete data?");

      if (answer && this.$route.params.id) {
        await axios.delete(
          `/masks/${this.$route.params.id}.json`
        )
          .then(response => {
            let data = response.data

            this.$router.push({
              name: 'Masks',
            })
          })
          .catch(error => {
            if (error.message) {
              this.addMessages([error.message])
            }
              this.addMessages(error.response.data.messages)
          })
      }
    },
    async persistMask() {
      this.runValidations()

      if (this.messages.length > 0) {
        return null
      }

      let maskId = this.$route.params.id;

      if (maskId) {

        await axios.put(
          `/masks/${this.$route.params.id}.json`, {
            mask: this.toSave
          }
        )
          .then(response => {
            let data = response.data
            // whatever you want
            return data
          })
          .catch(error => {
            for(let errorMessage of error.response.data.messages) {
              this.messages.push({
                str: errorMessage
              })
            }
          })
        if (this.messages.length > 0) {
          return null
        }
        return maskId
      } else {

        // create
        await axios.post(
          `/masks.json`, {
            mask: this.toSave
          }
        )
          .then(response => {
            let data = response.data
            // whatever you want
            this.id = data.mask.id
            this.authorId = data.mask.author_id
            return data
          })
          .catch(error => {
            if (error.message) {
              this.addMessages([error.message])
            } else {
              this.addMessages(error.response.data.messages)
            }
          })
        if (this.messages.length > 0) {
          return null
        }
        return this.id
      }
    },
    nextEditStep() {
      const steps = [
        'Basic Info',
        'Image & Purchasing',
        'Dimensions',
        'Filtration & Breathability'
      ]
      const currentIndex = steps.indexOf(this.tabToShow)
      if (currentIndex === -1) {
        return steps[0]
      }
      if (currentIndex >= steps.length - 1) {
        return null
      }
      return steps[currentIndex + 1]
    },
    async saveAndContinue() {
      const savedId = await this.persistMask()
      if (!savedId) {
        return
      }

      const nextStep = this.nextEditStep()
      if (window.innerWidth < 700) {
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
      if (nextStep) {
        this.tabToShow = nextStep
        this.displayTab = 'Misc. Info'
        this.$router.push({
          name: 'EditMask',
          params: { id: savedId },
          query: {
            tabToShow: nextStep,
            displayTab: 'Misc. Info'
          }
        })
        return
      }

      if (window.innerWidth < 700) {
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
      this.$router.push({
        name: 'ShowMask',
        params: { id: savedId },
        query: { displayTab: 'Misc. Info' }
      })
      this.mode = 'Show'
    },
    setDisplay(opt, name) {
      if (!name) {
        name = this.$route.name
      }

      this.$router.push({
        name: name,
        query: {
          displayTab: opt.name
        }
      })
    },

    setRouteTo(opt) {
      let routeName = this.$route.name

      let tabToShow = '';
      if ('target' in opt && 'value' in opt.target) {
        tabToShow = opt.target.value
      } else {
        tabToShow = opt.name
      }

      let newQuery = {
        tabToShow: tabToShow
      }

      let combinedQuery = Object.assign(
        JSON.parse(
          JSON.stringify(this.$route.query)
        ),
        newQuery
      )

      this.$router.push({
        name: routeName,
        query: combinedQuery
      })
    },
    navigateToStep(stepKey) {
      let routeName = this.$route.name

      let newQuery = {
        tabToShow: stepKey
      }

      let combinedQuery = Object.assign(
        JSON.parse(
          JSON.stringify(this.$route.query)
        ),
        newQuery
      )

      if (window.innerWidth < 700) {
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }

      this.$router.push({
        name: routeName,
        query: combinedQuery
      })
    },
    handleDisplayTabChange(option) {
      let routeName = this.$route.name

      let newQuery = {
        displayTab: option.name
      }

      let combinedQuery = Object.assign(
        JSON.parse(
          JSON.stringify(this.$route.query)
        ),
        newQuery
      )

      this.$router.push({
        name: routeName,
        query: combinedQuery
      })
    },
    visitMasks() {
      this.$router.push({
        name: 'Masks',
      })
    },
    update(event, property, index) {
      if (index !== null) {
        this[property][index] = event.target.value
      } else {
        this[property] = event.target.value
      }
    },
    deleteArrayOfObj(event, property, index) {
      if (index !== null) {
        this[property].splice(index, 1)
      }
    },
    updateArrayOfObj(event, property, index, nestedProp) {
      if (index !== null) {
        this[property][index][nestedProp] = event.target.value
      }
    }
  }
}
</script>

<style scoped>
  .main {
    display: flex;
    flex-direction: column;
  }
  .main-container {
    top:2em;
  }
  .tab-set-container {
    display: flex;
    justify-content: center;
    width: 100%;
    margin-bottom: 2rem;
  }
  .add-facial-measurements-button {
    margin: 1em auto;
  }

  .has-minimal-width {
    min-width: 25em;
  }

  .text-for-other {
    margin: 0 1.25em;
  }

  .justify-content-center {
    display: flex;
    justify-content: center;
  }

  .justify-items-center {
    display: flex;
    justify-items: center;
  }

  .almost-full-width {
    width: 90%;
  }
  .input-list {
    min-width: 20em;
  }

  .menu {
    justify-content: space-between;
    margin-top: 0;
    margin-bottom: 0;
  }
  .row {
    display: flex;
    flex-direction: row;
  }

  .row .button {
    width: 100%;
    margin: 1em;
    max-width: 10em;
  }

  .risk-score {
    border-radius: 100%;
    width: 5em;
    height: 5em;
  }
  .stat-cell {
    min-width: 9em;
  }
  .stat-bar-wrapper {
    position: relative;
    height: 2.25em;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 0.4em;
    background-color: #f1f1f1;
    overflow: hidden;
  }
  .stat-bar-axis {
    position: absolute;
    left: 0.5em;
    right: 0.5em;
    bottom: 0.35em;
    height: 2px;
    background-color: rgba(0, 0, 0, 0.2);
    z-index: 1;
  }
  .stat-bar {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    border-radius: 0.4em;
    opacity: 0.9;
  }
  .stat-bar-marker {
    position: absolute;
    width: 2px;
    top: 0;
    bottom: 0;
    background-color: #ffffff;
    box-shadow: 0 0 2px rgba(0, 0, 0, 0.6);
    z-index: 2;
  }
  .stat-bar-cover {
    position: absolute;
    top: 0;
    bottom: 0;
    right: 0;
    background-color: #f1f1f1;
    z-index: 1;
  }
  .stat-bar-label {
    position: relative;
    z-index: 3;
    font-weight: bold;
    color: #111;
    text-shadow: 1px 1px 2px #fff;
  }
  .stat-bar-tick {
    position: absolute;
    bottom: 0.15em;
    font-size: 0.7em;
    color: #333;
    opacity: 0.75;
    z-index: 1;
  }
  .stat-bar-tick-left {
    left: 0.4em;
  }
  .stat-bar-tick-right {
    right: 0.4em;
  }
  .stat-bar-missing {
    background-color: #e0e0e0;
  }
  .stat-bar-missing-fill {
    width: 100%;
    background-color: #b5b5b5;
  }

  .flex-dir-col {
    display: flex;
    flex-direction: column;
  }
  p {

    margin: 1em;
  }

  select {
    padding: 0.25em;
  }

  .quote {
    font-style: italic;
    margin: 1em;
    margin-left: 2em;
    padding-left: 1em;
    border-left: 5px solid black;
    max-width: 25em;
  }
  .author {
    margin-left: 2em;
  }
  .credentials {
    margin-left: 3em;
  }

  .italic {
    font-style: italic;
  }

  .tagline {
    text-align: center;
    font-weight: bold;
    margin-top: 0;
    margin-bottom: 0;
  }

  .text-align-center {
    text-align: center;
  }

  .align-items-center {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .left-pane-image {

  }
  p.left-pane {
    max-width: 50%;
  }

  p.narrow-p {
    max-width: 40em;
  }

  .notes {
    max-width: 20em;
  }

  .call-to-actions {
    display: flex;
    flex-direction: column;
    align-items: center;
    height: 14em;
  }
  .call-to-actions a {
    text-decoration: none;
  }
  .label-input {
    align-items:center;
    justify-content:space-between;
  }

  .grid.edit {
    display: grid;
    grid-template-columns: 100%;
    grid-template-rows: auto;
  }

  .grid {
    display: grid;
    grid-template-columns: 33% 33% 33%;
    grid-template-rows: auto;
  }

  .grid.view.quad {
    grid-template-columns: 25% 25% 25% 25%;
  }

  .grid.view.triple {
    grid-template-columns: 33% 33% 33%;
  }

  .grid.view.dual {
    grid-template-columns: 50% 50%;
  }

  .grid.view.single {
    grid-template-columns: 33% 33%;
  }

  .grid.dual {
    grid-template-columns: 50% 50%;
  }

  .centered {
    display: flex;
    justify-content: center;
  }

  .adaptive-wide img {
    width: 100%;
  }
  img {
    max-width: 30em;
  }

  img.preview {
    max-width:20em;
  }
  .edit-facial-measurements {
    display: flex;
    flex-direction: row;
  }
  th, td {
    padding: 0.5em;
    text-align: center;
  }

  .navigator {
    font-size: 1.5em;
  }

  .bar-charts {
    grid-template-columns: 33% 33% 33%;
  }

  .header {
    background-color: white;
    display: flex;
    justify-content: center;
    align-items: center;
    padding-top: 1em;
  }

  .main-section.with-sidebar {
    margin-left: 320px;
  }

  .columns {
    display: flex;
  }

  .tab-set {
    margin-left: 2em;
    margin-right: 2em;
  }

  .title {
    text-align: center;
  }
  .card {
    padding: 1em;
  }

  .filterCheckbox {
    display: flex;
    flex-direction: column;
  }

  .contextualizePopup  {
    position: fixed;
    display: flex;
    justify-content: center;
    width: 100%;
    margin-top: 10em;
  }

  #contextualize-button {
    margin-left: 2em;
    margin-right: 2em;
  }

  .one-column {
    display: none;
  }

  @media(max-width: 1300px) {
    .grid.view, .grid.view.quad {
      grid-template-columns: 50% 50%;
    }

    .grid.bar-charts {
      grid-template-columns: 100%;
    }

  }
  @media(max-width: 1000px) {
    .main-section.with-sidebar {
      margin-left: 0;
    }
  }
  @media(max-width: 1170px) {
    .main-section {
    }
  }
  @media(max-width: 700px) {
    .desktop {
      display: none;
    }
    .header {
      flex-direction: column;
    }
    .one-column {
      display: table;
    }

    .grid.view, .grid.view.triple, .grid.view.quad {
      grid-template-columns: 100%;
    }

    img {
      width: 100vw;
    }

    .call-to-actions {
      height: 14em;
    }

    .edit-facial-measurements {
      flex-direction: column;
    }

    .grid.view {
      grid-template-columns: 100%;
    }

    .hide-when-mobile {
      display: none;
    }

    .buttons, .edit tr {
      display:flex;
      flex-direction: column;
      align-items: center;
    }

    input {
      width: 85vw;
      margin: 1em;
      padding: 1em;
    }

    #contextualize-button {
      margin-left: 0em;
      margin-right: 0em;
    }

    .main-section {
    }

    .main-section.with-sidebar {
      margin-left: 0;
    }

    select {
      width: 90vw;
      padding: 1em;
    }

    .navigator {
      width: 98vw;
    }

    .button {
      width: 85vw;
    }

    .has-minimal-width {
      min-width: auto;
    }

    .colors {
    }
  }

  @media(min-width: 700px) {
    .hide-when-not-mobile {
      display: none;
    }

    .buttons {
      flex-direction: row;
    }
  }
</style>
