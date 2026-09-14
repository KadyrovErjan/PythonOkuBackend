# 🏗️ ITAdis CRM - Архитектура Production

## 📊 Общая схема

```
┌─────────────────────────────────────────────────────────────────────┐
│                           INTERNET                                   │
│                    (Users access from anywhere)                      │
└────────────────┬────────────────────────────┬───────────────────────┘
                 │                            │
                 │                            │
     ┌───────────▼──────────┐     ┌───────────▼──────────┐
     │   itadiscrm.com.kg   │     │ api.itadiscrm.com.kg │
     │   www.itadiscrm.com.kg│     │                      │
     └───────────┬──────────┘     └───────────┬──────────┘
                 │                            │
                 │                            │
     ┌───────────▼──────────────────────────────▼──────────┐
     │              CLOUDFLARE                              │
     │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
     │  • DNS Management                                    │
     │  • CDN (Content Delivery Network)                    │
     │  • DDoS Protection                                   │
     │  • SSL/TLS Termination                              │
     │  • Web Application Firewall (WAF)                    │
     │  • Caching (Static files, Images)                    │
     └───────────┬──────────────────────────────┬──────────┘
                 │                              │
                 │                              │
     ┌───────────▼──────────┐       ┌──────────▼───────────────┐
     │       VERCEL         │       │     AWS EC2 Instance     │
     │   ┌──────────────┐   │       │  ┌────────────────────┐  │
     │   │   Frontend   │   │       │  │   Ubuntu 22.04     │  │
     │   │  (React/Next)│◄──┼───────┼──┤                    │  │
     │   │   Vite App   │   │  API  │  │  Nginx:80/443      │  │
     │   └──────────────┘   │ Calls │  │  ┌──────────────┐  │  │
     │                      │       │  │  │    Nginx     │  │  │
     │  • Auto Deployment   │       │  │  │  (Reverse    │  │  │
     │  • CDN Global        │       │  │  │   Proxy)     │  │  │
     │  • SSL Automatic     │       │  │  └──────┬───────┘  │  │
     │  • Git Integration   │       │  │         │          │  │
     └──────────────────────┘       │  │  ┌──────▼───────┐  │  │
                                    │  │  │  Gunicorn    │  │  │
                                    │  │  │  (WSGI)      │  │  │
                                    │  │  │  Workers: 4  │  │  │
                                    │  │  └──────┬───────┘  │  │
                                    │  │         │          │  │
                                    │  │  ┌──────▼───────┐  │  │
                                    │  │  │   Django     │  │  │
                                    │  │  │  REST API    │  │  │
                                    │  │  │   Python     │  │  │
                                    │  │  └──────┬───────┘  │  │
                                    │  └─────────┼──────────┘  │
                                    │            │             │
                                    └────────────┼─────────────┘
                                                 │
                                                 │ PostgreSQL
                                                 │ Connection
                                                 │
                                    ┌────────────▼─────────────┐
                                    │    AWS RDS PostgreSQL    │
                                    │  ┌────────────────────┐  │
                                    │  │  PostgreSQL 15     │  │
                                    │  │  Database:         │  │
                                    │  │  itadis_db         │  │
                                    │  │                    │  │
                                    │  │  Auto Backups      │  │
                                    │  │  Multi-AZ (Opt)    │  │
                                    │  └────────────────────┘  │
                                    └──────────────────────────┘
```

---

## 🔄 Request Flow

### Frontend Request Flow

```
User Browser
    │
    ├─► https://itadiscrm.com.kg/dashboard
    │
    ▼
Cloudflare DNS (A record → Vercel)
    │
    ▼
Cloudflare CDN (Cache check)
    │
    ├─► [CACHE HIT] ──► Return cached content ──► User
    │
    └─► [CACHE MISS]
            │
            ▼
        Vercel Edge Network
            │
            ▼
        React/Next.js App
            │
            └─► Render HTML ──► Cloudflare ──► User
```

### API Request Flow

```
User Browser (Frontend)
    │
    ├─► API Request: GET /api/v1/students/
    │   Headers: Authorization: Bearer <JWT>
    │
    ▼
Cloudflare DNS (A record → AWS EC2 IP)
    │
    ▼
Cloudflare Proxy (DDoS check, WAF rules)
    │
    ▼
AWS EC2 (Elastic IP)
    │
    ▼
Nginx (Port 443)
    │
    ├─► SSL Termination (Let's Encrypt cert)
    │
    ├─► Check path:
    │   ├─► /static/* ──► Serve from /staticfiles/
    │   ├─► /media/*  ──► Serve from /media/
    │   └─► /api/*    ──► Proxy to Gunicorn
    │
    ▼
Gunicorn (Unix Socket)
    │
    ├─► Worker 1 ─┐
    ├─► Worker 2 ─┤
    ├─► Worker 3 ─┼─► Django WSGI App
    └─► Worker 4 ─┘
            │
            ▼
    Django Middleware
            │
            ├─► CorsMiddleware (Check origin)
            ├─► AuthenticationMiddleware (Verify JWT)
            ├─► PermissionMiddleware (Check permissions)
            │
            ▼
    Django URL Router
            │
            ▼
    DRF ViewSet (StudentViewSet)
            │
            ├─► Serializer (StudentSerializer)
            ├─► Filter (django_filters)
            ├─► Pagination (PageNumberPagination)
            │
            ▼
    Django ORM
            │
            ▼
    PostgreSQL Query
            │
            ▼
    AWS RDS PostgreSQL
            │
            ├─► Execute SELECT * FROM students
            ├─► Return rows
            │
            ▼
    Back through the stack:
    RDS → Django → Serializer → JSON → Gunicorn → Nginx → Cloudflare → User
```

---

## 🔐 Security Layers

```
┌────────────────────────────────────────────────────────────┐
│                    Security Layers                          │
├────────────────────────────────────────────────────────────┤
│  Layer 1: Cloudflare                                        │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│  • DDoS Protection (Automatic)                              │
│  • Rate Limiting (Configurable)                             │
│  • Bot Detection                                            │
│  • WAF Rules                                                │
│  • SSL/TLS Encryption                                       │
│  • Geo-blocking (Optional)                                  │
└────────────────────┬───────────────────────────────────────┘
                     │
┌────────────────────▼───────────────────────────────────────┐
│  Layer 2: AWS Security                                      │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│  • VPC (Virtual Private Cloud)                              │
│  • Security Groups                                          │
│    - EC2: Allow 22,80,443 only                             │
│    - RDS: Allow 5432 from EC2 SG only                      │
│  • IAM Roles & Policies                                     │
│  • Private Subnet for RDS                                   │
└────────────────────┬───────────────────────────────────────┘
                     │
┌────────────────────▼───────────────────────────────────────┐
│  Layer 3: Operating System (Ubuntu)                         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│  • UFW Firewall (22,80,443 only)                           │
│  • fail2ban (SSH brute-force protection)                    │
│  • Automatic security updates                               │
│  • Non-root user execution (itadis)                         │
│  • SSH key authentication only                              │
└────────────────────┬───────────────────────────────────────┘
                     │
┌────────────────────▼───────────────────────────────────────┐
│  Layer 4: Nginx                                             │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│  • SSL/TLS Termination                                      │
│  • Request size limits (10MB)                               │
│  • Timeout protection                                       │
│  • Headers security:                                        │
│    - X-Frame-Options: SAMEORIGIN                           │
│    - X-Content-Type-Options: nosniff                       │
│    - X-XSS-Protection: 1; mode=block                       │
└────────────────────┬───────────────────────────────────────┘
                     │
┌────────────────────▼───────────────────────────────────────┐
│  Layer 5: Django Application                                │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│  • JWT Authentication (simplejwt)                           │
│    - Access token: 30 min                                   │
│    - Refresh token: 7 days                                  │
│    - Token blacklist on logout                              │
│  • RBAC (Role-Based Access Control)                         │
│    - Owner, Admin, Teacher roles                            │
│  • CORS (Specific origins only)                             │
│  • CSRF Protection                                          │
│  • SQL Injection Protection (ORM)                           │
│  • XSS Protection (Template escaping)                       │
│  • DRF Throttling                                           │
│    - Anonymous: 100 req/hour                                │
│    - Authenticated: 1000 req/hour                           │
│    - Login: 5 req/min                                       │
└────────────────────┬───────────────────────────────────────┘
                     │
┌────────────────────▼───────────────────────────────────────┐
│  Layer 6: Database (PostgreSQL)                             │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│  • Argon2 Password Hashing                                  │
│  • Database user privileges (minimal)                       │
│  • Parameterized queries (ORM)                              │
│  • SSL connection (optional)                                │
│  • Automatic backups                                        │
│  • Encryption at rest (AWS)                                 │
└────────────────────────────────────────────────────────────┘
```

---

## 💾 Data Flow

### User Authentication Flow

```
1. User Login
   ├─► POST /api/v1/auth/login/
   │   Body: {username, password}
   │
   ├─► Django checks credentials
   │   ├─► Query User from PostgreSQL
   │   ├─► Verify password (Argon2)
   │   │
   │   ├─► [✓ Valid]
   │   │   ├─► Generate JWT tokens
   │   │   │   ├─► Access Token (30 min)
   │   │   │   └─► Refresh Token (7 days)
   │   │   └─► Return tokens + user data
   │   │
   │   └─► [✗ Invalid]
   │       └─► Return 401 Unauthorized

2. Authenticated Request
   ├─► GET /api/v1/students/
   │   Headers: Authorization: Bearer <access_token>
   │
   ├─► Django verifies JWT
   │   ├─► Decode token
   │   ├─► Check expiry
   │   ├─► Check blacklist
   │   │
   │   ├─► [✓ Valid]
   │   │   ├─► Extract user_id
   │   │   ├─► Load user from DB
   │   │   ├─► Check permissions
   │   │   └─► Process request
   │   │
   │   └─► [✗ Invalid]
   │       └─► Return 401 Unauthorized

3. Token Refresh
   ├─► POST /api/v1/auth/token/refresh/
   │   Body: {refresh}
   │
   ├─► Django verifies refresh token
   │   ├─► [✓ Valid]
   │   │   ├─► Generate new access token
   │   │   ├─► Rotate refresh token (optional)
   │   │   └─► Return new tokens
   │   │
   │   └─► [✗ Invalid/Expired]
   │       └─► Return 401 (User must re-login)
```

### Transaction Creation Flow

```
POST /api/v1/transactions/
Body: {
  student_id, amount, type, description
}

    │
    ▼
1. Authentication Check
    │
    ├─► Verify JWT
    │
    ▼
2. Permission Check
    │
    ├─► Check user role (Owner, Admin, Teacher)
    ├─► Check if user can create transactions
    │
    ▼
3. Validation
    │
    ├─► Serializer validation
    ├─► Check student exists
    ├─► Check amount > 0
    ├─► Check type in [PAYMENT, INCOME, EXPENSE]
    │
    ▼
4. Database Transaction (ATOMIC)
    │
    ├─► BEGIN TRANSACTION
    │
    ├─► Create Transaction record
    │   ├─► INSERT INTO transactions (...)
    │
    ├─► Update Student balance
    │   ├─► UPDATE students SET balance = balance + amount
    │
    ├─► Create AuditLog record
    │   ├─► INSERT INTO audit_log (action, user, timestamp)
    │
    ├─► COMMIT
    │
    └─► [Error] ──► ROLLBACK
                        │
                        └─► Return error to user
    │
    ▼
5. Return Response
    │
    ├─► 201 Created
    └─► Body: {transaction_data}
```

---

## 📦 Component Details

### Backend Stack

```
┌─────────────────────────────────────────────┐
│           Django Application                 │
├─────────────────────────────────────────────┤
│                                              │
│  Django 5.1.4                                │
│  ├─── Django REST Framework 3.15.2          │
│  │    ├─── ViewSets (CRUD operations)       │
│  │    ├─── Serializers (Data validation)    │
│  │    ├─── Permissions (RBAC)               │
│  │    └─── Pagination                       │
│  │                                           │
│  ├─── djangorestframework-simplejwt         │
│  │    ├─── Access Token                     │
│  │    ├─── Refresh Token                    │
│  │    └─── Token Blacklist                  │
│  │                                           │
│  ├─── django-filter                         │
│  │    └─── Advanced filtering               │
│  │                                           │
│  ├─── drf-spectacular                       │
│  │    ├─── OpenAPI 3 schema                 │
│  │    ├─── Swagger UI                       │
│  │    └─── ReDoc                            │
│  │                                           │
│  ├─── django-cors-headers                   │
│  │    └─── CORS management                  │
│  │                                           │
│  └─── Custom Apps                           │
│       └─── itadis_app                       │
│            ├─── Models (User, Student, etc) │
│            ├─── Views (API endpoints)       │
│            ├─── Services (Business logic)   │
│            └─── Permissions                 │
│                                              │
└─────────────────────────────────────────────┘
```

### Database Schema (Simplified)

```
┌──────────────────────┐     ┌──────────────────────┐
│       User           │     │      Group           │
├──────────────────────┤     ├──────────────────────┤
│ id (PK)              │     │ id (PK)              │
│ username             │     │ name                 │
│ email                │◄───┐│ teacher_id (FK)      │
│ full_name            │    ││ schedule             │
│ role (ENUM)          │    ││ capacity             │
│ phone_number         │    ││ status               │
│ avatar               │    ││ monthly_fee          │
│ created_at           │    ││ start_date           │
└──────────────────────┘    │└──────────────────────┘
                            │           │
                            │           │ 1:N
┌──────────────────────┐    │  ┌────────▼──────────┐
│    Transaction       │    │  │     Student       │
├──────────────────────┤    │  ├───────────────────┤
│ id (PK)              │    │  │ id (PK)           │
│ student_id (FK)      ├────┘  │ full_name         │
│ user_id (FK)         │◄──────┤ group_id (FK)     │
│ amount               │       │ phone_number      │
│ type (ENUM)          │       │ parent_phone      │
│ description          │       │ balance           │
│ date                 │       │ status            │
│ created_at           │       │ joined_date       │
└──────────────────────┘       │ notes             │
                               └───────────────────┘
┌──────────────────────┐              │
│      Balance         │              │
├──────────────────────┤              │
│ id (PK)              │              │
│ user_id (FK)         │◄─────────────┘
│ amount               │
│ updated_at           │
└──────────────────────┘

┌──────────────────────┐       ┌──────────────────────┐
│      Expense         │       │      Collection      │
├──────────────────────┤       ├──────────────────────┤
│ id (PK)              │       │ id (PK)              │
│ amount               │       │ user_id (FK)         │
│ category             │       │ amount               │
│ description          │       │ description          │
│ date                 │       │ date                 │
└──────────────────────┘       └──────────────────────┘

┌──────────────────────┐
│      AuditLog        │
├──────────────────────┤
│ id (PK)              │
│ user_id (FK)         │
│ action               │
│ model_name           │
│ object_id            │
│ changes              │
│ ip_address           │
│ timestamp            │
└──────────────────────┘
```

---

## 🔄 Deployment Pipeline

```
┌────────────────────────────────────────────────────────────┐
│                     Development                             │
├────────────────────────────────────────────────────────────┤
│  Developer                                                  │
│      │                                                      │
│      ├─► git add .                                         │
│      ├─► git commit -m "Feature: ..."                     │
│      └─► git push origin main                             │
└──────────────────┬─────────────────────────────────────────┘
                   │
┌──────────────────▼─────────────────────────────────────────┐
│                     GitHub                                  │
├────────────────────────────────────────────────────────────┤
│  • Code Repository                                          │
│  • Version Control                                          │
│  • Pull Requests                                            │
│  • GitHub Actions (Optional CI/CD)                          │
└──────────┬─────────────────────────┬───────────────────────┘
           │                         │
           │ Backend                 │ Frontend
           │                         │
┌──────────▼────────────┐   ┌────────▼────────────┐
│   AWS EC2 Deploy      │   │   Vercel Deploy     │
├───────────────────────┤   ├─────────────────────┤
│  Manual:              │   │  Automatic:         │
│  1. SSH to EC2        │   │  1. Detect push     │
│  2. git pull          │   │  2. npm install     │
│  3. update_app.sh     │   │  3. npm build       │
│  4. restart services  │   │  4. Deploy to edge  │
│                       │   │  5. Invalidate CDN  │
│  Automatic (future):  │   └─────────────────────┘
│  • GitHub Actions     │
│  • SSH deployment     │
│  • Zero-downtime      │
└───────────────────────┘
```

---

## 📊 Monitoring & Logging

```
┌─────────────────────────────────────────────────────────────┐
│                    Monitoring Stack                          │
└─────────────────────────────────────────────────────────────┘

Application Logs (Backend)
├─► Django Logs
│   └─► /backend/logs/django.log
│       • INFO, WARNING, ERROR levels
│       • JSON format
│       • Rotating (15MB, 10 backups)
│
├─► Gunicorn Logs
│   ├─► /backend/logs/gunicorn-access.log
│   └─► /backend/logs/gunicorn-error.log
│
└─► Systemd Journal
    └─► sudo journalctl -u itadis-crm

Web Server Logs
├─► Nginx Access
│   └─► /var/log/nginx/itadiscrm-access.log
│       • Request logs
│       • Response times
│       • Status codes
│
└─► Nginx Error
    └─► /var/log/nginx/itadiscrm-error.log
        • Server errors
        • Upstream errors

System Metrics (EC2)
├─► CPU Usage
│   └─► htop, top
│
├─► Memory Usage
│   └─► free -h
│
├─► Disk Usage
│   └─► df -h
│
└─► Network
    └─► ss -tulpn

Database Logs (RDS)
├─► PostgreSQL Logs
│   └─► AWS CloudWatch Logs
│       • Query logs (optional)
│       • Error logs
│       • Slow query logs
│
└─► Performance Insights
    └─► AWS RDS Console
        • Query performance
        • Top SQL
        • Wait events

Frontend Monitoring (Vercel)
├─► Build Logs
│   └─► Vercel Dashboard
│
├─► Function Logs
│   └─► Runtime logs
│
└─► Analytics
    ├─► Page views
    ├─► Core Web Vitals
    └─► Geographic data

CDN/Security (Cloudflare)
├─► Analytics
│   ├─► Requests
│   ├─► Bandwidth
│   └─► Cache hit ratio
│
├─► Security Events
│   ├─► Threats blocked
│   ├─► Challenge rate
│   └─► Bot traffic
│
└─► Performance
    ├─► Response times
    └─► Edge locations

Future Monitoring (Recommended)
├─► AWS CloudWatch
│   ├─► EC2 metrics
│   ├─► RDS metrics
│   ├─► Alarms
│   └─► Dashboards
│
├─► Sentry (Error Tracking)
│   ├─► Exception tracking
│   ├─► Performance monitoring
│   └─► Release tracking
│
└─► Uptime Monitoring
    ├─► UptimeRobot
    ├─► Pingdom
    └─► StatusCake
```

---

## 🚀 Scalability Options

### Vertical Scaling (More Power)

```
EC2 Instance Types:
├─► t2.micro  (1 vCPU, 1 GB RAM)   ← Current
├─► t2.small  (1 vCPU, 2 GB RAM)
├─► t2.medium (2 vCPU, 4 GB RAM)
├─► t2.large  (2 vCPU, 8 GB RAM)
└─► t3.xlarge (4 vCPU, 16 GB RAM)

RDS Instance Types:
├─► db.t3.micro  (2 vCPU, 1 GB)    ← Current
├─► db.t3.small  (2 vCPU, 2 GB)
├─► db.t3.medium (2 vCPU, 4 GB)
└─► db.m5.large  (2 vCPU, 8 GB)
```

### Horizontal Scaling (More Servers)

```
┌────────────────────────────────────────────────────┐
│           Application Load Balancer (ALB)           │
│  • Health checks                                    │
│  • SSL termination                                  │
│  • Path-based routing                               │
└──────┬─────────────┬─────────────┬──────────────────┘
       │             │             │
┌──────▼──────┐ ┌────▼──────┐ ┌────▼──────┐
│  EC2 #1     │ │  EC2 #2   │ │  EC2 #3   │
│  Django App │ │ Django App│ │ Django App│
└──────┬──────┘ └────┬──────┘ └────┬──────┘
       │             │             │
       └─────────────┴─────────────┘
                     │
              ┌──────▼──────┐
              │  RDS        │
              │ (Multi-AZ)  │
              └─────────────┘
```

### Caching Layer

```
┌────────────────────────────────────────┐
│          Redis/ElastiCache             │
│  ├─► Session storage                   │
│  ├─► Query result cache                │
│  ├─► Rate limiting data                │
│  └─► Temporary data                    │
└────────────────────────────────────────┘
           │
           ▼
┌────────────────────────────────────────┐
│         Django Application             │
│  • Cache API responses                 │
│  • Cache database queries              │
│  • Cache user sessions                 │
└────────────────────────────────────────┘
```

### Database Optimization

```
RDS PostgreSQL
├─► Read Replicas
│   ├─► Read Replica #1 (ap-south-1a)
│   ├─► Read Replica #2 (ap-south-1b)
│   └─► Load balancing reads
│
├─► Connection Pooling
│   └─► PgBouncer
│       • Reduce connection overhead
│       • Connection reuse
│
└─► Optimization
    ├─► Indexes on frequently queried fields
    ├─► Query optimization
    └─► Partitioning large tables
```

---

**Сохраните этот документ для понимания архитектуры системы! 📐**
