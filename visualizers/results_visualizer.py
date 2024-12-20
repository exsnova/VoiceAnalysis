# visualizers/results_visualizer.py
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict, List

class ResultsVisualizer:
    def __init__(self):
        self.emotion_colors = {
            "gioia": "#FFD700",
            "tristezza": "#4169E1",
            "rabbia": "#FF4500",
            "ansia": "#9932CC",
            "neutrale": "#90EE90",
            "depressione": "#483D8B",
            "eccitazione": "#FF69B4"
        }
        
        self.health_colors = {
            "healthy": "#90EE90",
            "mild_concern": "#FFD700",
            "moderate_concern": "#FFA500",
            "severe_concern": "#FF4500"
        }

    def visualize_emotional_analysis(self, results: Dict):
        """Crea visualizzazioni per l'analisi emotiva"""
        st.subheader("📊 Analisi Emotiva")
        
        # Radar chart dei parametri emotivi
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        # Prepara i dati per il radar chart
        categories = ['Velocità', 'Variabilità Pitch', 'Energia', 'Pause', 'Ritmo']
        values = [
            results['speech_rate_value'],
            results['pitch_variability_value'],
            results['voice_energy_value'],
            results['speech_pauses_value'],
            results['rhythm_stability_value']
        ]
        
        # Normalizza i valori
        values = [v/max(values) for v in values]
        angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False)
        values = np.concatenate((values, [values[0]]))  # Chiudi il poligono
        angles = np.concatenate((angles, [angles[0]]))  # Chiudi il poligono
        
        ax.plot(angles, values)
        ax.fill(angles, values, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        st.pyplot(fig)
        
        # Grafico a barre delle emozioni rilevate
        st.subheader("🎭 Distribuzione Emozioni")
        emotions_data = results['emotion_probabilities']
        
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(emotions_data.keys(), emotions_data.values())
        
        # Colora le barre
        for bar, emotion in zip(bars, emotions_data.keys()):
            bar.set_color(self.emotion_colors.get(emotion, "#808080"))
            
        plt.xticks(rotation=45)
        plt.ylabel("Probabilità")
        st.pyplot(fig)
        
        # Report testuale
        st.subheader("📝 Interpretazione Emotiva")
        self._generate_emotional_report(results)

    def visualize_health_analysis(self, results: Dict):
        """Crea visualizzazioni per l'analisi della salute vocale"""
        st.subheader("🏥 Analisi della Salute Vocale")
        
        # Heatmap dei parametri vitali
        vital_params = {
            'Respirazione': results['breathing']['rate'],
            'Qualità Vocale': results['voice_quality']['quality_score'],
            'Fatica': results['fatigue']['fatigue_score'],
            'Stress Vocale': results['voice_quality']['strain'],
            'Ritmo': results['speech_rhythm']['fluency']
        }
        
        # Convert to numpy array and reshape for heatmap
        values = np.array(list(vital_params.values())).reshape(1, -1)
        
        fig, ax = plt.subplots(figsize=(12, 4))
        sns.heatmap(values,
                xticklabels=list(vital_params.keys()),
                yticklabels=['Valori'],
                cmap='RdYlGn',
                center=0.5,
                ax=ax)
        st.pyplot(fig)
        
        # Timeline della fatica
        st.subheader("📉 Andamento Fatica nel Tempo")
        fatigue_data = results['fatigue']['timeline']
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(fatigue_data, marker='o')
        ax.set_ylabel("Livello di Fatica")
        ax.set_xlabel("Tempo (segmenti)")
        st.pyplot(fig)
        
        # Indicatori di salute
        cols = st.columns(4)
        with cols[0]:
            self._create_gauge_chart("Respirazione", 
                                results['breathing']['rate'],
                                min_val=10, max_val=30)
        with cols[1]:
            self._create_gauge_chart("Qualità Vocale", 
                                results['voice_quality']['quality_score'],
                                min_val=0, max_val=1)
        with cols[2]:
            self._create_gauge_chart("Stabilità", 
                                results['speech_rhythm'].get('stability', 0.5),
                                min_val=0, max_val=1)
        with cols[3]:
            # Usiamo l'ultimo valore della timeline come energy_level
            energy_level = results['fatigue']['timeline'][-1] if results['fatigue']['timeline'] else 0.5
            self._create_gauge_chart("Energia", 
                                energy_level,
                                min_val=0, max_val=1)
        
        # Report testuale
        st.subheader("📋 Valutazione Clinica")
        self._generate_health_report(results)

    def _create_gauge_chart(self, title: str, value: float, min_val: float, max_val: float):
        """Crea un grafico a gauge per indicatori di salute"""
        normalized_value = (value - min_val) / (max_val - min_val)
        color = self._get_health_color(normalized_value)
        
        fig = plt.figure(figsize=(4, 3))
        ax = fig.add_subplot(111, projection='polar')
        
        # Crea l'arco del gauge
        theta = np.linspace(0, np.pi, 100)
        r = [1] * 100
        ax.plot(theta, r, color='lightgray', lw=2)
        
        # Aggiungi il valore
        theta_value = normalized_value * np.pi
        ax.plot([0, theta_value], [0, 1], color=color, lw=3)
        
        ax.set_title(title)
        ax.set_rticks([])
        ax.set_xticks([])
        st.pyplot(fig)

    def _get_health_color(self, value: float) -> str:
        """Determina il colore in base al valore di salute"""
        if value >= 0.8:
            return self.health_colors['healthy']
        elif value >= 0.6:
            return self.health_colors['mild_concern']
        elif value >= 0.4:
            return self.health_colors['moderate_concern']
        else:
            return self.health_colors['severe_concern']

    def _interpret_breathing_rate(self, rate: float) -> str:
        """Interpreta la frequenza respiratoria"""
        if rate < 12:
            return "sotto la norma, possibile bradipnea"
        elif rate <= 20:
            return "nella norma"
        else:
            return "elevata, possibile tachipnea"

    def _interpret_breathing_regularity(self, irregularity: float) -> str:
        """Interpreta la regolarità del respiro"""
        if irregularity < 0.2:
            return "respiro molto regolare"
        elif irregularity < 0.4:
            return "respiro moderatamente regolare"
        else:
            return "respiro irregolare"

    def _interpret_voice_quality(self, quality: Dict) -> str:
        """Interpreta la qualità vocale"""
        quality_score = quality.get('quality_score', 0)
        hoarseness = quality.get('hoarseness', 0)
        strain = quality.get('strain', 0)
        
        issues = []
        if quality_score < 0.5:
            issues.append("qualità vocale compromessa")
        if hoarseness > 0.3:
            issues.append("presenza di raucedine")
        if strain > 0.4:
            issues.append("significativo sforzo vocale")
            
        if not issues:
            return "Qualità vocale nella norma"
        return f"Rilevate le seguenti problematiche: {', '.join(issues)}"

    def _interpret_fatigue(self, fatigue: Dict) -> str:
        """Interpreta i segni di fatica"""
        fatigue_score = fatigue.get('fatigue_score', 0)
        energy_trend = fatigue.get('timeline', [])
        
        if fatigue_score < 0.3:
            base_msg = "Livello di fatica contenuto"
        elif fatigue_score < 0.6:
            base_msg = "Moderati segni di affaticamento"
        else:
            base_msg = "Significativi segni di affaticamento"
            
        if len(energy_trend) > 1:
            trend_diff = energy_trend[-1] - energy_trend[0]
            if trend_diff < -0.2:
                trend_msg = ", con progressivo calo dell'energia"
            elif trend_diff > 0.2:
                trend_msg = ", con recupero di energia nel tempo"
            else:
                trend_msg = ", con livelli di energia stabili"
        else:
            trend_msg = ""
            
        return base_msg + trend_msg

    def _interpret_pauses(self, pauses: str) -> str:
        """Interpreta il pattern delle pause"""
        interpretations = {
            "frequent": "mostra una tendenza a pause frequenti",
            "normal": "presenta una distribuzione naturale delle pause",
            "rare": "mostra poche pause, possibile segnale di ansia o urgenza"
        }
        return interpretations.get(pauses, "presenta un pattern di pause non definito")

    def _generate_emotional_report(self, results: Dict):
        """Genera un report descrittivo dell'analisi emotiva"""
        dominant_emotion = results['dominant_emotion']
        confidence = results['emotion_probabilities'][dominant_emotion]
        
        suggestions = self._generate_emotional_suggestions(results)
        
        report = [
            f"**Emozione Dominante**: {dominant_emotion} (confidenza: {confidence:.1%})",
            "\n**Analisi Dettagliata**:",
            f"- La velocità del parlato è {results['speech_rate']}, "
            f"indicando un possibile stato di {self._interpret_speech_rate(results['speech_rate'])}",
            f"- La variabilità del pitch è {results['pitch_variability']}, "
            f"suggerendo {self._interpret_pitch_variability(results['pitch_variability'])}",
            f"- L'energia vocale {self._interpret_voice_energy(results['voice_energy'])}",
            f"- Il pattern delle pause {self._interpret_pauses(results['speech_pauses'])}",
            "\n**Suggerimenti**:",
        ]
        
        # Aggiungiamo i suggerimenti solo se non sono None
        if suggestions:
            report.append(suggestions)
        else:
            report.append("- Mantieni un respiro regolare e un tono controllato")
        
        st.markdown("\n".join(report))

    def _generate_health_report(self, results: Dict):
        """Genera un report descrittivo dell'analisi della salute"""
        breathing = results['breathing']
        voice_quality = results['voice_quality']
        fatigue = results['fatigue']
        
        report = [
            "**Valutazione Respiratoria**:",
            f"- Frequenza respiratoria: {breathing['rate']:.1f} respiri/min "
            f"({self._interpret_breathing_rate(breathing['rate'])})",
            f"- Regolarità: {self._interpret_breathing_regularity(breathing.get('irregularity', 0))}",
            "\n**Qualità Vocale**:",
            f"- {self._interpret_voice_quality(voice_quality)}",
            "\n**Indicatori di Fatica**:",
            f"- {self._interpret_fatigue(fatigue)}",
            "\n**Raccomandazioni**:",
            self._generate_health_recommendations(results)
        ]
        
        st.markdown("\n".join(report))

    def _generate_health_recommendations(self, results: Dict) -> str:
        """Genera raccomandazioni per la salute vocale"""
        recommendations = []
        
        if results['breathing']['rate'] > 20:
            recommendations.append("- Pratica esercizi di respirazione diaframmatica")
            
        if results['voice_quality'].get('hoarseness', 0) > 0.3:
            recommendations.append("- Riposa la voce e mantieni una buona idratazione")
            
        if results['fatigue'].get('fatigue_score', 0) > 0.3:
            recommendations.append("- Considera di fare più pause durante il parlato")
            
        if not recommendations:
            recommendations.append("- Mantieni le tue buone abitudini vocali")
            
        return "\n".join(recommendations)

    def _interpret_speech_rate(self, rate: str) -> str:
        """Interpreta la velocità del parlato"""
        interpretations = {
            "slow": "riflessione o stanchezza",
            "normal": "tranquillità e controllo",
            "fast": "eccitazione o agitazione"
        }
        return interpretations.get(rate, "stato non definito")

    def _interpret_pitch_variability(self, var: str) -> str:
        """Interpreta la variabilità del pitch"""
        interpretations = {
            "monotone": "possibile distacco emotivo o affaticamento",
            "moderate": "un buon equilibrio emotivo",
            "high": "forte coinvolgimento emotivo"
        }
        return interpretations.get(var, "variabilità non definita")

    def _interpret_voice_energy(self, energy: str) -> str:
        """Interpreta il livello di energia vocale"""
        interpretations = {
            "low": "indica possibile stanchezza o tristezza",
            "medium": "mostra un livello di energia equilibrato",
            "high": "suggerisce forte intensità emotiva"
        }
        return interpretations.get(energy, "energia non definita")

    def _generate_emotional_suggestions(self, results: Dict) -> str:
        """Genera suggerimenti basati sull'analisi emotiva"""
        dominant_emotion = results['dominant_emotion']
        suggestions = {
            "ansia": ["Prova esercizi di respirazione profonda per calmare l'ansia",
                    "Parla più lentamente e fai pause regolari",
                    "Concentrati su una cosa alla volta mentre parli"],
            
            "tristezza": ["Cerca di mantenere un tono più vivace quando possibile",
                        "Fai piccole pause per recuperare energia",
                        "Concentrati su aspetti positivi durante il discorso"],
            
            "rabbia": ["Fai pause più frequenti per mantenere il controllo",
                    "Cerca di moderare l'intensità della voce",
                    "Respira profondamente prima di parlare"],
            
            "gioia": ["Mantieni questo ottimo stato emotivo",
                    "Usa questa energia positiva per coinvolgere gli altri",
                    "Ricorda di fare comunque pause regolari"],
            
            "neutrale": ["Prova ad aggiungere più colore emotivo al tuo parlato",
                        "Varia il tono per mantenere l'attenzione",
                        "Usa la gestualità per enfatizzare il discorso"],
            
            "depressione": ["Cerca di aumentare gradualmente l'energia vocale",
                        "Fai pause regolari per recuperare",
                        "Mantieni frasi brevi e concise"],
            
            "eccitazione": ["Mantieni un ritmo controllato nel parlato",
                        "Fai pause regolari per organizzare il discorso",
                        "Modula l'intensità della voce quando necessario"]
        }    