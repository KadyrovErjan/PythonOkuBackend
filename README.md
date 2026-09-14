# 🎓 ITAdis CRM - Sistema de Gestión para Centro Educativo

> Sistema completo de gestión contable y administrativa para centros educativos

[![Django](https://img.shields.io/badge/Django-5.1.4-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)]()

---

## 📋 Descripción

ITAdis CRM es un sistema integral de gestión para centros educativos que incluye:

- 👥 **Gestión de Estudiantes** - Control completo de alumnos y grupos
- 💰 **Contabilidad** - Transacciones, pagos, y balance financiero
- 📊 **Analytics** - Reportes y estadísticas en tiempo real
- 🔐 **Multi-usuario** - Sistema de roles (Owner, Admin, Teacher)
- 📱 **API REST** - Backend completamente basado en API
- 🌐 **Multi-idioma** - Soporte para Kyrgyz y Ruso

---

## 🚀 Deployment

### 🌐 Production URLs

- **Frontend**: https://itadiscrm.com.kg
- **API**: https://api.itadiscrm.com.kg/api/v1/
- **Admin**: https://api.itadiscrm.com.kg/admin/
- **Swagger**: https://api.itadiscrm.com.kg/api/schema/swagger-ui/

### 📚 Documentación de Deploy

Hemos preparado guías completas para el deployment:

1. **[DEPLOYMENT_README.md](./DEPLOYMENT_README.md)** - Vista general del proyecto
2. **[QUICK_DEPLOY_CHECKLIST.md](./QUICK_DEPLOY_CHECKLIST.md)** - Checklist rápido (~90 min)
3. **[AWS_DEPLOYMENT_GUIDE.md](./AWS_DEPLOYMENT_GUIDE.md)** - Guía detallada AWS
4. **[VERCEL_FRONTEND_GUIDE.md](./VERCEL_FRONTEND_GUIDE.md)** - Guía Frontend en Vercel
5. **[USEFUL_COMMANDS.md](./USEFUL_COMMANDS.md)** - Comandos útiles

### ⚡ Quick Start

```bash
# 1. Backend на AWS (60 min)
ssh -i "itadis-crm-key.pem" ubuntu@your-elastic-ip
sudo ./deploy_scripts/setup_server.sh
sudo su - itadis
./deploy_scripts/deploy_app.sh

# 2. DNS в Cloudflare (15 min)
# Добавить A records → Elastic IP

# 3. Frontend на Vercel (15 min)
# Import from GitHub → Deploy
```

Ver [QUICK_DEPLOY_CHECKLIST.md](./QUICK_DEPLOY_CHECKLIST.md) para instrucciones completas.

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                      Internet                            │
└────────────────┬────────────────────────┬────────────────┘
                 │                        │
        ┌────────▼────────┐      ┌────────▼────────┐
        │   Cloudflare    │      │   Cloudflare    │
        │      (DNS)      │      │      (DNS)      │
        └────────┬────────┘      └────────┬────────┘
                 │                        │
        ┌────────▼────────┐      ┌────────▼────────┐
        │     Vercel      │      │    AWS EC2      │
        │   (Frontend)    │◄────►│   (Backend)     │
        └─────────────────┘      └────────┬────────┘
                                          │
                                  ┌────────▼────────┐
                                  │    AWS RDS      │
                                  │  (PostgreSQL)   │
                                  └─────────────────┘
```

---

## 💻 Desarrollo Local

### Requisitos

- Python 3.12+
- PostgreSQL 15+
- Docker y Docker Compose (opcional)

### Instalación

```bash
# 1. Clonar repositorio
git clone https://github.com/your-username/ITAdisCRMBackend.git
cd ITAdisCRMBackend/backend

# 2. Crear entorno virtual
python3.12 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar .env
cp .env.example .env
# Editar .env con tus datos

# 5. Migraciones
python manage.py migrate

# 6. Crear superusuario
python manage.py createsuperuser

# 7. Inicializar owner
python manage.py init_owner

# 8. Ejecutar servidor
python manage.py runserver
```

### Con Docker

```bash
# Construir y ejecutar
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

---

## 📦 Stack Tecnológico

### Backend
- **Framework**: Django 5.1.4
- **API**: Django REST Framework 3.15.2
- **Auth**: JWT (djangorestframework-simplejwt)
- **Database**: PostgreSQL 15
- **Password Hashing**: Argon2
- **Documentation**: drf-spectacular (OpenAPI 3)

### DevOps
- **App Server**: Gunicorn
- **Web Server**: Nginx
- **SSL**: Let's Encrypt (Certbot)
- **Cloud**: AWS (EC2, RDS)
- **DNS**: Cloudflare
- **Frontend Host**: Vercel

---

## 📁 Estructura del Proyecto

```
ITAdisCRMBackend/
├── backend/
│   ├── itadis_app/           # Django app principal
│   │   ├── models.py         # Modelos: User, Student, Group, Transaction
│   │   ├── serializers.py    # Serializers DRF
│   │   ├── views/            # ViewSets y APIViews
│   │   ├── services/         # Lógica de negocio
│   │   ├── permissions.py    # Permisos personalizados
│   │   └── filters.py        # Filtros django-filter
│   ├── mysite/               # Configuración Django
│   │   ├── settings.py       # Settings
│   │   └── urls.py           # URL routing
│   ├── manage.py
│   ├── requirements.txt
│   └── .env.example
├── deploy_scripts/           # Scripts de deployment
│   ├── setup_server.sh       # Setup inicial EC2
│   ├── deploy_app.sh         # Deploy aplicación
│   ├── update_app.sh         # Actualización
│   ├── itadis-crm.service    # Systemd service
│   └── nginx_itadiscrm       # Nginx config
├── AWS_DEPLOYMENT_GUIDE.md
├── QUICK_DEPLOY_CHECKLIST.md
├── VERCEL_FRONTEND_GUIDE.md
├── USEFUL_COMMANDS.md
└── README.md
```

---

## 🔐 Seguridad

### Implementado ✅
- ✅ JWT Authentication (access + refresh tokens)
- ✅ HTTPS/SSL obligatorio
- ✅ CORS configurado para dominios específicos
- ✅ Rate limiting (DRF Throttling)
- ✅ Secure cookies (CSRF, Session)
- ✅ Argon2 password hashing
- ✅ SQL injection protection (Django ORM)
- ✅ XSS protection

### Recomendado para Production 🔜
- [ ] AWS CloudWatch monitoring
- [ ] AWS RDS automatic backups
- [ ] fail2ban para protección SSH
- [ ] AWS WAF (Web Application Firewall)

---

## 📊 API Endpoints

### Authentication
```
POST   /api/v1/auth/login/          # Login (JWT)
POST   /api/v1/auth/logout/         # Logout
POST   /api/v1/auth/token/refresh/  # Refresh token
GET    /api/v1/auth/me/             # Current user info
```

### Users
```
GET    /api/v1/users/               # Lista usuarios
POST   /api/v1/users/               # Crear usuario
GET    /api/v1/users/{id}/          # Detalle usuario
PUT    /api/v1/users/{id}/          # Actualizar usuario
DELETE /api/v1/users/{id}/          # Eliminar usuario
```

### Students
```
GET    /api/v1/students/            # Lista estudiantes
POST   /api/v1/students/            # Crear estudiante
GET    /api/v1/students/{id}/       # Detalle estudiante
PUT    /api/v1/students/{id}/       # Actualizar estudiante
DELETE /api/v1/students/{id}/       # Eliminar estudiante
```

### Groups
```
GET    /api/v1/groups/              # Lista grupos
POST   /api/v1/groups/              # Crear grupo
GET    /api/v1/groups/{id}/         # Detalle grupo
PUT    /api/v1/groups/{id}/         # Actualizar grupo
DELETE /api/v1/groups/{id}/         # Eliminar grupo
```

### Transactions
```
GET    /api/v1/transactions/        # Lista transacciones
POST   /api/v1/transactions/        # Crear transacción
GET    /api/v1/transactions/{id}/   # Detalle transacción
PUT    /api/v1/transactions/{id}/   # Actualizar transacción
DELETE /api/v1/transactions/{id}/   # Eliminar transacción
```

### Analytics
```
GET    /api/v1/analytics/dashboard/           # Dashboard data
GET    /api/v1/analytics/financial-summary/   # Resumen financiero
GET    /api/v1/analytics/revenue-trends/      # Tendencias de ingresos
```

Ver documentación completa en **[Swagger UI](https://api.itadiscrm.com.kg/api/schema/swagger-ui/)**

---

## 🧪 Testing

```bash
# Ejecutar todos los tests
python manage.py test

# Test específico
python manage.py test itadis_app.tests.TestStudentModel

# Con coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

---

## 🔄 CI/CD

### GitHub Actions (Recomendado)

Crear `.github/workflows/deploy.yml`:

```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to AWS EC2
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.EC2_HOST }}
          username: itadis
          key: ${{ secrets.EC2_SSH_KEY }}
          script: |
            cd /home/itadis/apps/ITAdisCRMBackend
            ./deploy_scripts/update_app.sh
```

---

## 📝 Comandos Útiles

Ver [USEFUL_COMMANDS.md](./USEFUL_COMMANDS.md) para lista completa.

### Producción

```bash
# Conectar a servidor
ssh -i "itadis-crm-key.pem" ubuntu@your-elastic-ip

# Ver logs
sudo journalctl -u itadis-crm -f

# Reiniciar servicios
sudo systemctl restart itadis-crm nginx

# Actualizar app
cd /home/itadis/apps/ITAdisCRMBackend
./deploy_scripts/update_app.sh
```

---

## 🐛 Troubleshooting

Ver sección completa en [AWS_DEPLOYMENT_GUIDE.md](./AWS_DEPLOYMENT_GUIDE.md#troubleshooting)

### 502 Bad Gateway
```bash
sudo systemctl status itadis-crm
sudo journalctl -u itadis-crm -n 50
sudo systemctl restart itadis-crm nginx
```

### DB Connection Error
```bash
telnet itadis-crm-db.xxxxx.rds.amazonaws.com 5432
# Verificar Security Groups en AWS Console
```

---

## 📞 Soporte

- **Issues**: [GitHub Issues](https://github.com/your-username/ITAdisCRMBackend/issues)
- **Documentation**: Ver archivos `.md` en el repositorio
- **Email**: support@itadis.kg (ejemplo)

---

## 📄 Licencia

Este proyecto es propietario y confidencial.  
© 2024 ITAdis. Todos los derechos reservados.

---

## 🙏 Agradecimientos

- Django y Django REST Framework
- PostgreSQL
- AWS
- Vercel
- Cloudflare

---

**Desarrollado con ❤️ para ITAdis Education Center**

🚀 **[Empezar Deployment →](./QUICK_DEPLOY_CHECKLIST.md)**
