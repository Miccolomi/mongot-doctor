import sys

with open("mongot_monitor.py", "r") as f:
    text = f.read()

replacements = {
    # Fix broken replacements from previous step
    "Errhours": "Error",
    "cpu_millichourss": "cpu_millicores",
    "mhourss": "mores",
    "cRicerche": "cSearches", # if Ricerca broke it

    # K8s warnings
    "Ultimi Eventi K8s:": "Latest K8s Events:",
    
    # Discovery Panel
    "Scarica Log (.txt)": "Download Log (.txt)",
    "Indici Init": "Init Indexes",
    
    # Prometheus failures
    "Nessuna metrica Prometheus trovata. I fallback (Rete, Proxy, Exec) hanno fallito.": "No Prometheus metrics found. Fallbacks (Net, Proxy, Exec) failed.",
    
    # Indexing Pipeline
    "Indici in catalogo": "Indexes in catalog",
    "CS updates applicati": "Applied CS updates",
    "Batch in corso": "Batches in progress",
    "Failures imprevisti": "Unexpected failures",
    "Initial sync attivi": "Active initial syncs",
    
    # System Disk
    "Disco (data path)": "Disk (data path)",
    "Usato": "Used",
    "Totale": "Total",
    "Usata": "Used", # per la RAM/Heap
    
    # Lucene Merges
    "Merge attivi": "Active merges",
    "Docs in merge": "Merging docs",
    "Merge totali": "Total merges",
    "Merge scartati": "Discarded merges",
    
    # System Memory & Network
    "Sistema &amp; Rete": "System &amp; Network",
    "RAM usata": "RAM used",
    "Swap usata": "Swap used",
    
    # Killer Feature: Sync Pipeline Analyzer
    "Soglia allarme Merge:": "Merge alarm threshold:",
    "modifica": "edit",
    "Inserisci nuova soglia Merge in sec:": "Enter new Merge threshold in sec:",
    
    "ritardo": "delay",
    
    "Origine dati.<br>Registra ogni modifica al database.": "Data origin.<br>Records every database modification.",
    "Lettura in tempo reale.<br>Cattura i dati dall'Oplog.": "Real-time reading.<br>Captures data from the Oplog.",
    "Consumo JVM.<br>Ritardi se la CPU o RAM saturano.": "JVM usage.<br>Delays if CPU or RAM saturate.",
    "LENTO:": "SLOW:",
    "Merge: processo in background di deframmentazione su disco. Anche se sotto sforzo (diventa rosso), i documenti potrebbero essere già ricercabili nei segmenti RAM temporanei. Non indica necessariamente un lag lato utente.": "Merge: background disk defragmentation. Even under pressure (red), docs may be searchable in RAM segments. Doesn't necessarily mean user-facing lag.",
    "Scrittura su disco.<br>Fonde i dati nell'indice Lucene.": "Disk write.<br>Merges data into the Lucene index.",
    "Lag Search Sync: tempo effettivo tra la scrittura su MongoDB e la disponibilità della ricerca. Vede anche i dati nei segmenti RAM prima del merge su disco!": "Search Sync Lag: actual time between MongoDB write and search availability. Also spans RAM segments before disk merge!",
    "Indice Atlas Search.<br>Tempi di risposta al client.": "Atlas Search index.<br>Client response times.",
    
    # Tables & Empty states
    "Nessun pod mongot trovato": "No mongot pod found",
    "Nessun indice search trovato nel database": "No search index found in the database",
    "<tr><th>Nome</th><th>Collection</th><th>Tipo</th><th>Stato</th><th>Queryable</th><th>Documenti</th></tr>": "<tr><th>Name</th><th>Collection</th><th>Type</th><th>Status</th><th>Queryable</th><th>Documents</th></tr>",
    
    # JS fetch & popup prompts
    "Quanti log vuoi scaricare per": "How many logs do you want to download for",
    "\\nOpzioni: 10m (ultimi 10 min), 1h (ultima ora), 24h, all (tutto)\\n": "\\nOptions: 10m (last 10 mins), 1h (last hour), 24h, all\\n",
    "Nessun log scaricabile al momento": "No downloadable logs currently",
    "Inizio scaricamento log...": "Starting log download...",
    "Rete / Connessione fallita:": "Network / Connection failed:",
    "Impossibile contattare il server Python (": "Unable to contact the Python server (",
    
    "su": "on", # "su 10GB Heap"
    "Tot": "Total",

    "Nessun dato o lag irreperibile": "No data or untraceable lag"
}

# Apply sort length descending
for k in sorted(replacements.keys(), key=len, reverse=True):
    text = text.replace(k, replacements[k])

# Just to be safe with "su" isolated words:
text = text.replace(">su ", ">on ")
text = text.replace(" su ", " on ")

with open("mongot_monitor.py", "w") as f:
    f.write(text)

print("Second pass translations applied!")
