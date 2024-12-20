import numpy as np
import librosa
from typing import Dict
from config.health_params import HEALTH_PARAMETERS, AGE_REFERENCE

class HealthAnalyzer:
    def __init__(self):
        self.params = HEALTH_PARAMETERS
        self.age_ref = AGE_REFERENCE
        
    def analyze_health(self, audio_data: np.ndarray, sr: int, age_group: str = 'adult') -> Dict:
        """Analisi completa dello stato di salute vocale"""
        # Preprocessamento audio
        audio_data = self._preprocess_audio(audio_data, sr)
        
        # Analisi respirazione
        breathing = self._analyze_breathing(audio_data, sr, age_group)
        
        # Analisi qualità vocale
        voice_quality = self._analyze_voice_quality(audio_data, sr)
        
        # Analisi fatica
        fatigue = self._analyze_fatigue(audio_data, sr)
        
        # Analisi ritmo del parlato
        speech_rhythm = self._analyze_speech_rhythm(audio_data, sr)
        
        return {
            "breathing": breathing,
            "voice_quality": voice_quality,
            "fatigue": fatigue,
            "speech_rhythm": speech_rhythm
        }

    def _preprocess_audio(self, audio_data: np.ndarray, sr: int) -> np.ndarray:
        """Preprocessa l'audio per l'analisi"""
        # Normalizzazione
        audio_data = librosa.util.normalize(audio_data)
        
        # Rimozione silenzio
        audio_data, _ = librosa.effects.trim(audio_data, top_db=30)
        
        return audio_data

    def _analyze_breathing(self, audio_data: np.ndarray, sr: int, age_group: str) -> Dict:
        """Analisi dettagliata della respirazione"""
        # Rileva eventi respiratori
        onset_env = librosa.onset.onset_strength(y=audio_data, sr=sr)
        breath_events = librosa.onset.onset_detect(
            onset_envelope=onset_env,
            sr=sr,
            wait=sr//2
        )
        
        # Calcola frequenza respiratoria
        duration = len(audio_data) / sr
        breaths_per_minute = (len(breath_events) * 60) / duration if duration > 0 else 0
        
        # Analizza regolarità respiratoria
        if len(breath_events) > 1:
            breath_intervals = np.diff(breath_events) / sr
            breathing_regularity = 1 - (np.std(breath_intervals) / np.mean(breath_intervals)) if np.mean(breath_intervals) > 0 else 0
        else:
            breathing_regularity = 0
        
        return {
            "rate": float(breaths_per_minute),
            "regularity": float(breathing_regularity)
        }

    def _analyze_voice_quality(self, audio_data: np.ndarray, sr: int) -> Dict:
        """Analisi della qualità vocale"""
        # Calcola pitch e features correlate
        pitches, magnitudes = librosa.piptrack(y=audio_data, sr=sr)
        pitches_valid = pitches[magnitudes > np.max(magnitudes) * 0.1] if magnitudes.size > 0 else np.array([])
        
        # Jitter (variabilità del pitch)
        if len(pitches_valid) > 1:
            jitter = np.std(np.diff(pitches_valid)) / np.mean(pitches_valid) if np.mean(pitches_valid) > 0 else 0
        else:
            jitter = 0
            
        # Shimmer (variabilità dell'ampiezza)
        rms = librosa.feature.rms(y=audio_data)[0]
        shimmer = np.std(rms) / np.mean(rms) if np.mean(rms) > 0 else 0
        
        # Calcola HNR (Harmonic-to-Noise Ratio) in modo corretto
        S = np.abs(librosa.stft(audio_data))
        freqs = librosa.fft_frequencies(sr=sr)
        freq_mask = freqs <= 2000
        
        # Calcola la media dell'energia per le bande armoniche e rumore
        harmonic_energy = np.mean(S[freq_mask, :], axis=0)
        noise_energy = np.mean(S[~freq_mask, :], axis=0)
        
        # Calcola HNR medio
        hnr = np.mean(harmonic_energy) / np.mean(noise_energy) if np.mean(noise_energy) > 0 else 0
        
        # Calcolo strain vocale
        strain = (jitter + shimmer) / 2
        
        # Quality score
        quality_score = 1 - np.mean([jitter, shimmer, strain])
        
        return {
            "quality_score": float(quality_score),
            "hoarseness": float(1 - hnr if hnr < 1 else 0),
            "strain": float(strain)
        }

    def _analyze_fatigue(self, audio_data: np.ndarray, sr: int) -> Dict:
        """Analisi dei segni di fatica vocale"""
        # Dividi audio in segmenti temporali
        segment_duration = 3  # secondi
        samples_per_segment = sr * segment_duration
        segments = [audio_data[i:i + samples_per_segment] 
                   for i in range(0, len(audio_data), samples_per_segment)
                   if len(audio_data[i:i + samples_per_segment]) >= sr]
        
        if not segments:
            return {
                "fatigue_score": 0.0,
                "timeline": [0.0]
            }
            
        energy_trend = []
        
        for segment in segments:
            rms = librosa.feature.rms(y=segment)[0]
            energy_trend.append(float(np.mean(rms)))
        
        # Normalizza energy_trend
        if energy_trend:
            max_energy = max(energy_trend)
            energy_trend = [e/max_energy if max_energy > 0 else 0 for e in energy_trend]
            
        # Calcola fatigue score
        fatigue_score = 1 - (energy_trend[-1] / energy_trend[0]) if energy_trend and energy_trend[0] > 0 else 0
        
        return {
            "fatigue_score": float(fatigue_score),
            "timeline": energy_trend
        }

    def _analyze_speech_rhythm(self, audio_data: np.ndarray, sr: int) -> Dict:
        """Analisi del ritmo del parlato"""
        # Onset detection per il ritmo
        onset_env = librosa.onset.onset_strength(y=audio_data, sr=sr)
        tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
        
        # Calcola regolarità del ritmo
        if len(beats) > 1:
            beat_intervals = np.diff(beats)
            rhythm_regularity = 1 - (np.std(beat_intervals) / np.mean(beat_intervals)) if np.mean(beat_intervals) > 0 else 0
        else:
            rhythm_regularity = 0
            
        # Calcola fluidità basata sulla regolarità degli onset
        fluency = rhythm_regularity
        
        # Calcola stabilità come combinazione di tempo e regolarità
        stability = (rhythm_regularity + (1 - abs(tempo - 120)/120)) / 2
        
        return {
            "fluency": float(fluency),
            "stability": float(stability)
        }