FROM nginxinc/nginx-unprivileged:1.28-alpine
COPY web/nginx-main.conf /etc/nginx/nginx.conf
COPY web/nginx.conf /etc/nginx/conf.d/default.conf
COPY web/static/ /usr/share/nginx/html/
EXPOSE 8080
HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 CMD wget -q -O - http://127.0.0.1:8080/health || exit 1
