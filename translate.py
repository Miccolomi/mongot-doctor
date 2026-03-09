import sys

with open("mongot_monitor.py", "r") as f:
    text = f.read()

replacements = {
    # Backend errors
    "Lettura namespaces per CRDs": "Reading namespaces for CRDs",
    "MongoDBSearch CRD nel ns": "MongoDBSearch CRD in ns",
    "Pod list per Operator nel ns": "Pod list for Operator in ns",
    "Deployment list per Operator nel ns": "Deployment list for Operator in ns",
    "Errore discovery pod K8s": "K8s pod discovery error",
    "Discovery PVCs": "Discovery PVCs",
    "Discovery Services": "Discovery Services",
    "Lettura serverStatus": "Reading serverStatus",
    "Errore Oplog": "Oplog Error",
    "Lettura Oplog per lag": "Reading Oplog for lag",
    "Lettura database/collections": "Reading database/collections",
    "Lettura system.profile per profiler": "Reading system.profile for profiler",
    "Scrape fallito via proxy per": "Proxy scrape failed for",
    "Prometheus scrape fallito per": "Prometheus scrape failed for",
    "K8s API non disponibile": "K8s API not available",
    "Nessun errore rilevato in questo arco temporale.": "No errors detected in this timeframe.",
    "Raccoglie tutti gli errori di questo ciclo": "Collects all errors of this cycle",
    
    # UI Header & Select
    "Seleziona tempo refresh": "Select refresh time",
    "Nessun Auto-Refresh": "No Auto-Refresh",
    
    # Logs UI
    "▶ Mostra Live Logs Operator": "▶ Show Live Operator Logs",
    "▶ Mostra Live Logs del Pod": "▶ Show Live Pod Logs",
    "▼ Nascondi Logs Operator": "▼ Hide Operator Logs",
    "▼ Nascondi Logs": "▼ Hide Logs",
    "Caricamento in corso...": "Loading...",
    "Nessun log disponibile.": "No logs available.",
    "Scarica (.txt)": "Download (.txt)",
    "Filtra Log di": "Filter Logs of",
    "Tutti i Livelli": "All Levels",
    "Solo Errori": "Errors Only",
    "Avvia Download": "Start Download",
    "Annulla": "Cancel",
    "Errore:": "Error:",
    
    # Diagnostics & Status
    "Il backend Python ha rilevato dei fallimenti di rete o di permessi. Alcune rotte o metriche potrebbero mancare:": "The Python backend detected network or permission failures. Some routes or metrics may be missing:",
    "Nessun Errore Rilevato": "No Errors Detected",
    "Tutte le connessioni (K8s API, MongoDB Auth, Prometheus Scraping) sono attive e funzionanti.": "All connections (K8s API, MongoDB Auth, Prometheus Scraping) are active and functional.",
    
    # Advisor
    "Spazio Disco (Regola del 125%)": "Disk Space (125% Rule)",
    "Sul pod": "On pod",
    "lo spazio libero": "the free space",
    "è INFERIORE al 125% della dimensione indici attuale": "is LESS than 125% of current index size",
    "richiesti). Rischio blocco!": "required). Risk of stall!",
    "Lo spazio libero su tutti i pod è consono": "Free space on all pods is adequate",
    
    "Consolidamento Indici": "Index Consolidation",
    "Rilevati indici multipli sulle collection:": "Multiple indexes detected on collections:",
    "Azione: Unificali in un singolo indice dinamico.": "Action: Consolidate into a single dynamic index.",
    "Nessuna collection possiede più di un indice di ricerca. Ottimo.": "No collection has more than one search index. Optimal.",
    
    "Collo di Bottiglia I/O & Replica": "I/O Bottleneck & Replica",
    "Nessun collo di bottiglia I/O e Replica Lag rilevato sui dischi k8s.": "No I/O bottleneck and Replica Lag detected on K8s disks.",
    "Coda disco ALTA": "HIGH disk queue",
    "e Oplog Lag in crescita": "and Oplog Lag increasing",
    "Azione: Scala classe Storage / aumenta IOPS PVC.": "Action: Scale Storage class / increase PVC IOPS.",
    
    "Rapporto CPU / QPS": "CPU / QPS Ratio",
    "Allocati": "Allocated",
    "Core per": "Cores for",
    "QPS totali. Rapporto entro le linee guida.": "total QPS. Ratio within guidelines.",
    "Sottodimensionato!": "Under-provisioned!",
    "Il rapporto CPU": "The CPU ratio",
    "raccomandato": "recommended",
    "Azione: Aumenta i Limits CPU nel CRD.": "Action: Increase CPU Limits in the CRD.",
    
    "OOMKilled & Eventi K8s": "OOMKilled & K8s Events",
    "Nessun evento OOMKilled rilevato. Limiti heap entro parametri sicuri per allocare RAM ai file di Sistema (Mmap).": "No OOMKilled events detected. Heap limits within safe parameters for allocating RAM to System files (Mmap).",
    "Rilevati eventi OOMKilled recenti nei pod mongot! Aumentare Limits RAM o ridurre MaxCapacityMB o CacheSize.": "Recent OOMKilled events detected in mongot pods! Increase RAM Limits or reduce MaxCapacityMB or CacheSize.",
    
    "StorageClass Lenta": "Slow StorageClass",
    "Nessuna StorageClass palesemente lenta rilevata per i nodi Search.": "No obviously slow StorageClass detected for Search nodes.",
    "Trovati PVC associati a StorageClass lente o di default": "Found PVCs associated with slow or default StorageClasses",
    "MongoDB Search richiede dischi NVMe/SSD ad alte prestazioni (es. gp3, io2) per l'I/O Lucene.": "MongoDB Search requires high-performance NVMe/SSD disks (e.g. gp3, io2) for Lucene I/O.",
    
    "Versionamento K8s / Operator": "K8s / Operator Versioning",
    "Ambiente aggiornato o versionamento corretto. K8s:": "Environment up to date or correct versioning. K8s:",
    
    "Sync Pipeline Analyzer": "Sync Pipeline Analyzer",
    "Stato del Change Stream e tempi di sincronizzazione verso Search": "Change Stream Status and Sync Times towards Search",
    "Lettura Oplog": "Oplog Read",
    "Finestra disponibile": "Available window",
    "Elaborazione mongot": "mongot Processing",
    "Batch in ram": "Batches in RAM",
    "Indicizzazione Lucene": "Lucene Indexing",
    "Merge su disco": "Merge on disk",
    "Nessun dato o lag irreperibile": "No data or untraceable lag",
    
    "Attenzione: Mongot in forte ritardo di Replication": "Warning: Mongot heavily lagging in Replication",
    "Se continua, Mongot perderà il Resume Token e crasherà (Initial Sync obbligata). Aumenta la dimensione dell'Oplog di MongoDB o riavvia mongot!": "If this continues, Mongot will lose the Resume Token and crash (forced Initial Sync). Increase MongoDB Oplog size or restart mongot!",
    "Tracciamento Perfetto": "Perfect Tracking",
    "Il nodo mongot è perfettamente allineato con le scritture MongoDB.": "The mongot node is perfectly aligned with MongoDB writes.",
    
    "Indici Trovati": "Indexes Found",
    "CRDs Trovati": "CRDs Found",
    "Documenti (Ricerca)": "Documents (Search)",
    "Ricerche": "Searches",
    "Indici di Ricerca": "Search Indexes",
    "Tempo raccolta": "Collection time",
    "Connesso": "Connected",
    "Non disponibile": "Not available",
    "Aggiornato:": "Updated:",
    "Pod mongot": "mongot Pods",
    "Tutte le connessioni (K8s API, MongoDB Auth, Prometheus Scraping) sono attive e funzionanti.": "All connections (K8s API, MongoDB Auth, Prometheus Scraping) are active and functioning.",
    
    # Remaining ones
    "ore": "hours",
    "ore ": "hours ",
    "Intervallo (sec)": "Interval (sec)",
    "Nessun Auto-Refresh": "No Auto-Refresh"
}

# Apply sort length descending, so we don't accidentally replace sub-words of longer strings
for k in sorted(replacements.keys(), key=len, reverse=True):
    text = text.replace(k, replacements[k])

with open("mongot_monitor.py", "w") as f:
    f.write(text)

print("Translations applied!")
