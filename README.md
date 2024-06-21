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

## Deployment

### Get updates

```shell
git clone git@github.com:piMoll/recipy && cd recipy # only for the first time
git pull # from the second time on
```

### Migrations

```shell

# get correct python
. venv-source

# check migrations before apply
./manage.py showmigrations

# disable site
sudo a2dissite rezeptbue.ch
sudo systemctl restart apache2

# stop workers
sudo systemctl stop rezeptbuech

# apply migrations
./manage.py migrate

# restart workers
sudo systemctl start rezeptbuech

# reenable site
sudo a2ensite rezeptbue.ch
sudo systemctl restart apache2
```

### Code or Template

```shell
git pull
sudo systemctl restart rezeptbuech
```

### Static files

```shell
git pull
. venv-source
./manage.py collectstatic
```

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
