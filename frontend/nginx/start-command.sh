envsubst '$$BACKEND_URL'< /frontend/assets/js/app.js | tee /frontend/assets/js/app.js

nginx -g 'daemon off;'