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
        <p class='instructions'>{{ videoInstruction }}</p>
        <div class='video-container' v-show="!capturedPhotoReady">
          <video ref="videoEl" autoplay playsinline muted class='video' />
          <canvas ref="overlayCanvas" class='overlay-canvas'></canvas>
        </div>
        <div v-if="!capturedPhotoReady" class='video-controls'>
          <Button :shadow='true' @click="onTakePhotoClick" :disabled="takingPhoto || !mediaStream">{{ takePhotoButtonText }}</Button>
          <div v-if="takingPhoto" class='countdown'>{{ countdownRemaining }}</div>
        </div>
        <div v-if="capturedPhotoReady" class='photo-result-container'>
          <canvas ref="photoCanvas" class='photo-canvas' @click.prevent="onPhotoCanvasClick"></canvas>
          <div class='photo-controls'>
            <div v-if="flowStage === 'frontal_photo'">
              <Button :shadow='true' @click="retakePhoto">Retake photo</Button>
              <Button :shadow='true' @click="startAddPoints">Add points for re-scaling</Button>
            </div>
            <div v-else-if="flowStage === 'side_photo'">
              <Button :shadow='true' @click="retakePhoto">Retake the photo</Button>
              <Button :shadow='true' @click="startAddPoints">Add points for re-scaling</Button>
            </div>

            <div v-if="isSelectingPoints">
              <div class='rescale-input-row'>
                <span v-if="hasTwoPoints" style='font-weight: 600; margin-right: 0.5em;'>rescaling distance (mm)</span>
                <input v-if="hasTwoPoints && isFrontalStage" id='rescale-mm-front' type='number' min='1' step='0.1' v-model.number="frontalReferenceMm" @change="recomputeScales" />
                <input v-if="hasTwoPoints && isSideStage" id='rescale-mm-side' type='number' min='1' step='0.1' v-model.number="sideReferenceMm" @change="recomputeScales" />
              </div>
              <div class='next-row'>
                <Button v-if="isFrontalStage && hasTwoPoints" :shadow='true' @click="proceedToSideLive">Next</Button>
                <Button v-if="isSideStage && hasTwoPoints" :shadow='true' @click="computeMeasurements">Compute facial measurements</Button>
              </div>
            </div>

            <div v-if="showResults" class='results'>
              <div><strong>face_width (mm):</strong> {{ results.face_width_mm ?? '—' }}</div>
              <div><strong>face_length (mm):</strong> {{ results.face_length_mm ?? '—' }}</div>
              <div><strong>bitragion_subnasale_arc (mm):</strong> {{ results.bitragion_subnasale_arc_mm ?? '—' }}</div>
              <div><strong>nose_protrusion (mm):</strong> {{ results.nose_protrusion_mm ?? '—' }}</div>
            </div>
          </div>
        </div>
        <p v-if="videoError" class='video-error'>{{ videoError }}</p>
        <p class='video-error'>
          <div v-for="distance in distances" >
            {{ distance }}
          </div>
        </p>
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
// Local mediapipe import (installed via package.json)
// We will dynamically import to avoid heavy initial bundle


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
      drawConnectorsFn: null,
      drawLandmarksFn: null,
      canvasCtx: null,
      runningModeReady: false,
      settingVideoMode: false,
      useImageModeFallback: false,
      offscreenCanvas: null,
      mediaStream: null,
      animationFrameRequestId: null,
      landmarkUpdateTimerId: null,
      landmarks: [],
      distances: [],
      // Photo capture state
      takingPhoto: false,
      countdownRemaining: 0,
      countdownIntervalId: null,
      capturedPhotoReady: false,
      // Flow state
      flowStage: 'frontal_live', // frontal_live | frontal_photo | frontal_points | side_live | side_photo | side_points | results
      currentPhoto: 'frontal', // 'frontal' | 'side'
      // Offscreen canvases to store captured images
      frontalImageCanvas: null,
      sideImageCanvas: null,
      // Landmarks for captured images
      frontalLandmarks: null,
      sideLandmarks: null,
      // User-picked points (in photoCanvas pixel coords)
      frontalPoints: [],
      sidePoints: [],
      // Known real-world distances in mm
      frontalReferenceMm: null,
      sideReferenceMm: null,
      // Pixels-to-mm scales
      frontalMmPerPixel: null,
      sideMmPerPixel: null,
      // Results
      results: {
        face_width_mm: null,
        face_length_mm: null,
        bitragion_subnasale_arc_mm: null,
        nose_protrusion_mm: null
      }
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
    landmark97Text() {
      if (!this.displayedLandmark97) return ''
      const { x, y, z } = this.displayedLandmark97
      const rx = Math.round(x * 1000) / 1000
      const ry = Math.round(y * 1000) / 1000
      const rz = Math.round((z || 0) * 1000) / 1000
      return `Landmark 97: x=${rx}, y=${ry}, z=${rz}`
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
    },
    landmarksToProcess() {
      return [197, 196, 217, 126, 142, 36, 205, 207, 214, 210, 211, 32, 208, 199]
    },
    isFrontalStage() {
      return this.flowStage.startsWith('frontal')
    },
    isSideStage() {
      return this.flowStage.startsWith('side')
    },
    isSelectingPoints() {
      return this.flowStage === 'frontal_points' || this.flowStage === 'side_points'
    },
    hasTwoPoints() {
      const pts = this.isFrontalStage ? this.frontalPoints : this.sidePoints
      return pts && pts.length === 2
    },
    takePhotoButtonText() {
      return this.isFrontalStage ? 'Take a photo' : 'Take sideways photo'
    },
    videoInstruction() {
      if (this.flowStage === 'frontal_live') {
        return 'Take frontal photo with a ruler (or some other flat, reference object) on your forehead.'
      } else if (this.flowStage === 'side_live') {
        return "Repeat the same process, but face sideways so that we can have a good measure of depth. Have a reference object (e.g. a ruler) on the side of your forehead. Then press 'Take sideways photo' when you are ready."
      } else if (this.isSelectingPoints) {
        return 'Please click on two points on the image. You should know the distance between these two points. Add the distance to the text box below, in millimeters. They will help us get facial measurements in millimeters.'
      }
      return ''
    },
    showResults() {
      return this.flowStage === 'results'
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
    computeDistance(point_1, point_2) {
      return Math.sqrt(
        (point_1.x - point_2.x) ** 2
        + (point_1.y - point_2.y) ** 2
        + (point_1.z - point_2.z) ** 2
      )
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
        const mp = await import(/* @vite-ignore */ '@mediapipe/tasks-vision')
        if (!mp || (!mp.FaceLandmarker || !mp.FilesetResolver)) {
          throw new Error('tasks-vision exports missing')
        }
        const wasmBase = '/mediapipe/wasm/'
        let filesetResolver
        try {
          filesetResolver = await mp.FilesetResolver.forVisionTasks(wasmBase)
        } catch (e) {
          console.error('FilesetResolver.forVisionTasks failed', e)
          throw e
        }

        const modelUrl = 'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task'
        try {
          this.faceLandmarker = await mp.FaceLandmarker.createFromOptions(filesetResolver, {
            baseOptions: { modelAssetPath: modelUrl },
            runningMode: 'VIDEO',
            numFaces: 1,
            outputFaceBlendshapes: false,
            outputFacialTransformationMatrices: false
          })
        } catch (e) {
          console.error('FaceLandmarker.createFromOptions failed', e)
          throw e
        }
        if (this.faceLandmarker && typeof this.faceLandmarker.setOptions === 'function') {
          try {
            await this.faceLandmarker.setOptions({ runningMode: 'VIDEO' })
          } catch (e) {
            console.warn('setOptions VIDEO failed, will proceed', e)
          }
        }
        this.runningModeReady = true
        // Drawing utils
        this.DrawingUtilsClass = typeof mp.DrawingUtils === 'function' ? mp.DrawingUtils : null
        this.drawConnectorsFn = null
        this.drawLandmarksFn = null
        this.FaceLandmarkerClass = mp.FaceLandmarker
        this.visionInitialized = true
        this.videoError = ''
      } catch (e) {
        console.error('MediaPipe init error:', e)
        this.videoError = 'Failed to load face landmark model.'
      }
    },
    async ensureVideoRunningMode() {
      if (!this.faceLandmarker) return
      if (this.runningModeReady) return
      if (this.settingVideoMode) return
      this.settingVideoMode = true
      try {
        const maybePromise = this.faceLandmarker.setOptions({ runningMode: 'VIDEO' })
        if (maybePromise && typeof maybePromise.then === 'function') {
          await maybePromise
        }
        this.runningModeReady = true
      } catch (_) {
        this.runningModeReady = false
      } finally {
        this.settingVideoMode = false
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
        try { await this.$refs.videoEl.play() } catch (_) {}

        const onReady = async () => {
          // Size canvas to match video frame
          const video = this.$refs.videoEl
          const canvas = this.$refs.overlayCanvas
          const width = video.videoWidth || 640
          const height = video.videoHeight || 480
          canvas.width = width
          canvas.height = height
          const ctx = canvas.getContext('2d')
          this.canvasCtx = ctx
          // Prepare offscreen for fallback image mode
          this.offscreenCanvas = document.createElement('canvas')
          this.offscreenCanvas.width = width
          this.offscreenCanvas.height = height
          if (this.DrawingUtilsClass) {
            try {
              this.drawingUtils = new this.DrawingUtilsClass(ctx)
            } catch (_) {
              this.drawingUtils = null
            }
          }
          await this.ensureVideoRunningMode()
          this.processVideoFrame()
          // Start a 5-second interval to snapshot and display landmark 97
          this.landmarkUpdateTimerId = setInterval(() => {
            this.updateLandmarks()
          }, 5000)
          if (this.flowStage !== 'frontal_live' && this.flowStage !== 'side_live') {
            this.flowStage = 'frontal_live'
          }
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
    async stopVideoMode() {
      if (this.animationFrameRequestId) {
        cancelAnimationFrame(this.animationFrameRequestId)
        this.animationFrameRequestId = null
      }
      if (this.landmarkUpdateTimerId) {
        clearInterval(this.landmarkUpdateTimerId)
        this.landmarkUpdateTimerId = null
      }
      if (this.countdownIntervalId) {
        clearInterval(this.countdownIntervalId)
        this.countdownIntervalId = null
      }
      this.takingPhoto = false
      this.countdownRemaining = 0
      this.capturedPhotoReady = false
      this.runningModeReady = false
      this.useImageModeFallback = false
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
      const video = this.$refs && this.$refs.videoEl
      if (video) {
        try { video.pause && video.pause() } catch (_) {}
        try { video.srcObject = null } catch (_) {}
      }
      this.offscreenCanvas = null
      // Fully dispose the faceLandmarker so re-entering video re-initializes cleanly
      if (this.faceLandmarker) {
        try {
          if (typeof this.faceLandmarker.close === 'function') {
            await this.faceLandmarker.close()
          } else if (typeof this.faceLandmarker.delete === 'function') {
            this.faceLandmarker.delete()
          }
        } catch (_) {}
        this.faceLandmarker = null
        this.visionInitialized = false
      }
    },
    async updateLandmarks() {
      try {
        this.distances = []

        if (!this.faceLandmarker || !this.$refs.videoEl) return
        if (!this.runningModeReady && !this.useImageModeFallback) return
        let result
        if (this.useImageModeFallback) {
          // Use current offscreen image
          const off = this.offscreenCanvas
          if (!off) return
          // Ensure IMAGE mode
          await this.ensureImageRunningMode()
          result = this.faceLandmarker.detect(off)
        } else {
          // Ensure VIDEO mode
          await this.ensureVideoRunningMode()
          result = this.faceLandmarker.detectForVideo(this.$refs.videoEl, performance.now())
        }
        if (result && result.faceLandmarks && result.faceLandmarks.length > 0) {
          this.landmarks = result.faceLandmarks[0]
          for (let i = 0; i< this.landmarksToProcess.length - 1; i++) {
            this.distances.push(
              {
                'name': `${this.landmarks[i]}, ${this.landmarks[i+1]}`,
                distance: this.computeDistance(
                  this.landmarks[i],
                  this.landmarks[i+1],
                )
              }
            )
          }
        }
      } catch (_) {
        // ignore transient errors
      }
    },
    async processVideoFrame() {
      if (this.tabToShow !== 'video' || !this.faceLandmarker || !this.$refs.videoEl || !this.$refs.overlayCanvas) return

      if (this.useImageModeFallback) {
        this.processImageFrame()
        return
      }

      const video = this.$refs.videoEl
      const canvas = this.$refs.overlayCanvas
      const ctx = this.canvasCtx || this.$refs.overlayCanvas.getContext('2d')
      this.canvasCtx = ctx
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      if (!this.runningModeReady) {
        try {
          await this.ensureVideoRunningMode()
        } catch (_) {}
        this.animationFrameRequestId = requestAnimationFrame(() => this.processVideoFrame())
        return
      }
      const nowMs = performance.now()
      let result = null
      try {
        result = this.faceLandmarker.detectForVideo(video, nowMs)
        this.runningModeReady = true
      } catch (err) {
        // If running mode isn't VIDEO yet, request switch and retry next frame silently
        const msg = (err && err.message) || ''
        if (msg.includes('runningMode') || msg.includes('VIDEO')) {
          this.runningModeReady = false
          // switch to IMAGE fallback to avoid blocking
          await this.ensureImageRunningMode()
          this.useImageModeFallback = true
          this.animationFrameRequestId = requestAnimationFrame(() => this.processImageFrame())
          return
        }
        // For other errors, surface message
        this.videoError = 'Face landmark detection failed.'
        this.animationFrameRequestId = requestAnimationFrame(() => this.processVideoFrame())
        return
      }

      if (result && result.faceLandmarks) {
        for (const landmarks of result.faceLandmarks) {
          // Preferred: instance methods if available
          if (this.drawingUtils && typeof this.drawingUtils.drawConnectors === 'function') {
            this.drawingUtils.drawConnectors(
              landmarks,
              this.FaceLandmarkerClass.FACE_LANDMARKS_TESSELATION,
              { color: '#00FF00AA', lineWidth: 0.5 }
            )
            this.drawingUtils.drawConnectors(
              landmarks,
              this.FaceLandmarkerClass.FACE_LANDMARKS_FACE_OVAL,
              { color: '#FF0000AA', lineWidth: 1 }
            )
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
            this.drawingUtils.drawLandmarks(landmarks, { color: '#FFFFFFAA', radius: 0.5 })
          } else {
            // Fallback: function utilities or minimal renderer
            const drawConns = this.drawConnectorsFn
            const drawPts = this.drawLandmarksFn
            const drawLineSet = (connections, style) => {
              if (drawConns) {
                drawConns(ctx, landmarks, connections, style)
              } else {
                // Minimal fallback: draw straight lines for connections
                ctx.save()
                ctx.strokeStyle = style?.color || '#00FF00AA'
                ctx.lineWidth = style?.lineWidth || 1
                ctx.beginPath()
                for (const [startIdx, endIdx] of connections) {
                  const s = landmarks[startIdx]
                  const e = landmarks[endIdx]
                  ctx.moveTo(s.x * canvas.width, s.y * canvas.height)
                  ctx.lineTo(e.x * canvas.width, e.y * canvas.height)
                }
                ctx.stroke()
                ctx.restore()
              }
            }
            drawLineSet(this.FaceLandmarkerClass.FACE_LANDMARKS_TESSELATION, { color: '#00FF00AA', lineWidth: 0.5 })
            drawLineSet(this.FaceLandmarkerClass.FACE_LANDMARKS_FACE_OVAL, { color: '#FF0000AA', lineWidth: 1 })
            drawLineSet(this.FaceLandmarkerClass.FACE_LANDMARKS_RIGHT_EYE, { color: '#00AAFF', lineWidth: 1 })
            drawLineSet(this.FaceLandmarkerClass.FACE_LANDMARKS_LEFT_EYE, { color: '#00AAFF', lineWidth: 1 })
            drawLineSet(this.FaceLandmarkerClass.FACE_LANDMARKS_LIPS, { color: '#FF00AA', lineWidth: 1 })
            if (drawPts) {
              drawPts(ctx, landmarks, { color: '#FFFFFFAA', radius: 0.5 })
            } else {
              ctx.save()
              ctx.fillStyle = '#FFFFFFAA'
              for (const p of landmarks) {
                ctx.beginPath()
                ctx.arc(p.x * canvas.width, p.y * canvas.height, 0.5, 0, 2 * Math.PI)
                ctx.fill()
              }
              ctx.restore()
            }
          }
        }
      }

      this.animationFrameRequestId = requestAnimationFrame(() => this.processVideoFrame())
    }
    ,
    async ensureImageRunningMode() {
      if (!this.faceLandmarker) return
      try {
        const maybe = this.faceLandmarker.setOptions({ runningMode: 'IMAGE' })
        if (maybe && typeof maybe.then === 'function') await maybe
      } catch (_) {}
    },
    processImageFrame() {
      if (this.tabToShow !== 'video' || !this.faceLandmarker || !this.$refs.videoEl || !this.$refs.overlayCanvas) return
      if (!this.useImageModeFallback) {
        this.animationFrameRequestId = requestAnimationFrame(() => this.processVideoFrame())
        return
      }

      const video = this.$refs.videoEl
      const canvas = this.$refs.overlayCanvas
      const ctx = this.canvasCtx || this.$refs.overlayCanvas.getContext('2d')
      this.canvasCtx = ctx
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      // Draw current video frame to offscreen and run IMAGE detection
      if (!this.offscreenCanvas) {
        this.offscreenCanvas = document.createElement('canvas')
        this.offscreenCanvas.width = canvas.width
        this.offscreenCanvas.height = canvas.height
      }
      const off = this.offscreenCanvas
      const offctx = off.getContext('2d')
      offctx.drawImage(video, 0, 0, off.width, off.height)

      let result = null
      try {
        result = this.faceLandmarker.detect(off)
      } catch (err) {
        // If IMAGE mode is also unavailable, schedule retry via video path
        this.useImageModeFallback = false
        this.animationFrameRequestId = requestAnimationFrame(() => this.processVideoFrame())
        return
      }

      if (result && result.faceLandmarks) {
        for (const landmarks of result.faceLandmarks) {
          if (this.drawingUtils && typeof this.drawingUtils.drawConnectors === 'function') {
            this.drawingUtils.drawConnectors(landmarks, this.FaceLandmarkerClass.FACE_LANDMARKS_TESSELATION, { color: '#00FF00AA', lineWidth: 0.5 })
            this.drawingUtils.drawConnectors(landmarks, this.FaceLandmarkerClass.FACE_LANDMARKS_FACE_OVAL, { color: '#FF0000AA', lineWidth: 1 })
            this.drawingUtils.drawConnectors(landmarks, this.FaceLandmarkerClass.FACE_LANDMARKS_RIGHT_EYE, { color: '#00AAFF', lineWidth: 1 })
            this.drawingUtils.drawConnectors(landmarks, this.FaceLandmarkerClass.FACE_LANDMARKS_LEFT_EYE, { color: '#00AAFF', lineWidth: 1 })
            this.drawingUtils.drawConnectors(landmarks, this.FaceLandmarkerClass.FACE_LANDMARKS_LIPS, { color: '#FF00AA', lineWidth: 1 })
            this.drawingUtils.drawLandmarks(landmarks, { color: '#FFFFFFAA', radius: 0.5 })
          } else {
            const drawConns = this.drawConnectorsFn
            const drawPts = this.drawLandmarksFn
            const drawLineSet = (connections, style) => {
              if (drawConns) {
                drawConns(ctx, landmarks, connections, style)
              } else {
                ctx.save(); ctx.strokeStyle = style?.color || '#00FF00AA'; ctx.lineWidth = style?.lineWidth || 1; ctx.beginPath()
                for (const [startIdx, endIdx] of connections) {
                  const s = landmarks[startIdx]; const e = landmarks[endIdx]
                  ctx.moveTo(s.x * canvas.width, s.y * canvas.height)
                  ctx.lineTo(e.x * canvas.width, e.y * canvas.height)
                }
                ctx.stroke(); ctx.restore()
              }
            }
            drawLineSet(this.FaceLandmarkerClass.FACE_LANDMARKS_TESSELATION, { color: '#00FF00AA', lineWidth: 0.5 })
            drawLineSet(this.FaceLandmarkerClass.FACE_LANDMARKS_FACE_OVAL, { color: '#FF0000AA', lineWidth: 1 })
            drawLineSet(this.FaceLandmarkerClass.FACE_LANDMARKS_RIGHT_EYE, { color: '#00AAFF', lineWidth: 1 })
            drawLineSet(this.FaceLandmarkerClass.FACE_LANDMARKS_LEFT_EYE, { color: '#00AAFF', lineWidth: 1 })
            drawLineSet(this.FaceLandmarkerClass.FACE_LANDMARKS_LIPS, { color: '#FF00AA', lineWidth: 1 })
            if (drawPts) { drawPts(ctx, landmarks, { color: '#FFFFFFAA', radius: 0.5 }) } else {
              ctx.save(); ctx.fillStyle = '#FFFFFFAA'
              for (const p of landmarks) { ctx.beginPath(); ctx.arc(p.x * canvas.width, p.y * canvas.height, 0.5, 0, 2 * Math.PI); ctx.fill() }
              ctx.restore()
            }
          }
        }
      }

      this.animationFrameRequestId = requestAnimationFrame(() => this.processImageFrame())
    }
    ,
    retakePhoto() {
      this.capturedPhotoReady = false
      if (this.isFrontalStage || this.flowStage === 'frontal_photo' || this.flowStage === 'frontal_points') {
        this.flowStage = 'frontal_live'
        this.frontalPoints = []
      } else {
        this.flowStage = 'side_live'
        this.sidePoints = []
      }
    }
    ,
    startAddPoints() {
      if (!this.capturedPhotoReady) return
      if (this.flowStage === 'frontal_photo') {
        this.flowStage = 'frontal_points'
      } else if (this.flowStage === 'side_photo') {
        this.flowStage = 'side_points'
      }
      this.$nextTick(() => this.redrawCurrentPhoto())
    }
    ,
    onPhotoCanvasClick(event) {
      if (!this.isSelectingPoints) return
      const canvas = this.$refs.photoCanvas
      if (!canvas) return
      const rect = canvas.getBoundingClientRect()
      const x = (event.clientX - rect.left) * (canvas.width / rect.width)
      const y = (event.clientY - rect.top) * (canvas.height / rect.height)
      if (this.flowStage === 'frontal_points') {
        if (this.frontalPoints.length >= 2) this.frontalPoints = []
        this.frontalPoints.push({ x, y })
      } else if (this.flowStage === 'side_points') {
        if (this.sidePoints.length >= 2) this.sidePoints = []
        this.sidePoints.push({ x, y })
      }
      this.$nextTick(() => this.redrawCurrentPhoto())
    }
    ,
    redrawCurrentPhoto() {
      const canvas = this.$refs.photoCanvas
      if (!canvas) return
      const ctx = canvas.getContext('2d')
      if (!ctx) return
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      const storeCanvas = (this.flowStage.startsWith('frontal')) ? null : null
      const lm = (this.flowStage.startsWith('frontal')) ? this.frontalLandmarks : this.sideLandmarks
      // Draw mirrored image to match preview using last captured frame if available
      let imgCanvas = this.flowStage.startsWith('frontal') ? this.frontalImageCanvas : this.sideImageCanvas
      if (!imgCanvas) return
      ctx.save(); ctx.translate(canvas.width, 0); ctx.scale(-1, 1); ctx.drawImage(imgCanvas, 0, 0, canvas.width, canvas.height); ctx.restore()
      if (lm) {
        this.drawLandmarksOnCanvas(ctx, canvas, lm, /*isMirrored*/ true)
      }
      const points = this.flowStage.startsWith('frontal') ? this.frontalPoints : this.sidePoints
      if (points && points.length > 0) {
        ctx.save(); ctx.fillStyle = 'red'; ctx.strokeStyle = 'red'; ctx.lineWidth = 2
        for (const p of points) { ctx.beginPath(); ctx.arc(p.x, p.y, 4, 0, Math.PI * 2); ctx.fill() }
        if (points.length === 2) { ctx.beginPath(); ctx.moveTo(points[0].x, points[0].y); ctx.lineTo(points[1].x, points[1].y); ctx.stroke() }
        ctx.restore()
      }
    }
    ,
    recomputeScales() {
      if (this.frontalPoints.length === 2 && this.frontalReferenceMm) {
        const dx = this.frontalPoints[0].x - this.frontalPoints[1].x
        const dy = this.frontalPoints[0].y - this.frontalPoints[1].y
        const d = Math.sqrt(dx*dx + dy*dy)
        if (d > 0) this.frontalMmPerPixel = this.frontalReferenceMm / d
      }
      if (this.sidePoints.length === 2 && this.sideReferenceMm) {
        const dx = this.sidePoints[0].x - this.sidePoints[1].x
        const dy = this.sidePoints[0].y - this.sidePoints[1].y
        const d = Math.sqrt(dx*dx + dy*dy)
        if (d > 0) this.sideMmPerPixel = this.sideReferenceMm / d
      }
    }
    ,
    proceedToSideLive() {
      this.recomputeScales()
      this.capturedPhotoReady = false
      this.flowStage = 'side_live'
      this.currentPhoto = 'side'
    }
    ,
    computeMeasurements() {
      this.recomputeScales()
      const out = { face_width_mm: null, face_length_mm: null, bitragion_subnasale_arc_mm: null, nose_protrusion_mm: null }
      if (this.frontalLandmarks && this.frontalMmPerPixel) {
        const w = this.frontalImageCanvas?.width || 1
        const h = this.frontalImageCanvas?.height || 1
        let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity
        for (const p of this.frontalLandmarks) {
          const x = (1 - p.x) * w // mirrored to match display
          const y = p.y * h
          if (x < minX) minX = x; if (x > maxX) maxX = x
          if (y < minY) minY = y; if (y > maxY) maxY = y
        }
        if (isFinite(minX) && isFinite(maxX)) out.face_width_mm = Math.round((maxX - minX) * this.frontalMmPerPixel)
        if (isFinite(minY) && isFinite(maxY)) out.face_length_mm = Math.round((maxY - minY) * this.frontalMmPerPixel)
      }
      // TODO: bitragion_subnasale_arc_mm and nose_protrusion_mm depend on specific landmark indices and side depth; will finalize after clarification
      this.results = out
      this.flowStage = 'results'
    },
    onTakePhotoClick() {
      if (this.takingPhoto || !this.$refs.videoEl) return
      // Start a visible 3-second countdown then capture
      this.takingPhoto = true
      this.countdownRemaining = 3
      if (this.countdownIntervalId) {
        clearInterval(this.countdownIntervalId)
        this.countdownIntervalId = null
      }
      this.countdownIntervalId = setInterval(async () => {
        this.countdownRemaining -= 1
        if (this.countdownRemaining <= 0) {
          clearInterval(this.countdownIntervalId)
          this.countdownIntervalId = null
          try {
            await this.capturePhotoFromVideo()
          } finally {
            this.takingPhoto = false
          }
        }
      }, 1000)
    }
    ,
    async capturePhotoFromVideo() {
      try {
        const video = this.$refs.videoEl
        if (!video) return
        const width = video.videoWidth || 640
        const height = video.videoHeight || 480

        // Prepare destination canvas shown in UI
        this.capturedPhotoReady = true
        await this.$nextTick()
        const photoCanvas = this.$refs.photoCanvas
        if (!photoCanvas) return
        photoCanvas.width = width
        photoCanvas.height = height
        const ctx = photoCanvas.getContext('2d')
        if (!ctx) return

        // Draw the current video frame
        ctx.save()
        // The video preview is mirrored via CSS. For the snapshot, we also mirror visually
        // by applying a horizontal flip so the image matches the preview.
        ctx.translate(width, 0)
        ctx.scale(-1, 1)
        ctx.drawImage(video, 0, 0, width, height)
        ctx.restore()

        // Keep an unmirrored copy for redraws and analysis
        const storeCanvas = document.createElement('canvas')
        storeCanvas.width = width
        storeCanvas.height = height
        const storeCtx = storeCanvas.getContext('2d')
        if (storeCtx) {
          storeCtx.drawImage(video, 0, 0, width, height)
        }

        // Run landmark detection on the unmirrored pixel coordinates. Since we drew the
        // image mirrored into photoCanvas, pass a temporary offscreen canvas with the
        // original orientation to FaceLandmarker for correct coordinates.
        const analysisCanvas = document.createElement('canvas')
        analysisCanvas.width = width
        analysisCanvas.height = height
        const analysisCtx = analysisCanvas.getContext('2d')
        if (analysisCtx) {
          analysisCtx.drawImage(video, 0, 0, width, height)
        }

        let result = null
        // Ensure model is available
        if (!this.faceLandmarker) {
          await this.ensureVisionInitialized()
        }
        if (this.faceLandmarker) {
          try {
            await this.ensureImageRunningMode()
            result = this.faceLandmarker.detect(analysisCanvas)
          } catch (e) {
            // ignore detection errors; image will still be shown
          }
        }

        if (result && result.faceLandmarks && result.faceLandmarks.length > 0) {
          const detected = result.faceLandmarks[0]
          if (this.isFrontalStage) {
            this.frontalLandmarks = detected
            this.frontalImageCanvas = storeCanvas
          } else {
            this.sideLandmarks = detected
            this.sideImageCanvas = storeCanvas
          }
          // Draw landmarks on the mirrored canvas by mirroring x coordinates
          this.drawLandmarksOnCanvas(ctx, photoCanvas, detected, /*isMirrored*/ true)
        } else {
          // store image even if no landmarks
          if (this.isFrontalStage) {
            this.frontalImageCanvas = storeCanvas
          } else {
            this.sideImageCanvas = storeCanvas
          }
        }

        // Move to photo stage
        if (this.isFrontalStage) {
          this.flowStage = 'frontal_photo'
          this.currentPhoto = 'frontal'
        } else {
          this.flowStage = 'side_photo'
          this.currentPhoto = 'side'
        }
      } catch (_) {
        // Silent fail
      }
    }
    ,
    drawLandmarksOnCanvas(ctx, canvas, landmarks, isMirrored = false) {
      const width = canvas.width
      const height = canvas.height
      const maybeUtilsClass = this.DrawingUtilsClass
      if (maybeUtilsClass) {
        try {
          const utils = new maybeUtilsClass(ctx)
          const connectionsSets = [
            this.FaceLandmarkerClass?.FACE_LANDMARKS_TESSELATION,
            this.FaceLandmarkerClass?.FACE_LANDMARKS_FACE_OVAL,
            this.FaceLandmarkerClass?.FACE_LANDMARKS_RIGHT_EYE,
            this.FaceLandmarkerClass?.FACE_LANDMARKS_LEFT_EYE,
            this.FaceLandmarkerClass?.FACE_LANDMARKS_LIPS
          ].filter(Boolean)

          const maybeMirrorPoint = (p) => ({ x: isMirrored ? 1 - p.x : p.x, y: p.y, z: p.z })
          const mirroredLandmarks = landmarks.map(maybeMirrorPoint)

          for (const connections of connectionsSets) {
            utils.drawConnectors(mirroredLandmarks, connections, { color: '#00FF00AA', lineWidth: 0.75 })
          }
          utils.drawLandmarks(mirroredLandmarks, { color: '#FFFFFFAA', radius: 0.75 })
          return
        } catch (_) {
          // fallback below
        }
      }

      // Fallback manual drawing
      const drawLineSet = (connections, style) => {
        if (!connections) return
        ctx.save()
        ctx.strokeStyle = style?.color || '#00FF00AA'
        ctx.lineWidth = style?.lineWidth || 1
        ctx.beginPath()
        for (const [startIdx, endIdx] of connections) {
          const s = landmarks[startIdx]
          const e = landmarks[endIdx]
          const sx = (isMirrored ? 1 - s.x : s.x) * width
          const ex = (isMirrored ? 1 - e.x : e.x) * width
          const sy = s.y * height
          const ey = e.y * height
          ctx.moveTo(sx, sy)
          ctx.lineTo(ex, ey)
        }
        ctx.stroke()
        ctx.restore()
      }

      drawLineSet(this.FaceLandmarkerClass?.FACE_LANDMARKS_TESSELATION, { color: '#00FF00AA', lineWidth: 0.5 })
      drawLineSet(this.FaceLandmarkerClass?.FACE_LANDMARKS_FACE_OVAL, { color: '#FF0000AA', lineWidth: 1 })
      drawLineSet(this.FaceLandmarkerClass?.FACE_LANDMARKS_RIGHT_EYE, { color: '#00AAFF', lineWidth: 1 })
      drawLineSet(this.FaceLandmarkerClass?.FACE_LANDMARKS_LEFT_EYE, { color: '#00AAFF', lineWidth: 1 })
      drawLineSet(this.FaceLandmarkerClass?.FACE_LANDMARKS_LIPS, { color: '#FF00AA', lineWidth: 1 })
      ctx.save(); ctx.fillStyle = '#FFFFFFAA'
      for (const p of landmarks) {
        const px = (isMirrored ? 1 - p.x : p.x) * width
        const py = p.y * height
        ctx.beginPath(); ctx.arc(px, py, 0.75, 0, Math.PI * 2); ctx.fill()
      }
      ctx.restore()
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
  .instructions {
    margin: 0.5em 0 0 0;
    text-align: center;
    font-weight: 500;
  }
  .video-controls {
    display: flex;
    align-items: center;
    gap: 0.75em;
    margin-top: 0.75em;
  }
  .countdown {
    font-size: 1.5em;
    font-weight: 700;
  }
  .photo-result-container {
    position: relative;
    width: 100%;
    max-width: 30em;
    margin-top: 0.75em;
  }
  .photo-canvas {
    width: 100%;
    height: auto;
    display: block;
    /* Not mirrored here; we draw mirrored pixels in code */
  }
  .photo-controls { margin-top: 0.75em; display: flex; flex-direction: column; gap: 0.5em; align-items: center }
  .rescale-input-row { display: flex; align-items: center; gap: 0.5em; margin-top: 0.5em }
  .next-row { margin-top: 0.5em }
  .results { margin-top: 0.75em; text-align: left; width: 100% }
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


