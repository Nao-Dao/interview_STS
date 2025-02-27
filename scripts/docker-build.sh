
cd ui && npm install && npm run build

cd .. && docker build . -t mupsycho/speechtospeech:v1.2.1
