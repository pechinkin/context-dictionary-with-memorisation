this is a folder for mvp 1.
it will be the simple console-app which uses python & ElasticSearch for searchings through 2 datasets - one with definitions, second with sentences

sources i used: 
for [sentences](https://www.kaggle.com/datasets/amontgomerie/cefr-levelled-english-text)
for [dictionary](https://github.com/benjihillard/English-Dictionary-Database/blob/a0722819e61d19c6c8cc3c79eb2983d5df3fe998/english%20Dictionary.csv)

--downloading elastic search--
(you need docker for that)

1.
```
docker build -t custom-elasticsearch:8.15.1 .
docker run -d --name es01 -p 9200:9200 --memory=1g custom-elasticsearch:8.15.1
docker exec -it es01 /usr/share/elasticsearch/bin/elasticsearch-reset-password -u elastic -b
```
2. type y in a question
3. copy a password and put it to the password.txt file

--working with python--
(you need python to be downloaded for this part)

4. 
```
python3 -m venv venv
source venv/bin/activate
```
8. pip install -r requirements.txt
9. python3 move_data_to_elastic.py
(takes ~10 minutes to execute)
10. python3 app.py

--finishing--

11. deactivate
12. (to stop container, delete it and its image)
```
docker stop es01 && docker rm es01 && docker rmi custom-elasticsearch:8.15.1
```
(if you want to remove this container and image)
14. now you can delete this directory
