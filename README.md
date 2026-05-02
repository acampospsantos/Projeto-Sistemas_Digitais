# Módulo Sonar
## Resumo do projeto
Projeto consiste num módulo sonar: o servo se movimenta de 0 a 180º, enquanto o sensor ultrassônico faz o monitoramento do ambiente. Dados com a angulação do servo e se algo foi detectado estarão sendo impressos em tempo real pelo display LCD.

## Componentes utilizados
- Arduino UNO
- Jumpers
- LCD 16 X 2
- Resistor 200Ω
- Micro servo
- Sensor de distância ultrassônico
- Buzzer

## Galeria do protótipo
### Protótipo físico
<img width="1306" height="680" alt="Screenshot_3" src="https://github.com/user-attachments/assets/af9473e0-fef8-4c06-8d4d-1bddcd4cfeb5" />


### Visão Esquemática
<img width="985" height="766" alt="Screenshot_4" src="https://github.com/user-attachments/assets/7c67abb8-d020-48dd-b18a-200642f65d82" />


### Implementação
```
//Importação de bibliotecas
#include <LiquidCrystal.h>
#include <Servo.h>

//Criação dos Objetos
LiquidCrystal lcd(7,6,5,4,3,2); //Criei objeto --> Passando pinos q o display tá conectado
Servo servo1; //Objeto criado da biblioteca do Servo


//Definição dos pinos
#define pinServo 11
#define pinEcho 8
#define pinTriger 9
#define pinBuzzer 13
#define pinLed 12

//Variáveis 
int pos; //Posição º do Servo motor


void setup(){
  Serial.begin(9600);
  //Configurações iniciais do LCD
  lcd.begin(16, 2);//Configura o modelo do display em nosso caso 16×2 --> Passo quantas colunas e linhas tem o Display
  lcd.clear(); //Comando pra limpar a tela
  
  //Configurações iniciais do Servo motor
  servo1.attach(pinServo, 500, 2500); //Define que o Servo está conectado a Porta 11
  servo1.write(0);
}

void loop(){
  funcServoMotor();
  //distanciaObjeto();
}


//Função padrão Ultrassônico
long readUltrasonicDistance(int triggerPin, int echoPin){
  pinMode(triggerPin, OUTPUT);  // Clear the trigger
  digitalWrite(triggerPin, LOW);
  delayMicroseconds(2);
  // Sets the trigger pin to HIGH state for 10 microseconds
  digitalWrite(triggerPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(triggerPin, LOW);
  pinMode(echoPin, INPUT);
  // Reads the echo pin, and returns the sound wave travel time in microseconds
  return pulseIn(echoPin, HIGH);
}


//Função do Servo Motor
void funcServoMotor(){
  for (pos = 0; pos <= 180; pos = pos + 1) {
    servo1.write(pos);
    funcSensorUltrassonico(pos);
    delay(10);
  }
  for(pos = 180; pos >= 0; pos = pos - 1){
    servo1.write(pos);
    funcSensorUltrassonico(pos);
    delay(10);
  }
}


//Função do Sensor Ultrassônico + Display
void funcSensorUltrassonico(int pos){
  lcd.clear();
  //Posiciona o cursor na coluna e linha indicada no comando
  lcd.setCursor(3,0); //Setta texto - coluna x linha
  lcd.print("Ang: "); //imprime o texto que vai ser expresso
  lcd.print(pos); //imprime o texto que vai ser expresso
  lcd.print("º");
  
  if (0.01723 * readUltrasonicDistance(pinTriger, pinEcho) <= 30) { //(unidade cm)
    lcd.setCursor(3,1); //Setta texto - coluna x linha
    lcd.print("Detectado!"); //imprime o texto que vai ser expresso
    tone(pinBuzzer, 100);
    piscaLed();
  } else if (0.01723 * readUltrasonicDistance(pinTriger, pinEcho) > 30) {
    lcd.setCursor(3,1); //Setta texto - coluna x linha
    lcd.print(""); //imprime o texto que vai ser expresso
    noTone(pinBuzzer);
  }
  delay(50);    
}

void piscaLed(){
  digitalWrite(pinLed, HIGH);
  delay(300);
  digitalWrite(pinLed, LOW);
  delay(300);
}
void distanciaObjeto(){
  int distancia = 0.01723 * readUltrasonicDistance(pinTriger, pinEcho);
  Serial.print("Distancia pro Objeto: ");
  Serial.print(distancia);
  Serial.println("cm");
  delay(100);
}
```
