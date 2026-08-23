# PythonOku deploy on AWS EC2 with Docker Compose

## Local Docker Desktop test first

Run this on your computer before uploading to EC2.

From the `mysite/` directory:

```bash
docker compose --env-file .env.local config --quiet
docker compose --env-file .env.local up -d --build
```

Open:

```text
http://localhost:8080
http://localhost:8080/admin/
```

Create local admin:

```bash
docker compose --env-file .env.local exec web python manage.py createsuperuser
```

Load the Python course:

```bash
docker compose --env-file .env.local exec web python manage.py seed_python_course
```

View logs:

```bash
docker compose --env-file .env.local logs -f web
docker compose --env-file .env.local logs -f nginx
```

Stop local containers:

```bash
docker compose --env-file .env.local down
```

Delete local Docker database too:

```bash
docker compose --env-file .env.local down -v
```

If you want to test the real domain locally before DNS points to EC2, add this to Windows `hosts` as Administrator:

```text
127.0.0.1 pythonoku.edu.kg
127.0.0.1 www.pythonoku.edu.kg
```

Then open:

```text
http://pythonoku.edu.kg:8080
```

Remove these `hosts` lines before testing the real EC2 server.

## 1. Server requirements

Open inbound ports in the EC2 Security Group:

- `22` for SSH
- `80` for HTTP
- later `443` for HTTPS

Install Docker and Docker Compose plugin on the EC2 instance.

## 2. Environment

Inside `mysite/`, create production `.env`:

```bash
cp .env.example .env
nano .env
```

Minimum values to change:

```env
DEBUG=False
SECRET_KEY=your-long-random-secret
ALLOWED_HOSTS=your-ec2-public-ip,pythonoku.edu.kg,www.pythonoku.edu.kg
CSRF_TRUSTED_ORIGINS=http://your-ec2-public-ip,http://pythonoku.edu.kg,http://www.pythonoku.edu.kg
DB_PASSWORD=your-strong-db-password
NGINX_PORT=80
```

For the first deploy without a domain, you can use only the EC2 public IP.

## 2.1 Domain DNS

Your domain is:

```text
pythonoku.edu.kg
```

In the registrar/DNS panel, add:

```text
A      @      YOUR_EC2_PUBLIC_IPV4
A      www    YOUR_EC2_PUBLIC_IPV4
```

If the panel does not support `@`, use `pythonoku.edu.kg` as the host/name.

Keep TTL around `300` or `3600`.

Also make sure EC2 Security Group allows inbound:

- `80/tcp`
- later `443/tcp`

## 3. Build and run

Run from the `mysite/` directory:

```bash
docker compose up -d --build
```

Check logs:

```bash
docker compose logs -f web
docker compose logs -f nginx
```

## 4. Create admin account

```bash
docker compose exec web python manage.py createsuperuser
```

## 5. Load the Python course seed data

```bash
docker compose exec web python manage.py seed_python_course
```

## 6. Useful commands

Restart:

```bash
docker compose restart
```

Run migrations manually:

```bash
docker compose exec web python manage.py migrate
```

Collect static manually:

```bash
docker compose exec web python manage.py collectstatic --noinput
```

Stop:

```bash
docker compose down
```

Stop and delete database/media/static volumes:

```bash
docker compose down -v
```

Use `down -v` carefully: it deletes PostgreSQL data.
