#include <Servo.h>
#include <EEPROM.h>

#include <Wire.h>
#include <MMA8653.h>
MMA8653 accel;

int posEEP = 0;

// #define EEPROM_OUT_

// -----------------------------------
// ピン配置
// -----------------------------------
// DCモータ
const byte DC_MOTOR_DRIVER_A_01    = 2;
const byte DC_MOTOR_DRIVER_A_02    = 4;
const byte DC_MOTOR_DRIVER_B_01    = 7;
const byte DC_MOTOR_DRIVER_B_02    = 8;
const byte DC_MOTOR_DRIVER_PWM_A   = 3;
const byte DC_MOTOR_DRIVER_PWM_B   = 5;
// サーボモータ
const byte servoMotorPinNumber[8] = { 2, 4, 7, 8, 9, 10, 11, 12 };
// LED
const byte ledPinNumber[6] = { 14, 15, 16, 17, 18, 19 };
// ブザー
const byte buzzerPinNumber[6] = { 14, 15, 16, 17, 18, 19 };
// タッチセンサー
const byte touchSensorPinNumber[6] = { 14, 15, 16, 17, 18, 19 };
// センサー
const byte sensorPinNumber[8] = {0, 1, 2, 3, 4, 5, 6, 7 };

// 入力ピン番号(デジタル)
const byte digitalInOutPinNumber[6] = { 14, 15, 16, 17, 18, 19 };
// 入力ピン番号(アナログ)
const byte analogInputPinNumber[8] = {0, 1, 2, 3, 4, 5, 6, 7 };
// 入力ピン状態
const byte ServoPinOffset = 2;    // サーボモータピンオフセット
const byte SensorPinOffset = 10;  // センサーピンオフセット
byte analogInputPinState[8];  // 0:digital, 1:analog, 2:parts, 3:open
const byte DIGITAL     = 0;   // デジタル入力
const byte ANALOG      = 1;   // アナログ入力
const byte I2C         = 2;   // I2C入力
const byte OUTPUTPARTS = 3;   // 出力パーツ
const byte OPEN        = 4;   // 開放

byte pinState[18];  // 接続状態

boolean IsSVMultiAction = false;
byte SvmNumber = 0;
byte SvmDelay = 0;
byte SvmPorts[8];
byte SvmDegrees[8];

// -----------------------------------
// パーツID
// -----------------------------------
const byte PIDOpen        = 0x00;
const byte PIDDC          = 0x01;
const byte PIDSV          = 0x02;
const byte PIDLED         = 0x03;
const byte PIDBuzzer      = 0x04;
const byte PIDColorLED    = 0x05;
const byte PIDLightSensor = 0x10;
const byte PIDTouchSensor = 0x11;
const byte PIDSoundSensor = 0x12;
const byte PIDIRSensor    = 0x13;
const byte PIDAccelerationSensor = 0x14;
const byte PIDButton      = 0x15;

// -----------------------------------
// 通信プロトコル
// -----------------------------------
#define SCRATCH_COMMAND_HEAD1    (0x54)
#define SCRATCH_COMMAND_HEAD2    (0xFE)
#define SCRATCH_COMMAND_DCON     (64)
#define SCRATCH_COMMAND_DCOFF    (68)
#define SCRATCH_COMMAND_MTID     (128)
// ハードウェア初期値
#define SV_INIT_VAL  (90)

// -----------------------------------
// カラーLEDの色
// -----------------------------------
#define White 0
#define Red 1
#define Green 2
#define Blue 3
#define Cyan 4
#define Magenta 5
#define Yellow 6

// 制御変数
int inputState = 0;         // 受信状態変数
// サーボモーター
Servo sv[8];

// 音高
const byte freqOffset = 48;
const unsigned int FREQUENCY[] = {
//  33, 35, 37, 39, 41, 44, 46, 49, 52, 55, 58, 62,
//  65, 69, 73, 78, 82, 87, 92, 98, 104, 110, 117, 123,
  130, 139, 147, 156, 165, 175, 185, 196, 208, 220, 233, 247,  // 48～
  262, 277, 294, 311, 330, 349, 370, 392, 415, 440, 466, 494,  // 60～
  523, 554, 587, 622, 659, 698, 740, 784, 831, 880, 932, 988,  // 72～
  1047, 1109, 1175, 1245, 1319, 1397, 1480, 1568, 1661, 1760, 1865, 1976,  // 84～
  2093, 2217, 2349, 2489, 2637, 2794, 2960, 3136, 3322, 3520, 3729, 3951,  // 96～
  4186
};

void startBuzzer(byte pin, byte code);
void stopBuzzer(byte pin);
void colorLedControl(byte color, byte sw, byte pos);
void multiServoSyncWriteWithDelay(byte port[], byte deg[], byte num, byte dt);

#ifdef EEPROM_OUT_
int eepWritePos;
int eepReadPos;
#endif
bool waitForConfInfo;
bool isSetIOConf;
// ---------------------------------------------------------------------
// 概要    ：初期化処理
// Date    ：2012/-/-  0.01  新規作成
// ---------------------------------------------------------------------
void setup() {
//  Serial.begin(9600);
  Serial.begin(115200);
  Serial.flush();

  randomSeed(analogRead(0)); //

  for (int i = 0;i < 8;i++) {
    analogInputPinState[i] = OPEN;  // センサーピンを全て開放に設定
  }
  waitForConfInfo = true;
  // ボード起動済みデータを送信
  ScratchBoardSensorReport(128, 128);

#ifdef EEPROM_OUT_ 
  eepWritePos = 0;
#endif
}

int rand_num;

// ---------------------------------------------------------------------
// 概要    ：メイン処理
// Date    ：2012/-/-  0.01  新規作成
// ---------------------------------------------------------------------
void loop() {
  int id ,data;
  int sample;
  static byte sindx = 0;
  
  // シリアルポートからデータ受信
  if (readSerialPort(&id, &data)) {
    // データを受信した場合、ボードへ出力
    outputSignal(id, data);
  } else {
    // サーボモータの値を送信する
//    delay(100);
  }
}

void readSensor(byte pin) {
  int sample = 0;
  switch (analogInputPinState[pin]) {
    case DIGITAL:      // デジタルセンサー入力
      sample = digitalRead(digitalInOutPinNumber[pin]);
    break;
    case ANALOG:       // アナログセンサー入力
      sample = analogRead(analogInputPinNumber[pin]);
      sample = map(sample, 0, 1024, 0, 101);
    break;
    case I2C:          // I2C通信(加速度のみ対応)
      // 加速度センサ接続時の処理
      int sensVal;
      accel.update();
      sensVal = accel.getX();
      sample = map(sensVal, -128, 128, 0, 101);
      Serial.write(sample & 0xff);
      sensVal = accel.getY();
      sample = map(sensVal, -128, 128, 0, 101);
      Serial.write(sample & 0xff);
      sensVal = accel.getZ();
      sample = map(sensVal, -128, 128, 0, 101);
    break;
    default:  // 開放/出力パーツ
    break;
  }
  Serial.write(sample & 0xff);
}

// ---------------------------------------------------------------------
// 概要    ：DCモータピン初期化処理
// Date    ：2013/09/06  0.01  新規作成
// ---------------------------------------------------------------------
void initDCMotor(byte pin) {
  if (pin == 0) {
    // サーボモーターのデタッチ
    sv[4].detach();    
    sv[5].detach();    
    
    pinMode(DC_MOTOR_DRIVER_A_01, OUTPUT);
    pinMode(DC_MOTOR_DRIVER_A_02, OUTPUT);
    digitalWrite(DC_MOTOR_DRIVER_A_01, LOW);
    digitalWrite(DC_MOTOR_DRIVER_A_02, LOW);
  } else {
    // サーボモーターのデタッチ
    sv[6].detach();    
    sv[7].detach();    

    pinMode(DC_MOTOR_DRIVER_B_01, OUTPUT);
    pinMode(DC_MOTOR_DRIVER_B_02, OUTPUT);
    digitalWrite(DC_MOTOR_DRIVER_B_01, LOW);
    digitalWrite(DC_MOTOR_DRIVER_B_02, LOW);
  }    
}

// ---------------------------------------------------------------------
// 概要    ：サーボモータピン初期化処理
// Date    ：2013/09/06  0.01  新規作成
// ---------------------------------------------------------------------
void initSVMotor(byte pin) {
  sv[pin].attach(servoMotorPinNumber[pin], 500, 2500);
}

// ---------------------------------------------------------------------
// 概要    ：センサーピンの初期化処理
// Date    ：2013/09/06  0.01  新規作成
// ---------------------------------------------------------------------
void initSensorPin(byte pin, byte parts) {
  switch (parts) {
    case PIDOpen:                // 開放
    
    break;
    case PIDLED:                 // LED
    case PIDBuzzer:              // ブザー
    case PIDColorLED:            // カラーLED
      // 出力パーツ
      analogInputPinState[pin] = OUTPUTPARTS;
      pinMode(digitalInOutPinNumber[pin], OUTPUT);
    break;
    case PIDLightSensor:         // 光センサー
    case PIDSoundSensor:         // 音センサー
    case PIDIRSensor:            // 赤外線センサー
    // アナログ入力設定
      analogInputPinState[pin] = ANALOG;
    break;
    case PIDAccelerationSensor:  // 加速度センサー
      // I2C入力設定
      analogInputPinState[pin] = I2C;
      Wire.begin();
      accel.begin(false, 2);
    break;
    case PIDTouchSensor:         // タッチセンサー
    case PIDButton:              // ボタン
      // デジタル入力設定
      analogInputPinState[pin] = DIGITAL;
      pinMode(digitalInOutPinNumber[pin], INPUT_PULLUP);
    break;
  }
}


void ScratchBoardSensorReport(int sensor, int value) //PicoBoard protocol, 2 bytes per sensor
{
  Serial.write( B10000000
                | ((sensor & B1111)<<3)
                | ((value>>7) & B111));
  Serial.write( value & B1111111);
}

boolean readSerialPort(int *id, int *data)
{
  int inByte, sensorHighByte;

  if (Serial.available() > 1)
  {
    inByte = Serial.read();
    if (inByte >= 128) // Are we receiving the word's header?
    {
      sensorHighByte = inByte;
      *id = ((inByte >> 4) & 0x07);
      while (!Serial.available()); // Wait for the end of the word with data
      inByte = Serial.read();
      if (inByte <= 127) // This prevents Linux ttyACM driver to fail
      {
        *data = ((sensorHighByte & 0x0F) << 7) | (inByte & 0x7F);
        return true;
      }
    }
  }
  return false;
}


#define DCMOTOR_ON   (1)
#define DCMOTOR_OFF  (2)
#define DCMOTOR_PWR  (4)

// ---------------------------------------------------------------------
// 概要    ：基板からの信号に対する処理
// Date    ：2013/09/06  0.01  新規作成
// ---------------------------------------------------------------------
void outputSignal(int id, unsigned int data) {
  int target_drv1, target_drv2, target_pwm;
  int act, cfg;

  switch (id) {
    case 0:  // DC Motor
    {
      byte pin = (data >> 10) & 0x0001;

      if (pin == 0) {
        target_pwm = DC_MOTOR_DRIVER_PWM_A;
        target_drv1 = DC_MOTOR_DRIVER_A_01;
        target_drv2 = DC_MOTOR_DRIVER_A_02;
      } else {
        target_pwm = DC_MOTOR_DRIVER_PWM_B;
        target_drv1 = DC_MOTOR_DRIVER_B_01;
        target_drv2 = DC_MOTOR_DRIVER_B_02;
      }

      act = ((data >> 7) & 0x007);        // 動作の取得
      cfg = (data & 0x007f);    // 設定値の取得
      if (act == DCMOTOR_ON) {               // モータON
        if (cfg == 0) {                      // cw.
          digitalWrite(target_drv1, HIGH);
          digitalWrite(target_drv2, LOW);
        } else if (cfg == 1) {               // ccw.
          digitalWrite(target_drv1, LOW);
          digitalWrite(target_drv2, HIGH);
        }
      } else if (act == DCMOTOR_OFF) {       // モータOFF
        if (cfg == 0) {                      // brake
          digitalWrite(target_drv1, HIGH);
          digitalWrite(target_drv2, HIGH);
        } else if (cfg == 1) {               // coast
          digitalWrite(target_drv1, LOW);
          digitalWrite(target_drv2, LOW);
        }
      } else if (act == DCMOTOR_PWR) {       // モータパワー設定
        analogWrite(target_pwm, cfg*2.55);
      } else {
      }
    }
    break;

    case 1:  // Servo motor
    {
      byte pin = (data >> 8) & 0x0007;
      byte deg = data & 0x00FF;
      if (IsSVMultiAction) {
#ifdef EEPROM_OUT_
      EEPROM.write(eepWritePos, 0x10);
      eepWritePos++;
#endif        
        SvmPorts[SvmNumber] = pin;
        SvmDegrees[SvmNumber] = deg;
        SvmNumber++;
      } else {
#ifdef EEPROM_OUT_
        EEPROM.write(eepWritePos, 0x11);
        eepWritePos++;
#endif
        sv[pin].write(deg);
      }
    }
    break;

    case 2:  // Buzzer
    {
      byte pin = (data >> 8) & 0x0007;
      byte onOff = (data >> 7) & 0x0001;
      
      if (onOff == 1) {
        byte freq = data & 0x007f;
        startBuzzer(pin, freq - freqOffset);
      } else {
        stopBuzzer(pin);
      }
    }
    break;

    case 3:  // LED
    {
      byte pin = (data >> 8) & 0x0007;
      byte onOff = (data >> 7) & 0x0001;
      
      digitalWrite( ledPinNumber[pin], (onOff == 0) ? LOW : HIGH) ;
    }
    break;
    
    case 5:  // Servomotors
    {
      byte subID = (data >> 7) & 0x0f;
      if(subID == 0) {
        byte flag = (data >> 6) & 0x0001;
  //      SvmNumber = (data >> 7) & 0x0007;
        if (flag == 0) {  // start
  #ifdef EEPROM_OUT_
          EEPROM.write(eepWritePos, 0x20);
          eepWritePos++;
  #endif
          SvmNumber = 0;                // 角度を設定するサーボの数
          IsSVMultiAction = true;      // 複数サーボモーターモード開始
          SvmDelay = (data) & 0x003F;  // 1度移動あたりの遅延(ms)
        } else {          // end
  #ifdef EEPROM_OUT_
          EEPROM.write(eepWritePos, 0x21);
          eepWritePos++;
  #endif
          IsSVMultiAction = false;     // 複数サーボモーターモード終了
          multiServoSyncWriteWithDelay(SvmPorts, SvmDegrees, SvmNumber, SvmDelay);
        }
      } else if (subID == 1) {
        byte pin = data & 0x07;
        readSensor(pin);
      }
    }
    break;

    case 4:  // I/O configuration
    {
      // ボードとの通信開始の合図
      // 入力処理の場合は、センサー入力を有効にする
      waitForConfInfo = false;
      
      byte pin = (data >> 6) & 0x001f;  // All
      byte parts = (data) & 0x001F;     // 
/*      
      pinState[pin] = parts;            // 接続されているパーツ情報を保存
      EEPROM.write(pin, parts);         // EEPROMに接続情報を退避
*/      
      // パーツごとに初期化処理を行う
      switch (parts) {
        case PIDDC:                  // DCモータ
          initDCMotor(pin);
        break;
        case PIDSV:                  // サーボモータ
          initSVMotor(pin - ServoPinOffset);
        break;

        case PIDLightSensor:         // 光センサー
        case PIDSoundSensor:         // 音センサー
        case PIDIRSensor:            // 赤外線センサー
        case PIDAccelerationSensor:  // 加速度センサー
        case PIDTouchSensor:         // タッチセンサー
        case PIDButton:              // ボタン
        case PIDLED:                 // LED
        case PIDBuzzer:              // ブザー
        case PIDColorLED:            // カラーLED
          initSensorPin(pin -SensorPinOffset, parts);
        break;
      }
    }
    break;

    // 終了
    case 7:
    {
      Serial.end();
    }
    break;
  }
}

// ---------------------------------------------------------------------
// 概要    : ブザー出力処理
// 引数    : byte pin       ブザー出力ピン位置
//         : byte code      コードインデックス
// Date    : 2012/-/-  0.01  新規作成
// ---------------------------------------------------------------------
void startBuzzer(byte pin, byte code)
{
  pinMode(buzzerPinNumber[pin], OUTPUT);
  tone(buzzerPinNumber[pin], FREQUENCY[code]);
}

void stopBuzzer(byte pin)
{
  noTone(buzzerPinNumber[pin]);
}

// ---------------------------------------------------------------------
// 概要     : 複数サーボモータ処理(同期回転)+遅延時間
// 引数     : byte port[]   接続ピンIndex
//          : byte deg[]    角度
//          : byte num      サーボモータの数
//          : byte dt       1度あたりの遅延時間[ms]
// Date     : 2013/09/03 0.01  新規作成
// ---------------------------------------------------------------------
void multiServoSyncWriteWithDelay(byte port[], byte deg[], byte num, byte dt) {
#ifdef EEPROM_OUT_
  EEPROM.write(eepWritePos, 0x30);
  eepWritePos++;
  EEPROM.write(eepWritePos, num);
  eepWritePos++;
  EEPROM.write(eepWritePos, dt);
  eepWritePos++;
  for (int i = 0;i < num;i++) {
    EEPROM.write(eepWritePos, port[i]);
    eepWritePos++;
    EEPROM.write(eepWritePos, deg[i]);
    eepWritePos++;
  }
#endif
  byte maxDelta = 0;
  byte before[8];
  double delta[8];
  
  // 最大変位角度を取得
  for (int i = 0;i < num;i++) {
    before[i] = sv[port[i]].read();  // 設定前の角度を取得
    delta[i] = deg[i] - before[i];           // 差分を取得
    maxDelta = (abs(delta[i]) > maxDelta) ? abs(delta[i]) : maxDelta;
  }
  for (int i = 0;i < num;i++) {
    delta[i] = (double)(delta[i]) / (double)(maxDelta);
  }
  for (int t = 1; t <= (int)maxDelta; t++) {
    for (int i = 0; i < num; i++) {
      sv[port[i]].write(before[i]+delta[i]*t);
    }
    // センサー送信が何もない場合のためにデータを送っておく
    ScratchBoardSensorReport(128, 128);
    delay(dt);
  }  
}

