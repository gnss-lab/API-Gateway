docker-build:
	docker build -t api-gateway . 
docker-run:
	docker run -d -p 20722:8000 \
	-e PORT_SERVER='8000' \
	-v database-api-gateway:/usr/src/app/database \
	--rm --name api-gateway-iszf -it api-gateway
docker-stop:
	docker stop api-gateway-iszf
