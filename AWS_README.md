# 🚀 AWS EC2 - EVA02 Deployment

## 🔐 Credenciales de Acceso EC2

```
Usuario: fr.pisani@duocuc.cl
Contraseña: Hola112243@
```

## 📍 Conexión a Instancia EC2

### Opción 1: AWS Console

1. Ir a [AWS Console](https://console.aws.amazon.com)
2. Navegar a **EC2 > Instances**
3. Buscar la instancia de **EVA02**
4. Usar **Connect** o conectarse vía SSH

### Opción 2: SSH desde Terminal

```bash
# Conectarse a la instancia EC2
ssh -i "tu-clave-privada.pem" ec2-user@tu-ip-publica

# Ejemplo
ssh -i "eva02-key.pem" ec2-user@54.123.45.67
```

## 🐳 Docker Compose en AWS

### Verificar estado de servicios

```bash
# SSH a la instancia
ssh -i "eva02-key.pem" ec2-user@[IP-PUBLICA]

# Ver contenedores corriendo
sudo docker-compose ps

# Ver logs
sudo docker-compose logs -f app
sudo docker-compose logs -f prometheus
sudo docker-compose logs -f grafana
```

## 📊 Acceso a Grafana en AWS

```
URL: http://[IP-PUBLICA-EC2]:3000

Usuario: admin
Contraseña: admin2
```

## 🔍 Acceso a Prometheus en AWS

```
URL: http://[IP-PUBLICA-EC2]:9090
```

## 🌐 Acceso a la Aplicación FastAPI en AWS

```
URL: http://[IP-PUBLICA-EC2]:8000
Documentación: http://[IP-PUBLICA-EC2]:8000/api/v1/openapi.json
```

## 🔧 Comandos Útiles en EC2

```bash
# Ver IP pública asignada
curl http://169.254.169.254/latest/meta-data/public-ipv4

# Reiniciar Docker Compose
sudo docker-compose restart

# Actualizar aplicación (pull de cambios)
cd /home/ec2-user/eva02
git pull origin main
sudo docker-compose up -d --build

# Ver recursos usados
free -h          # Memoria
df -h            # Disco
top              # Procesos
```

## 🔐 Security Groups (Firewall AWS)

Asegúrate que estos puertos estén abiertos:

| Puerto | Servicio | Acceso |
|--------|----------|--------|
| 8000 | FastAPI | HTTP |
| 3000 | Grafana | HTTP |
| 9090 | Prometheus | HTTP (interno) |
| 5432 | PostgreSQL | Interno (no público) |
| 22 | SSH | Desde tu IP |

## 📝 Notas Importantes

- **Reemplazar [IP-PUBLICA-EC2]** con la IP asignada a tu instancia
- **Guarda la clave privada (.pem)** en lugar seguro
- **Los datos persisten** en volúmenes de Docker en la instancia
- **Hacer backup** periódicamente de la base de datos

---

**Última actualización**: 2026-06-23
