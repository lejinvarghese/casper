docker network create pg

docker run --name postgres --network pg -e POSTGRES_PASSWORD=Liberty! -p 5432:5432 -d pgvector/pgvector:pg16

docker run -it -d -p 3210:3210 --network pg --env-file scripts/.env --name lobe-chat-database lobehub/lobe-chat-database

docker run -it -d --name lobe-chat-database -p 3210:3210 \
  -e DATABASE_URL=postgres://postgres:Liberty!\@postgres:5432/conversations \
  -e NEXT_AUTH_SECRET=3904039cd41ea1bdf6c93db0db96e250 \
  -e NEXT_AUTH_SSO_PROVIDERS=auth0 \
  -e APP_URL=http://localhost:3210 \
  -e NEXTAUTH_URL=http://localhost:3210/api/auth \
  lobehub/lobe-chat-database