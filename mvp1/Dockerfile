# Use the official Elasticsearch image as the base image
FROM docker.elastic.co/elasticsearch/elasticsearch:8.15.1

# Set environment variables
ENV ELASTIC_PASSWORD=MVP1_DANYA_P
ENV discovery.type=single-node

# Copy custom configuration files if needed
# COPY elasticsearch.yml /usr/share/elasticsearch/config/

# Install any additional plugins if needed
# RUN bin/elasticsearch-plugin install <plugin-name>

# Expose the default Elasticsearch port
EXPOSE 9200

# Set the entrypoint to the Elasticsearch startup script
ENTRYPOINT ["/usr/share/elasticsearch/bin/elasticsearch"]
