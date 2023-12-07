// MQ137
#include <math.h>

#define Vcc 5
#define RL 1.0  //The value of resistor RL is 1K --> measured
#define R0 12.96  //The value of resistor R0 is 1K --> measured + calculated
#define m -0.276 //Enter calculated Slope
#define b -0.224 //Enter calculated intercept

float calculate_ppm(float analog_value){
  float VRL = 0;
  float Rs = 0;
  double ppm = 0;

  VRL = analog_value*(Vcc/4096.0); //Convert analog value to voltage
  Rs = ((Vcc/VRL)-1) * RL;
  
  float ratio = Rs/R0;
  ppm = pow(10, ((log10(ratio)-b)/m)); //use formula to calculate ppm
  return ppm;
}