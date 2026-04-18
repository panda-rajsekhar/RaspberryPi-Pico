const int ORANGE = 1;
const int BLUE   = 5;
const int GREEN  = 9;

unsigned long previousPanda = 0;
const int interval = 300;

int state = 0;

void setup() {
  pinMode(ORANGE, OUTPUT);
  pinMode(BLUE, OUTPUT);
  pinMode(GREEN, OUTPUT);
}

void loop() {
  unsigned long Panda = millis();

  if (Panda - previousPanda >= interval) {
    previousPanda = Panda;

    switch (state) {
      case 0: // GREEN ON
        digitalWrite(GREEN, HIGH);
        digitalWrite(ORANGE, LOW);
        digitalWrite(BLUE, LOW);
        break;

      case 1: // ORANGE ON
        digitalWrite(GREEN, LOW);
        digitalWrite(ORANGE, HIGH);
        digitalWrite(BLUE, LOW);
        break;

      case 2: // BLUE ON
        digitalWrite(GREEN, LOW);
        digitalWrite(ORANGE, LOW);
        digitalWrite(BLUE, HIGH);
        break;

      case 3: // ORANGE + BLUE ON
        digitalWrite(GREEN, LOW);
        digitalWrite(ORANGE, HIGH);
        digitalWrite(BLUE, HIGH);
        break;

      case 4: // ALL OFF
        digitalWrite(GREEN, LOW);
        digitalWrite(ORANGE, LOW);
        digitalWrite(BLUE, LOW);
        break;
    }

    state = (state + 1) % 5;
  }

  // Non-blocking space for future logic
}
