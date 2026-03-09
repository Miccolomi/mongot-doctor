with open("mongot_monitor.py", "r") as f:
    text = f.read()

replacements = {
    "Rilevato:": "Detected:",
    "Tutti i pod hanno spazio libero > 125% della dimensione usata": "All pods have free space > 125% of the used size",
    "Indice di sicurezza peggihours:": "Worst safety index:",
    "peggihours": "worst",
    "mhours than": "more than",
    "enonre": "ensure",
    "isones": "issues",
    "isone": "issue",
    "I CRD gestiti dall\\'Operator K8s sono in stato corretto (Running).": "CRDs managed by the K8s Operator are in a correct state (Running).",
    "L\\'Operator usa un tag esatto immutabile:": "The Operator uses an exact immutable tag:",
    "Finestra Oplog Ampia e Sicura": "Ample and Safe Oplog Window",
    "Finestra totale stimata:": "Estimated total window:",
    "Lag attuale massimo:": "Max current lag:",
    "Stato CRD MongoDB Search": "MongoDB Search CRD Status",
    "Performance Storage Class (PVC)": "Storage Class Performance (PVC)",
    "Versionamento K8s Operator (MCK)": "K8s Operator Versioning (MCK)",
    "Rischio OOMKilled & MMap": "OOMKilled & MMap Risk",
    "🔥 SRE Predittivo: Oplog Window Exceeded": "🔥 Predictive SRE: Oplog Window Exceeded",
    "Stato:": "Status:"
}

for k, v in replacements.items():
    text = text.replace(k, v)

with open("mongot_monitor.py", "w") as f:
    f.write(text)
