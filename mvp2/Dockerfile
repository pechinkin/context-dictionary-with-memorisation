FROM docker.elastic.co/elasticsearch/elasticsearch:8.15.1

ENV discovery.type=single-node
ENV xpack.security.enabled=true
ENV ELASTIC_PASSWORD=mvp2elastic
ENV bootstrap.memory_lock=true

EXPOSE 9200 9300

USER elasticsearch