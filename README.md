microservice-project/
│
├── users-service/          # Flask Microservice
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── routes.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── products-service/       # FastAPI Microservice
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── .env                    # Local credentials (git-ignored)
└── docker-compose.yml      # Orchestrates all containers



DOCKER

docker-compose down
docker-compose build --no-cache products-service 
docker-compose up --build


