String cmd;
int moduleCount = 5;
int ptime = 10;

#define CLK_PIN 9
#define DATA_PIN 11
#define SELECT_PIN 10

void setup() {
  Serial.begin(9600);
  Serial.println("Starting!");

  // Set up pins
  pinMode(CLK_PIN, OUTPUT);
  pinMode(DATA_PIN, INPUT);
  pinMode(SELECT_PIN, OUTPUT);

  delay(10);
  //Serial.println(F("Syntax: p[2-digit pin id] [value 5-25]"));
}

void pulse() {
  digitalWrite(CLK_PIN, HIGH);
  delay(ptime);
  digitalWrite(CLK_PIN, LOW);
  delay(ptime);
}

void resetRegister() {
  for (int i = 0; i < moduleCount; i++) {
    pulse();
  }
}

int readData() {
  delay(10);
  return digitalRead(DATA_PIN);
}

void execute(String command) {
  if (command.substring(0, 4) == "help") {
    // Help command
    Serial.println(F("----------- Available Commands: -----------"));
    Serial.println(F("  help       - Prints this message"));
    Serial.println(F("  clk        - Sends a pulse on the CLK line"));
    Serial.println(F("  reset      - Pulses the CLK enough times to clear the shift register"));
    Serial.println(F("  get        - Gathers and prints the states of all modules"));
    Serial.println(F("  set        - Sets the number of modules"));
    Serial.println(F("  data       - Gets the current state of the DATA line"));
    Serial.println(F("  select [X] - Sets the SELECT line to 0 or 1"));
    Serial.println(F("  ptime [X]  - Sets the pulse half-time"));
    Serial.println(F("  con        - Powers the clock line"));
    Serial.println(F("  coff       - Unpowers the clock line"));
    Serial.println(F("-------------------------------------------"));
    
  } else if (command.substring(0, 3) == "clk") {
    // Send a pulse along the clock line
    pulse();
    int dataLine = readData();
    Serial.print(F("DATA Pin is now: "));
    Serial.println(dataLine);
  
  } else if (command.substring(0, 5) == "reset") {
    // Pulses the clock enough times to clear the shift register
    resetRegister();
    
  } else if (command.substring(0, 3) == "get") {
    // Gets and prints the state of each module
    // Reset the register
    resetRegister();
    // Prime the select line
    digitalWrite(SELECT_PIN, HIGH);
    delay(50);
    pulse();
    digitalWrite(SELECT_PIN, LOW);
    delay(50);
    for (int i = 0; i < moduleCount; i++) {
      int value = readData();
      Serial.print(i);
      Serial.print(F(": "));
      Serial.println(value);
      pulse();
      //delay(50);
    }
    
  } else if (command.substring(0, 3) == "set") {
    // Sets the module count to the provided number
    moduleCount = (command.substring(4)).toInt();
    
  } else if (command.substring(0, 4) == "data") {
    // Prints the current state of the data pin
    Serial.println(readData());
    
  } else if (command.substring(0, 6) == "select") {
    // Prints the current state of the data pin
    int newState = (command.substring(7, 8)).toInt();
    digitalWrite(SELECT_PIN, newState);
    
  } else if (command.substring(0, 5) == "ptime") {
    // Prints the current state of the data pin
    int ptime = (command.substring(6)).toInt();
    Serial.print(F(">Set to "));
    Serial.println(ptime);
    
  } else if (command.substring(0, 3) == "con") {
    // Prints the current state of the data pin
    digitalWrite(CLK_PIN, HIGH);
    
  } else if (command.substring(0, 4) == "coff") {
    // Prints the current state of the data pin
    digitalWrite(CLK_PIN, LOW);
  }
}

void loop() {
  if(Serial.available() > 0) {
    delay(100);
    cmd = "";
    while (Serial.available() > 0) {
      cmd += Serial.readString();
    }
    Serial.print(F("> "));
    
    Serial.println(cmd);
    execute(cmd);
  }
  delay(10);
}
