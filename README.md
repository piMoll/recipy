## Bedeutung der Tags

- **Favorit:** Klassiker. Etwas, was wir oft kochen.
- **Hauptgericht:** Rezepte, die als Hauptmahlzeit taugen. Kann auch noch eine Beilage benötigen.
- **Dessert:** Alles was süss ist, also auch Dinge, die man eher zum Apero isst.
- **Gemüse:** Besteht zum grössten Teil aus leichtem Gemüse. Kann aber auch wenig(!) Fleisch enthalten, oder hat eine fleischlose Variante.  
  Vitaminreich, gesund, kann aber auch deftig sein, nicht verwechseln mit Leicht.
- **Fleisch:** Fleischlastig, wenn man den Raubtierhunger stillen muss.
- **Fisch:** Enthält Fisch oder Meeresfrüchte. Dient vorallem als Exclusion-Tag für Patricia.
- **Beilage:** Kann z.B. mit Fleisch kombiniert werden. Wenn man etwas spezielles Kochen will, und noch Ideen für eine Beilage sucht.
- **Sauce:** Saucen, Dips, Marinaden, sowie Rezepte, die einfach eine Sauce enthalten.
- **Drink:** Allgemeine Getränke und Cocktails.
- **Tapas:** Alles, was als Vorspeise, Apero, Brunch, Mitbringsel oder Fingerfood serviert werden kann.
- **schnell:** Schnelle und unkomplizierte Gerichte. Kann auch deftig sein, nicht verwechseln mit Leicht.
- **leicht:** Für den kleinen Hunger; Kalorienarm. 
- **unvollständig:** Wurden automatisch importiert und noch nicht kontrolliert, fehlende Tags oder Bilder.
- **ungetestet:** Rezepte, die wir noch nicht probiert haben.

## Development

### Database

```postgresql
create database recipy;

create user django with password '****' createdb; -- sync with recipy/settings.py
```

### Requirements

```shell
sudo apt install libpython-dev libpq-dev
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
./manage.py showmigrations # check if everything is okay
./manage.py migrate
```

### Persist new python packages

```shell
pip freeze -l --exclude typing_extensions > requirements.txt
```

### Tests

```shell
./manage.py test
```

### Sync DB

```shell
ssh -t rezeptbue.ch sudo -u postgres pg_dump -c rezeptbuech > db_rezeptbuech_$(date -uI).sql
psql -h localhost -d recipy -u django < db_rezeptbuech_$(date -uI).sql
```

### Sync Media Uploads

```shell
scp -r rezeptbue.ch:/var/www/rezeptbue.ch/media media
```
