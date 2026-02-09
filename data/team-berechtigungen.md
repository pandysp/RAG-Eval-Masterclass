# Team und Berechtigungen

## Rollen-Übersicht

CloudBase verwendet ein dreistufiges Rollenmodell. Jedes Teammitglied hat genau eine Rolle pro Workspace.

### Admin

Der **Admin** hat die höchste Berechtigungsstufe und volle Kontrolle über den Workspace.

Berechtigungen:
- Alle Projekte erstellen, bearbeiten und löschen
- Teammitglieder einladen und entfernen
- Rollen anderer Mitglieder ändern
- Workspace-Einstellungen verwalten (Abrechnung, Integrationen, SSO)
- API-Schlüssel generieren und widerrufen
- Audit-Logs einsehen (Enterprise Plan)
- Datenexporte durchführen

Beim Erstellen eines Workspaces wird der Ersteller automatisch zum Admin. Es muss immer mindestens **1 Admin** pro Workspace geben.

### Projektleiter (PL)

Der **Projektleiter** kann Projekte eigenständig verwalten, hat aber keinen Zugriff auf Workspace-weite Einstellungen.

Berechtigungen:
- Projekte erstellen und eigene Projekte verwalten
- Aufgaben in zugewiesenen Projekten erstellen, bearbeiten und zuweisen
- Teammitglieder zu eigenen Projekten hinzufügen
- Berichte und Zeiterfassungen für eigene Projekte exportieren
- Gantt-Diagramme und Kalender nutzen

Einschränkungen:
- **Kann keine** Teammitglieder zum Workspace einladen oder entfernen
- **Kann keine** Workspace-Einstellungen oder Abrechnung ändern
- **Kann keine** API-Schlüssel generieren

### Mitglied

Das **Mitglied** ist die Standardrolle mit Basiszugriff.

Berechtigungen:
- Aufgaben in zugewiesenen Projekten ansehen und eigene Aufgaben bearbeiten
- Kommentare und Dateien zu Aufgaben hinzufügen
- Eigene Zeiterfassung nutzen
- Persönliche Benachrichtigungseinstellungen anpassen

Einschränkungen:
- **Kann keine** neuen Projekte erstellen
- **Kann keine** Aufgaben anderen zuweisen
- **Kann keine** Projekteinstellungen ändern

## Rollenänderung

Rollen können nur von **Admins** geändert werden:
1. Gehen Sie zu **Einstellungen → Team → Mitglieder**
2. Klicken Sie auf das Mitglied
3. Wählen Sie die neue Rolle aus dem Dropdown-Menü
4. Die Änderung wird sofort wirksam

## Gastnutzer

Seit dem Update vom **15. November 2025** unterstützt CloudBase auch Gastnutzer. Gäste können:
- Einzelne Projekte ansehen (nur Lesezugriff)
- Kommentare hinterlassen

Gäste zählen **nicht** zum Nutzerlimit des jeweiligen Plans. Pro Workspace sind maximal **10 Gäste** möglich.

## Berechtigungsmatrix

| Aktion | Admin | Projektleiter | Mitglied | Gast |
|--------|:-----:|:-------------:|:--------:|:----:|
| Projekte erstellen | ✅ | ✅ | ❌ | ❌ |
| Aufgaben zuweisen | ✅ | ✅ | ❌ | ❌ |
| Eigene Aufgaben bearbeiten | ✅ | ✅ | ✅ | ❌ |
| Kommentare schreiben | ✅ | ✅ | ✅ | ✅ |
| Team verwalten | ✅ | ❌ | ❌ | ❌ |
| Abrechnung verwalten | ✅ | ❌ | ❌ | ❌ |
| API-Schlüssel | ✅ | ❌ | ❌ | ❌ |
