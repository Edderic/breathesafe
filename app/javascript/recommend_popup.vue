<template>
  <div>
  <Popup @onclose='hidePopup' v-if='showPopup'>
    <div  style='padding: 1em;'>
      <h3>{{title}}:</h3>
      <p>{{explanation}}</p>
      <TabSet :options="tabOptions" :tabToShow="tabToShow" @update="onTabUpdate"/>
      <table v-if="tabToShow === 'manual'">
        <thead>
          <tr>
            <th></th>
            <th></th>
            <th></th>
          </tr>
        </thead>
        <tbody v-if='explanationToShow == ""'>
          <tr v-for='key in recommenderKeys' :key="key">
            <th>{{ facialMeasurements[key]?.eng }}</th>
            <td>
              <CircularButton text='?' @click='show(key)'/>
            </td>
            <td>
              <input class='num' type="number" :value='getFacialMeasurement(key)' @change="update($event, key)">
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="tabToShow === 'video'" class='video-wrapper'>
        <div class='video-container'>
          <video ref="videoEl" autoplay playsinline muted class='video' />
          <canvas ref="overlayCanvas" class='overlay-canvas'></canvas>
        </div>
        <p v-if="videoError" class='video-error'>{{ videoError }}</p>
      </div>
      <br>

      <div class='explanation justify-content-center' v-if='explanationToShow != ""'>
        <h2>
          {{engToShow}}
        </h2>
        <div>
          <img :src="imageToShow" alt="">
        </div>
        <p>
            {{explanationToShow}}
        </p>
      </div>

      <div class='justify-content-center'>
        <Button v-if='!hideButton && keyToShow == ""' :shadow='true' @click="recommend">{{title}}</Button>
        <Button v-if='keyToShow != ""' :shadow='true' @click="keyToShow = ''">Back</Button>
      </div>
    </div>
  </Popup>
  </div>
</template>

<script>
import axios from 'axios';
import CircularButton from './circular_button.vue'
import Button from './button.vue'
import PersonIcon from './person_icon.vue'
import Popup from './pop_up.vue'
import { deepSnakeToCamel } from './misc.js'
import { getFacialMeasurements } from './facial_measurements.js'
import SortingStatus from './sorting_status.vue'
import { mapActions, mapWritableState, mapState } from 'pinia';
import { useMainStore } from './stores/main_store';
import { Respirator, displayableMasks, sortedDisplayableMasks } from './masks.js'
import { useFacialMeasurementStore } from './stores/facial_measurement_store'
import TabSet from './tab_set.vue'


export default {
  name: 'RecommendPopup',
  components: {
    Button,
    CircularButton,
    Popup,
    PersonIcon,
    SortingStatus,
    TabSet
  },
  data() {
    return {
      search: "",
      keyToShow: "",
      recommenderKeys: [],
      tabToShow: 'manual',
      tabOptions: [
        { text: 'manual' },
        { text: 'video' }
      ],
      videoError: '',
      visionInitialized: false,
      faceLandmarker: null,
      drawingUtils: null,
      DrawingUtilsClass: null,
      FaceLandmarkerClass: null,
      mediaStream: null,
      animationFrameRequestId: null
    }
  },
  props: {
    hideButton: {
      default: false
    },
    title: {
      default: 'Recommend'
    },

    explanation: {
      default: ''
    },
    showPopup: {
      default: false
    },
  },
  computed: {
    facialMeasurements() {
      return getFacialMeasurements()
    },
    explanationToShow() {
      if (!this.keyToShow) {
        return ""
      }
      return this.facialMeasurements[this.keyToShow]['explanation']
    },
    imageToShow() {
      if (!this.keyToShow) {
        return ""
      }
      return this.facialMeasurements[this.keyToShow]['image_url']
    },
    engToShow() {
      if (!this.keyToShow) {
        return ""
      }
      return this.facialMeasurements[this.keyToShow]['eng']
    }
  },
  async created() {
    this.load(this.$route.query, {})
    await this.fetchRecommenderKeys()
    this.$watch(
      () => this.$route.query,
      (toQuery, fromQuery) => {
          this.load.bind(this)
      }
    )
    this.$watch(
      () => this.showPopup,
      (newVal) => {
        if (!newVal) {
          this.stopVideoMode()
        }
      }
    )
  },
  beforeUnmount() {
    this.stopVideoMode()
  },
  methods: {
    async fetchRecommenderKeys() {
      try {
        const resp = await axios.get('/mask_recommender/recommender_columns.json')
        const cols = (resp.data && resp.data.recommender_columns) || []
        const keys = []
        for (const col of cols) {
          const camel = col.replace(/_([a-z])/g, (_, c) => c.toUpperCase())
          const key = `${camel}Mm`
          if (this.facialMeasurements[key]) keys.push(key)
        }
        this.recommenderKeys = keys
      } catch (e) {
        this.recommenderKeys = []
      }
    },
    ...mapActions(useFacialMeasurementStore, ['getFacialMeasurement', 'updateFacialMeasurement']),
    load(toQuery, fromQuery) {
      for (let facialMeasurement in this.facialMeasurements) {
        if (toQuery[facialMeasurement]) {
          this.updateFacialMeasurement(facialMeasurement, toQuery[facialMeasurement])
        }
      }
    },
    show(key) {
      this.keyToShow = key
    },
    hidePopup() {
      this.$emit('hidePopUp', true)
    },
    update(event, key) {
      this.$emit('updateFacialMeasurement', event, key)
      this.updateFacialMeasurement(key, event.target.value)
    },
    recommend() {
      let event = {
        target: {
          value: this.facialMeasurements.bitragionSubnasaleArcMm.value
        }
      }

      this.$emit(
        'updateFacialMeasurement',
        event,
        'bitragionSubnasaleArcMm'
      )
    },
    onTabUpdate(payload) {
      const name = payload && payload.name ? payload.name : 'manual'
      this.tabToShow = name
      if (name === 'video') {
        this.$nextTick(() => this.startVideoMode())
      } else {
        this.stopVideoMode()
      }
    },
    async ensureVisionInitialized() {
      if (this.visionInitialized && this.faceLandmarker) return
      try {
        const visionModule = await import('https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/vision_bundle.mjs')
        const { FaceLandmarker, FilesetResolver, DrawingUtils } = visionModule
        const filesetResolver = await FilesetResolver.forVisionTasks(
          'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm'
        )
        this.faceLandmarker = await FaceLandmarker.createFromOptions(filesetResolver, {
          baseOptions: {
            modelAssetPath:
              'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task'
          },
          runningMode: 'VIDEO',
          numFaces: 1,
          outputFaceBlendshapes: false,
          outputFacialTransformationMatrixes: false
        })
        // Drawing utils will be initialized once canvas context is available
        this.DrawingUtilsClass = DrawingUtils
        this.FaceLandmarkerClass = FaceLandmarker
        this.visionInitialized = true
      } catch (e) {
        this.videoError = 'Failed to load face landmark model.'
      }
    },
    async startVideoMode() {
      try {
        await this.ensureVisionInitialized()
        if (!this.$refs.videoEl || !this.$refs.overlayCanvas) return

        // Start camera
        this.mediaStream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'user' },
          audio: false
        })
        this.$refs.videoEl.srcObject = this.mediaStream

        const onReady = async () => {
          // Size canvas to match video frame
          const video = this.$refs.videoEl
          const canvas = this.$refs.overlayCanvas
          const width = video.videoWidth || 640
          const height = video.videoHeight || 480
          canvas.width = width
          canvas.height = height
          const ctx = canvas.getContext('2d')
          this.drawingUtils = new this.DrawingUtilsClass(ctx)
          this.processVideoFrame()
        }

        if (this.$refs.videoEl.readyState >= 2) {
          onReady()
        } else {
          this.$refs.videoEl.onloadedmetadata = onReady
        }
      } catch (e) {
        this.videoError = 'Unable to access camera.'
      }
    },
    stopVideoMode() {
      if (this.animationFrameRequestId) {
        cancelAnimationFrame(this.animationFrameRequestId)
        this.animationFrameRequestId = null
      }
      if (this.mediaStream) {
        try {
          this.mediaStream.getTracks().forEach(t => t.stop())
        } catch (_) {}
        this.mediaStream = null
      }
      const canvas = this.$refs && this.$refs.overlayCanvas
      if (canvas) {
        const ctx = canvas.getContext('2d')
        ctx && ctx.clearRect(0, 0, canvas.width, canvas.height)
      }
    },
    processVideoFrame() {
      if (this.tabToShow !== 'video' || !this.faceLandmarker || !this.$refs.videoEl || !this.$refs.overlayCanvas) return

      const video = this.$refs.videoEl
      const canvas = this.$refs.overlayCanvas
      const ctx = canvas.getContext('2d')
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      const nowMs = performance.now()
      const result = this.faceLandmarker.detectForVideo(video, nowMs)

      if (result && result.faceLandmarks) {
        for (const landmarks of result.faceLandmarks) {
          // Tesselation
          this.drawingUtils.drawConnectors(
            landmarks,
            this.FaceLandmarkerClass.FACE_LANDMARKS_TESSELATION,
            { color: '#00FF00AA', lineWidth: 0.5 }
          )
          // Silhouette
          this.drawingUtils.drawConnectors(
            landmarks,
            this.FaceLandmarkerClass.FACE_LANDMARKS_FACE_OVAL,
            { color: '#FF0000AA', lineWidth: 1 }
          )
          // Eyes and lips
          this.drawingUtils.drawConnectors(
            landmarks,
            this.FaceLandmarkerClass.FACE_LANDMARKS_RIGHT_EYE,
            { color: '#00AAFF', lineWidth: 1 }
          )
          this.drawingUtils.drawConnectors(
            landmarks,
            this.FaceLandmarkerClass.FACE_LANDMARKS_LEFT_EYE,
            { color: '#00AAFF', lineWidth: 1 }
          )
          this.drawingUtils.drawConnectors(
            landmarks,
            this.FaceLandmarkerClass.FACE_LANDMARKS_LIPS,
            { color: '#FF00AA', lineWidth: 1 }
          )
          // Draw individual points lightly
          this.drawingUtils.drawLandmarks(landmarks, { color: '#FFFFFFAA', radius: 0.5 })
        }
      }

      this.animationFrameRequestId = requestAnimationFrame(() => this.processVideoFrame())
    }
  }
}
</script>

<style scoped>
  button {
    display: flex;
    cursor: pointer;
    padding: 0.25em;
  }

  input[type='number'] {
    min-width: 2em;
    font-size: 24px;
    padding-left: 0.25em;
    padding-right: 0.25em;
  }

  .explanation {
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  p {
    margin: 1em;
  }

  .justify-content-center {
    display: flex;
    justify-content: center;
  }

  .adaptive-wide img {
    width: 100%;
  }
  img {
    max-width: 30em;
  }

  .video-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 1em;
  }
  .video-container {
    position: relative;
    width: 100%;
    max-width: 30em;
  }
  .video-container .video {
    width: 100%;
    height: auto;
    display: block;
    transform: scaleX(-1); /* Mirror for selfie view */
  }
  .video-container .overlay-canvas {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    transform: scaleX(-1); /* Match mirroring */
  }
  .video-error {
    color: #b00020;
    margin-top: 0.5em;
  }

  tbody tr:hover {
    cursor: pointer;
    background-color: rgb(230,230,230);
  }

  th, td {
    text-align: center;
  }

  .num {
    width: 3em;
  }

  tr.checkboxes td {
    display: flex;
    flex-direction: row;
  }

  @media(max-width: 700px) {
    #search {
      width: 70vw;
      padding: 1em;
    }
  }

</style>


