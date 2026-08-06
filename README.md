# Módulo Sonar
## Resumo do projeto
Este projeto consiste na implementação de um módulo sonar utilizando um servo motor e um sensor ultrassônico para realizar o monitoramento do ambiente.

O servo motor realiza uma varredura contínua de 0° a 180°, enquanto o sensor ultrassônico mede a distância até possíveis obstáculos. As informações de ângulo do servo e distância detectada são exibidas em tempo real em um display LCD.

O sistema possui sinalização visual e sonora para indicar a presença de objetos:

- LED verde: permanece aceso quando nenhum obstáculo é detectado.
- LED vermelho: acende quando um objeto é identificado.
- Buzzer: emite um alerta sonoro sempre que há uma detecção.

OBS: Além do modo automático de varredura, o projeto também oferece um modo manual, permitindo ao usuário controlar a posição do servo por meio de um joystick.

## Funcionalidades:
- Varredura automática de 0° a 180°.
- Medição de distância utilizando sensor ultrassônico.
- Exibição do ângulo e da distância em um display LCD.
- Sinalização visual com LEDs de status.
- Alerta sonoro por buzzer.
- Controle manual do servo via joystick.

## Componentes utilizados
- Arduino UNO
- Jumpers
- LED
- Resistores
- LCD 16 X 2
- Resistor 200Ω
- Micro servo
- Sensor de distância ultrassônico
- Buzzer
- Joystick

## Galeria do protótipo
### Protótipo físico
<img width="1539" height="783" alt="Screenshot_3" src="https://github.com/user-attachments/assets/fb07b6f3-607e-4b7f-8221-6629d4468006" />


### Visão Esquemática
<img width="1064" height="825" alt="Screenshot_4" src="https://github.com/user-attachments/assets/fa602fbf-c74f-4742-be32-ab3e62b0e54f" />

# Versão física final
<img width="864" height="492" alt="Frente - Módulo sonar" src="https://github.com/user-attachments/assets/068d3fad-9ced-4cf1-863e-eeb158ae6369" />
<img width="792" height="651" alt="Costas - Módulo sonar" src="https://github.com/user-attachments/assets/37ad170f-a36b-4663-bf06-345b1a33f062" />

