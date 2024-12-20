# config/emotional_params.py
EMOTIONAL_PARAMETERS = {
    # Velocità del parlato
    "speech_rate": {
        "slow": {"range": (100, 130), "emotion": ["tristezza", "depressione"]},
        "normal": {"range": (130, 170), "emotion": ["neutrale"]},
        "fast": {"range": (170, 200), "emotion": ["eccitazione", "ansia"]}
    },
    
    # Variabilità del pitch
    "pitch_variability": {
        "monotone": {"threshold": 10, "emotion": ["depressione", "apatia"]},
        "moderate": {"threshold": 30, "emotion": ["calma", "neutrale"]},
        "high": {"threshold": 50, "emotion": ["gioia", "eccitazione"]}
    },
    
    # Energia vocale
    "voice_energy": {
        "low": {"threshold": 0.1, "emotion": ["tristezza", "stanchezza"]},
        "medium": {"threshold": 0.3, "emotion": ["neutrale"]},
        "high": {"threshold": 0.5, "emotion": ["rabbia", "gioia"]}
    },
    
    # Pause nel parlato
    "speech_pauses": {
        "frequent": {"threshold": 0.3, "emotion": ["ansia", "incertezza"]},
        "normal": {"threshold": 0.2, "emotion": ["neutrale"]},
        "rare": {"threshold": 0.1, "emotion": ["eccitazione", "urgenza"]}
    },
    
    # Stabilità ritmica
    "rhythm_stability": {
        "unstable": {"threshold": 0.4, "emotion": ["stress", "agitazione"]},
        "stable": {"threshold": 0.2, "emotion": ["calma", "controllo"]}
    }
}

# Testi di riferimento per calibrazione
REFERENCE_TEXTS = {
    "neutrale": "Il sole splende alto nel cielo azzurro.",
    "gioia": "Che meravigliosa giornata! Sono così felice di essere qui!",
    "tristezza": "Mi manca tanto quel periodo della mia vita...",
    "rabbia": "Non posso credere che sia successo di nuovo!",
    "ansia": "Non so se ce la farò, ci sono così tante cose da fare..."
}

