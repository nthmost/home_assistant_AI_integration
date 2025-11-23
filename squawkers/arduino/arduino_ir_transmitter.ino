/*
 * Squawkers McGraw IR Transmitter for Arduino
 *
 * This sketch transmits the IR codes from the GitHub repo
 * to test if they work with your Squawkers.
 *
 * Hardware Setup:
 * - IR LED (940nm) connected to pin 3 (with 100-220Ω resistor)
 * - Button connected to pin 2 (with pull-up resistor)
 *
 * Required Library:
 * - IRremote by shirriff (install via Arduino Library Manager)
 *
 * Instructions:
 * 1. Install IRremote library
 * 2. Connect IR LED to pin 3
 * 3. Connect button to pin 2
 * 4. Upload this sketch
 * 5. Point IR LED at Squawkers
 * 6. Press button to send "dance" command
 */

#include <IRremote.h>

// Pin definitions
const int IR_SEND_PIN = 3;      // IR LED (via 220Ω resistor)
const int BUTTON_PIN = 2;       // S1 button on proto shield (to GND)
const int STATUS_LED = 13;      // LED1 on proto shield (or built-in LED)

// IR carrier frequency
const int CARRIER_FREQ = 38;    // 38kHz

// Squawkers IR timing codes from GitHub
// Format: [mark, space, mark, space, ...] in microseconds

// Dance command
const uint16_t DANCE_CODE[] = {
  3000, 3000, 1000, 2000, 2000, 1000, 1000, 2000,
  2000, 1000, 2000, 1000, 1000, 2000, 2000, 1000, 1000
};
const int DANCE_CODE_LENGTH = 17;

// Reset command
const uint16_t RESET_CODE[] = {
  3000, 3000, 1000, 2000, 2000, 1000, 2000, 1000,
  1000, 2000, 1000, 2000, 2000, 1000, 1000, 2000, 1000
};
const int RESET_CODE_LENGTH = 17;

// Response Mode - Button A
const uint16_t RESPONSE_A_CODE[] = {
  3000, 3000, 1000, 2000, 1000, 2000, 1000, 2000,
  1000, 2000, 2000, 1000, 1000, 2000, 2000, 1000, 1000
};
const int RESPONSE_A_CODE_LENGTH = 17;

IRsend irsend(IR_SEND_PIN);

void setup() {
  Serial.begin(9600);
  pinMode(BUTTON_PIN, INPUT_PULLUP);  // S1 button with internal pull-up
  pinMode(STATUS_LED, OUTPUT);         // LED1 for status indication
  digitalWrite(STATUS_LED, LOW);       // Start with LED off

  Serial.println("Squawkers McGraw IR Transmitter");
  Serial.println("================================");
  Serial.println("Proto Shield v.5 Configuration:");
  Serial.println("  IR LED on pin 3 (via 220ohm resistor)");
  Serial.println("  S1 button on pin 2");
  Serial.println("  LED1 status on pin 13");
  Serial.println("");
  Serial.println("Press S1 button to send DANCE command");
  Serial.println("(Hold for 2 sec to send RESET)");
  Serial.println("");

  // Blink LED to show we're ready
  for (int i = 0; i < 3; i++) {
    digitalWrite(STATUS_LED, HIGH);
    delay(100);
    digitalWrite(STATUS_LED, LOW);
    delay(100);
  }
  Serial.println("Ready!");
}

void loop() {
  // Check if button is pressed
  if (digitalRead(BUTTON_PIN) == LOW) {
    delay(50); // Debounce

    // Check if held for 2 seconds
    unsigned long pressStart = millis();
    while (digitalRead(BUTTON_PIN) == LOW && (millis() - pressStart) < 2000) {
      delay(10);
    }

    if (millis() - pressStart >= 2000) {
      // Long press = RESET
      Serial.println("Sending RESET command...");
      sendSquawkersCode(RESET_CODE, RESET_CODE_LENGTH);
    } else {
      // Short press = DANCE
      Serial.println("Sending DANCE command...");
      sendSquawkersCode(DANCE_CODE, DANCE_CODE_LENGTH);
    }

    // Wait for button release
    while (digitalRead(BUTTON_PIN) == LOW) {
      delay(10);
    }
    delay(200); // Prevent multiple triggers
  }

  // Also allow serial commands for testing
  if (Serial.available()) {
    char cmd = Serial.read();

    if (cmd == 'd' || cmd == 'D') {
      Serial.println("Sending DANCE command (serial)...");
      sendSquawkersCode(DANCE_CODE, DANCE_CODE_LENGTH);
    }
    else if (cmd == 'r' || cmd == 'R') {
      Serial.println("Sending RESET command (serial)...");
      sendSquawkersCode(RESET_CODE, RESET_CODE_LENGTH);
    }
    else if (cmd == 'a' || cmd == 'A') {
      Serial.println("Sending RESPONSE A command (serial)...");
      sendSquawkersCode(RESPONSE_A_CODE, RESPONSE_A_CODE_LENGTH);
    }
  }
}

void sendSquawkersCode(const uint16_t* code, int length) {
  // Turn on status LED while transmitting
  digitalWrite(STATUS_LED, HIGH);

  // Enable IR carrier at 38kHz
  irsend.enableIROut(CARRIER_FREQ);

  // Send the timing pattern
  // code[] contains alternating mark/space durations
  for (int i = 0; i < length; i++) {
    if (i % 2 == 0) {
      // Even index = mark (IR on)
      irsend.mark(code[i]);
    } else {
      // Odd index = space (IR off)
      irsend.space(code[i]);
    }
  }

  // Final space to end transmission
  irsend.space(0);

  // Blink LED rapidly to confirm transmission complete
  for (int i = 0; i < 2; i++) {
    digitalWrite(STATUS_LED, LOW);
    delay(50);
    digitalWrite(STATUS_LED, HIGH);
    delay(50);
  }
  digitalWrite(STATUS_LED, LOW);

  Serial.println("Code sent!");
  Serial.println("Did Squawkers respond?");
  Serial.println("");
}
