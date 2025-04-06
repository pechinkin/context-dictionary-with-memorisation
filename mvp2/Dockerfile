# Use Bitnami Elasticsearch image
FROM bitnami/elasticsearch:8.12.2

# Set environment variables
ENV discovery.type=single-node
ENV xpack.security.enabled=true
ENV xpack.security.http.ssl.enabled=false
ENV xpack.security.transport.ssl.enabled=false
ENV ELASTIC_PASSWORD=changeme

# Expose the default Elasticsearch port
EXPOSE 9200

# Create a directory for the password file
RUN mkdir -p /opt/bitnami/elasticsearch/config

# Create a password file
RUN echo "changeme" > /opt/bitnami/elasticsearch/config/password.txt

# Set the password file permissions
RUN chmod 644 /opt/bitnami/elasticsearch/config/password.txt