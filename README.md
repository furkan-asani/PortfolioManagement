## **Deployment-Anleitung für die Portfolio Management Applikation**

1. Klone dieses Repository in ein Verzeichnis mit dem folgenden Befehl:
    
    ```
    bashCopy code
    git clone https://github.com/furkan-asani/PortfolioManagement.git
    
    ```
    
2. Im Verzeichnis "Resources" befindet sich die Docker Compose Datei. Führe diesen Befehl aus, um die Docker Container beim ersten Mal zum Laufen zu bringen.
    
    ```
    Copy code
    docker-compose up -d
    
    ```
    
    Hinweis: Später reicht es, die Container über Docker Desktop zu starten.
    
3. Installiere einen Postgres DB Client, um eine Verbindung zur Datenbank herzustellen. Entweder kann dieser innerhalb des Python-Containers in VS Code oder auf der lokalen Umgebung installiert werden. Der Connectionstring bleibt dabei sehr ähnlich, nur der Port verändert sich:
    - Innerhalb des Containers:
        
        ```
        bashCopy code
        postgresql+psycopg2://root:password@postgres_db:5432/portfolio
        
        ```
        
    - Auf der lokalen Maschine:
        
        ```
        bashCopy code
        postgresql+psycopg2://root:password@postgres_db:5433/portfolio
        
        ```
        
4. Die Datenbank ist derzeit noch leer und besitzt kein Datenschema. Um die Tabellendefinition und alles weitere zu erstellen, kopiere den Inhalt der "CreateTablesStatement.sql" Datei, die ebenfalls im Verzeichnis "Resources" liegt, und führe ihn über den installierten DB-Client auf der Datenbank aus.
5. Führe auch die Befehle aus der "Migration.sql" aus, die ebenfalls im Verzeichnis "Resources" liegen.
6. Installiere die Abhängigkeiten für die Python-Anwendung. Verbinde dich dazu über VS Code mit dem gestarteten Python-Container. Klicke auf den grünen Button mit dem "><" Zeichen und wähle "Attach to running container" aus. Wähle den Python-Container aus, um ein neues VS Code Fenster zu öffnen, das mit dem Container verbunden ist. Clone das Repository in den Container mit dem Befehl aus Schritt 1. Führe anschließend im Verzeichnis "Resources" den folgenden Befehl aus:
    
    ```
    bashCopy code
    pip install -r ./requirements.txt
    
    ```
    
7. Importiere deine Wertpapiere über die Importskripte, die sich in der "ImportScripts.py" im Verzeichnis "PortfolioManagement/Bonds/Code" befinden. Lege deine zu importierenden Dateien im Import-Verzeichnis ab. In der "ImportScripts.py" gibt es drei Klassen für jeden deiner Depotanbieter. Führe die Datei deswegen dreimal aus und ändere die Klasse in der "example" Variable, um den jeweiligen Anbieter zu importieren.
8. Erstelle ein neues Verzeichnis namens "FileDrop" im Verzeichnis "PortfolioManagement". In diesem Verzeichnis kannst du Dateien ablegen, die du mit Transaktionen oder Wertpapieren verknüpfen möchtest.
9. Wenn du die ISIN-to-Ticker/Symbol-Umwandlung von OPEN FIGI verwenden möchtest, erstelle einen Account auf der Website **[https://www.openfigi.com/](https://www.openfigi.com/)** , um einen API Key zu erhalten. Um diesen API Key zu verwenden, gibt es mehrere Möglichkeiten. Die einfachste ist, den API Key in der "ISINToTickerConverter.py" in der Methode "__map_jobs
10. Einpflegen der Ticker bzw. Symbole in der Datenbank. Die Symbole der gewünschten Wertpapiere sollten im Idealfall über yahoo finance herausgefunden werden
11. Testen und allgemeine Verwendung des Programms läuft dann über die Operations.ipynb. Um diese auszuführen, werden Sie von VS Code aufgefordert weitere Abhängigkeiten zu installieren.
