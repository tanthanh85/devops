FROM mcr.microsoft.com/playwright:v1.52.0-noble
WORKDIR /monitor
COPY package.json ./
RUN npm install --omit=optional && npm cache clean --force
COPY synthetic-check.js ./
USER pwuser
CMD ["node", "synthetic-check.js"]

