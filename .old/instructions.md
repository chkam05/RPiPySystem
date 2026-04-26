# Przebudowa systemu "RPI"

Przebuduj mi cały system z wersji mikroserwisowej, na wersję kilkuserwisową:

- API
- BLUETOOTH_CONTROLLER
- IO_CONTROLLER
- SUPERVISOR
- WEB

## Opis starego systemu

Aktualny system, składa się z katalogów:

- auth_service - który jest serwisem API do autoryzacji użytkowników
- bluetooth_service - który jest serwisem API do komunikacji bluetooth
- control_service - który jest stroną internetową
- email_service - który jest serwisem do wysyłania wiadomości e-mail
- io_service - który jest serwisem do obsług urządzeń IO
- logs - katalog logów
- nginx - katalog z konfiguracją nginx
- scripts - katalog z skryptami
- secrets - który jest katalogiem z kluczami
- supervisor_controller - który zbiorem skryptów do supervisora
- system_service - który jest serwisem API
- tests - który jest zbiorem testów
- utils - który jest zbiorem głównych klas bazowych.

Dodatkowo znajdują się pliki:

- .env.dev - jako plik konfiguracyjny środowiska
- launch2.sh - który odpowiednio uruchomi system, oraz pozwala nim zarządzać z konsoli poleceń.
- requirements.txt - lista wymaganych bibliotek pythona.
- supervisord.conf - plik konfiguracyjny supervisord, który kontroluje cały system.

Twoim zadaniem, jest stworzenie nowego systemu, który będzie bazować na aktualnym kodzie, i zbuduje go w katalogu "NEW_PROJECT".

To ma być zupełnie nowy system, który nie będzie linkować do starych plików.

## Opis nowego systemu

Nowy system ma składać się z katalogów:

- "api" - gdzie będzie API całego systemu.
- "bluetooth_controller" - gdzie będzie kontroler bluetooth, ale nie będzie udostępniać swojego API na zewnątrz, tylko "API" będzie się z tym kontrolerem komunikować na poziomie lokalnym (najlepiej przez lokalne API).
- "config" - katalog na pliki konfiguracyjne (np ten z nginx).
- "core" - zamiast "utils", na klasy bazowe.
- "io_controller" - gdzie będzie kontroler portu IO RaspberryPI, nie będzie udostępniać swojego API na zewnątrz, tylko "API" będzie się z tym kontrolerem komunikować na poziomie lokalnym (najlepiej przez lokalne API).
- "logs" - katalog logów z supervisora
- "scripts" - będzie katalogiem na dodatkowe skrypty sh
  - cleanup.sh - do czyszczenia plików.
  - init_nginx.sh - do rekonfiguracji serwera nginx.
  - setup.sh - do instalacji/konfiguracji całego systemu.
  - stop_nging.sh - do zatrzymania pracy serwera nginx.
  - stop_supervisord.sh - do zatrzymania całego systemu "RPI"
- "secrets" - do trzymania kluczy.
- "supervisor_controller" - skrypty do samego supervisora.
- "tests" - katalog do testów jednostkowych/integracyjnych.

Przeanaliuj całą strukturę obecnego systemu i przepisz go na nową strukturę.

## API

Jak ma wyglądć struktura serwisu API:

```
/api
    /auth
        /controllers
            - sessions_controller.py
            - users_controller.py
        /models
            - modele danych kontrolerów z danej ścieżki "/api/auth"
        /storage
            
    /bluetooth
        /controllers
            - device_controller.py
        /models
            - modele danych kontrolerów z danej ścieżki "/api/bluetooth"
    /db
        - katalog na bazdy danych w formacie json.
    /email
        /controllers
            - kontroler do wysyłania, odbierania wiadomości e-mail (na razie nie implementuj)
        /models
            - modele danych kontrolerów z danej ścieżki "/api/email" (na razie nie implementuj)
    /health
        /controllers
            - health_controller.py
    /io
        /controllers
            - kontroler do komunikacji z portem IO Raspberry PI, wewnętznie, przez odpowiedni kontroler (na razie nie implementuj)
        /models
            - modele danych kontrolerów z danej ścieżki "/api/io" (na razie nie implementuj)
    /storage
        - klasy do zarządzania danymi znajdującymi się w "/api/db"
    /system
        /controllers (kontrolery do zbierania informacji o systemie)
            - network_controller.py
            - os_info_controller.py
            - os_usage_controller.py
            - supervisor_controller.py
        /exceptions
            - klasy exception dla kontrolerów z danej ścieżki "/api/system"
        /models
            - modele danych kontrolerów z danej ścieżki "/api/system"
    - app.py - plik uruchomieniowy seriwsu
    - config.py - plik konfiguracyjny serwisu
    - service.py - plik klasy serwisu
    - swagger.py - plik konfiguracyjny swaggera
```

- Pamiętaj o aktualizacji wszystkich plikó konfiguracyjnych.
- Może uda Ci się tak skonfigurować swagger, by miał rozwijaną listę po prawej stronie, z którego będzie można wybrać aktualną ścieżkę kontrolera:
  - "/api/auth"
  - "/api/bluetooth"
  - "/api/e-mail"
  - "/api/health"
  - "/api/io"
  - "/api/system"

## Ważne

Pamiętaj o tym by nie ruszać starych plików, nie robić żadnych importów startych plików, wszystko napisz w katalogu "./NEW_PROJECT" - cała konfiguracja, skrypty, kody.