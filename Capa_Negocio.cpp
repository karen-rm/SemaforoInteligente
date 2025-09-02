#include <WiFi.h>
#include <WebServer.h>

// Configuración de red Wi-Fi
const char *ssid = "BUAP_Trabajadores";   //"BUAP_Trabajadores";//"Wifi";           // Cambia por tu SSID                        
const char *password = "BuaPW0rk.2017";  //"BuaPW0rk.2017"; //"12345678";   // Cambia por tu contraseña Wi-Fi        

// Asignación de pines
#define PIN_LED_VERDE     15  // Salida LED VERDE
#define PIN_LED_AMARILLO  16  // Salida LED AMARILLO
#define PIN_LED_ROJO      17  // Salida LED ROJO

// Crear un servidor web en el puerto 80
WebServer server(80);

// Variables para la rutina
unsigned long tiempoAnterior = 0;
int fase = 0;
bool rutinaActiva = false;
int parpadeos = 0;
bool ledEncendido = false;

unsigned long duracionVerde = 5000;
unsigned long duracionAmarillo = 2000;
unsigned long duracionRojo = 9000;

void configurarRutas(){
  
  // Rutas para controlar el LED VERDE
  server.on("/led/verde/on", HTTP_GET, []() {
    digitalWrite(PIN_LED_VERDE, HIGH);  // Enciende el LED
    server.send(200, "text/plain", "LED Verde Encendido");
  });

    server.on("/led/verde/off", HTTP_GET, []() {
    digitalWrite(PIN_LED_VERDE, LOW);  // Apaga el LED
    server.send(200, "text/plain", "LED Verde Apagado");
  });

  server.on("/led/amarillo/on", HTTP_GET, []() {
    digitalWrite(PIN_LED_AMARILLO, HIGH);  // Enciende el LED
    server.send(200, "text/plain", "LED AMARILLO Encendido");
  });

    server.on("/led/amarillo/off", HTTP_GET, []() {
    digitalWrite(PIN_LED_AMARILLO, LOW);  // Apaga el LED
    server.send(200, "text/plain", "LED AMARILLO Apagado");
  });

  server.on("/led/rojo/on", HTTP_GET, []() {
    digitalWrite(PIN_LED_ROJO, HIGH);  // Enciende el LED
    server.send(200, "text/plain", "LED rojo Encendido");
  });

  server.on("/led/rojo/off", HTTP_GET, []() {
    digitalWrite(PIN_LED_ROJO, LOW);  // Apaga el LED
    server.send(200, "text/plain", "LED rojo Apagado");
  });

  server.on("/rutinaSemaforo/on", HTTP_GET, []() {
    if (!rutinaActiva) {
      digitalWrite(PIN_LED_VERDE, LOW);
      digitalWrite(PIN_LED_AMARILLO, LOW);
      digitalWrite(PIN_LED_ROJO, LOW);
      rutinaActiva = true;
      fase = 0;
      tiempoAnterior = millis();
      Serial.println("Rutina iniciada");
    }
    server.send(200, "text/plain", "Rutina encendida");
  });

  server.on("/rutinaSemaforo/off", HTTP_GET, []() {
    rutinaActiva = false;
    digitalWrite(PIN_LED_VERDE, LOW);
    digitalWrite(PIN_LED_AMARILLO, LOW);
    digitalWrite(PIN_LED_ROJO, LOW);
    server.send(200, "text/plain", "Rutina apagada");
    Serial.println("Rutina detenida");
  });

  server.on("/configurar", HTTP_GET, []() {
  if (server.hasArg("verde"))     duracionVerde    = server.arg("verde").toInt();
  if (server.hasArg("amarillo"))  duracionAmarillo = server.arg("amarillo").toInt();
  if (server.hasArg("rojo"))      duracionRojo     = server.arg("rojo").toInt();

  String respuesta = "Tiempos actualizados (en ms):\n";
  respuesta += "Verde: " + String(duracionVerde) + "\n";
  respuesta += "Amarillo: " + String(duracionAmarillo) + "\n";
  respuesta += "Rojo: " + String(duracionRojo);

  server.send(200, "text/plain", respuesta);
});


}

void setup() {
  // Inicialización de la comunicación serie
  Serial.begin(9600);

  // Configuración de pines
  pinMode(PIN_LED_VERDE, OUTPUT);  // Salida LED VERDE
  pinMode(PIN_LED_AMARILLO, OUTPUT);  // Salida LED AMARILLO
  pinMode(PIN_LED_ROJO, OUTPUT);  // Salida LED ROJO
    
  // Conectar a la red Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Conectando a WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("El dispositivo se ha conectado");
  Serial.println(WiFi.localIP()); 

  digitalWrite(PIN_LED_VERDE, HIGH);
  digitalWrite(PIN_LED_AMARILLO, HIGH);
  digitalWrite(PIN_LED_ROJO, HIGH);
  configurarRutas();
  // Iniciar el servidor
  server.begin();
  Serial.println("Servidor HTTP iniciado");
}

void loop() {
  // Maneja las solicitudes entrantes
  server.handleClient();

  if (!rutinaActiva) return;

  unsigned long ahora = millis();

  switch (fase) {
    case 0: // Verde encendido 5s
      digitalWrite(PIN_LED_VERDE, HIGH);
      if (ahora - tiempoAnterior >= duracionVerde) {
        digitalWrite(PIN_LED_VERDE, LOW);
        parpadeos = 0;
        fase = 1;
        tiempoAnterior = ahora;
      }
      break;

    case 1: // Verde parpadeo ON
      digitalWrite(PIN_LED_VERDE, HIGH);
      if (ahora - tiempoAnterior >= 500) {
        fase = 2;
        tiempoAnterior = ahora;
      }
      break;

    case 2: // Verde parpadeo OFF
      digitalWrite(PIN_LED_VERDE, LOW);
      if (ahora - tiempoAnterior >= 500) {
        parpadeos++;
        if (parpadeos < 3) {
          fase = 1;
        } else {
          fase = 3;
        }
        tiempoAnterior = ahora;
      }
      break;

    case 3: // Amarillo 1.5s
      digitalWrite(PIN_LED_AMARILLO, HIGH);
      if (ahora - tiempoAnterior >= duracionAmarillo) {
        digitalWrite(PIN_LED_AMARILLO, LOW);
        fase = 4;
        tiempoAnterior = ahora;
      }
      break;

    case 4: // Rojo 9.5s
      digitalWrite(PIN_LED_ROJO, HIGH);
      if (ahora - tiempoAnterior >= duracionRojo) {
        digitalWrite(PIN_LED_ROJO, LOW);
        fase = 0;  //Reiniciar rutina
        tiempoAnterior = ahora;
      }
      break;
  }
}