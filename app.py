import streamlit as st
from audio_recorder_streamlit import audio_recorder
import numpy as np
from pydub import AudioSegment
import io
from analyzers.emotional_analyzer import EmotionalAnalyzer
from analyzers.health_analyzer import HealthAnalyzer
from visualizers.results_visualizer import ResultsVisualizer
from config.emotional_params import REFERENCE_TEXTS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_audio_to_numpy(audio_bytes):
    """Convert audio bytes to numpy array with proper format"""
    try:
        # Converti da bytes a AudioSegment
        audio = AudioSegment.from_wav(io.BytesIO(audio_bytes))
        
        # Ottieni i parametri dell'audio
        channels = audio.channels
        sample_width = audio.sample_width
        
        # Converti in array numpy
        samples = np.array(audio.get_array_of_samples())
        
        # Se stereo, prendi la media dei canali
        if channels == 2:
            samples = samples.reshape((-1, 2))
            samples = np.mean(samples, axis=1)
        
        # Normalizza a float32 tra -1 e 1
        if sample_width == 1:  # 8-bit
            samples = samples / float(2**7)
        elif sample_width == 2:  # 16-bit
            samples = samples / float(2**15)
        elif sample_width == 4:  # 32-bit
            samples = samples / float(2**31)
            
        # Assicurati che sia float32 mono
        samples = samples.astype(np.float32)
        
        # Assicurati che sia un array 1D
        if len(samples.shape) > 1:
            samples = samples.flatten()
            
        return samples
        
    except Exception as e:
        logger.error(f"Error converting audio: {e}", exc_info=True)
        raise e

def main():
    st.title("🎤 Analizzatore Vocale Avanzato")
    st.write("Registra la tua voce per un'analisi completa emotiva e della salute vocale")
    
    # Analysis mode selection
    analysis_mode = st.radio(
        "Scegli la modalità di analisi",
        ["Lettura Brano di Riferimento", "Parlato Libero"],
        horizontal=True
    )
    
    if analysis_mode == "Lettura Brano di Riferimento":
        selected_text = st.selectbox(
            "Scegli il brano da leggere",
            list(REFERENCE_TEXTS.keys()),
            format_func=lambda x: f"Brano {x.title()}"
        )
        st.info(f"**Leggi il seguente testo:**\n\n{REFERENCE_TEXTS[selected_text]}")
    
    # Advanced options
    with st.expander("⚙️ Opzioni Avanzate"):
        age_group = st.selectbox(
            "Fascia d'età",
            ["child", "adult", "elderly"],
            format_func=lambda x: {
                "child": "Bambino (< 12 anni)",
                "adult": "Adulto (12-65 anni)",
                "elderly": "Anziano (> 65 anni)"
            }[x]
        )
    
    # Recording section
    st.markdown("### 🎙️ Registrazione")
    st.info("Premi il bottone per iniziare a registrare. Premi di nuovo per fermare la registrazione.")
    
    # Audio recorder
    audio_bytes = audio_recorder(pause_threshold=2.0, sample_rate=16000)
    
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        
        try:
            audio_data = convert_audio_to_numpy(audio_bytes)
            
            st.markdown("### 📊 Analisi")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔍 Analisi Emotiva"):
                    try:
                        with st.spinner("Analizzo le emozioni..."):
                            if len(audio_data) < 8000:  # Meno di 0.5 secondi a 16kHz
                                st.warning("⚠️ La registrazione è troppo breve per un'analisi accurata")
                            
                            emotional_analyzer = EmotionalAnalyzer()
                            emotional_results = emotional_analyzer.analyze_emotions(
                                audio_data,
                                sr=16000,
                                text_type=selected_text if analysis_mode == "Lettura Brano di Riferimento" else None
                            )
                            
                            if emotional_results:
                                visualizer = ResultsVisualizer()
                                visualizer.visualize_emotional_analysis(emotional_results)
                            else:
                                st.error("Non sono riuscito ad analizzare le emozioni. Prova a registrare una frase più lunga.")
                            
                    except Exception as e:
                        st.error(f"Errore durante l'analisi emotiva: {str(e)}")
                        logger.error(f"Emotional analysis error: {e}", exc_info=True)
            
            with col2:
                if st.button("🏥 Analisi Salute"):
                    try:
                        with st.spinner("Analizzo i parametri vocali..."):
                            health_analyzer = HealthAnalyzer()
                            # Crea un dict vuoto di base per i risultati
                            base_results = {
                                'breathing': {'rate': 0, 'regularity': 0},
                                'voice_quality': {'quality_score': 0, 'hoarseness': 0, 'strain': 0},
                                'fatigue': {'fatigue_score': 0, 'timeline': [0]},
                                'speech_rhythm': {'fluency': 0}
                            }
                            
                            # Esegui l'analisi
                            health_results = health_analyzer.analyze_health(
                                audio_data,
                                sr=16000,
                                age_group=age_group
                            )
                            
                            # Unisci i risultati base con quelli ottenuti
                            health_results = {**base_results, **health_results}
                            
                            visualizer = ResultsVisualizer()
                            visualizer.visualize_health_analysis(health_results)
                    except Exception as e:
                        st.error(f"Errore durante l'analisi della salute: {str(e)}")
                        logger.error(f"Health analysis error: {e}", exc_info=True)
                        
        except Exception as e:
            st.error(f"Errore durante l'analisi dell'audio: {str(e)}")
            logger.error(f"Audio analysis error: {e}", exc_info=True)

if __name__ == "__main__":
    main()