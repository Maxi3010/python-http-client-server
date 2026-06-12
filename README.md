# Networking HTTP Client and Server

Ein kompaktes Python-Projekt, das die Grundlagen von TCP, HTTP/1.1 und TLS
ohne externe Bibliotheken demonstriert. Es enthaelt einen kleinen lokalen
Webserver sowie einen interaktiven Kommandozeilen-Browser, der Webseiten
abruft, HTTP-Header darstellt und gefundene Links zur Navigation anbietet.

## Funktionen

- HTTP- und HTTPS-Verbindungen ueber TCP-Sockets
- TLS mit Zertifikatspruefung ueber Pythons Standard-SSL-Kontext
- Vollstaendiges Einlesen von Antworten beliebiger Groesse
- Unterstuetzung fuer `Transfer-Encoding: chunked`
- Parsing von Statuszeile, Headern und HTML-Links
- Navigation ueber relative und absolute Links
- Lokaler, nebenlaeufiger HTTP-Testserver
- Schutz des Servers vor Directory-Traversal-Angriffen
- Automatisierte Unit- und Integrationstests
- Keine externen Python-Abhaengigkeiten

## Projektstruktur

```text
.
|-- Maximilian.py          # Interaktiver HTTP-Kommandozeilen-Browser
|-- connection_helper.py   # Wiederverwendbare TCP-/TLS-Verbindung
|-- webserver.py           # Lokaler statischer HTTP-Server
|-- example.html           # Beispielseite mit zwei Links
|-- link1.html
|-- link2.html
|-- tests/
|   `-- test_networking.py
|-- LICENSE
`-- README.md
```

## Voraussetzungen

- Python 3.10 oder neuer
- Freier lokaler TCP-Port, standardmaessig `8080`

Das Projekt verwendet ausschliesslich die Python-Standardbibliothek. Eine
Installation zusaetzlicher Pakete ist nicht erforderlich.

## Schnellstart

Repository klonen und in das Projektverzeichnis wechseln:

```bash
git clone <repository-url>
cd Networking_Maximilian_Knapp
```

Den lokalen Webserver starten:

```bash
python webserver.py
```

Der Server ist anschliessend unter
[`http://127.0.0.1:8080/`](http://127.0.0.1:8080/) erreichbar.

In einem zweiten Terminal den Kommandozeilen-Browser starten:

```bash
python Maximilian.py
```

Als URL kann fuer den lokalen Test beispielsweise Folgendes eingegeben werden:

```text
http://127.0.0.1:8080/example
```

Der Client zeigt Status und Header sowie eine nummerierte Linkliste an. Mit
der jeweiligen Nummer wird ein Link geoeffnet, mit `0` endet das Programm.

## Serveroptionen

Host, Port und Dokumentenverzeichnis koennen angepasst werden:

```bash
python webserver.py --host 127.0.0.1 --port 9000 --directory .
```

Alle Optionen:

```bash
python webserver.py --help
```

## Tests

Die Tests lassen sich ohne weitere Installation ausfuehren:

```bash
python -m unittest discover -s tests -v
```

Sie pruefen unter anderem:

- HTTP-Status-, Header- und Body-Parsing
- Dekodierung von Chunked Transfer Encoding
- Extraktion von Linktext und Linkziel
- Zusammenspiel von Client und lokalem Server
- Fehlerantworten und Schutz vor Pfadmanipulation

## Technische Hinweise

Der Client sendet bewusst rohe HTTP/1.1-Anfragen, um den Netzwerkablauf
nachvollziehbar zu halten. Er ist ein Lernprojekt und kein Ersatz fuer eine
vollstaendige HTTP-Bibliothek wie `urllib3` oder `requests`.

Der Server ist fuer lokale Entwicklung und Demonstrationen vorgesehen. Fuer
einen produktiven Internetbetrieb sollte ein etablierter Application- oder
Webserver mit zusaetzlicher Absicherung eingesetzt werden.

## Lizenz

Der aus dem bereitgestellten Ausgangscode uebernommene Anteil steht unter der
BSD-3-Clause-Lizenz. Details befinden sich in [LICENSE](LICENSE).
