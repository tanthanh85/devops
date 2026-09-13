FROM mcr.microsoft.com/playwright:v1.52.0-noble
ARG KUBECTL_VERSION=v1.31.9
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && curl --fail --silent --show-error --location \
       "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl" \
       --output /usr/local/bin/kubectl \
    && chmod 0755 /usr/local/bin/kubectl \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /tests
COPY package.json ./
RUN npm install --omit=optional && npm cache clean --force
COPY tests/ ./tests/
ENV NODE_PATH=/tests/node_modules
RUN mkdir -p /tests/test-results /tests/playwright-report \
    && chown -R pwuser:pwuser /tests
USER pwuser
CMD ["npx", "playwright", "test"]
