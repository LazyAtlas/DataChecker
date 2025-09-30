# DataChecker

**DataChecker** è un'applicazione desktop per Windows che consente di analizzare file CSV in modo rapido e intuitivo.
Grazie all'interfaccia grafica e ai filtri automatici, è pensata per semplificare il lavoro con dati tabellari, anche per utenti non tecnici.

## Funzionalità principali

- Caricamento di file CSV con rilevamento automatico del separatore
- Riconoscimento intelligente delle colonne (Modello, Parte, Colore, Annullato)
- Filtri testuali e checkbox per visualizzare solo i dati rilevanti
- Visualizzazione tabellare con possibilità di mostrare/nascondere colonne
- Interfaccia grafica scura, compatta e reattiva

## Requisiti

- Windows 10 o superiore
- Visual C++ Redistributable (per l'eseguibile)
- Python 3.11 (solo se si vuole compilare da sorgente)
- Librerie Python:
  - `pandas`

## Installazione

### Eseguibile

Se vuoi usare direttamente il programma:
1. Scarica `DataChecker.exe` dalla sezione [Releases](https://github.com/LazyAtlas/DataChecker/releases)
2. Avvia il file: non richiede installazione

### Da sorgente

1. Installa Python 3.11
2. Installa le dipendenze:

 Da powershell >  pip install pandas
               > python data_checker.py

## Compilazione

Per generare l'eseguibile `.exe`, usa lo script `build_and_sign.bat`.  
Assicurati di modificare i percorsi di `pyinstaller.exe` e `signtool.exe` secondo il tuo ambiente.

## Autore

Antonio – [LazyAtlas](https://github.com/LazyAtlas)


P.S la versione è stabile e funzionante ma in alcuni casi è possibile che troppi dati possano causare errori (soprattutto se le colonne non sono uguali tra i file diversi)
Nel qual caso è possibile si verifichi l'errore NAN che potrete correggere effettuando "RESET" e impostando il separatore su (|). 
               
