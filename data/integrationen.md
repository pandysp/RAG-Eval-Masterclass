# Integrationen

## Übersicht

CloudBase lässt sich mit zahlreichen Drittanbieter-Tools verbinden, um Arbeitsabläufe zu optimieren. Integrationen sind ab dem **Professional Plan** verfügbar.

## Verfügbare Integrationen

### Slack

Die Slack-Integration wurde am **15. März 2025** veröffentlicht. Sie ermöglicht:
- Benachrichtigungen über Aufgabenänderungen direkt in Slack-Channels
- Erstellen von Aufgaben aus Slack-Nachrichten mit dem Befehl `/cloudbase create`
- Status-Updates in Echtzeit

Einrichtung: **Einstellungen → Integrationen → Slack → Verbinden**

### Jira

Die Jira-Integration ist seit **1. Juni 2025** verfügbar. Sie unterstützt:
- Bidirektionale Synchronisation von Issues und Aufgaben
- Automatisches Mapping von Jira-Prioritäten auf CloudBase-Prioritäten
- Import bestehender Jira-Projekte

Einrichtung: **Einstellungen → Integrationen → Jira → Verbinden**

Hinweis: Es werden nur **Jira Cloud**-Instanzen unterstützt. Jira Server und Data Center werden derzeit nicht unterstützt.

### Google Workspace

- Google Calendar: Deadlines als Kalendereinträge synchronisieren
- Google Drive: Dateien direkt aus Drive an Aufgaben anhängen

### Microsoft 365

- Outlook-Kalender-Synchronisation
- OneDrive-Anbindung für Dateianhänge
- Teams-Benachrichtigungen (Beta, seit **10. Januar 2026**)

## Webhooks

Für benutzerdefinierte Integrationen steht ein Webhook-System zur Verfügung. Unterstützte Events:
- `task.created`, `task.updated`, `task.completed`
- `project.created`, `project.archived`
- `member.invited`, `member.removed`

Webhooks können unter **Einstellungen → API & Integrationen → Webhooks** konfiguriert werden. Pro Workspace sind maximal **20 Webhooks** möglich.

## API-Dokumentation

Die vollständige API-Dokumentation finden Sie unter: **https://docs.cloudbase.de/api/v2**

Die API verwendet REST mit JSON-Antworten. Authentifizierung erfolgt über Bearer-Token. API-Schlüssel werden unter **Einstellungen → API & Integrationen → API-Schlüssel** generiert.

## Geplante Integrationen

- **Notion** — geplant für Q3 2026
- **Asana** — geplant für Q4 2026
- **GitHub** — in Evaluation
