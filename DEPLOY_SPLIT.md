# PythonOku: split frontend and backend deployment

This repository is now ready for a split deployment:

- `frontend/` goes to GitHub and Vercel.
- `mysite/` goes to AWS EC2 with Docker Compose.
- Public site: `https://pythonoku.edu.kg`
- Backend API: `https://api.pythonoku.edu.kg/api/`

## Frontend on Vercel

1. Push the repository to GitHub.
2. In Vercel, import the repository.
3. Set the project root directory to `frontend`.
4. Keep the build command as `npm run build`.
5. Keep the output directory as `dist`.
6. Add the environment variable:

```env
VITE_API_BASE_URL=https://api.pythonoku.edu.kg/api/
```

7. Add the custom domain `pythonoku.edu.kg` in Vercel.

`frontend/vercel.json` keeps React routes working after refresh, so `/login` and dashboard routes do not become 404 pages.

## Backend on AWS EC2

On EC2, upload or pull only the backend project files, then run from `mysite/`:

```bash
cp .env.example .env
nano .env
docker compose up -d --build
```

Minimum production values:

```env
DEBUG=False
SECRET_KEY=your-long-random-secret
ALLOWED_HOSTS=api.pythonoku.edu.kg,YOUR_EC2_PUBLIC_IPV4
CSRF_TRUSTED_ORIGINS=https://api.pythonoku.edu.kg,https://pythonoku.edu.kg,https://www.pythonoku.edu.kg
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=https://pythonoku.edu.kg,https://www.pythonoku.edu.kg
DB_PASSWORD=your-strong-db-password
NGINX_PORT=80
```

Open inbound ports in the EC2 Security Group:

- `22/tcp` for SSH
- `80/tcp` for HTTP
- `443/tcp` for HTTPS after SSL is configured

## DNS

Use the main domain for Vercel and an API subdomain for AWS:

```text
pythonoku.edu.kg      -> Vercel
www.pythonoku.edu.kg  -> Vercel
api.pythonoku.edu.kg  -> YOUR_EC2_PUBLIC_IPV4
```

The exact Vercel DNS record depends on how the domain is connected in Vercel. Use the DNS values Vercel shows in the Domains screen.

## If `/login` returns 404 from AWS

If Nginx logs contain a line like this:

```text
open() "/etc/nginx/html/login" failed
```

then the browser is reaching the backend server for a frontend route. In the split setup this means DNS is still wrong or the frontend has not been attached in Vercel yet.

Fix the DNS and server environment:

```text
pythonoku.edu.kg      -> Vercel
www.pythonoku.edu.kg  -> Vercel
api.pythonoku.edu.kg  -> EC2 public IPv4
```

On EC2, update `mysite/.env` so the backend is an API service:

```env
ALLOWED_HOSTS=api.pythonoku.edu.kg,YOUR_EC2_PUBLIC_IPV4
CSRF_TRUSTED_ORIGINS=https://api.pythonoku.edu.kg,https://pythonoku.edu.kg,https://www.pythonoku.edu.kg
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=https://pythonoku.edu.kg,https://www.pythonoku.edu.kg
```

Then restart:

```bash
cd ~/PythonOku/mysite
docker compose up -d --build
docker compose logs -f nginx
```

Check:

```bash
curl -I http://127.0.0.1/api/
curl -I http://YOUR_EC2_PUBLIC_IPV4/
```

The main site `/login` should be opened on Vercel through `https://pythonoku.edu.kg/login`, not through the EC2 backend.

## Secret rotation

Do not paste production `.env` values into chat, GitHub, or tickets. If a secret was pasted anywhere, rotate it before continuing:

- generate a new `SECRET_KEY`
- create a new Gemini API key and disable the exposed one
- create a new Gmail App Password and disable the exposed one
- replace the default database password with a strong password
- restart the backend containers after updating `.env`

## SEO checklist

The frontend includes:

- public homepage at `/`
- title and description tags
- canonical URL
- Open Graph tags
- JSON-LD organization data
- `robots.txt`
- `sitemap.xml`

After deployment:

1. Open `https://pythonoku.edu.kg/robots.txt`.
2. Open `https://pythonoku.edu.kg/sitemap.xml`.
3. Add the domain to Google Search Console.
4. Submit `https://pythonoku.edu.kg/sitemap.xml`.
5. Request indexing for `https://pythonoku.edu.kg/`.
