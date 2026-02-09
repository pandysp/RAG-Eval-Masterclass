# Fehlerbehebung

## Häufige Probleme und Lösungen

### Synchronisationsfehler

**Symptom:** Änderungen werden nicht auf anderen Geräten angezeigt.

**Lösung:**
1. Prüfen Sie Ihre Internetverbindung
2. Melden Sie sich ab und wieder an (**Profil → Abmelden**)
3. Leeren Sie den Browser-Cache (Strg+Shift+Entf)
4. Falls das Problem weiterhin besteht, warten Sie 15 Minuten — es kann sich um eine geplante Wartung handeln

**Fehlercode:** `SYNC_001` — Wird angezeigt, wenn der Server nicht erreichbar ist. In diesem Fall prüfen Sie den Status unter **https://status.cloudbase.de**.

### Berechtigungsfehler

**Symptom:** "Sie haben keine Berechtigung, diese Aktion durchzuführen."

**Lösung:**
1. Prüfen Sie Ihre Rolle im aktuellen Projekt (sichtbar unter **Projekt → Einstellungen → Mitglieder**)
2. Nur **Admins** und **Projektleiter** können Projekteinstellungen ändern
3. Nur **Admins** können Teammitglieder einladen oder entfernen
4. Kontaktieren Sie Ihren Workspace-Admin, um Berechtigungen anzupassen

**Fehlercode:** `AUTH_403` — Unzureichende Berechtigungen für die gewünschte Aktion.

### Import-Fehler

**Symptom:** CSV-Import schlägt fehl oder Daten werden falsch zugeordnet.

**Lösung:**
1. Stellen Sie sicher, dass die CSV-Datei **UTF-8-kodiert** ist
2. Verwenden Sie **Semikolon (;)** als Trennzeichen (nicht Komma)
3. Die erste Zeile muss die Spaltenüberschriften enthalten
4. Maximal **5.000 Zeilen** pro Import
5. Dateigrößenlimit: **10 MB**
6. Laden Sie die Import-Vorlage herunter unter **Projekt → Importieren → Vorlage herunterladen**

**Fehlercode:** `IMPORT_422` — Die Datei konnte nicht verarbeitet werden. Prüfen Sie Format und Kodierung.

### Langsame Ladezeiten

**Symptom:** Die Anwendung reagiert langsam oder lädt lange.

**Mögliche Ursachen:**
- Projekte mit mehr als **500 aktiven Aufgaben** können langsamer laden
- Browser-Erweiterungen können die Performance beeinträchtigen
- Veralteter Browser (empfohlen: Chrome 120+, Firefox 115+, Safari 17+)

**Lösung:**
1. Archivieren Sie abgeschlossene Aufgaben regelmäßig
2. Deaktivieren Sie testweise Browser-Erweiterungen
3. Aktualisieren Sie Ihren Browser auf die neueste Version

### E-Mail-Benachrichtigungen kommen nicht an

**Symptom:** Keine E-Mail-Benachrichtigungen trotz aktivierter Einstellungen.

**Lösung:**
1. Prüfen Sie Ihren Spam-Ordner
2. Fügen Sie **noreply@cloudbase.de** zu Ihren Kontakten hinzu
3. Prüfen Sie die Benachrichtigungseinstellungen unter **Profil → Benachrichtigungen**
4. Bei Unternehmens-Firewalls: Bitten Sie Ihre IT, die Domain **cloudbase.de** freizugeben

## Kontakt

Bei weiterhin bestehenden Problemen wenden Sie sich an den Support:
- E-Mail: **support@cloudbase.de**
- Antwortzeit: 24 Stunden (Starter/Professional), 4 Stunden (Enterprise)
