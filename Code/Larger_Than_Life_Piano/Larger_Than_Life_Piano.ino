/* Arduino program for the Larger than Life Piano - a House of General Science project.
 * Written for the Fall 2021 Rochester Maker Faire.
 * Written by Will Ebmeyer - 11/18/2021
 * 
 * Reused/modified for an Arduino Uno for Imagine RIT 2022 (previously assumed an Arduino Mega)
 *  -Will Ebmeyer
 * 
 * This program reads from pins 31-44 on an Arduino Mega to determine whether a key
 * has been pressed or released on the piano.  If it detects such an event, it sends
 * a signal over serial to a connected computer in the format "keyDown|[KEY]" or
 * "keyUp|[KEY]."
 * The pins should be connected to the piano keys—which themselves must be connected
 * to GROUND (NOT VOLTAGE, IT DOESN'T WORK WITH VOLTAGE).
*/

#define KEY_COUNT 13
#define DELAY_TIME 1

#define CLK_PIN 9
#define DATA_PIN 11
#define SELECT_PIN 10

bool key_states[KEY_COUNT];
bool prev_key_states[KEY_COUNT];
int on_time[KEY_COUNT];
int off_time[KEY_COUNT];

void setup() {
  // Set up the serial
  Serial.begin(9600);

  // Set up pins
  pinMode(CLK_PIN, OUTPUT);
  pinMode(DATA_PIN, INPUT);
  pinMode(SELECT_PIN, OUTPUT);


  // Populate previous key state array by assuming they're all ON
  // This makes sure the 'key release' signals are sent immediately
  for (int i = 0; i < KEY_COUNT; i++) {
    prev_key_states[i] = true;
  }

  // Make sure to reset the data line
  resetRegister();
}

void pulse() {
  digitalWrite(CLK_PIN, HIGH);
  delay(1);
  digitalWrite(CLK_PIN, LOW);
  delay(1);
}

void resetRegister() {
  for (int i = 0; i < KEY_COUNT; i++) {
    pulse();
  }
}

void prepareRead() {
  // Reset the register
  //resetRegister();

  // Prime the select line
  digitalWrite(SELECT_PIN, HIGH);
  digitalWrite(CLK_PIN, HIGH);
  delay(5);
  digitalWrite(SELECT_PIN, LOW);
  delay(5);
  digitalWrite(CLK_PIN, LOW);
}

bool readNext() {
  // Read the next state
  bool result = digitalRead(DATA_PIN);
  pulse();
  return result;
}

void loop() {
  // Send 'alive' packet
  Serial.println("alive");
  
  // Read from keyboard and send keyDown/keyUp events if applicable
  prepareRead();
  for (int i = 0; i < KEY_COUNT; i++) {
    // Read state of key
    bool key = readNext();

    //Serial.print(key); // Print all key states - used for debugging purposes
    if (key == true) {
      on_time[i]++;
      off_time[i] = 0;
    } else {
      on_time[i] = 0;
      off_time[i]++;
    }

    // Compare key with last available record of key
    if (on_time[i] == DELAY_TIME) {
      key_states[i] = true;
    }
    if (off_time[i] == DELAY_TIME) {
      key_states[i] = false;
    }
    
    if (key_states[i] != prev_key_states[i]) {
      // State changed, send event signal over serial
      if (key == false) {
        Serial.print("keyUp|");
        Serial.print(i);
        Serial.print("\n");
      } else {
        Serial.print("keyDown|");
        Serial.print(i);
        Serial.print("\n");
      }
      prev_key_states[i] = key_states[i];
    }
  }
  //Serial.print("\n"); // Only enable this if you've reenabled the above "Serial.print(key);" line.  This, too, is for debugging purspoes

  // Sleep to reduce strain on the Arduino
  delay(10);
}
