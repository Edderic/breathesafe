// Keep cues local and replace stale speech rather than building a delayed queue.
export function createCaptureAudio(environment, onUnavailable) {
  const synth = environment.speechSynthesis;
  let timer, listener, revision = 0;
  function cancel() {
    revision++;
    if (timer) environment.clearTimeout(timer);
    if (listener) synth?.removeEventListener('voiceschanged', listener);
    timer = listener = null;
    synth?.cancel();
  }
  function speak(text, rate = 1.4) {
    cancel();
    if (!synth || !environment.SpeechSynthesisUtterance) {
      onUnavailable('Spoken cues are unavailable in this browser.'); return;
    }
    const current = revision;
    function attempt(final = false) {
      if (current !== revision) return;
      const voice = synth.getVoices().find(v => v.localService && /^en(?:[-_]|$)/i.test(v.lang));
      if (!voice) {
        if (final) { cancel(); onUnavailable('No local English voice is available. Enable an English system voice, then test audio again.'); }
        return;
      }
      if (timer) environment.clearTimeout(timer);
      if (listener) synth.removeEventListener('voiceschanged', listener);
      timer = listener = null;
      const utterance = new environment.SpeechSynthesisUtterance(text);
      utterance.voice = voice; utterance.lang = voice.lang; utterance.rate = rate;
      utterance.onerror = event => {
        if (current === revision && !['canceled', 'interrupted'].includes(event.error)) onUnavailable('Audio could not play. Check your sound output and try Test audio.');
      };
      synth.speak(utterance);
    }
    listener = () => attempt();
    synth.addEventListener('voiceschanged', listener);
    timer = environment.setTimeout(() => attempt(true), 1500);
    attempt();
  }
  return { speak, cancel };
}

export function capturedFrameCue(index, compact = false) {
  if (index === 0) return 'Frontal captured.';
  const number = index;
  return compact ? `${number}.` : `Frame ${number}.`;
}
