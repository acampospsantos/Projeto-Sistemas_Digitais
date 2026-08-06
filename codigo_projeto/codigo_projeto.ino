// ====================================================================
//  Radar Ultrassônico — Arduino UNO
//
//  O servo carrega um sensor ultrassônico (HC-SR04) e existem 2 modos:
//    AUTOMÁTICO -> o servo varre sozinho de 0° a 180° e volta.
//    MANUAL     -> o joystick controla o ângulo do servo.
//  Apertar o botão do joystick troca de um modo para o outro.
//
//  O sensor mede a distância o tempo todo. Se algo entrar a até 50 cm,
//  o LED vermelho acende e o buzzer apita. Caso contrário, o LED verde
//  fica aceso. O ângulo e a distância aparecem no display LCD.
// ====================================================================

// ----- Bibliotecas ---------------------------------------------------------------------------------------------------
#include <Wire.h>               // comunicação I2C (usada pelo display)
#include <LiquidCrystal_I2C.h>  // controla o display LCD
#include <Servo.h>              // controla o servo motor

// ----- Display e Servo ------------------------------------------------------------------------------------------------
LiquidCrystal_I2C lcd(0x27, 16, 2);  // display de 16 colunas x 2 linhas
Servo servo;

// ----- Pinos ----------------------------------------------------------------------------------------------------------
#define pinServo 10
#define pinTrigger 9 // ultrassônico: envia o pulso de som
#define pinEcho 8 // ultrassônico: recebe o eco de volta
#define pinBuzzer 13
#define pinLedVermelho 12
#define pinLedVerde 11
#define pinJoyX A0 // eixo X do joystick
#define pinBotao 2 // botão do joystick (apertar)

// ----- Configuração que você pode mudar --------------------------------------------------------------------------------
const int DISTANCIA_ALERTA = 50; // distância (cm) que dispara o alerta

// ----- Variáveis de controle --------------------------------------------------------------------------------------------
int anguloServo = 0; // posição atual do servo (0 a 180)
int direcao = 1; // no modo automático: +1 = indo, -1 = voltando
bool modoManual = false; // false = automático, true = joystick
bool botaoAntes = false; // guarda se o botão já estava apertado

// -------------------------------------------------------------------------------------------------------------------------
void setup() {
  Serial.begin(9600); // envia "angulo,distancia" para o sonar no PC (Python)
  // configura os pinos
  pinMode(pinTrigger, OUTPUT);
  pinMode(pinEcho, INPUT);
  pinMode(pinBuzzer, OUTPUT);
  pinMode(pinLedVermelho, OUTPUT);
  pinMode(pinLedVerde, OUTPUT);
  pinMode(pinBotao, INPUT_PULLUP); // HIGH quando solto, LOW quando apertado
  // liga o display
  lcd.init();
  lcd.backlight();
  // liga o servo e coloca no ângulo inicial
  servo.attach(pinServo, 500, 2500);  // 500/2500 = alcance do servo (em µs)
  servo.write(anguloServo);
}

//---------------------------------------------------------------------------------------------------------------------------

void loop() {
  verificaBotao();   // troca de modo se o botão foi apertado
  if (modoManual) {
    moveServoComJoystick();
  } else {
    moveServoAutomatico();
  }
  float distancia = medeDistancia();
  mostraNoLCD(distancia);
  verificaAlerta(distancia);
  enviaParaPC(distancia);  // manda angulo e distancia para o sonar no PC
  delay(15);  // pequena pausa; aumente este número para o servo ir mais devagar
}

// Envia "angulo,distancia" pela serial para o programa de visualizacao (Python).
void enviaParaPC(float distancia) {
  Serial.print(anguloServo);
  Serial.print(",");
  Serial.println(distancia, 1);  // 1 casa decimal
}

// Troca entre automático e manual quando o botão é apertado.
void verificaBotao() {
  bool apertadoAgora = (digitalRead(pinBotao) == LOW);
  // só troca no instante em que o botão passa de solto para apertado
  if (apertadoAgora && !botaoAntes) {
    modoManual = !modoManual;
  }
  botaoAntes = apertadoAgora;
}

// Modo automático: anda 1 grau por vez e inverte ao chegar nas pontas.
void moveServoAutomatico() {
  anguloServo = anguloServo + direcao;
  if (anguloServo >= 180) direcao = -1;  // chegou no fim: começa a voltar
  if (anguloServo <= 0)   direcao =  1;  // voltou ao início: vai de novo
  servo.write(anguloServo);
}

// Modo manual: o eixo X do joystick define o ângulo do servo.
void moveServoComJoystick() {
  int leitura = analogRead(pinJoyX);            // valor de 0 a 1023
  anguloServo = map(leitura, 0, 1023, 0, 180);  // converte para 0 a 180
  servo.write(anguloServo);
}

// Mede a distância em centímetros usando o sensor ultrassônico.
float medeDistancia() {
  // envia um pulso curto (10 µs) pelo trigger
  digitalWrite(pinTrigger, LOW);
  delayMicroseconds(2);
  digitalWrite(pinTrigger, HIGH);
  delayMicroseconds(10);
  digitalWrite(pinTrigger, LOW);
  // mede quanto tempo o eco demorou a voltar (em microssegundos)
  long tempo = pulseIn(pinEcho, HIGH, 25000);  // espera no máximo 25 ms
  return tempo * 0.01723;  // transforma o tempo em centímetros
}

// Mostra o ângulo, o modo e a distância no display.
void mostraNoLCD(float distancia) {
  lcd.setCursor(0, 0);
  lcd.print("Ang: ");
  lcd.print(anguloServo);
  lcd.print("   "); // apaga sobras do número anterior
  lcd.setCursor(9, 0);
  lcd.print(modoManual ? "MANUAL" : "AUTO  ");
  lcd.setCursor(0, 1);
  lcd.print("Dist: ");
  if (distancia > 0) {
    lcd.print(distancia, 1);
    lcd.print(" cm   "); // espaços limpam sobras de uma medida maior
  } else {
    lcd.print("N/D       "); // nada detectado (espaços limpam a linha)
  }
}

// Liga o alerta (LED vermelho + buzzer) quando há algo perto.
void verificaAlerta(float distancia) {
  bool perto = (distancia > 0 && distancia <= DISTANCIA_ALERTA);
  if (perto) {
    digitalWrite(pinLedVerde, LOW);
    digitalWrite(pinLedVermelho, HIGH);
    tone(pinBuzzer, 1000); // apita em 1000 Hz
  } else {
    digitalWrite(pinLedVermelho, LOW);
    digitalWrite(pinLedVerde, HIGH);
    noTone(pinBuzzer); // silêncio
  }
}