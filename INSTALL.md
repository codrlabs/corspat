## Build App
1. Fill `app/.env.template` with necessary information then rename it to `.env`
2. Using Docker Compose:
   - Run the command `docker compose -f "corspat\docker-compose.dev.yml" up -d --build`
   - "Right Button > Compose Up" on `corspat\docker-compose.dev.yml`
3. Create tables using `app/sql/create_tables.sql`
