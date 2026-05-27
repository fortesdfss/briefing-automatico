# Agendamento (rodar todo dia às 9h)

O script roda automaticamente todo dia, sem você abrir nada. Cada SO tem seu jeito:

## macOS — launchd (recomendado)

Cria um `~/Library/LaunchAgents/com.jppace.briefing.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.jppace.briefing</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>/Users/SEU_USER/briefing-automatico/connectors/SUA_MARCA/pull.py</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key><integer>9</integer>
    <key>Minute</key><integer>0</integer>
  </dict>
  <key>StandardOutPath</key><string>/tmp/briefing.log</string>
  <key>StandardErrorPath</key><string>/tmp/briefing.err</string>
</dict>
</plist>
```

Carrega:

```bash
launchctl load ~/Library/LaunchAgents/com.jppace.briefing.plist
```

Roda em **userspace** (sem sudo). Pra desativar: `launchctl unload`.

## Windows — Task Scheduler

Via GUI ou linha de comando:

```cmd
schtasks /create /tn "BriefingDiario" /tr "python C:\path\to\pull.py" /sc daily /st 09:00
```

## Linux — cron

Adiciona ao crontab (`crontab -e`):

```
0 9 * * * /usr/bin/python3 /path/to/connectors/SUA_MARCA/pull.py >> /tmp/briefing.log 2>&1
```

## Status

🛠️ Em construção. Templates prontos, instruções específicas por conector virão.
