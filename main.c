/*********************************
LEADIY-M3测试程序示例V2.2
作者: Colin
版权所有:  深圳市软芯微电子科技有限公司
芯片型号:  stm32f103CB
*************************************/

#include "string.h"
#include "stm32f10x.h"
#include "sys.h"
#include "usart.h"
#include "delay.h"
#include "drv_Uart.h"


int16_t Gyro[3], Acc[3], Angle[3], Mag[3];
int32_t Altitude, Pressure;
float Temper, GyroDPS[3], AccG[3], MagGauss[3], AngleDeg[3];


/*读两个字节组成一个16位数*/
int16_t ReadW(void)
{
unsigned char BufC;
int16_t BufW;
    
  BufC = uartRead();
  BufW = (uint16_t)BufC;
  BufC = uartRead();
  BufW = (int16_t)(((uint16_t)BufC  << 8) | BufW);
  return BufW;
}


int main(void)
{
unsigned char BufC;
uint16_t BufW; 

  /* 系统初始化*/
  systemInit();

  delay_ms(300);
  printf("LEADIY-M3 TEST V2\r\n");

  while (1)
  {
    if(uartAvailable()) //检测是否收到LEADIY-M3数据
    {  
      BufC = uartRead(); //读一个字节
      if((BufC==0xA7)){  //判断是否为帧 头
        BufC = uartRead(); //读一个字节
        if (BufC==0x7A) { //判断是否为帧头
          BufC = uartRead(); //读一个字节
          switch(BufC) //帧类型判断
          {
            case 0x70: //标识为角速度帧
              BufC = uartRead(); //帧长度，可不用
              BufC = uartRead(); //效验位
              Gyro[0] = ReadW();      //X轴
              Gyro[1] = ReadW();      //Y轴
              Gyro[2] = ReadW();      //Z轴

              /*GYRO的量程为2000度每秒*/
              /* 得到以"dps" ("度/秒")为单位的角速度值*/
              GyroDPS[0] = (float)Gyro[0]*4/16.4;
              GyroDPS[1] = (float)Gyro[1]*4/16.4;
              GyroDPS[2] = (float)Gyro[2]*4/16.4;

              printf("GYRO X：%d  Y：%d  Z：%d\r\n", Gyro[0], Gyro[1], Gyro[2]);
              printf("GyroDPS X: %.2f, Y: %.2f, Z: %.2f\r\n", GyroDPS[0], GyroDPS[1], GyroDPS[2]);
              break;
            case 0x71: //标识为加速度帧
              BufC = uartRead(); //帧长度，可不用
              BufC = uartRead(); //效验位
              Acc[0] = ReadW();      //X轴
              Acc[1] = ReadW();      //Y轴
              Acc[2] = ReadW();      //Z轴

              /*ACC的量程为8G*/
              /*得到以"g"为单位的加速度*/
              AccG[0] = (float)Acc[0] / 4096;
              AccG[1] = (float)Acc[1] / 4096;
              AccG[2] = (float)Acc[2] / 4096;
              printf("ACC X：%d  Y：%d  Z：%d\r\n", Acc[0], Acc[1], Acc[2]);
              printf("AccG X：%.2f  Y：%.2f  Z：%.2f\r\n", AccG[0], AccG[1], AccG[2]);
              break;
            case 0x72: //标识为姿态帧
              BufC = uartRead(); //帧长度，可不用
              BufC = uartRead(); //效验位
              Angle[0] = ReadW();   //X轴角度(横滚)
              Angle[1] = ReadW();   //Y轴角度(俯仰)
              Angle[2] = ReadW();   //Z轴角度(偏航)

              AngleDeg[0] = (float)Angle[0] / 100;
              AngleDeg[1] = (float)Angle[1] / 100;
              AngleDeg[2] = (float)Angle[2] / 100;
              if (AngleDeg[2]<0) AngleDeg[2] += 360; //将航向值转化到0---360度区间
              printf("ANGLE X：%d  Y：%d  Z：%d \r\n", Angle[0], Angle[1], Angle[2]);
              printf("AngleDeg X：%.2f  Y：%.2f  Z：%.2f \r\n", AngleDeg[0], AngleDeg[1], AngleDeg[2]);
              break;
            case 0x73: //标识为 地磁帧
              BufC = uartRead(); //帧长度，可不用
              BufC = uartRead(); //效验位
              Mag[0] = ReadW();   //X轴
              Mag[1] = ReadW();   //Y轴
              Mag[2] = ReadW();   //Z轴

              /*地磁设置为2.5Ga*/
              /*得到以"Gauss"为单位的地磁*/
              MagGauss[0] = (float)Mag[0] / 660; 
              MagGauss[1] = (float)Mag[1] / 660; 
              MagGauss[2] = (float)Mag[2] / 660; 
              printf("Mag X：%d  Y：%d  Z：%d \r\n", Mag[0], Mag[1], Mag[2]);
              printf("MagGauss X：%.2f  Y：%.2f  Z：%.2f \r\n", MagGauss[0], MagGauss[1], MagGauss[2]);
              break;
            case 0x74: //标识为温度、气压帧
              BufC = uartRead(); //帧长度，可不用
              BufC = uartRead(); //效验位
              Temper = ReadW() / 10;   //X轴
              BufW = ReadW();   //气压低16位
              Pressure = (int32_t)(((uint32_t)(ReadW() << 16))|BufW); 
              printf("Temperature(Degree)：%.2f  Pressure(Pa)：%d \r\n", Temper, Pressure);
              break;
            case 0x75: // 标识为高度帧
              BufC = uartRead(); //帧长度，可不用
              BufC = uartRead(); //效验位
              BufW = ReadW();   //高度低16位

              /*得到以"CM"为单位的海拔高度*/
              Altitude = (int32_t)(((uint32_t)(ReadW() << 16))|BufW); 
              printf("Altitude(cm)：%d \r\n", Altitude);
              break;
            default:  break;
          }
        }
      }
    }
  }

}


