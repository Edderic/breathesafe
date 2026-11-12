<template>
  <main class="pilot">
    <p>MasqFit · Local research</p><h1>3D webcam pilot</h1>
    <p>Capture a neutral face, reconstruct a surface, calibrate with a tape arc, and inspect projected frontal landmarks.</p>
    <p class="notice">Experimental surface and points. Tape calibration sets scale; it does not validate 3D accuracy or ARKit equivalence. Reconstruction, camera alignment, and landmark agreement require separate review.</p>
    <p v-if="error" role="alert" class="error">{{ error }}</p><p v-if="message" role="status">{{ message }}</p>
    <label>Capture mode for new session<select aria-label="Capture mode for new session" v-model="newCaptureMode" :disabled="busy" @change="prepareCaptureMode">
      <option value="head_turn">Head turns · fixed camera</option><option value="moving_camera">Head still · move camera</option>
      <option value="moving_camera_two_pass">Head still · eye-level + lower camera passes</option>
    </select></label>
    <p>Choose the mode before New session. Existing sessions retain their saved capture mode.</p>
    <details><summary>Optional capture-comparison labels</summary>
      <p>Set these before New session. Use the same group and conditions for repeated 10/20/30-second captures. Describe lighting, camera position and any changes; avoid participant names.</p>
      <label>Comparison group<input v-model="comparisonGroup" maxlength="80" /></label>
      <label>Conditions<input v-model="comparisonConditions" maxlength="1000" placeholder="Same diffuse light, camera distance and settings" /></label>
      <label>Repeat<input v-model.number="comparisonRepeat" type="number" min="1" max="10" /></label>
    </details>
    <div class="toolbar">
      <button @click="guard(connect)">Connect processor</button><button @click="guard(createSession)" :disabled="busy">New session</button>
      <select v-model="resumeId" aria-label="Saved session">
        <option value="">Select a saved session (newest first in each group)</option>
        <optgroup v-for="group in savedSessionGroups" :key="group.label" :label="group.label">
          <option v-for="s in group.sessions" :key="s.id" :value="s.id">{{ s.capture_context?.group ? s.capture_context.group+' · repeat '+s.capture_context.repeat+' · ' : '' }}{{ s.created_at }} · {{ s.status }} · {{ s.id }}</option>
        </optgroup>
      </select>
      <button @click="guard(resume)" :disabled="!resumeId || busy">Resume</button>
      <label>Reload exported session<input type="file" accept=".zip" @change="restore" :disabled="busy" /></label>
    </div>
    <details v-if="diagnostics"><summary>Setup diagnostics · {{ diagnostics.ready ? 'tools ready' : 'setup required' }}</summary><pre>{{ JSON.stringify(diagnostics, null, 2) }}</pre></details>
    <p v-else>Start the loopback processor and research preview using <code>python/dimension_pipeline/WEBCAM_PILOT.md</code>.</p>
    <template v-if="session">
      <p>Session {{ session.id }} · {{ session.status }} <span v-if="session.stage">· {{ session.stage }}</span> · {{ approvedCaptureCount }}/61 approved images saved locally · Capture mode: {{ session.capture_context?.capture_mode || 'head_turn (legacy)' }}</p>
      <section v-if="session.result" class="camera-settings">
        <h3>Depth filtering experiments</h3>
        <p>Compare 2/3/4-view fusion agreement, speckle removal and two added geometric-consistency passes on frozen depth maps. Raw geometry, captures and annotations stay intact. Variants are read-only and require coverage/detail review.</p>
        <button @click="guard(()=>action('depth-experiments'))" :disabled="processing || busy || session.captures.length!==61">Run depth filtering experiments</button>
        <button v-if="depthRun && ['failed','cancelled','interrupted','completed_with_failures'].includes(depthRun.status) && depthRun.variants.some(v=>v.artifacts?.some(a=>a.path.endsWith('/dense.ply')))" @click="guard(()=>action('depth-experiments',{resume_run_id:depthRun.id}))" :disabled="processing || busy">Resume saved point-cloud checkpoints</button>
        <p v-if="depthRun">Experiment {{ depthRun.status }} · {{ depthRun.stage }} <span v-if="depthRun.error">· {{ depthRun.error }}</span></p>
        <table v-if="depthRun?.variants.length"><thead><tr><th>Variant</th><th>Status / coverage</th><th>Points / faces</th><th>Plane residual / raw mesh height</th><th>Raw proximity</th><th>Seconds (cached depths)</th><th>Recommendation</th></tr></thead><tbody>
          <tr v-for="row in depthRun.variants" :key="row.id"><td>{{ row.label }}</td><td>{{ row.status }} · {{ row.coverage_status || row.error || 'pending' }}</td><td>{{ row.retained_points ?? '—' }} / {{ row.metrics?.faces ?? '—' }}</td>
            <td>{{ row.metrics?.roughness.plane_rms_fraction_of_raw_head_height.rms === undefined ? '—' : (row.metrics.roughness.plane_rms_fraction_of_raw_head_height.rms*100).toFixed(4)+'%' }}</td>
            <td>{{ row.metrics?.coverage.global_retention_within_tolerance === undefined ? '—' : (row.metrics.coverage.global_retention_within_tolerance*100).toFixed(2)+'%' }}</td>
            <td>{{ row.processing_seconds?.toFixed(1) ?? '—' }}</td><td>{{ row.recommendation?.decision || 'pending' }}<details v-if="row.recommendation?.reason"><summary>Review notes</summary>{{ row.recommendation.reason }}</details></td></tr>
        </tbody></table>
        <p v-if="depthRun?.variants.length">Local-plane residual screens roughness; lower values can also remove real detail. Raw proximity measures agreement with the raw surface, not independently validated coverage or accuracy. Timings include saved fusion checkpoints and meshing/metrics; source depth estimation is reused.</p>
        <p v-if="depthRows.some(v=>v.status==='completed')">Open mesh comparison below to select a filtered variant against the original full mesh. Existing tape/landmark triangle indices do not apply to a variant.</p>
      </section>
      <section v-if="session.result" class="camera-settings">
        <h3>Image-guided refinement experiments</h3>
        <p>Run three bounded CPU trials with regularity weights 0.05, 0.20 and 0.50 on the original full mesh. Only approved, masked turn images guide geometry. The frontal photo is held out for registration and fresh projections after refinement.</p>
        <p>No hole filling or automatic simplification. Regularization can remove anatomical detail. Refined variants remain uncalibrated and require new tape routes, calibration and point review.</p>
        <button @click="guard(()=>action('refinement-experiments'))" :disabled="processing || busy || session.captures.length!==61">Run image refinement experiments</button>
        <button @click="guard(()=>action('refinement-experiments',{suite:'iterations'}))" :disabled="processing || busy || session.captures.length!==61">Run 8 vs 24 iterations · weight 0.20</button>
        <button @click="guard(()=>action('refinement-experiments',{suite:'iterations',profiles:['iterations24']}))" :disabled="processing || busy || session.captures.length!==61">Run 24 iterations · weight 0.20</button>
        <p>The iteration comparison starts both trials independently from the raw mesh. The native optimizer also changes its final rigidity phase with the iteration budget; 24 iterations is not a continuation of the 8-iteration output.</p>
        <p v-if="refinementRun">Refinement {{ refinementRun.status }} · {{ refinementRun.stage }} <span v-if="refinementRun.error">· {{ refinementRun.error }}</span></p>
        <table v-if="refinementRun?.variants.length"><thead><tr><th>Variant</th><th>Status / coverage</th><th>Faces</th><th>Seconds</th><th>Fresh ray hits</th><th>Recommendation</th></tr></thead><tbody>
          <tr v-for="row in refinementRun.variants" :key="row.id"><td>{{ row.label }}</td><td>{{ row.status }} · {{ row.coverage_status || row.error || 'pending' }}</td><td>{{ row.metrics?.faces ?? '—' }}</td><td>{{ row.processing_seconds?.toFixed(1) ?? '—' }}</td><td>{{ row.projection_hits ?? '—' }} <button v-if="row.status==='completed'" @click="guard(()=>download('refinement-projection/'+row.id,'refinement-'+row.id+'.json'))">Download fresh projections</button></td><td>{{ row.recommendation?.decision }}<details v-if="row.recommendation?.reason"><summary>Review notes</summary>{{ row.recommendation.reason }}</details></td></tr>
        </tbody></table>
        <p>Use mesh comparison below to inspect refinement against the raw surface with shared lighting and framing. Exports include each variant, its fresh analysis topology, detector output, camera, projection attachments and provenance. Cancel retains completed variants; after interruption, start a fresh isolated run.</p>
      </section>
      <p v-if="session.error" role="alert" class="error">{{ session.error }}</p>
      <details v-if="savedQuality.length"><summary>Capture quality · {{ savedQuality.filter(c=>c.capture_quality.flags.length).length }} / {{ savedQuality.length }} frames flagged for review</summary>
        <p>Advisory screening only. Sharpness depends on visible texture and lighting; a high score does not validate reconstruction accuracy. Frames are retained.</p>
        <table><thead><tr><th>Frame</th><th>Sharpness</th><th>Head size (pixels)</th><th>Review notes</th></tr></thead>
          <tbody><tr v-for="c in savedQuality" :key="c.slot"><td>{{ c.slot }}</td><td>{{ c.capture_quality.sharpness?.toFixed(1) ?? 'Unavailable' }}</td><td>{{ c.capture_quality.head_size_px?.join(' × ') ?? 'Unknown' }}</td><td>{{ qualityMessages(c.capture_quality).join(' ') || 'No screening flags' }}</td></tr></tbody></table>
      </details>
      <div class="toolbar">
        <button @click="guard(() => download('export', 'webcam-'+session.id+'.zip'))" :disabled="processing || busy">Export session</button>
        <button v-if="session.result" @click="guard(() => download('mesh', 'full-unscaled-surface.ply'))">Download full unscaled mesh</button>
        <button v-if="session.calibrated?.full_mesh" @click="guard(() => download('mesh-mm', 'full-calibrated-mm-surface.ply'))">Download full calibrated mesh (mm)</button>
        <button @click="guard(deleteSession)" :disabled="processing || busy">Delete this local session</button>
        <button v-if="processing" @click="guard(() => action('cancel'))">Cancel processing</button>
        <button v-if="['capturing', 'failed', 'cancelled', 'interrupted'].includes(session.status)" @click="guard(() => action('start'))" :disabled="session.captures.length !== 61 || hasUnapprovedFrames || busy">{{ session.status === 'capturing' ? 'Reconstruct approved images' : 'Restart reconstruction' }}</button>
      </div>
      <section v-if="session.status === 'capturing'">
        <h2>Capture and mask review</h2>
        <p>Use steady diffuse light across both sides of your face and a plain background. Avoid bright windows behind you and harsh highlights. Keep the camera fixed, mouth closed and expression neutral. Include both ears and chin in every pose. Review each image for blur and each mask for background, shoulders and neck.</p>
        <div class="toolbar"><button @click="guard(startCamera)" :disabled="!!stream">Enable camera</button><button @click="stopCamera">Stop camera</button>
          <label><input type="checkbox" v-model="consent" /> I consent to storing and processing these captures locally.</label>
        </div>
        <section v-if="stream" class="camera-settings"><h3>Camera consistency</h3>
          <p>After positioning yourself, lock supported settings before the first photo. Unsupported or unverified controls stay explicitly labeled. Start a new session to change settings after capture begins.</p>
          <label v-for="control in cameraControls" :key="control.id"><input type="checkbox" v-model="selectedLocks" :value="control.id" :disabled="!control.supported || busy || captureSettingsFrozen" />
            {{ control.label }}: {{ controlLabel(control) }}</label>
          <div class="toolbar"><button @click="guard(lockCameraSettings)" :disabled="busy || captureSettingsFrozen || !selectedLocks.length">Lock selected camera settings</button>
            <button @click="guard(restoreCameraSettings)" :disabled="busy || captureSettingsFrozen || !cameraAttempts.length">Restore initial camera settings</button></div>
          <p v-if="cameraControlMessage" role="status">{{ cameraControlMessage }}</p>
        </section>
        <div class="columns">
          <section><div class="camera-preview"><video ref="video" autoplay playsinline muted class="preview" /><div class="framing-guide" aria-hidden="true"></div></div><p>Mirrored preview · stored photos are unmirrored. Keep ears and chin inside the guide throughout the sweep; move closer if your head looks small.</p>
            <p>{{ guidance }}</p><p aria-live="polite">{{ countdown || '' }}</p>
            <div class="toolbar"><label><input type="checkbox" v-model="audioEnabled" @change="updateAudio" /> Speak countdown and capture cues</label>
              <label>{{ captureMode==='moving_camera_two_pass' ? 'Active capture time (pause excluded)' : 'Sweep duration' }}<select aria-label="Sweep duration" v-model.number="sweepDuration" :disabled="busy">
                <option :value="10">10 seconds · 60 frames</option>
                <option :value="20">20 seconds · 60 frames</option>
                <option :value="30">30 seconds · 60 frames</option>
              </select></label>
              <button @click="testAudio" :disabled="busy || !audioEnabled">Test audio</button></div>
            <p v-if="captureMode==='moving_camera_two_pass'"><strong>Two camera passes · 30 + 30 frames:</strong> pass 1 moves at eye level from your left profile through frontal to your right profile in {{ sweepDuration/2 }} seconds. Then capture pauses: lower the camera slightly (about 10–15° below eye level, aiming gently upward), keeping it on your right side. Click Start lower pass when ready. Pass 2 returns from your right profile through frontal to your left profile in {{ sweepDuration/2 }} seconds. Each pass crosses frontal halfway through, at {{ sweepDuration/4 }} seconds. Keep head, torso, expression, lights, lens and approximate camera distance fixed. Look straight ahead rather than tracking the camera. Left/right mean the subject’s sides. Capture a separate eye-level frontal photo first. Each pass has a three-second preparation countdown; repositioning is not captured.</p>
            <p v-else-if="captureMode==='moving_camera'"><strong>Head still · move camera · 60 frames:</strong> a helper starts with the camera at your left profile, moves it along an eye-level arc to directly in front at {{ sweepDuration/2 }} seconds, and finishes at your right profile at {{ sweepDuration }} seconds. Left/right mean the subject’s sides. Keep the same camera, lens, lighting and approximate face-to-camera distance. Keep lights stationary. Keep your head and torso still, look at a fixed point ahead, and do not follow the camera. Move the camera’s position around the head, rather than swiveling it from one spot. Capture a separate frontal photo with the camera directly in front. Three preparation seconds come before the sweep.</p>
            <p v-else><strong>One continuous 60-frame sweep:</strong> start at your right profile, look directly at the camera halfway through ({{ sweepDuration/2 }} seconds), and finish at your left profile. Keep your chin level and turn smoothly. A three-second preparation countdown comes before the {{ sweepDuration }}-second capture countdown. Capture the designated frontal photo separately.</p>
            <p v-if="sweeping" role="status">{{ capturePass ? 'Pass '+capturePass+' · ' : '' }}{{ captureRemaining }} seconds remaining in sweep · {{ selected }}/60 frames captured</p>
            <p v-if="lowerPassReady" role="status">30 eye-level frames captured. Keep your head still. Reposition the camera slightly lower on your right side, then start pass 2. No frames are captured during this pause.</p>
            <button v-if="lowerPassReady" @click="continueLowerPass">Start lower pass</button>
            <p v-if="audioMessage" role="status">{{ audioMessage }}</p>
            <div class="toolbar"><button @click="guard(() => takePhoto(selected))" :disabled="!stream || !consent || busy">{{ selected === 0 ? 'Capture frontal' : 'Capture / retake selected frame' }}</button>
              <button @click="guard(startSweep)" :disabled="!stream || !consent || busy">Capture all 60 frames</button>
              <button @click="stopCapture" :disabled="!busy || !!bulkProgress">Stop capture sequence</button>
            </div>
          </section>
          <section><label>Capture to review<select v-model.number="selected" :disabled="busy || reviewLoading" @change="guard(reviewSelected)"><option v-for="i in 61" :key="i" :value="i-1">{{ slot(i-1) }} {{ approved(i-1) ? '✓ saved' : frames[i-1] ? '· review needed' : '' }}</option></select></label>
            <div class="toolbar"><button @click="guard(() => changeReviewFrame(-1))" :disabled="selected === 0 || busy || reviewLoading" aria-keyshortcuts="ArrowLeft">← Previous frame</button>
              <button @click="guard(() => changeReviewFrame(1))" :disabled="selected === 60 || busy || reviewLoading" aria-keyshortcuts="ArrowRight">Next frame →</button></div>
            <p>Shortcuts: <kbd>←</kbd> / <kbd>→</kbd> previous / next frame · <kbd>A</kbd> approve, save and advance. Shortcuts pause in input fields and dropdowns. Each mask loads automatically when switching frames.</p>
            <p v-if="reviewLoading" role="status">Loading frame and mask…</p>
            <section v-if="reviewFrame?.capture_quality" class="quality-panel" aria-label="Frame quality">
              <strong>Frame quality</strong>
              <p>Head: {{ reviewFrame.capture_quality.head_size_px?.join(' × ') ?? 'Unknown' }} pixels · {{ Math.round((reviewFrame.capture_quality.head_height_fraction || 0)*100) }}% of image height. Sharpness: {{ reviewFrame.capture_quality.sharpness?.toFixed(1) ?? 'Unavailable' }}.</p>
              <ul v-if="reviewFrame.capture_quality.flags.length"><li v-for="note in qualityMessages(reviewFrame.capture_quality)" :key="note">{{ note }}</li></ul>
              <p v-else>No screening flags. Check ears, chin and mask boundaries visually.</p>
              <small>Provisional screening threshold: sharpness {{ reviewFrame.capture_quality.policy.sharpness_warning_below }}. Low texture can also lower the score. Retake flagged frames if needed; acceptance keeps them.</small>
            </section>
            <p v-if="session.mask_experiment"><strong>Upper-neck mask experiment:</strong> {{ session.mask_experiment.instructions }} Original photos are reused; these proposed masks have not been approved. Use A to approve and advance.</p>
            <p>Paint <strong>include</strong> to restore ears, chin and intended upper-neck coverage; paint <strong>exclude</strong> to remove shoulders, clothing and background. The green overlay shows included pixels. Check mask coverage before relying on the reconstruction.</p>
            <div class="toolbar"><button @click="guard(reviewSelected)" :disabled="busy || reviewLoading">Load / generate mask</button><label><input type="checkbox" v-model="includeBrush" /> Include brush</label>
              <label>Brush size<input type="range" v-model.number="brushSize" min="3" max="120" /></label></div>
            <canvas ref="maskCanvas" class="mask-editor" @pointerdown="brushStart" @pointermove="brushMove" @pointerup="brushEnd" @pointercancel="brushEnd" />
            <button @click="guard(approveMask)" :disabled="!reviewFrame || busy || reviewLoading" aria-keyshortcuts="a">{{ session.mask_experiment ? 'Approve and save this mask' : 'Approve and save this head-only mask' }}</button>
            <div class="toolbar"><button @click="guard(acceptAllFrames)" :disabled="busy || reviewLoading || painting || !bulkCandidates.length || !!session.mask_experiment">Accept all frames</button>
              <button v-if="bulkProgress" @click="bulkCancelled=true">Stop accepting</button></div>
            <p v-if="!session.mask_experiment">Accept all saves the current masks for every pending captured frame, including the frontal photo, and generates missing masks automatically. This skips individual mask review.</p>
            <p v-if="bulkProgress" role="status">Accepted {{ bulkProgress.completed }} / {{ bulkProgress.total }} frames · {{ slot(selected) }}</p>
          </section>
        </div>
      </section>
      <section v-if="session.result">
        <h2>Surface, scale and frontal points</h2>
        <p>{{ surface.units === 'mm' ? 'Tape-calibrated millimeters' : 'Unscaled reconstruction coordinates' }} · human webcam surface · anatomical accuracy unvalidated.</p>
        <div class="columns">
          <section><h3>Undistorted frontal image</h3>
            <svg v-if="frontUrl" :viewBox="`0 0 ${frontCamera.width} ${frontCamera.height}`" role="img" aria-label="Frontal detections and camera alignment">
              <image :href="frontUrl" :width="frontCamera.width" :height="frontCamera.height" />
              <path v-if="showWire" :d="wirePath" stroke="#0ff" fill="none" stroke-width="0.6" opacity=".5" />
              <circle v-for="(p,i) in session.result.raw_predictions" :key="i" :cx="p.x*frontCamera.width" :cy="p.y*frontCamera.height" :r="i === pointIndex ? 8 : 3" :fill="i === pointIndex ? '#ff7b00' : '#00ffba'" @click="pointIndex=i" />
            </svg>
            <label><input type="checkbox" v-model="showWire" /> Show camera-aligned surface wireframe</label>
            <p>Inspect silhouette, ears, nose and chin alignment. A correct ray hit cannot distinguish reconstruction error, registration error, and detector disagreement.</p>
            <label>MediaPipe index<input type="number" v-model.number="pointIndex" min="0" :max="detections.length-1" /></label>
            <pre v-if="point">{{ JSON.stringify(point, null, 2) }}</pre>
            <div class="toolbar"><button v-for="decision in ['pending','accepted','rejected']" :key="decision" @click="guard(() => decide(decision))" :disabled="!point">{{ decision }}</button></div>
          </section>
          <section><h3>Rotatable surface</h3>
            <svg ref="viewport" viewBox="0 0 720 480" role="img" aria-label="Rotate surface; Control-click to trace tape route" tabindex="0" @pointerdown="surfaceDown" @pointermove="surfaceMove" @pointerup="surfaceUp" @pointercancel="drag=null" @wheel="surfaceWheel">
              <rect width="720" height="480" fill="#192b38" />
              <polygon v-for="f in faces" :key="f.index" :points="f.points" :fill="f.fill" :stroke="surfaceEdges ? '#14202b' : 'none'" :stroke-width="surfaceEdges ? .45 : 0" :stroke-opacity=".45" stroke-linejoin="round" />
              <polyline v-for="(line,i) in routeLines" :key="'route'+i" :points="line" fill="none" stroke="#d75b10" stroke-width="2" stroke-dasharray="5 2" />
              <g v-for="(p,i) in routeMarks" :key="i"><circle :cx="p.x" :cy="p.y" r="5" fill="#ff7b00" /><text :x="p.x+7" :y="p.y-5">{{ i+1 }}</text></g>
              <circle v-if="selectedMark" :cx="selectedMark.x" :cy="selectedMark.y" r="7" fill="#15c8ae" stroke="white" />
            </svg>
            <label>Yaw<input type="range" v-model.number="yaw" min="-180" max="180" /></label><label>Tilt<input type="range" v-model.number="pitch" min="-90" max="90" /></label>
            <div class="toolbar"><button @click="resetSurfaceView">Reset view / fit surface</button>
              <button @click="yaw=-35; pitch=0">¾ view left</button><button @click="yaw=35; pitch=0">¾ view right</button>
              <label><input type="checkbox" v-model="smoothLighting" /> Smooth lighting</label>
              <label><input type="checkbox" v-model="surfaceEdges" /> Show mesh edges</label></div>
            <label>Zoom {{ zoom.toFixed(1) }}×<input type="range" v-model.number="zoom" min="0.5" max="3" step="0.1" /></label>
            <label>Light direction<input type="range" v-model.number="lightAzimuth" min="-80" max="80" /></label>
            <p>Drag to rotate. Adjust light direction to reveal contours; use the zoom slider or Shift + scroll to zoom. Ctrl-click (or enable tap placement) to add tape contact controls on visible surface. Missing ear/chin coverage requires a new capture.</p>
            <label><input type="checkbox" v-model="tapPlacement" /> Tap to place route controls</label>
          </section>
        </div>
        <button @click="comparisonOpen=!comparisonOpen">{{ comparisonOpen ? 'Close mesh comparison' : 'Compare full and analysis meshes' }}</button>
        <WebcamMeshComparison v-if="comparisonOpen" :api-base="API" :session-id="session.id" :source-key="session.result.full_mesh+'|'+[...depthRows,...refinementRows].filter(v=>v.status==='completed').map(v=>v.id).join('|')"
          :analysis-mesh="session.result.surface.mesh" :camera="frontCamera" :scale-factor="session.calibrated?.report.mm_per_reconstruction_unit || 1" :units="surface.units"
          :yaw="yaw" :pitch="pitch" :zoom="zoom" :light-azimuth="lightAzimuth" :smooth-lighting="smoothLighting" :surface-edges="surfaceEdges"
          @rotate="yaw=$event.yaw;pitch=$event.pitch" @zoom="zoom=$event" @frame="comparisonFrame=$event" />
        <button @click="regionalOpen=!regionalOpen">{{ regionalOpen ? 'Close regional inspection' : 'Inspect nose and mask-contact regions' }}</button>
        <button @click="nosePhotosOpen=!nosePhotosOpen">{{ nosePhotosOpen ? 'Close nose source photos' : 'Inspect nose on source photos' }}</button>
        <WebcamNosePhotos v-if="nosePhotosOpen" :api-base="API" :session-id="session.id" :source-key="session.result.full_mesh+'|'+refinementRows.filter(v=>v.status==='completed').map(v=>v.id).join('|')" :variants="refinementRows.filter(v=>v.status==='completed')" />
        <button @click="landmarkOpen=!landmarkOpen">{{ landmarkOpen ? 'Close landmark review' : 'Review anatomical landmarks' }}</button>
        <WebcamLandmarkReview v-if="landmarkOpen" :api-base="API" :session-id="session.id" :variants="refinementRows.filter(v=>v.status==='completed')" :frontal-url="frontUrl" />
        <WebcamRegionalInspection v-if="regionalOpen" :api-base="API" :session-id="session.id" :source-key="session.result.full_mesh+'|'+refinementRows.filter(v=>v.status==='completed').map(v=>v.id).join('|')"
          :variants="refinementRows.filter(v=>v.status==='completed')" :frontal-url="frontUrl" />
        <h3>Tape calibration and independent check</h3>
        <p>Trace left tragion → subnasale → right tragion for scale, including intermediate tape-contact points. Separately trace left tragion → menton → right tragion for the independent check. Routes use mesh edges between controls and may overestimate a smooth tape arc.</p>
        <div class="toolbar"><label>Route<select v-model="routeKind"><option value="scale">Scale via subnasale</option><option value="check">Independent check via menton</option></select></label>
          <label>Next point<select v-model="routeLabel"><option value="left_tragion">Left tragion (start)</option><option value="control">Intermediate control</option><option value="subnasale">Subnasale</option><option value="menton">Menton</option><option value="right_tragion">Right tragion (end)</option></select></label>
          <button @click="routes[routeKind].pop(); coverageReviewed=false">Undo last route point</button><button @click="routes[routeKind]=[]; coverageReviewed=false">Clear route</button>
          <button @click="guard(saveDraft)" :disabled="processing">Save route draft locally</button></div>
        <p>{{ routes[routeKind].map((p,i) => `${i+1}: ${p.label}`).join(' → ') || 'No controls placed' }}</p>
        <p v-if="routePreview.length">Mesh-edge route: {{ routePreview.some(p => p.status !== 'ok') ? 'Disconnected surface — cannot calibrate' : routePreview.reduce((sum,p) => sum+p.length, 0).toFixed(3)+' '+surface.units }}. Dashed route overlays include hidden segments; rotate to inspect the full contact route.</p>
        <div class="toolbar"><label v-for="i in 3" :key="'s'+i">Scale reading {{ i }} (mm)<input v-model.number="scaleReadings[i-1]" type="number" min="1" step="0.1" /></label></div>
        <div class="toolbar"><label v-for="i in 3" :key="'c'+i">Independent check {{ i }} (mm)<input v-model.number="checkReadings[i-1]" type="number" min="1" step="0.1" /></label></div>
        <label><input type="checkbox" v-model="coverageReviewed" /> I inspected both complete tape routes, including ears, nose and chin, and found no missing coverage or bridged holes.</label>
        <button @click="guard(calibrate)" :disabled="!coverageReviewed || busy || processing">Calibrate and report independent check</button>
        <pre v-if="session.calibrated">{{ JSON.stringify(session.calibrated.report, null, 2) }}</pre>
        <details><summary>Reconstruction and camera diagnostics</summary><pre>{{ JSON.stringify(session.result.diagnostics, null, 2) }}</pre></details>
      </section>
    </template>
  </main>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue';
import { captureNativeFrame, nativeCameraConstraints, captureGuidance, runCaptureSweep, sweepCues } from './webcam_capture';
import { createCaptureAudio, capturedFrameCue } from './webcam_capture_audio';
import { captureQuality, qualityMessages } from './webcam_capture_quality';
import { inspectCameraControls, applyCameraControl, cameraControlSnapshot } from './webcam_camera_controls';
import { attachmentPoint, projectMesh, pickSurface } from './face_annotation_geometry';
import { surfaceFraming, surfaceVertexNormals, shadedSurfaceFaces } from './webcam_surface_view';
import { projectPoint } from './dimension_fixture_geometry';
import { buildSurfaceGraph, surfacePath } from './face_surface_paths';
import WebcamMeshComparison from './webcam_mesh_comparison.vue';
import WebcamRegionalInspection from './webcam_regional_inspection.vue';
import WebcamLandmarkReview from './webcam_landmark_review.vue';
import WebcamNosePhotos from './webcam_nose_photos.vue';

const API = 'http://127.0.0.1:5182';
const session = ref(null), sessions = ref([]), diagnostics = ref(null), resumeId = ref('');
const savedSessionGroups = computed(() => {
  const sorted = [...sessions.value].sort((a,b) => {
    const time = s => Date.parse(s.created_at) || 0;
    return time(b)-time(a) || a.id.localeCompare(b.id);
  });
  const ready = s => ['surface_ready','calibrated'].includes(s.status);
  return [
    {label:'Surfaces ready · newest first',sessions:sorted.filter(ready)},
    {label:'Other sessions · newest first',sessions:sorted.filter(s => !ready(s))},
  ].filter(group => group.sessions.length);
});
const error = ref(''), message = ref(''), busy = ref(false), consent = ref(false);
const comparisonGroup=ref(''),comparisonConditions=ref(''),comparisonRepeat=ref(1);
const newCaptureMode=ref('head_turn');
const captureMode=computed(()=>session.value?.capture_context?.capture_mode || 'head_turn');
function prepareCaptureMode(){if(newCaptureMode.value==='moving_camera')sweepDuration.value=20;else if(newCaptureMode.value==='moving_camera_two_pass')sweepDuration.value=30;}
const cameraControls=ref([]),selectedLocks=ref([]),cameraAttempts=ref([]),cameraControlMessage=ref('');
let initialCameraControls=[];
const video = ref(null), stream = ref(null), countdown = ref(0), selected = ref(0), frames = ref({}), captureCancelled = ref(false);
const audioEnabled = ref(true), audioMessage = ref('');
const sweepDuration = ref(10), sweeping = ref(false), captureRemaining = ref(0);
const capturePass=ref(0),lowerPassReady=ref(false);let lowerPassResolve;
function continueLowerPass(){lowerPassReady.value=false;lowerPassResolve?.(true);lowerPassResolve=null;}
const captureAudio = createCaptureAudio(window, text => { audioMessage.value=text; });
function cue(text) { if (audioEnabled.value) captureAudio.speak(text, 1.8); }
function updateAudio() { captureAudio.cancel(); audioMessage.value=''; }
function testAudio() { audioMessage.value='You should hear “Frame one.”'; cue('Frame one.'); }
function stopCapture() { captureCancelled.value=true; captureAudio.cancel(); lowerPassResolve?.(false);lowerPassResolve=null;lowerPassReady.value=false; }
const maskCanvas = ref(null), reviewFrame = ref(null), includeBrush = ref(false), brushSize = ref(30);
const reviewLoading = ref(false);
const bulkProgress = ref(null), bulkCancelled = ref(false);
let reviewRevision = 0;
const frontUrl = ref(''), pointIndex = ref(0), showWire = ref(false), yaw = ref(0), pitch = ref(0), zoom = ref(1), viewport = ref(null);
const lightAzimuth = ref(-40), surfaceEdges = ref(false), smoothLighting = ref(true);
const comparisonOpen=ref(false),comparisonFrame=ref(null);
const regionalOpen=ref(false);
const landmarkOpen=ref(false);
const nosePhotosOpen=ref(false);
function resetSurfaceView() { yaw.value=0; pitch.value=0; zoom.value=1; }
function surfaceWheel(event) {
  if (!event.shiftKey) return;
  event.preventDefault(); zoom.value=Math.max(.5,Math.min(3,zoom.value*(event.deltaY>0 ? .95 : 1.05)));
}
const routes = ref({ scale: [], check: [] }), routeKind = ref('scale'), routeLabel = ref('left_tragion'), tapPlacement = ref(false);
const scaleReadings = ref(['','','']), checkReadings = ref(['','','']), coverageReviewed = ref(false);
let pollTimer, maskWorker, workerCounter = 0, maskPixels, painting = false, drag = null, disposed = false;
const pending = new Map();
const slot = i => i === 0 ? 'front' : 'turn_'+String(i-1).padStart(2, '0');
const guidance = computed(() => captureGuidance(selected.value,captureMode.value));
const approved = i => !frames.value[i]?.pending && session.value?.captures.some(c => c.slot === slot(i) && c.mask_approved === true);
const approvedCaptureCount=computed(()=>session.value?.captures.filter(c=>c.mask_approved===true).length || 0);
const hasUnapprovedFrames = computed(() => Object.values(frames.value).some(f => f.pending) || session.value?.captures.some(c=>c.mask_approved!==true));
const captureSettingsFrozen=computed(()=>!!session.value?.captures.length || Object.keys(frames.value).length>0);
const savedQuality=computed(()=>session.value?.captures.filter(c=>c.capture_quality).sort((a,b)=>a.slot.localeCompare(b.slot)) || []);
const bulkCandidates = computed(() => Object.keys(frames.value).map(Number).filter(index => !approved(index)).sort((a,b)=>a-b));
const depthRun=computed(()=>session.value?.depth_experiments?.runs.at(-1));
const depthRows=computed(()=>session.value?.depth_experiments?.runs.flatMap(run=>run.variants) || []);
const refinementRun=computed(()=>session.value?.refinement_experiments?.runs.at(-1));
const refinementRows=computed(()=>session.value?.refinement_experiments?.runs.flatMap(run=>run.variants) || []);
const processing = computed(() => session.value?.status === 'processing' || depthRun.value?.status==='processing' || refinementRun.value?.status==='processing');
async function guard(fn) { error.value=''; try { await fn(); } catch (e) { error.value=e.message; } }
async function api(path, payload) {
  const response = await fetch(API+path, payload === undefined ? {} : { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload) });
  const result = await response.json(); if (!response.ok) throw Error(result.error || 'Local processor request failed.'); return result;
}
async function connect() { diagnostics.value=await api('/diagnostics'); sessions.value=await api('/sessions'); message.value='Connected to private local processor.'; }
async function adopt(state) {
  comparisonOpen.value=false;comparisonFrame.value=null;
  regionalOpen.value=false;
  landmarkOpen.value=false;
  nosePhotosOpen.value=false;
  resetSurfaceView();
  reviewRevision++; reviewLoading.value=false;
  stopCamera(); frames.value={}; reviewFrame.value=null; routes.value={scale:[],check:[]}; coverageReviewed.value=false;
  session.value=state; selected.value=0; schedulePoll();
  comparisonGroup.value=state.capture_context?.group || '';comparisonConditions.value=state.capture_context?.conditions || '';comparisonRepeat.value=state.capture_context?.repeat || 1;
  newCaptureMode.value=state.capture_context?.capture_mode || 'head_turn';
  prepareCaptureMode();
  if (frontUrl.value) URL.revokeObjectURL(frontUrl.value); frontUrl.value='';
  if (state.calibrated) {
    const report=state.calibrated.report;
    routes.value={scale:report.scale.route,check:report.independent_check.route};
    scaleReadings.value=[...report.scale.readings_mm]; checkReadings.value=[...report.independent_check.readings_mm];
  }
  if (state.draft) {
    routes.value={scale:state.draft.scale_route,check:state.draft.check_route};
    scaleReadings.value=state.draft.scale_readings_mm; checkReadings.value=state.draft.check_readings_mm;
  }
  if (state.result) await loadFrontal();
}
async function createSession() { await adopt(await api('/sessions', {capture_context:{group:comparisonGroup.value,conditions:comparisonConditions.value,repeat:comparisonRepeat.value,capture_mode:newCaptureMode.value}})); await connect(); }
async function resume() { await adopt(await api('/sessions/'+resumeId.value)); }
function schedulePoll() { clearTimeout(pollTimer); if (!disposed && processing.value) pollTimer=setTimeout(() => guard(refresh), 1500); }
async function refresh() {
  const id=session.value.id, state=await api('/sessions/'+id);
  if (session.value?.id !== id) return;
  session.value=state; if (state.result && !frontUrl.value) await loadFrontal(); schedulePoll();
}
async function action(name, payload={}) { const state=await api(`/sessions/${session.value.id}/${name}`,payload); if (name !== 'cancel') session.value=state; schedulePoll(); }
async function deleteSession() { await api(`/sessions/${session.value.id}/delete`,{}); session.value=null; stopCamera(); clearTimeout(pollTimer); await connect(); }
async function download(kind, name) {
  const response=await fetch(`${API}/sessions/${session.value.id}/${kind}`); if (!response.ok) throw Error((await response.json()).error);
  const url=URL.createObjectURL(await response.blob()), a=document.createElement('a'); a.href=url; a.download=name; a.click(); setTimeout(() => URL.revokeObjectURL(url),1000);
}
const base64 = blob => new Promise((resolve,reject) => { const r=new FileReader(); r.onerror=reject; r.onload=() => resolve(r.result.split(',')[1]); r.readAsDataURL(blob); });
const blobOf = canvas => new Promise(resolve => canvas.toBlob(resolve,'image/png'));
const sha = async blob => Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',await blob.arrayBuffer())),v=>v.toString(16).padStart(2,'0')).join('');
async function restore(event) { await guard(async () => { const file=event.target.files[0]; if (!file) return; busy.value=true; try {
  const response=await fetch(API+'/restore',{method:'POST',headers:{'Content-Type':'application/zip'},body:file});
  const result=await response.json(); if(!response.ok) throw Error(result.error); await adopt(result); await connect();
} finally { busy.value=false; event.target.value=''; } }); }
async function startCamera() {
  if (!navigator.mediaDevices?.getUserMedia) throw Error('Camera access requires a local secure browser context.');
  stream.value=await navigator.mediaDevices.getUserMedia(nativeCameraConstraints);
  try {
    await nextTick(); video.value.srcObject=stream.value; await video.value.play();
    cameraControls.value=inspectCameraControls(stream.value.getVideoTracks()[0]);initialCameraControls=cameraControls.value.map(c=>({...c}));
    selectedLocks.value=cameraControls.value.filter(c=>c.supported).map(c=>c.id);cameraAttempts.value=[];cameraControlMessage.value='';
  }catch(error){stopCamera();throw error;}
}
function stopCamera() { stopCapture(); stream.value?.getTracks().forEach(t=>t.stop()); stream.value=null;cameraControls.value=[];cameraAttempts.value=[];initialCameraControls=[]; }
function controlLabel(control) {
  const attempt=cameraAttempts.value.find(a=>a.id===control.id);
  if(attempt?.verified && attempt.requested.mode==='manual')return 'Locked (verified)';
  if(attempt && !attempt.verified)return `${attempt.status}: ${attempt.error || 'settings changed'}`;
  return control.supported ? `${control.current_mode} · available to lock` : `Unavailable — ${control.reason}`;
}
async function configureCamera(restore=false) {
  if(!stream.value || busy.value || captureSettingsFrozen.value)return;
  busy.value=true;
  try {
    const track=stream.value.getVideoTracks()[0],current=inspectCameraControls(track);
    const controls=restore ? initialCameraControls.filter(c=>cameraAttempts.value.some(a=>a.id===c.id)) : current.filter(c=>selectedLocks.value.includes(c.id)&&c.supported);
    for(const control of controls) {
      const attempt=await applyCameraControl(track,control,{mode:restore ? control.current_mode:'manual',value:control.current_value});
      cameraAttempts.value=[...cameraAttempts.value.filter(a=>a.id!==control.id),attempt];
    }
    cameraControls.value=inspectCameraControls(track);
    cameraControlMessage.value=cameraAttempts.value.map(a=>`${cameraControls.value.find(c=>c.id===a.id)?.label}: ${a.verified ? (a.requested.mode==='manual' ? 'lock verified':'initial mode restored') : a.error}`).join(' · ');
  }finally{busy.value=false;}
}
async function lockCameraSettings(){await configureCamera();}
async function restoreCameraSettings(){await configureCamera(true);}
const pause = ms => new Promise(resolve=>setTimeout(resolve,ms));
async function countIn(pose='') { for (let i=3;i>0;i--) { if (captureCancelled.value || disposed) throw Error('Capture stopped.'); countdown.value=i; cue(i===3 && pose ? `${pose} Three.` : String(i)); await pause(1000); } countdown.value=0; }
function snap(index, sequence=null) {
  const frame=captureNativeFrame(video.value,stream.value.getVideoTracks()[0].getSettings());
  frame.camera_controls=cameraControlSnapshot(stream.value.getVideoTracks()[0],cameraAttempts.value);
  frame.pending=true;
  frame.capture_sequence=sequence;
  frames.value[index]=frame;
  if (!sequence) cue(capturedFrameCue(index));
}
async function takePhoto(index) { busy.value=true; captureCancelled.value=false; try { await countIn(); if (captureCancelled.value) return; snap(index); await reviewSelected(); } finally { busy.value=false; countdown.value=0; } }
async function startSweep() {
  busy.value=true; captureCancelled.value=false;
  const duration=sweepDuration.value, mode=captureMode.value, sequenceId=crypto.randomUUID();
  try {
    if(mode==='moving_camera_two_pass') {
      let started;
      for(let pass=1;pass<=2;pass++) {
        capturePass.value=pass;
        if(pass===2) {
          sweeping.value=false;lowerPassReady.value=true;
          cue('Pass one complete. Keep head still. Lower camera on subject’s right. Click Start lower pass when ready.');
          const proceed=await new Promise(resolve=>{lowerPassResolve=resolve;});
          if(!proceed || captureCancelled.value || disposed)return;
        }
        await countIn(pass===1 ? 'Eye level. Camera at subject’s left. Head still.' : 'Lower camera at subject’s right. Head still.');
        if(captureCancelled.value || disposed)return;
        if(pass===1)started=performance.now();
        const passStarted=performance.now();sweeping.value=true;
        const complete=await runCaptureSweep({durationSeconds:duration/2,frameCount:30,cancelled:()=>captureCancelled.value||disposed,
          capture:(index,timing)=>{const global=(pass-1)*30+index;selected.value=global;snap(global,{id:sequenceId,protocol:'stationary_head_two_height_camera_arcs_v1',capture_mode:mode,frame_index:global,duration_ms:duration*1000,pass_index:pass,pass_frame_index:index,pass_height:pass===1?'eye_level':'lower',direction:pass===1?'left_to_right':'right_to_left',pass_duration_ms:duration*500,pass_intended_elapsed_ms:timing.intended_elapsed_ms,pass_elapsed_ms:timing.elapsed_ms,intended_elapsed_ms:(pass-1)*duration*500+timing.intended_elapsed_ms,elapsed_ms:performance.now()-started,pass_started_elapsed_ms:passStarted-started,timing_basis:'elapsed_includes_repositioning_and_second_countdown; intended_is_active_capture_only'});},
          countdown:remaining=>{captureRemaining.value=remaining;if(remaining!==0 || pass===2)cue(sweepCues(mode,remaining,duration/2));},
        });
        if(!complete)return;
      }
      selected.value=1;if(!disposed)await reviewSelected();return;
    }
    await countIn(mode==='moving_camera' ? 'Camera at subject’s left. Keep head still.' : 'Right profile.');
    if (captureCancelled.value || disposed) return;
    sweeping.value=true;
    const complete=await runCaptureSweep({ durationSeconds:duration,
      cancelled:()=>captureCancelled.value || disposed,
      capture:(index,timing)=>{ selected.value=index; snap(index,{id:sequenceId,protocol:mode==='moving_camera' ? 'stationary_head_left_to_right_camera_arc_v1' : 'right_to_left_sweep_v1',capture_mode:mode,frame_index:index,duration_ms:duration*1000,...timing}); },
      countdown:remaining=>{ captureRemaining.value=remaining; cue(sweepCues(mode,remaining,duration)); },
    });
    if (complete) { selected.value=1; message.value='Sweep complete. Review and approve all 60 masks.'; }
    if (!disposed) await reviewSelected();
  } catch (error) { captureAudio.cancel(); throw error;
  } finally { busy.value=false; countdown.value=0; sweeping.value=false;capturePass.value=0;lowerPassReady.value=false;lowerPassResolve=null; }
}
function workerSegment(canvas) {
  if (!maskWorker) {
    maskWorker=new Worker('/mediapipe/webcam_mask_worker.js');
    maskWorker.onmessage=({data})=>{ const request=pending.get(data.id); if (!request) return; pending.delete(data.id); data.error ? request.reject(Error(data.error)) : request.resolve(data); };
    maskWorker.onerror=event=>{ for (const request of pending.values()) request.reject(Error(event.message || 'Mask worker failed.')); pending.clear(); };
  }
  return new Promise(async (resolve,reject)=>{ const id=++workerCounter; pending.set(id,{resolve,reject}); try { const image=await createImageBitmap(canvas); maskWorker.postMessage({id,image},[image]); } catch(e) { pending.delete(id); reject(e); } });
}
async function changeReviewFrame(direction) {
  if (busy.value || reviewLoading.value || painting) return;
  const index=Math.max(0,Math.min(60,selected.value+direction));
  if (index===selected.value) return;
  selected.value=index;
  await reviewSelected();
}
function reviewKeydown(event) {
  if (session.value?.status !== 'capturing' || busy.value || reviewLoading.value || painting || event.repeat || event.isComposing || event.ctrlKey || event.metaKey || event.altKey || event.shiftKey || event.defaultPrevented) return;
  if (event.target?.closest?.('input, textarea, select, [contenteditable]:not([contenteditable="false"]), [role="textbox"]')) return;
  if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
    event.preventDefault(); guard(() => changeReviewFrame(event.key === 'ArrowLeft' ? -1 : 1));
  } else if (event.key.toLowerCase() === 'a' && reviewFrame.value) {
    event.preventDefault(); guard(approveMask);
  }
}
async function reviewSelected() {
  const revision=++reviewRevision, index=selected.value;
  reviewLoading.value=true; reviewFrame.value=null; maskPixels=null;
  if (maskCanvas.value) maskCanvas.value.getContext('2d').clearRect(0,0,maskCanvas.value.width,maskCanvas.value.height);
  try {
  let frame=frames.value[index];
  if (!frame && session.value?.captures.some(c=>c.slot===slot(index))) {
    const c=session.value.captures.find(c=>c.slot===slot(index));
    const [imgResponse,maskResponse]=await Promise.all(['image','mask'].map(kind=>fetch(`${API}/sessions/${session.value.id}/captures/${slot(index)}/${kind}`)));
    if (!imgResponse.ok || !maskResponse.ok) throw Error('Could not reload saved capture.');
    const [image,mask]=await Promise.all([createImageBitmap(await imgResponse.blob()),createImageBitmap(await maskResponse.blob())]);
    const canvas=document.createElement('canvas'); canvas.width=image.width; canvas.height=image.height; canvas.getContext('2d').drawImage(image,0,0); image.close();
    const maskC=document.createElement('canvas'); maskC.width=mask.width; maskC.height=mask.height; maskC.getContext('2d').drawImage(mask,0,0); mask.close();
    frame={...c,canvas,mask:maskC,provenance:c.mask_provenance,pending:c.mask_approved!==true};
    if (revision !== reviewRevision || disposed) return;
    frames.value[index]=frame;
  }
  if (!frame) { message.value='Capture this frame first.'; return; }
  if (!frame.mask) {
    message.value='Generating a local person-feature mask…';
    const result=await workerSegment(frame.canvas), small=document.createElement('canvas'); small.width=result.width; small.height=result.height;
    const context=small.getContext('2d'), pixels=context.createImageData(result.width,result.height);
    result.values.forEach((v,i)=>{ pixels.data.set([v,v,v,255],i*4); }); context.putImageData(pixels,0,0);
    const mask=document.createElement('canvas'); mask.width=frame.canvas.width; mask.height=frame.canvas.height;
    const ctx=mask.getContext('2d'); ctx.imageSmoothingEnabled=false; ctx.drawImage(small,0,0,mask.width,mask.height);
    frame.mask=mask; frame.provenance=result.provenance;
  }
  if (revision !== reviewRevision || index!==selected.value || disposed) return;
  measureQuality(frame);
  reviewFrame.value=frame; maskPixels=frame.mask; await nextTick(); renderMask(); message.value='Review this mask, correct ears and neck, then approve.';
  } finally { if (revision === reviewRevision) reviewLoading.value=false; }
}
function renderMask() {
  const frame=reviewFrame.value, canvas=maskCanvas.value; if (!frame || !canvas) return;
  canvas.width=frame.canvas.width; canvas.height=frame.canvas.height;
  const ctx=canvas.getContext('2d'); ctx.drawImage(frame.canvas,0,0);
  const overlay=maskPixels.getContext('2d').getImageData(0,0,canvas.width,canvas.height);
  for (let i=0;i<overlay.data.length;i+=4) { const included=overlay.data[i]; overlay.data.set([0,220,100,included ? 100 : 0],i); }
  const temp=document.createElement('canvas'); temp.width=canvas.width; temp.height=canvas.height; temp.getContext('2d').putImageData(overlay,0,0); ctx.drawImage(temp,0,0);
}
function brushStart(event) { if (!reviewFrame.value || busy.value || reviewLoading.value) return; painting=true; maskCanvas.value.setPointerCapture(event.pointerId); brushMove(event); }
function brushMove(event) {
  if (!painting || !maskPixels) return;
  reviewFrame.value.pending=true;
  reviewFrame.value.maskEdited=true;
  const rect=maskCanvas.value.getBoundingClientRect(), x=(event.clientX-rect.left)*maskPixels.width/rect.width, y=(event.clientY-rect.top)*maskPixels.height/rect.height;
  const ctx=maskPixels.getContext('2d'); ctx.fillStyle=includeBrush.value ? 'white':'black'; ctx.beginPath(); ctx.arc(x,y,brushSize.value*maskPixels.width/rect.width/2,0,2*Math.PI); ctx.fill();
  // Canvas anti-aliasing is thresholded to a binary mask at approval.
  renderMask();
}
function measureQuality(frame) {
  frame.capture_quality=captureQuality(frame.canvas.getContext('2d').getImageData(0,0,frame.canvas.width,frame.canvas.height),frame.mask.getContext('2d').getImageData(0,0,frame.mask.width,frame.mask.height));
}
function brushEnd() { if(painting && reviewFrame.value)measureQuality(reviewFrame.value);painting=false; }
async function approveMask() {
  if (!reviewFrame.value || busy.value || reviewLoading.value || painting || session.value?.status !== 'capturing') return;
  busy.value=true;
  try {
    await saveAcceptedFrame(selected.value, reviewFrame.value, 'individual');
    message.value='Approved capture saved locally.';
    if (selected.value<60) { selected.value++; await reviewSelected(); }
  } finally { busy.value=false; }
}
async function saveAcceptedFrame(index, frame, method) {
  const ctx=frame.mask.getContext('2d'), pixels=ctx.getImageData(0,0,frame.mask.width,frame.mask.height);
  let foreground=false, background=false;
  for (let i=0;i<pixels.data.length;i+=4) {
    const v=pixels.data[i]>=128 ? 255:0; foreground ||= v===255; background ||= v===0;
    pixels.data.set([v,v,v,255],i);
  }
  if (!foreground || !background) throw Error('Mask must include both head pixels and background. Correct this mask before accepting.');
  ctx.putImageData(pixels,0,0);
  measureQuality(frame);
  const edited=!!(frame.maskEdited || frame.provenance?.manual_edits);
  const provenance={...frame.provenance, acceptance_method:method,
    review_status:method==='bulk' ? 'accepted_without_individual_review' : 'individually_accepted',
    manual_edits:edited, correction:edited ? 'manual_brush_edits' : 'none'};
  const [image,mask]=await Promise.all([blobOf(frame.canvas),blobOf(frame.mask)]);
  if (disposed) return;
  await action('capture',{slot:slot(index),image:await base64(image),mask:await base64(mask),sha256:await sha(image),approved:true,mirrored:false,
    timestamp:frame.timestamp,camera_settings:frame.camera_settings,camera_controls:frame.camera_controls || null,mask_provenance:provenance,capture_sequence:frame.capture_sequence || null});
  frame.pending=false; frame.provenance=provenance;
}
async function acceptAllFrames() {
  if (busy.value || reviewLoading.value || painting || session.value?.status !== 'capturing' || session.value?.mask_experiment) return;
  const indices=[...bulkCandidates.value];
  if (!indices.length) return;
  busy.value=true; bulkCancelled.value=false;
  const progress={completed:0,total:indices.length}; bulkProgress.value=progress;
  try {
    for (const index of indices) {
      if (bulkCancelled.value || disposed) break;
      selected.value=index;
      await reviewSelected();
      if (bulkCancelled.value || disposed) break;
      if (!reviewFrame.value) throw Error('Capture is missing.');
      await saveAcceptedFrame(index,reviewFrame.value,'bulk');
      progress.completed++; bulkProgress.value={...progress};
      // Saved frames can be reloaded; release full-resolution canvas memory.
      delete frames.value[index];
    }
    if (!disposed) {
      await reviewSelected();
      const remaining=Array.from({length:61},(_,index)=>index).filter(index=>!approved(index)).length;
      message.value=`${bulkCancelled.value ? 'Stopped accepting' : 'Accepted'}: ${progress.completed} / ${progress.total} frames saved. ${remaining} captures still need to be saved.`;
    }
  } catch (error) {
    throw Error(`Stopped at ${slot(selected.value)} after saving ${progress.completed} / ${progress.total} frames: ${error.message}`);
  } finally { busy.value=false; bulkProgress.value=null; }
}
const surface=computed(()=>session.value?.calibrated?.surface || session.value?.result?.surface);
const frontCamera=computed(()=>{ const r=session.value?.result; return r ? (session.value.calibrated?.cameras || r.cameras)[r.frontal_camera_key] : null; });
const detections=computed(()=>session.value?.calibrated?.projected_points || session.value?.result?.projected_points || []);
const point=computed(()=>detections.value[pointIndex.value]);
function displayPoint(point) { const c=frontCamera.value; const p=c.R.map((r,i)=>r.reduce((s,v,j)=>s+v*point[j],c.t[i])); return [p[0],-p[1],-p[2]]; }
const displayRecord=computed(()=>surface.value ? {...surface.value,mesh:{...surface.value.mesh,vertices:surface.value.mesh.vertices.map(displayPoint)}} : null);
const framing=computed(()=>comparisonOpen.value && comparisonFrame.value ? comparisonFrame.value : displayRecord.value ? surfaceFraming(displayRecord.value.mesh) : {center:[0,0,0],scale:1});
const displayProjection=p=>projectPoint(p,framing.value.center,yaw.value,pitch.value,framing.value.scale*zoom.value);
const projected=computed(()=>displayRecord.value ? projectMesh(displayRecord.value,framing.value.center,yaw.value,pitch.value,framing.value.scale*zoom.value) : []);
const lightingNormals=computed(()=>displayRecord.value ? surfaceVertexNormals(displayRecord.value.mesh) : null);
const faces=computed(()=>displayRecord.value ? shadedSurfaceFaces(displayRecord.value,projected.value,yaw.value,pitch.value,lightAzimuth.value,smoothLighting.value ? lightingNormals.value : null) : []);
const routeMarks=computed(()=>displayRecord.value ? routes.value[routeKind.value].map(a=>displayProjection(attachmentPoint(displayRecord.value,a))) : []);
const graph=computed(()=>displayRecord.value ? buildSurfaceGraph(displayRecord.value) : null);
const routePreview=computed(()=>{
  const controls=routes.value[routeKind.value];
  return displayRecord.value ? controls.slice(1).map((a,i)=>surfacePath(displayRecord.value,graph.value,controls[i],a)) : [];
});
const routeLines=computed(()=>routePreview.value.filter(p=>p.status==='ok').map(path=>path.points.map(p=>{const q=displayProjection(p);return `${q.x},${q.y}`;}).join(' ')));
const selectedMark=computed(()=>{
  if (!point.value?.attachment || !displayRecord.value) return null;
  const p=displayProjection(attachmentPoint(displayRecord.value,point.value.attachment));
  const hit=pickSurface(displayRecord.value,projected.value,p.x,p.y);
  return hit && Math.abs(hit.depth-p.depth)<.001/Math.max(framing.value.scale,1e-9) ? p : null;
});
const wirePath=computed(()=>{
  if (!showWire.value || !surface.value) return '';
  const c=frontCamera.value, vertices=surface.value.mesh.vertices.map(p=>{
    const q=c.R.map((row,i)=>row.reduce((s,v,j)=>s+v*p[j],c.t[i]));
    return q[2]>0 ? [c.fx*q[0]/q[2]+c.cx,c.fy*q[1]/q[2]+c.cy] : null;
  });
  return surface.value.mesh.triangles.filter((_,i)=>i%Math.max(1,Math.ceil(surface.value.mesh.triangles.length/2000))===0).map(f=>{
    const p=f.map(i=>vertices[i]); return p.every(Boolean) ? `M${p[0]}L${p[1]}L${p[2]}Z` : '';
  }).join(' ');
});
async function loadFrontal() { const response=await fetch(`${API}/sessions/${session.value.id}/frontal`); if (!response.ok) throw Error('Could not load undistorted frontal image.'); frontUrl.value=URL.createObjectURL(await response.blob()); }
function surfaceDown(event) {
  if (event.ctrlKey || tapPlacement.value) {
    const rect=viewport.value.getBoundingClientRect(), x=(event.clientX-rect.left)*720/rect.width, y=(event.clientY-rect.top)*480/rect.height;
    const hit=pickSurface(displayRecord.value,projected.value,x,y);
    if (!hit) { error.value='No surface at that point. Missing coverage cannot be traced.'; return; }
    const {depth,...a}=hit; routes.value[routeKind.value].push({...a,label:routeLabel.value}); routeLabel.value='control'; coverageReviewed.value=false;
  } else { drag={x:event.clientX,y:event.clientY,yaw:yaw.value,pitch:pitch.value}; viewport.value.setPointerCapture(event.pointerId); }
}
function surfaceMove(event) { if (drag) { yaw.value=Math.max(-180,Math.min(180,drag.yaw+(event.clientX-drag.x)*.4)); pitch.value=Math.max(-90,Math.min(90,drag.pitch+(event.clientY-drag.y)*.4)); } }
function surfaceUp() { drag=null; }
async function calibrate() { await action('calibrate',{scale_readings_mm:scaleReadings.value,check_readings_mm:checkReadings.value,scale_route:routes.value.scale,check_route:routes.value.check,coverage_reviewed:coverageReviewed.value}); }
async function saveDraft() { await action('draft',{scale_readings_mm:scaleReadings.value,check_readings_mm:checkReadings.value,scale_route:routes.value.scale,check_route:routes.value.check}); message.value='Route draft saved locally.'; }
async function decide(decision) { await action('decisions',{index:pointIndex.value,decision}); }
onMounted(()=>window.addEventListener('keydown',reviewKeydown));
onBeforeUnmount(()=>{ disposed=true; reviewRevision++; window.removeEventListener('keydown',reviewKeydown); clearTimeout(pollTimer); stopCamera(); maskWorker?.terminate(); for(const p of pending.values()) p.reject(Error('Workspace closed.')); pending.clear(); if(frontUrl.value) URL.revokeObjectURL(frontUrl.value); });
</script>

<style scoped>
.camera-preview{position:relative}.framing-guide{position:absolute;inset:8% 25%;border:2px dashed #fff9;border-radius:40%;pointer-events:none}.quality-panel,.camera-settings{padding:12px;background:#f0f6f8;border:1px solid #c9dbe3;margin:12px 0}.quality-panel p{margin:8px 0}.quality-panel ul{padding-left:20px}table{border-collapse:collapse;font-size:13px}td,th{padding:6px;text-align:left;border-bottom:1px solid #ccc}
.pilot{max-width:1400px;margin:auto;padding:24px;color:#203944}.notice{padding:14px;background:#fff4d9;border-left:4px solid #bc7700}.error{color:#a41c12}.toolbar{display:flex;flex-wrap:wrap;align-items:center;gap:12px;margin:16px 0}.columns{display:grid;grid-template-columns:1fr 1fr;gap:24px}.columns>section{min-width:0}button,input,select{font:inherit;padding:8px}button{cursor:pointer}button:disabled{cursor:default}label{display:inline-flex;gap:8px;align-items:center;flex-wrap:wrap;margin:6px}input[type=number]{width:90px}video,svg,.mask-editor{width:100%;display:block;background:#edf2f5}video{min-height:180px}.preview{transform:scaleX(-1)}.mask-editor,svg{touch-action:none;aspect-ratio:3/2}.mask-editor{height:auto;aspect-ratio:auto}svg text{font-size:12px}pre{white-space:pre-wrap;overflow-wrap:anywhere;max-height:400px;overflow:auto;font-size:12px}h2{margin-top:32px}@media(max-width:850px){.columns{grid-template-columns:1fr}}
</style>
