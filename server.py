from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from pydantic import BaseModel
from typing import List, Optional
import os
import json
import uuid
from datetime import datetime
import re

app = FastAPI(title="iPad-Hilfe API", description="Modern FAQ API for iPad Help App")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
try:
    MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = MongoClient(MONGO_URL)
    db = client.ipad_hilfe
    faq_collection = db.faq_items
    preferences_collection = db.user_preferences
    print(f"Connected to MongoDB at: {MONGO_URL}")
except Exception as e:
    print(f"MongoDB connection error: {e}")

# Pydantic models
class FAQItem(BaseModel):
    id: str
    question: str
    answer: str
    category: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class UserPreferences(BaseModel):
    user_id: str
    has_seen_intro: bool = False
    favorites: List[str] = []
    theme: str = "light"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class CategoryInfo(BaseModel):
    name: str
    icon: str
    description: str
    count: int

# FAQ Data - Complete German content from Swift app
FAQ_DATA = [
    {
        "id": "8e678d11-9107-4ecf-ad81-34f9ec663d94",
        "question": "Wie erstelle ich eine Apple-ID nur für die Schule?",
        "answer": "1. Gehe zu 'Einstellungen' > 'Bei Apple-ID anmelden'\n2. Tippe auf 'Neue Apple-ID erstellen'\n3. Verwende deine Schul-E-Mail-Adresse\n4. Wähle ein sicheres Passwort (mindestens 8 Zeichen)\n5. Bestätige deine E-Mail-Adresse über den Link\n6. Aktiviere die Zwei-Faktor-Authentifizierung für zusätzliche Sicherheit\n\nTipp: Verwende diese Apple-ID nur für schulische Zwecke und teile deine Anmeldedaten niemals mit anderen.",
        "category": "Erste Schritte"
    },
    {
        "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
        "question": "Wie verbinde ich mich mit dem Heim-WLAN?",
        "answer": "1. Öffne 'Einstellungen' > 'WLAN'\n2. Stelle sicher, dass WLAN aktiviert ist\n3. Wähle dein Heimnetzwerk aus der Liste\n4. Gib das WLAN-Passwort ein\n5. Tippe auf 'Verbinden'\n6. Ein Häkchen zeigt erfolgreiche Verbindung an\n\nBei Problemen: Setze die Netzwerkeinstellungen zurück unter 'Einstellungen' > 'Allgemein' > 'iPad übertragen/zurücksetzen' > 'Zurücksetzen' > 'Netzwerkeinstellungen'.",
        "category": "Erste Schritte"
    },
    {
        "id": "b2c3d4e5-f6g7-8901-2345-678901bcdefg",
        "question": "Wie mache ich Screenshots und Bildschirmaufnahmen?",
        "answer": "**Screenshot:**\n1. Drücke gleichzeitig die Ein-/Aus-Taste und die Lauter-Taste\n2. Das Bild erscheint kurz in der Ecke\n3. Tippe darauf für Bearbeitungsoptionen oder wische weg zum Speichern\n\n**Bildschirmaufnahme:**\n1. Füge 'Bildschirmaufnahme' zum Kontrollzentrum hinzu: Einstellungen > Kontrollzentrum\n2. Wische vom rechten oberen Rand nach unten\n3. Tippe den runden Aufnahme-Button\n4. Warte 3 Sekunden, dann beginnt die Aufnahme\n5. Tippe die rote Statusleiste zum Stoppen",
        "category": "Erste Schritte"
    },
    {
        "id": "693ab7b3-621b-4a09-b991-f6e8f278bcf2",
        "question": "Wie nutze ich GoodNotes für Arbeitsblätter?",
        "answer": "1. **PDF importieren:** Tippe '+' > 'Importieren' > wähle dein Arbeitsblatt\n2. **Schreibwerkzeuge:** Nutze Stift, Marker oder Text-Tool aus der Symbolleiste\n3. **Handschrift:** Schreibe direkt auf das PDF mit dem Apple Pencil\n4. **Text hinzufügen:** Tippe 'T' und tippe an gewünschte Stelle\n5. **Lasso-Tool:** Markiere und verschiebe Inhalte\n6. **Speichern:** Automatisch gespeichert, exportiere über Teilen-Button\n\nTipp: Erstelle separate Ordner für jedes Fach und nutze aussagekräftige Namen für deine Notizen.",
        "category": "Apps & Tools"
    },
    {
        "id": "c3d4e5f6-g7h8-9012-3456-789012cdefgh",
        "question": "Wie organisiere ich Seiten in Pages?",
        "answer": "**Neue Seite einfügen:**\n1. Tippe '+' oben links\n2. Wähle 'Seitenumbruch' oder Vorlage\n\n**Seiten verwalten:**\n1. Tippe das Seiten-Symbol (links oben)\n2. Ziehe Seiten zum Umordnen\n3. Tippe Seite an und wähle 'Löschen' falls nötig\n\n**Layout anpassen:**\n1. Tippe 'Format' (Pinsel-Symbol)\n2. Wähle 'Layout' für Ränder und Spalten\n3. Nutze 'Absatz' für Textformatierung\n\nTipp: Verwende Vorlagen für einheitliches Design und erstelle eigene Vorlagen für wiederkehrende Dokumente.",
        "category": "Apps & Tools"
    },
    {
        "id": "d4e5f6g7-h8i9-0123-4567-890123defghi",
        "question": "Wie speichere ich PDF-Dateien in iCloud Drive?",
        "answer": "**Aus Safari:**\n1. Öffne PDF im Browser\n2. Tippe Teilen-Button (Pfeil nach oben)\n3. Wähle 'In Dateien sichern'\n4. Navigiere zu iCloud Drive\n5. Wähle Ordner oder erstelle neuen\n\n**Aus E-Mail:**\n1. Tippe auf PDF-Anhang\n2. Tippe Teilen-Button\n3. Wähle 'In Dateien sichern' > iCloud Drive\n\n**Aus anderen Apps:**\nNutze immer den Teilen-Button und wähle 'In Dateien sichern'\n\nTipp: Erstelle eine logische Ordnerstruktur wie 'Schule/Fach/Jahr' für bessere Organisation.",
        "category": "Apps & Tools"
    },
    {
        "id": "e5f6g7h8-i9j0-1234-5678-901234efghij",
        "question": "Wie nutze ich mebis effektiv auf dem iPad?",
        "answer": "**Zugriff:**\n1. Öffne Safari und gehe zu mebis.bayern.de\n2. Melde dich mit deinen Schuldaten an\n3. Füge mebis zum Homescreen hinzu: Teilen > 'Zum Home-Bildschirm'\n\n**Navigation:**\n- Tippe 'Kurse' für deine Fächer\n- Nutze 'Mitteilungen' für Nachrichten\n- Unter 'Dateien' findest du alle Materialien\n\n**Dateien herunterladen:**\n1. Tippe auf gewünschte Datei\n2. Wähle 'In Dateien sichern'\n3. Speichere in iCloud Drive für offline Zugriff\n\nTipp: Lade wichtige Materialien herunter, bevor du das WLAN verlässt.",
        "category": "Apps & Tools"
    },
    {
        "id": "cffbbca4-47fc-448a-9be7-eeb48338f29c",
        "question": "Mein iPad reagiert nicht – was kann ich tun?",
        "answer": "**Schritt für Schritt:**\n1. **Warten:** Manchmal braucht das iPad einen Moment\n2. **Neustart erzwingen:** Drücke Ein-/Aus-Taste + Lauter-Taste gleichzeitig 10 Sekunden\n3. **Akku prüfen:** Lade dein iPad mindestens 30 Minuten\n4. **Apps schließen:** Doppeltippe Home-Button, wische Apps nach oben\n5. **Speicher prüfen:** Einstellungen > Allgemein > iPad-Speicher\n\n**Falls nichts hilft:**\n- Kontaktiere deine Lehrkraft\n- Notiere Fehlermeldungen\n- Sichere wichtige Daten regelmäßig\n\nWichtiger Hinweis: Setze dein iPad nie ohne Rücksprache zurück!",
        "category": "Troubleshooting"
    },
    {
        "id": "f6g7h8i9-j0k1-2345-6789-012345fghijk",
        "question": "Warum sehe ich keine Internetverbindung trotz WLAN-Symbol?",
        "answer": "**Problemlösung:**\n1. **WLAN-Status prüfen:** Einstellungen > WLAN - steht 'Verbunden'?\n2. **Router-Verbindung testen:** Versuche eine Webseite zu öffnen\n3. **WLAN aus-/einschalten:** Kontrollzentrum > WLAN-Symbol tippen\n4. **Netzwerk vergessen:** Einstellungen > WLAN > (i) neben Netzwerk > 'Netzwerk ignorieren'\n5. **Neu verbinden:** Netzwerk auswählen, Passwort eingeben\n6. **DNS ändern:** WLAN-Einstellungen > DNS konfigurieren > Manuell > 8.8.8.8 hinzufügen\n\n**In der Schule:**\nInformiere die IT oder deine Lehrkraft - manchmal sind Schulnetzwerke überlastet.",
        "category": "Troubleshooting"
    },
    {
        "id": "g7h8i9j0-k1l2-3456-7890-123456ghijkl",
        "question": "Wie lösche ich eine App, die nicht richtig funktioniert?",
        "answer": "**App löschen:**\n1. **Home-Bildschirm:** Halte App-Symbol gedrückt bis Menü erscheint\n2. Tippe 'App entfernen' > 'App löschen'\n3. Bestätige mit 'Löschen'\n\n**Alternative über Einstellungen:**\n1. Einstellungen > Allgemein > iPad-Speicher\n2. Wähle problematische App\n3. Tippe 'App löschen'\n\n**App neu installieren:**\n1. App Store öffnen\n2. Suche nach der App\n3. Tippe 'Laden' (Cloud-Symbol bei bereits gekauften Apps)\n\n**Wichtig:** Schulapps nur nach Rücksprache löschen! Deine Daten könnten verloren gehen.",
        "category": "Troubleshooting"
    },
    {
        "id": "h8i9j0k1-l2m3-4567-8901-234567hijklm",
        "question": "App stürzt ständig ab - was hilft?",
        "answer": "**Sofortmaßnahmen:**\n1. **App vollständig schließen:** Doppeltippe Home-Button, wische App nach oben\n2. **iPad neustarten:** Ein-/Aus-Taste + Lauter-Taste 10 Sekunden\n3. **App-Update prüfen:** App Store > Profil > Updates\n4. **Speicher freigeben:** Einstellungen > Allgemein > iPad-Speicher\n\n**Weitere Lösungen:**\n- App löschen und neu installieren\n- iOS-Update prüfen: Einstellungen > Allgemein > Software-Update\n- Hintergrund-App-Aktualisierung ausschalten\n\n**Bei Schulapps:** Informiere sofort deine Lehrkraft, da möglicherweise ein bekanntes Problem vorliegt.",
        "category": "Troubleshooting"
    },
    {
        "id": "i9j0k1l2-m3n4-5678-9012-345678ijklmn",
        "question": "Wie strukturiere ich Ordner in der Dateien-App?",
        "answer": "**Ordnerstruktur erstellen:**\n1. Öffne 'Dateien'-App\n2. Wähle 'iCloud Drive'\n3. Tippe '+' (oben rechts) > 'Neuer Ordner'\n4. Benenne Ordner logisch (z.B. 'Schule_2025')\n\n**Empfohlene Struktur:**\n```\nSchule_2025/\n├── Deutsch/\n│   ├── Hausaufgaben/\n│   └── Klassenarbeiten/\n├── Mathematik/\n├── Englisch/\n└── Projekte/\n```\n\n**Dateien organisieren:**\n- Halte Datei gedrückt > 'Bewegen'\n- Ziehe Dateien zwischen Ordnern\n- Nutze aussagekräftige Namen mit Datum\n\nTipp: Erstelle einen 'Aktuell'-Ordner für laufende Aufgaben.",
        "category": "Dateien & Organisation"
    },
    {
        "id": "j0k1l2m3-n4o5-6789-0123-456789jklmno",
        "question": "Wie verschiebe ich Dokumente in iCloud Drive?",
        "answer": "**Einzelne Dateien verschieben:**\n1. Öffne 'Dateien'-App\n2. Navigiere zur gewünschten Datei\n3. Halte Datei gedrückt > 'Bewegen'\n4. Navigiere zum Zielordner\n5. Tippe 'Bewegen'\n\n**Mehrere Dateien gleichzeitig:**\n1. Tippe 'Auswählen' (oben rechts)\n2. Markiere gewünschte Dateien\n3. Tippe 'Bewegen' (unten)\n4. Wähle Zielordner\n\n**Von anderen Apps:**\n- Nutze Teilen-Button > 'In Dateien sichern'\n- Wähle iCloud Drive als Ziel\n\nTipp: Überprüfe regelmäßig deinen iCloud-Speicher unter Einstellungen > Apple-ID > iCloud.",
        "category": "Dateien & Organisation"
    },
    {
        "id": "k1l2m3n4-o5p6-7890-1234-567890klmnop",
        "question": "Wie sichere ich wichtige Dateien offline?",
        "answer": "**Offline-Verfügbarkeit aktivieren:**\n1. Öffne 'Dateien'-App\n2. Navigiere zur gewünschten Datei\n3. Halte Datei gedrückt\n4. Wähle 'Offline verfügbar machen'\n5. Cloud-Symbol wird durch Pfeil-nach-unten ersetzt\n\n**Ganze Ordner offline:**\n1. Wähle Ordner\n2. Tippe Teilen-Button\n3. 'Offline verfügbar machen'\n\n**Speicherplatz verwalten:**\n- Einstellungen > Allgemein > iPad-Speicher\n- Lösche alte Offline-Dateien regelmäßig\n\n**Wichtig für Klassenarbeiten:** Sichere alle relevanten Materialien vor Prüfungen offline, falls das WLAN ausfällt.",
        "category": "Dateien & Organisation"
    },
    {
        "id": "l2m3n4o5-p6q7-8901-2345-678901lmnopq",
        "question": "Wie teile ich ein Dokument mit meiner Lehrerin?",
        "answer": "**Via mebis:**\n1. Öffne mebis in Safari\n2. Gehe zu entsprechendem Kurs\n3. Suche 'Aufgabe abgeben' oder ähnlich\n4. Tippe 'Datei hinzufügen'\n5. Wähle dein Dokument aus Dateien-App\n\n**Via E-Mail:**\n1. Öffne dein Dokument\n2. Tippe Teilen-Button\n3. Wähle 'Mail'\n4. Gib Lehrkraft-E-Mail ein\n5. Aussagekräftiger Betreff und höfliche Nachricht\n\n**Via AirDrop (falls erlaubt):**\n1. Aktiviere AirDrop im Kontrollzentrum\n2. Teilen-Button > AirDrop\n3. Wähle Lehrkraft aus Liste\n\nTipp: Benenne Dateien eindeutig: 'Nachname_Fach_Aufgabe_Datum.pdf'",
        "category": "Kommunikation & Zusammenarbeit"
    },
    {
        "id": "m3n4o5p6-q7r8-9012-3456-789012mnopqr",
        "question": "Wie nutze ich AirDrop in der Schule?",
        "answer": "**AirDrop aktivieren:**\n1. Wische vom rechten oberen Rand nach unten (Kontrollzentrum)\n2. Halte Netzwerk-Bereich gedrückt\n3. Tippe AirDrop\n4. Wähle 'Für jeden' oder 'Nur Kontakte'\n\n**Dateien senden:**\n1. Öffne zu teilende Datei\n2. Tippe Teilen-Button\n3. Wähle AirDrop\n4. Tippe auf Empfänger-Gerät\n\n**Dateien empfangen:**\n1. AirDrop muss aktiviert sein\n2. Benachrichtigung erscheint\n3. Tippe 'Akzeptieren'\n4. Datei wird in entsprechender App geöffnet\n\n**Schulregeln beachten:** Frage deine Lehrkraft, wann AirDrop erlaubt ist. Deaktiviere es nach Gebrauch für mehr Privatsphäre.",
        "category": "Kommunikation & Zusammenarbeit"
    },
    {
        "id": "n4o5p6q7-r8s9-0123-4567-890123nopqrs",
        "question": "Wie arbeite ich gemeinsam in einem Pages-Dokument?",
        "answer": "**Dokument für Zusammenarbeit freigeben:**\n1. Öffne dein Pages-Dokument\n2. Tippe '...' (oben rechts) > 'Personen hinzufügen'\n3. Wähle 'Link teilen' oder 'Personen einladen'\n4. Setze Berechtigungen: 'Kann bearbeiten' oder 'Kann anzeigen'\n5. Teile Link via Mail, Nachrichten oder mebis\n\n**Während der Zusammenarbeit:**\n- Verschiedene Farben zeigen andere Bearbeiter\n- Kommentare hinzufügen: Text markieren > 'Kommentar'\n- Änderungen werden automatisch gesynchronisiert\n\n**Tipps für Teamwork:**\n- Teilt Abschnitte unter euch auf\n- Nutzt Kommentare für Feedback\n- Speichert regelmäßig eine Kopie\n\nWichtig: Alle Beteiligten brauchen Apple-ID und Internetverbindung.",
        "category": "Kommunikation & Zusammenarbeit"
    },
    {
        "id": "o5p6q7r8-s9t0-1234-5678-901234opqrst",
        "question": "Wie richte ich eine Codesperre ein?",
        "answer": "**Code einrichten:**\n1. Einstellungen > 'Face ID & Code' (oder Touch ID & Code)\n2. Tippe 'Code aktivieren'\n3. Gib 6-stelligen Code ein\n4. Bestätige Code durch erneute Eingabe\n\n**Sicherheitsoptionen:**\n- 'Face ID verwenden für': iPad entsperren aktivieren\n- 'Code anfordern': 'Sofort' wählen\n- 'Daten löschen': Nach 10 Fehlversuchen (Optional)\n\n**Starken Code wählen:**\n- Keine Geburtsdaten oder 123456\n- Nicht dieselben Ziffern wiederholen\n- Code niemandem verraten\n\n**Face ID konfigurieren:**\n1. 'Face ID konfigurieren'\n2. Halte iPad 25-35 cm entfernt\n3. Bewege Kopf für kompletten Kreis\n\nWichtig: Merke dir deinen Code - ohne ihn ist dein iPad unbrauchbar!",
        "category": "Sicherheit & Verantwortung"
    },
    {
        "id": "p6q7r8s9-t0u1-2345-6789-012345pqrstu",
        "question": "Was tun, wenn ich mein iPad verliere?",
        "answer": "**Sofortmaßnahmen:**\n1. **'Wo ist?' verwenden:**\n   - Gehe zu icloud.com/find\n   - Melde dich mit deiner Apple-ID an\n   - Wähle dein iPad aus der Geräteliste\n\n2. **iPad orten:**\n   - Siehst du den Standort? Gehe dorthin\n   - Tippe 'Ton abspielen' zum Auffinden\n\n3. **Als verloren markieren:**\n   - Wähle 'Als verloren markieren'\n   - Gib Telefonnummer für Rückgabe ein\n   - Erstelle Nachricht für den Finder\n\n4. **Schule/Eltern informieren:**\n   - Melde Verlust sofort der Schule\n   - Informiere deine Eltern\n\n5. **Fernlöschung (Notfall):**\n   - Nur wenn iPad gestohlen wurde\n   - 'iPad löschen' - ALLE Daten weg!\n\n**Vorbeugung:** Aktiviere 'Wo ist?' unter Einstellungen > Apple-ID > 'Wo ist?'",
        "category": "Sicherheit & Verantwortung"
    },
    {
        "id": "q7r8s9t0-u1v2-3456-7890-123456qrstuv",
        "question": "Wie aktualisiere ich das System sicher?",
        "answer": "**Vor dem Update:**\n1. **Backup erstellen:** Einstellungen > Apple-ID > iCloud > iCloud-Backup > 'Jetzt sichern'\n2. **Akku laden:** Mindestens 50% oder am Ladegerät\n3. **WLAN-Verbindung:** Stabile Internetverbindung sicherstellen\n4. **Speicherplatz:** Mindestens 5 GB frei\n\n**Update durchführen:**\n1. Einstellungen > Allgemein > Software-Update\n2. 'Laden und installieren' antippen\n3. Code eingeben wenn gefordert\n4. 'Jetzt installieren' bestätigen\n5. iPad startet automatisch neu\n\n**Nach dem Update:**\n- Apps prüfen, ob sie noch funktionieren\n- Einstellungen kontrollieren\n- Bei Problemen: Neustart erzwingen\n\n**Schulrichtlinie:** Frage deine Lehrkraft, ob Updates erlaubt sind - manchmal müssen alle gleiche Version haben.",
        "category": "Sicherheit & Verantwortung"
    },
    {
        "id": "r8s9t0u1-v2w3-4567-8901-234567rstuvw",
        "question": "Wie nutze ich Split View für zwei Apps nebeneinander?",
        "answer": "**Split View aktivieren:**\n1. Öffne erste App (z.B. Safari)\n2. Wische vom unteren Bildschirmrand nach oben (App-Umschalter)\n3. Ziehe zweite App (z.B. GoodNotes) an rechten/linken Rand\n4. Apps teilen sich jetzt den Bildschirm\n\n**Split View anpassen:**\n- Ziehe mittleren Balken zum Größe ändern\n- Ziehe App nach oben zum Schließen\n- Tippe oberen Balken zum Wechseln zwischen Apps\n\n**Praktische Kombinationen:**\n- Safari + GoodNotes (Recherche + Notizen)\n- mebis + Dateien (Material kopieren)\n- Pages + Taschenrechner (Rechnen + Schreiben)\n- E-Mail + Dateien (Anhänge verwalten)\n\n**Tipp:** Nicht alle Apps unterstützen Split View. Probiere verschiedene Kombinationen für deinen Workflow.",
        "category": "Tipps & Tricks"
    },
    {
        "id": "s9t0u1v2-w3x4-5678-9012-345678stuvwx",
        "question": "Wie personalisiere ich das Kontrollzentrum?",
        "answer": "**Kontrollzentrum anpassen:**\n1. Einstellungen > Kontrollzentrum\n2. Unter 'Weitere Bedienelemente' findest du zusätzliche Optionen\n3. Tippe '+' zum Hinzufügen nützlicher Funktionen\n4. Tippe '-' zum Entfernen ungenutzter Elemente\n\n**Nützliche Bedienelemente für Schule:**\n- Bildschirmaufnahme (für Tutorials)\n- Notizen (schnelle Gedanken)\n- Taschenrechner (Mathe)\n- Timer (Arbeitszeiten)\n- Bildschirmzeit (Nutzung überwachen)\n- Apple TV Remote (Präsentationen)\n\n**Kontrollzentrum nutzen:**\n- Wische vom rechten oberen Rand nach unten\n- Halte Elemente gedrückt für mehr Optionen\n- Ordne Elemente durch Ziehen\n\nTipp: Stelle häufig genutzte Funktionen oben für schnellen Zugriff.",
        "category": "Tipps & Tricks"
    },
    {
        "id": "t0u1v2w3-x4y5-6789-0123-456789tuvwxy",
        "question": "Wie setze ich den Apple Pencil effektiv ein?",
        "answer": "**Apple Pencil koppeln:**\n1. Entferne Kappe (Pencil 1) oder tippe seitlich an iPad (Pencil 2)\n2. Befolge Bildschirmanweisungen zur Kopplung\n3. Akku-Status in Widgets oder Einstellungen > Apple Pencil\n\n**Effektive Nutzung:**\n**In GoodNotes:**\n- Verschiedene Stiftarten für unterschiedliche Zwecke\n- Radierer am Pencil-Ende (falls verfügbar)\n- Handflächenerkennung für natürliches Schreiben\n\n**In anderen Apps:**\n- Markup in PDFs und Fotos\n- Zeichnen in Keynote-Präsentationen\n- Handschriftnotizen in Mail\n\n**Tipps:**\n- Doppeltippe Pencil für Werkzeugwechsel\n- Neigung für Schattierungen nutzen\n- Druckstärke variieren für unterschiedliche Linien\n\n**Pflege:** Lade regelmäßig und bewahre sicher auf.",
        "category": "Tipps & Tricks"
    },
    {
        "id": "u1v2w3x4-y5z6-7890-1234-567890uvwxyz",
        "question": "Wie nehme ich ein kurzes Erklärvideo auf?",
        "answer": "**Bildschirmaufnahme mit Ton:**\n1. Füge 'Bildschirmaufnahme' zum Kontrollzentrum hinzu\n2. Öffne Kontrollzentrum\n3. **Halte** Aufnahme-Button gedrückt (nicht nur tippen!)\n4. Aktiviere 'Mikrofon Audio' für Erklärungen\n5. Tippe 'Aufnahme starten'\n6. Erkläre während du arbeitest\n7. Tippe rote Statusleiste zum Stoppen\n\n**Video bearbeiten:**\n1. Öffne Video in Fotos-App\n2. Tippe 'Bearbeiten'\n3. Schneide Anfang/Ende mit Reglern\n4. Füge Titel über Markup hinzu\n\n**Gute Erklärvideos:**\n- plane im Voraus was du zeigst\n- Sprich langsam und deutlich\n- Halte Videos unter 3 Minuten\n- Teste Tonqualität vorher\n\n**Teilen:** Via AirDrop, Mail oder in mebis hochladen.",
        "category": "Multimedia & Projekte"
    },
    {
        "id": "v2w3x4y5-z6a7-8901-2345-678901vwxyza",
        "question": "Wie bearbeite ich Fotos für Schulprojekte?",
        "answer": "**Grundbearbeitung in Fotos-App:**\n1. Öffne Foto > 'Bearbeiten'\n2. **Automatisch:** Tippe Zauberstab für Schnellverbesserung\n3. **Belichtung:** Regler für Helligkeit anpassen\n4. **Farben:** Lebendigkeit und Wärme einstellen\n5. **Zuschneiden:** Für bessere Komposition\n\n**Erweiterte Bearbeitung:**\n- **Filter:** Für verschiedene Stimmungen\n- **Markup:** Text und Pfeile hinzufügen\n- **Perspektive:** Schiefe Linien korrigieren\n\n**Für Projekte optimieren:**\n1. Hohe Auflösung beibehalten\n2. Kontrast erhöhen für bessere Lesbarkeit\n3. Unwichtiges wegschneiden\n4. Einheitliche Filter für Serie verwenden\n\n**Speichern:** 'Kopie sichern' um Original zu behalten\n\n**Tipp:** Nutze Raster beim Fotografieren (Einstellungen > Kamera > Raster) für bessere Komposition.",
        "category": "Multimedia & Projekte"
    },
    {
        "id": "w3x4y5z6-a7b8-9012-3456-789012wxyzab",
        "question": "Wie füge ich Audioaufnahmen in Präsentationen ein?",
        "answer": "**Audio aufnehmen:**\n1. Öffne Sprachmemos-App\n2. Tippe roten Aufnahme-Button\n3. Sprich deutlich ins Mikrofon\n4. Tippe Stopp-Button\n5. Benenne Aufnahme sinnvoll\n\n**In Keynote einfügen:**\n1. Öffne deine Präsentation\n2. Tippe '+' > 'Medien' > 'Audio'\n3. Wähle deine Aufnahme aus Sprachmemos\n4. Positioniere Audio-Symbol auf Folie\n5. Tippe Symbol > 'Wiedergabe' für Optionen\n\n**Einstellungen optimieren:**\n- 'Automatisch starten' für nahtlose Wiedergabe\n- 'Ausblenden' wenn Symbol stören könnte\n- Lautstärke testen vor Präsentation\n\n**Alternativen:**\n- GarageBand für professionellere Aufnahmen\n- Hintergrundmusik aus Apple-Bibliothek\n\n**Tipp:** Teste Audio vor wichtigen Präsentationen mit verschiedenen Lautsprechern.",
        "category": "Multimedia & Projekte"
    }
]

# Category configuration
CATEGORIES = [
    {"name": "Erste Schritte", "icon": "play-circle", "description": "Grundlagen für den Start"},
    {"name": "Apps & Tools", "icon": "grid-3x3-gap", "description": "Wichtige Apps und Werkzeuge"},
    {"name": "Troubleshooting", "icon": "tools", "description": "Probleme lösen"},
    {"name": "Dateien & Organisation", "icon": "folder", "description": "Ordnung in deinen Dateien"},
    {"name": "Kommunikation & Zusammenarbeit", "icon": "people", "description": "Teamwork und Austausch"},
    {"name": "Sicherheit & Verantwortung", "icon": "shield-check", "description": "Sicher und verantwortlich"},
    {"name": "Tipps & Tricks", "icon": "lightbulb", "description": "Profi-Tipps für Fortgeschrittene"},
    {"name": "Multimedia & Projekte", "icon": "play-btn", "description": "Kreative Projekte"}
]

@app.on_event("startup")
async def startup_event():
    """Initialize database with FAQ data if empty"""
    try:
        # Check if FAQ data exists
        if faq_collection.count_documents({}) == 0:
            print("Initializing FAQ database with sample data...")
            for item in FAQ_DATA:
                item["created_at"] = datetime.now()
                item["updated_at"] = datetime.now()
            faq_collection.insert_many(FAQ_DATA)
            print(f"Inserted {len(FAQ_DATA)} FAQ items")
        else:
            print(f"FAQ database already contains {faq_collection.count_documents({})} items")
    except Exception as e:
        print(f"Database initialization error: {e}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db.command("ping")
        return {"status": "healthy", "database": "connected", "timestamp": datetime.now()}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e), "timestamp": datetime.now()}

@app.get("/api/categories", response_model=List[CategoryInfo])
async def get_categories():
    """Get all FAQ categories with item counts"""
    try:
        categories_with_counts = []
        for category in CATEGORIES:
            count = faq_collection.count_documents({"category": category["name"]})
            categories_with_counts.append(CategoryInfo(
                name=category["name"],
                icon=category["icon"],
                description=category["description"],
                count=count
            ))
        return categories_with_counts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching categories: {str(e)}")

@app.get("/api/faq", response_model=List[FAQItem])
async def get_faq_items(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in questions and answers"),
    limit: int = Query(100, description="Maximum number of items to return")
):
    """Get FAQ items with optional filtering and search"""
    try:
        # Build query
        query = {}
        if category:
            query["category"] = category
        
        # Execute query
        cursor = faq_collection.find(query).limit(limit)
        items = list(cursor)
        
        # Convert MongoDB _id to string and remove it
        for item in items:
            item.pop("_id", None)
        
        # Apply search filter if provided
        if search:
            search_lower = search.lower()
            items = [
                item for item in items
                if search_lower in item["question"].lower() or search_lower in item["answer"].lower()
            ]
        
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching FAQ items: {str(e)}")

@app.get("/api/faq/{faq_id}", response_model=FAQItem)
async def get_faq_item(faq_id: str):
    """Get a specific FAQ item by ID"""
    try:
        item = faq_collection.find_one({"id": faq_id})
        if not item:
            raise HTTPException(status_code=404, detail="FAQ item not found")
        
        item.pop("_id", None)
        return item
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching FAQ item: {str(e)}")

@app.get("/api/search", response_model=List[FAQItem])
async def search_faq(
    q: str = Query(..., description="Search query"),
    limit: int = Query(20, description="Maximum number of results")
):
    """Advanced search in FAQ items"""
    try:
        if not q or len(q.strip()) < 2:
            return []
        
        search_query = q.strip().lower()
        
        # Get all items for search
        cursor = faq_collection.find({})
        items = list(cursor)
        
        # Remove MongoDB _id
        for item in items:
            item.pop("_id", None)
        
        # Score and sort results
        scored_results = []
        for item in items:
            score = 0
            question_lower = item["question"].lower()
            answer_lower = item["answer"].lower()
            
            # Exact phrase match gets highest score
            if search_query in question_lower:
                score += 10
            if search_query in answer_lower:
                score += 5
            
            # Word matches
            search_words = search_query.split()
            for word in search_words:
                if word in question_lower:
                    score += 3
                if word in answer_lower:
                    score += 1
            
            if score > 0:
                scored_results.append((item, score))
        
        # Sort by score and return top results
        scored_results.sort(key=lambda x: x[1], reverse=True)
        return [item for item, _ in scored_results[:limit]]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.get("/api/preferences/{user_id}", response_model=UserPreferences)
async def get_user_preferences(user_id: str):
    """Get user preferences"""
    try:
        prefs = preferences_collection.find_one({"user_id": user_id})
        if not prefs:
            # Create default preferences
            default_prefs = {
                "user_id": user_id,
                "has_seen_intro": False,
                "favorites": [],
                "theme": "light",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            preferences_collection.insert_one(default_prefs)
            default_prefs.pop("_id", None)
            return default_prefs
        
        prefs.pop("_id", None)
        return prefs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching preferences: {str(e)}")

@app.put("/api/preferences/{user_id}")
async def update_user_preferences(user_id: str, preferences: UserPreferences):
    """Update user preferences"""
    try:
        prefs_dict = preferences.dict()
        prefs_dict["updated_at"] = datetime.now()
        
        result = preferences_collection.update_one(
            {"user_id": user_id},
            {"$set": prefs_dict},
            upsert=True
        )
        
        return {"success": True, "modified": result.modified_count > 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating preferences: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)