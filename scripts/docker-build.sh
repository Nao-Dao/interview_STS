
cd ui && npm install && npm run build

cd .. && docker build . -t test
