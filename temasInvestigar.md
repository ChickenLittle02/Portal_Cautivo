Perfecto — te doy una **guía práctica, completa y paso-a-paso** para montar el *servidor web del portal* en una computadora y **configurar el gateway** (la misma máquina o distinta) para que **intercepte** las solicitudes HTTP de clientes y las entregue al servidor web del portal. Incluiré todos los comandos exactos (Debian/Ubuntu), ejemplos de ficheros de configuración, reglas `iptables` explicadas línea a línea, pruebas y cómo limpiar/persistir las reglas. No hace nada en background: todo lo puedes ejecutar en tu VM de laboratorio ahora mismo.

---

# Resumen de la topología que vamos a crear

* Máquina (gateway) con 2 interfaces en el escenario recomendado:

  * **WAN**: `wlan0` (conectada al hotspot del móvil o a Internet)
  * **LAN**: `wlan1` o `eth1` (la red local donde estarán los clientes)
* El **servidor web del portal** corre en la misma máquina en `0.0.0.0:8080` (puede ser Python) — esto simplifica usando `REDIRECT`. Si el servidor estuviera en otra máquina, usarías `DNAT` a su IP:puerto.

Objetivo: cuando un cliente no autorizado en la LAN haga una petición HTTP, la caja **redirige** esa petición al servidor portal (puerto 8080). Tras autenticarse, el portal marca al cliente como autorizado y el gateway le deja pasar tráfico normal a Internet.

---

# PASO 0 — requisitos e instalación básica

En Debian/Ubuntu instala lo necesario:

```bash
sudo apt update
sudo apt install -y hostapd dnsmasq iptables ipset conntrack tcpdump python3
```

* `hostapd` si vas a crear un AP en la misma máquina (opcional).
* `dnsmasq` para DHCP/DNS en la LAN.
* `ipset` para mantener lista de clientes autorizados.
* `conntrack` para borrar entradas de flujo si necesitas cortar conexiones activas.
* `python3` para el servidor web de ejemplo.

---

# PASO 1 — configurar interfaces y habilitar ip_forward

Asume:

* LAN iface = `wlan1` → IP estática `192.168.50.1/24`
* WAN iface = `wlan0` → obtiene IP por DHCP (hotspot)

Configura la IP LAN y activa forwarding:

```bash
sudo ip link set wlan1 up
sudo ip addr add 192.168.50.1/24 dev wlan1

# Habilitar reenvío IPv4 en el kernel (temporal)
sudo sysctl -w net.ipv4.ip_forward=1

# Para hacerlo persistente:
echo "net.ipv4.ip_forward=1" | sudo tee /etc/sysctl.d/99-ipforward.conf
sudo sysctl --system
```

---

# PASO 2 — DHCP + DNS (dnsmasq) para la LAN

Crea `/etc/dnsmasq.d/lab.conf` con:

```
interface=wlan1
bind-interfaces
dhcp-range=192.168.50.10,192.168.50.200,12h
dhcp-option=3,192.168.50.1    # gateway
dhcp-option=6,192.168.50.1    # DNS server
server=8.8.8.8                # upstream DNS
```

Reinicia dnsmasq:

```bash
sudo systemctl restart dnsmasq
sudo systemctl enable dnsmasq
```

Prueba: conecta un cliente al AP/red y verifica que reciba una IP `192.168.50.x`.

---

# PASO 3 — crear el servidor HTTP (portal) simple en Python

Guarda un archivo `portal_simple.py` con este contenido (solo sirve la página de login y procesa POST; no llama a nada externo):

```python
#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import urllib.parse, sqlite3, time, uuid, html
DB = "portal.db"
PORT = 8080

# init DB minimal
def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users(username TEXT PRIMARY KEY, password TEXT, created_at INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS sessions(session_id TEXT PRIMARY KEY, username TEXT, expiry INTEGER)")
    conn.commit(); conn.close()

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        # simple status or login page
        if self.path.startswith("/status"):
            self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
            return
        self.send_response(200)
        self.send_header("Content-Type","text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"""<html><body>
            <h2>Portal Login</h2>
            <form method="POST" action="/login">
             User: <input name="user"><br>
             Pass: <input name="pass" type="password"><br>
             <input type="submit" value="Login">
            </form></body></html>""")

    def do_POST(self):
        if self.path != "/login":
            self.send_response(404); self.end_headers(); return
        length = int(self.headers.get("Content-Length",0))
        data = urllib.parse.parse_qs(self.rfile.read(length).decode())
        user = data.get("user",[""])[0]
        pwd = data.get("pass",[""])[0]
        now = int(time.time())
        conn = sqlite3.connect(DB); cur = conn.cursor()
        cur.execute("INSERT OR REPLACE INTO users(username,password,created_at) VALUES(?,?,?)",(user,pwd,now))
        sid = str(uuid.uuid4()); expiry = now + 3600
        cur.execute("INSERT INTO sessions(session_id,username,expiry) VALUES(?,?,?)",(sid,user,expiry))
        conn.commit(); conn.close()
        self.send_response(200)
        self.send_header("Content-Type","text/html; charset=utf-8")
        self.send_header("Set-Cookie", f"session_id={sid}; Path=/; HttpOnly")
        self.end_headers()
        self.wfile.write(b"<html><body><h2>Logged in</h2></body></html>")

class ThreadedHTTP(ThreadingMixIn, HTTPServer):
    daemon_threads = True

if __name__ == "__main__":
    init_db()
    s = ThreadedHTTP(("0.0.0.0", PORT), H)
    print("Portal listening on port", PORT)
    s.serve_forever()
```

Ejecuta:

```bash
python3 portal_simple.py
```

(usa `sudo` solo si quieres bind a puerto 80; con 8080 no es necesario).

---

# PASO 4 — crear `ipset` para clientes autorizados

Usaremos un conjunto de IPs llamadas `allowed` (más escalable que reglas individuales).

```bash
sudo ipset create allowed hash:ip
```

(ignora error si ya existe).

---

# PASO 5 — reglas `iptables` para interceptar HTTP y permitir tráfico autorizado

A continuación reglas con explicación **línea a línea**. Ajusta interfaces `wlan1` (LAN) y `wlan0` (WAN) si tus nombres son distintos.

1. Limpieza inicial (solo en la VM de laboratorio; **no** en un host de producción sin consola):

```bash
sudo iptables -F
sudo iptables -t nat -F
sudo iptables -X
```

2. Permitir tráfico a servicios locales (DHCP/DNS si corre en la misma máquina):

```bash
sudo iptables -A INPUT -i wlan1 -p udp --dport 67:68 -j ACCEPT   # DHCP
sudo iptables -A INPUT -i wlan1 -p udp --dport 53 -j ACCEPT     # DNS UDP
sudo iptables -A INPUT -i wlan1 -p tcp --dport 53 -j ACCEPT     # DNS TCP
```

3. Política por defecto para FORWARD — bloquear todo por defecto:

```bash
sudo iptables -P FORWARD DROP
```

4. NAT para que el tráfico autorizado salga con la IP del gateway:

```bash
sudo iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE
```

5. Permitir conexiones establecidas de retorno (necesario para respuestas):

```bash
sudo iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT
```

6. Permitir forward a Internet sólo para IPs en `ipset allowed`:

```bash
sudo iptables -I FORWARD -m set --match-set allowed src -o wlan0 -j ACCEPT
```

7. Interceptar y redirigir HTTP (puerto 80) de clientes **no autorizados** al portal local 8080:

```bash
# Primero: si la fuente está en allowed, RETURN (no redirigir)
sudo iptables -t nat -A PREROUTING -i wlan1 -p tcp --dport 80 -m set --match-set allowed src -j RETURN

# Si no está en allowed, REDIRECT al puerto 8080 (servidor portal corriendo local)
sudo iptables -t nat -A PREROUTING -i wlan1 -p tcp --dport 80 -j REDIRECT --to-port 8080
```

### Por qué esto funciona

* `PREROUTING` en la tabla `nat` cambia el destino del paquete **antes** del enrutado. `REDIRECT` cambia destino al host local en puerto 8080.
* Clientes autorizados están en `ipset allowed` y hacen `RETURN`, por lo que no se toca su tráfico.
* FORWARD policy `DROP` impide que clientes no autorizados lleguen a Internet; cuando el portal autoriza, su IP se añade a `allowed` y la regla de FORWARD permite su tráfico.

---

# PASO 6 — autorizar desde el servidor portal (lógica)

En tu servidor web, cuando validas credenciales debes **añadir la IP del cliente al ipset**. Ejemplo (pseudocódigo Python; aquí se queda dentro de Python si lo prefieres usando `subprocess` — pero pediste no usar comandos externos en versiones previas; para el gateway la única forma real es ejecutar ipset/iptables o exponer una API que el gateway consuma):

Si el servidor está corriendo en la misma máquina del firewall, el script Python puede ejecutar:

```python
import subprocess
subprocess.run(["sudo","ipset","add","allowed", client_ip], check=False)
```

(Nota: para seguridad, dale permisos solo a esos comandos en `/etc/sudoers` para el usuario que corre el servicio).

Si el servidor está en otra máquina, crea una API segura en el gateway o usa SSH con clave para ejecutar `ipset add` en el gateway — siempre teniendo en cuenta seguridad.

---

# PASO 7 — pruebas paso a paso

1. Levanta el portal:

   ```bash
   python3 portal_simple.py
   ```
2. Asegúrate que `ipset allowed` existe:

   ```bash
   sudo ipset list allowed
   ```
3. Aplica las reglas `iptables` anteriores (ajusta interfaces).
4. En el cliente (conectado por DHCP a LAN), abre el navegador y visita `http://example.com` o simplemente `http://192.0.2.1`. Deberías ver la página del portal (porque la petición HTTP fue redirigida al localhost:8080).
5. Introduce credenciales. El portal debe insertar la IP del cliente en `ipset` (ver `sudo ipset list allowed`).
6. Tras autorizar, intenta navegar a `http://example.com` — ahora el navegador deberá llegar a Internet (la regla FORWARD + MASQUERADE permiten salida).

Puedes depurar con:

```bash
# ver reglas
sudo iptables -t nat -L -n -v
sudo iptables -L FORWARD -n -v

# capturar tráfico HTTP en LAN
sudo tcpdump -i wlan1 -n tcp port 80 -A

# ver leases dnsmasq
sudo tail -f /var/log/syslog | grep dnsmasq
```

---

# PASO 8 — cortar sesiones y limpieza

* Para revocar autorización (por expiración o logout):

```bash
sudo ipset del allowed 192.168.50.42
# y eliminar conntrack entradas para cortar conexiones activas:
sudo conntrack -D -s 192.168.50.42
```

* Para limpiar todas las reglas (laboratorio):

```bash
sudo iptables -F
sudo iptables -t nat -F
sudo iptables -X
```

* Para destruir ipset:

```bash
sudo ipset destroy allowed
```

---

# PASO 9 — persistencia y arranque automático

* Guardar reglas (Debian/Ubuntu):

```bash
sudo apt install iptables-persistent
sudo netfilter-persistent save
```

* O usar `iptables-save > /etc/iptables/rules.v4` y `iptables-restore` en arranque.
* Crear systemd unit para el portal Python (ejemplo breve):

```
/etc/systemd/system/portal.service
[Unit]
Description=Captive Portal
After=network.target

[Service]
User=portaluser
ExecStart=/usr/bin/python3 /opt/portal/portal_simple.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

`sudo systemctl enable --now portal.service`

---

# Consideraciones finales y advertencias importantes

* **HTTPS**: no intentes interceptar HTTPS; redirigirlo produce errores de certificado. La técnica correcta es redirigir solo HTTP y confiar en las comprobaciones OS para abrir el portal. Documenta esta limitación.
* **Permisos**: ejecutar `ipset`/`iptables` desde un servicio requiere privilegios. En lugar de ejecutar todo como root, configura `sudoers` para permitir los comandos específicos sin contraseña para el usuario que corre el portal.
* **Seguridad**: no almacenes contraseñas en texto plano en producción; usa `pbkdf2_hmac` para hash y HTTPS para la interfaz administrativa.
* **DoH/DoT**: clientes que usan DNS-over-HTTPS/TLS pueden evitar detección por DNS, la detección basada en HTTP aún suele funcionar (OS checks).
* **Snapshots**: haz snapshot de VM antes de modificar reglas.
* **Testing**: prueba con múltiples clientes, expiración de sesiones y con `conntrack` para entender flujo.

---

Si quieres ahora:

* te genero **un script `setup_gateway.sh`** que aplica las reglas (solo pide que confirmes interfaces `wlan1` y `wlan0`),
* o te doy un **systemd unit** ya listo y un ejemplo `sudoers` seguro para permitir `ipset add/del` sin contraseña,

dime cuál prefieres y te lo creo en este mismo mensaje.
