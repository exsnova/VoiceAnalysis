# analyzers/emotional_analyzer.py
import numpy as np
import librosa
import soundfile as sf
from typing import Dict, List, Tuple
from pathlib import Path
import json
from scipy.stats import zscore
from config.emotional_params import EMOTIONAL_PARAMETERS, REFERENCE_TEXTS

class EmotionalAnalyzer:
    def __init__(self):
        self.params = EMOTIONAL_PARAMETERS
        self.reference_texts = REFERENCE_TEXTS
        
    def analyze_emotions(self, audio_data: np.ndarray, sr: int, text_type: str = None) -> Dict:
        """Analisi semplificata dello stato emotivo dalla voce"""
        try:
            # Ensure audio is 1D float32
            audio_data = np.asarray(audio_data, dtype=np.float32)
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
            
            # Basic checks
            if len(audio_data) < sr * 0.5:  # Minimum 0.5 seconds
                return self._get_default_results()
                
            # Extract energy features
            S = np.abs(librosa.stft(audio_data))
            rms = librosa.feature.rms(S=S)[0]
            energy = float(np.mean(rms))  # Convert to Python scalar
            
            # Calculate tempo
            onset_env = librosa.onset.onset_strength(y=audio_data, sr=sr)
            tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
            tempo = float(tempo)  # Convert to Python scalar
            
            # Calculate pitch features safely
            pitches, magnitudes = librosa.piptrack(y=audio_data, sr=sr)
            pitch_values = pitches[magnitudes > np.max(magnitudes) * 0.1]
            if len(pitch_values) > 0:
                pitch_mean = float(np.mean(pitch_values))
                pitch_std = float(np.std(pitch_values))
            else:
                pitch_mean = 0.0
                pitch_std = 0.0
            
            # Prepare emotion scores
            emotion_scores = {
                'gioia': 0.0,
                'tristezza': 0.0,
                'rabbia': 0.0,
                'ansia': 0.0,
                'neutrale': 0.2
            }
            
            # Simple rule-based scoring with explicit float conversions
            if energy > 0.1:
                emotion_scores['gioia'] = float(energy)
                emotion_scores['rabbia'] = float(energy * 0.5)
            else:
                emotion_scores['tristezza'] = float(0.1 - energy)
                
            if pitch_std > 0:
                emotion_scores['gioia'] += float(min(pitch_std / 100, 0.3))
                emotion_scores['ansia'] += float(min(pitch_std / 200, 0.2))
            
            if tempo > 120:
                emotion_scores['ansia'] += float(min((tempo - 120) / 100, 0.3))
                emotion_scores['rabbia'] += float(min((tempo - 120) / 150, 0.2))
            else:
                emotion_scores['tristezza'] += float(min((120 - tempo) / 100, 0.3))
            
            # Normalize scores
            total = sum(emotion_scores.values())
            if total > 0:
                emotion_scores = {k: float(v/total) for k, v in emotion_scores.items()}
            else:
                emotion_scores = {k: 0.2 for k in emotion_scores}
            
            # Get speech rate
            speech_rate = self._get_speech_rate(tempo)
            pitch_variability = self._get_pitch_variability(pitch_std)
            voice_energy = self._get_energy_level(energy)
            
            # Prepare results with explicit float conversions
            results = {
                'dominant_emotion': max(emotion_scores.items(), key=lambda x: x[1])[0],
                'emotion_probabilities': emotion_scores,
                'speech_rate': speech_rate,
                'pitch_variability': pitch_variability,
                'voice_energy': voice_energy,
                'speech_pauses': 'normal',
                'rhythm_stability': 'stable',
                'speech_rate_value': float(min(tempo/200, 1.0)),
                'pitch_variability_value': float(min(pitch_std/100, 1.0)) if pitch_std > 0 else 0.5,
                'voice_energy_value': float(min(energy*10, 1.0)),
                'speech_pauses_value': 0.5,
                'rhythm_stability_value': 0.5
            }
            
            return results
            
        except Exception as e:
            print(f"Error in analyze_emotions: {str(e)}")
            return self._get_default_results()
      
    def _get_speech_rate(self, tempo: float) -> str:
        """Determina la velocità del parlato in base al tempo"""
        if tempo > 170:
            return 'fast'
        elif tempo < 130:
            return 'slow'
        return 'normal'
        
    def _get_pitch_variability(self, std: float) -> str:
        """Determina la variabilità del pitch in base alla deviazione standard"""
        if std > 50:
            return 'high'
        elif std > 20:
            return 'moderate'
        return 'monotone'
        
    def _get_energy_level(self, energy: float) -> str:
        """Determina il livello di energia vocale"""
        if energy > 0.1:
            return 'high'
        elif energy > 0.05:
            return 'medium'
        return 'low'
    
    def _get_default_results(self) -> Dict:
        """Risultati di default quando l'analisi non è possibile"""
        return {
            'dominant_emotion': 'neutrale',
            'emotion_probabilities': {
                'gioia': 0.2,
                'tristezza': 0.2,
                'rabbia': 0.2,
                'ansia': 0.2,
                'neutrale': 0.2
            },
            'speech_rate': 'normal',
            'pitch_variability': 'moderate',
            'voice_energy': 'medium',
            'speech_pauses': 'normal',
            'rhythm_stability': 'stable',
            'speech_rate_value': 0.5,
            'pitch_variability_value': 0.5,
            'voice_energy_value': 0.5,
            'speech_pauses_value': 0.5,
            'rhythm_stability_value': 0.5
        }