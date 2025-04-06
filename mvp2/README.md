```
docker-compose up --build
```
when it finishes (mvp2-python-app exited with code 0), open new terminal window, create and enter venv:
```
python3 -m venv venv
source venv/bin/activate
```
after that, download all requirements by
```
pip install -r requirements.txt
```
run the app by using
```
python3 check_elastic.py
```
to finish the app, type `exit`. 
to finish the venv, type
```
deactivate
```

then go back to tab with running docker-compose and type
```
docker-compose down
```
