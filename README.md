# PreExamAPI

Jest to import repozytorium API projektu [PreExam](https://preexam.pl/) z GitLab'a.

## Co warto zobaczyć
  Poniżej znajdują się przykłady bardziej ciekawych rozwiązań technicznych i algotytmów, mojego autorstwa.
   + [Walidator](https://github.com/lukaszpodeszwa/preexam-api/blob/main/api/middlewares/validator.py)
   + [Przetwarzanie MJML na HTML i interejs do wysłania maili](https://github.com/lukaszpodeszwa/preexam-api/blob/main/api/mailing.py)
   + [Implementacja zasobu kategorii używając stuktury drzewa](https://github.com/lukaszpodeszwa/preexam-api/blob/main/api/categories/service.py)

## Instalacja

 - Klonujemy repozytorium `git clone https://gitlab.com/preexam/api.git folder_docelowy` 
 - Pobieramy i instalujemy [Pythona 3.7.3](https://www.python.org/downloads/release/python-373/)
 - Instalujemy narzędzie pip, jeśli nie jest zainstalowane.
 - [Instalujemy i aktywujemy środowisko wirtualne](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/) (Opcjonalne)
 - Instalujemy wymagane pakiety poleceniem `pip3 install requirements.txt` <br>


## Uruchamianie API
  Należy wyeksportować następujące zmienne środowiskowe:
  ```bash
  export DATABASE_URI=''               # Adres bazy dancyh, z której ma kożystać API.
  export MAILJET_ID=''                 # ID konta Mailjet.
  export MAILJET_SECRET=''             # Secret do konta Mailjet.
  export MJML_ID=''                    # ID konta MJML.
  export MJML_SECRET=''                # Secret konta MJML.
  export PYTHONPATH=                   # Ścieżka do folderu, do którego sklonowaliśmy repo.
  export OAUTH_GOOGLE_CLIENT_ID=''     # Id klienta w Google OpenIdConnect. O ile nie robimy nic z zasobem oauth to można ustawić cokolwiek.
  export OAUTH_GOOGLE_CLIENT_SECRET='' # Sekret klienta. j/w
  export OAUTH_GOOGLE_REDIRECT_URI=''  # Ustawiony redirect uri. j/w
  export API_IMAGES_DIR=' '            # Ścieżka do folderu, w któym będą zapisywane obrazki. Folder musi mieć odpowiednie uprawnienia tj. zapis odczyt.
  ```

### Uruchamianie lokalne/testowe API

  + Ustawiamy wymagane zmienne. W tym wypadku adres DATABASE_URI jest raczej adresem bazy testowej
  + Będąc w katalogu głównym projektu wydajemy polecenie `python3 api/app.py` Skrypt ten uruchomi api w trybie deweloperskim z włączonym debugowaniem. **To polecenie nie służy do uruchmiania na produkcji**

### Uruchamianie produkcyjne/sandboxowe API na serwerze

  + Po instalacji zależności wydajemy polecenie <br>

  ```bash
  gunicorn3 -b *adres_ip* -e DATABASE_URI=test@test.pl \
                            MAILJET_ID='' \
                            MAILJET_SECRET='' \
                            MJML_ID='' \
                            MJML_SECRET='' \
                            PYTHONPATH='' \
                            OAUTH_GOOGLE_CLIENT_ID='' \
                            OAUTH_GOOGLE_CLIENT_SECRET='' \
                            OAUTH_GOOGLE_REDIRECT_URI='' \
                            API_IMAGES_DIR='' \
                            'api:app.init_app()'` Oczywiście polecenie to powinno się zmodyfikować o obsługę logowania, https itd.
  ```

## Tworzenie zmian

Główną gałęzią repo jest gałąź develop na niej rozwijane jest API.<br>
Kolejne wersje są meargami gałęzi develop do gałęzi master.

Projekt ten używa prostego feature-branch workflow.<br>
Wygląda to następująco:

* `git checkout master/develop` przełączamy się na główną gałąź repo(aktualnie jest to master, po rozgałęzieniu będzie to develop)
* `git pull origin master/develop` pobieramy aktualną wersję gałęzi master lubdevelop
* `git checkout -b nazwa_naszego_brancha` tworzymy brancha, na którym będziemy wprowadzać nasze zmiany
* tworzymy zmiany
* `git push origin nazwa_naszego_brancha` wypychamy gałąź do repo
* Tworzymy mearge request do odpowiedniej gałęzi i przypisujemy go do odpowiedniej osoby. Na tę chwilę tą osobą jest @lukaszpodeszwa

