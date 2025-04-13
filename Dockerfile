FROM nginx:stable-alpine

# Copy the jaeger binary over
COPY --from=jaegertracing/all-in-one:latest /go/bin/all-in-one-linux /usr/sbin/all-in-one-linux

# Copy our config/scripts over
COPY ./nginx_jaeger_proxy.conf /etc/nginx/conf.d/jaeger_proxy.conf
COPY ./entrypoint.sh /docker_entrypoint.sh
RUN chmod +x /docker_entrypoint.sh

# Setup for execution
# Note: additional args are transparently passed to jaeger
ENTRYPOINT [ "/docker_entrypoint.sh" ]
CMD []
