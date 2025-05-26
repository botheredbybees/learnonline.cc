FROM nginx:alpine

WORKDIR /usr/share/nginx/html

# Copy static files
COPY ./static ./static
COPY ./js ./js
COPY ./index.html .
COPY ./public/favicon.ico .

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]