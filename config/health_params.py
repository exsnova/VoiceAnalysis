# config/health_params.py
HEALTH_PARAMETERS = {
    # Analisi della respirazione
    "breathing": {
        "normal": {"range": (12, 20), "desc": "Respiri al minuto"},
        "rapid": {"range": (20, 30), "desc": "Possibile affanno/ansia"},
        "shallow": {"threshold": 0.3, "desc": "Respiro superficiale"},
        "irregular": {"variance_threshold": 0.4, "desc": "Irregolarità respiratoria"}
    },
    
    # Qualità vocale
    "voice_quality": {
        "hoarseness": {
            "jitter_threshold": 0.015,
            "shimmer_threshold": 0.05,
            "desc": "Raucedine/Irritazione"
        },
        "nasality": {
            "nasal_formant_threshold": 1000,
            "desc": "Congestione nasale"
        },
        "tremor": {
            "frequency_modulation": 0.1,
            "desc": "Tremore vocale"
        }
    },
    
    # Indicatori di fatica
    "fatigue": {
        "pitch_stability": {"threshold": 0.2, "desc": "Stabilità del tono"},
        "energy_decline": {"threshold": 0.3, "desc": "Calo energia nel tempo"},
        "articulation": {"threshold": 0.7, "desc": "Chiarezza articolazione"}
    },
    
    # Indicatori di febbre/malessere
    "illness": {
        "vocal_strain": {"threshold": 0.4, "desc": "Sforzo vocale"},
        "pitch_lowering": {"threshold": -20, "desc": "Abbassamento tono"},
        "breath_support": {"threshold": 0.6, "desc": "Supporto respiratorio"}
    },
    
    # Analisi del ritmo parlato
    "speech_rhythm": {
        "fluency": {"threshold": 0.8, "desc": "Fluidità del parlato"},
        "pause_pattern": {"threshold": 0.3, "desc": "Pattern delle pause"},
        "speed_consistency": {"variance_threshold": 0.2, "desc": "Consistenza velocità"}
    }
}

# Valori di riferimento per età
AGE_REFERENCE = {
    "child": {"pitch_range": (200, 400), "breathing_range": (20, 30)},
    "adult": {"pitch_range": (85, 255), "breathing_range": (12, 20)},
    "elderly": {"pitch_range": (75, 245), "breathing_range": (12, 18)}
}