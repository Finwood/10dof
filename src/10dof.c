#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/delay.h>

#include <stdio.h>

#include "uart.h"
#include "twi.h"
#include "L3G4200D.h"


#define	ADDR_A	0xa6
#define	ADDR_G	0xd2
#define	ADDR_C	0x3c
#define	ADDR_P	0xee

#define OK 0

char ubuf[128];
uint8_t ulen;

#define BMP_DEBUG_MODE	0

uint8_t bmpReadEEPROM (void);
uint8_t bmpGetTempPress (uint8_t precision, int16_t *temperature, int32_t *pressure);
int16_t bmpAC1, bmpAC2, bmpAC3, bmpB1, bmpB2, bmpMB, bmpMC, bmpMD;
uint16_t bmpAC4, bmpAC5, bmpAC6;

volatile int32_t X = 0, Y = 0, Z = 0;
volatile int16_t x = 0, y = 0, z = 0;

int main(void) {
	// enable INT0 for rising edge
//	EICRA |= (1 << ISC01) | (1 << ISC00);
//	EIMSK |= (1 << INT0);

	// set LED pin as output
	DDRD |= (1 << PD4);

	TCCR0B = (1 << CS02) | (0 << CS01) | (1 << CS00); // 1024 prescaler
	TIMSK0 = (1 << TOIE0);

	uartInit();
	twiInit();

	sei();

	twiSetSlave(I2C_ADDR_L3G);
	ulen = sprintf(ubuf, "Gyro \"who-am-i\": 0x%02X\r\n", twiReceive(L3G_WHO_AM_I)); uartSendMultiple(ubuf, ulen);


//	twiSetVal(L3G_CTRL_REG3, 1 << 7); // enable INT1
//	twiSetVal(L3G_INT1_CFG, 1 << 5); // interrupt on Z High event
//	twiSetVal(L3G_CTRL_REG4, 1 << 7); // enable Block Data Update
//	twiSetVal(L3G_INT1_TSH_ZH, 0x00); // 1 dps
//	twiSetVal(L3G_INT1_TSH_ZL, 0x72); // 1 dps
	twiSetVal(L3G_CTRL_REG1, 0b00001100); // 100Hz, cut-off 12.5, switch on, enable z-axis only

/*	while (1) {
//		if (PIND & 1 << 2) {
//			if (twiReceive(L3G_STATUS_REG) & 1 << 2) { // if new z-data available
				
				z = (buf[1] << 8) | buf[0];
//			}
//		}
	}
*/
/*	bmpReadEEPROM();

	uint8_t i;
	int16_t t;
	int32_t p, T, P;

	// 2^3 = 8 values
	#define FOO 3
	while (1) {
		T = 0;
		P = 0;
		for (i = 0; i < (1 << FOO); i++) {
			bmpGetTempPress(3, &t, &p);
			T += t;
			P += p;
		}
		T >>= FOO;
		P >>= FOO;

		ulen = sprintf(ubuf, "T = %li.%01li *C, p = %li.%02li hPa\r\n", T/10, T%10, P/100, P%100); uartSendMultiple(ubuf, ulen);
		_delay_ms(1000);
	}
*/
/*	twiSetSlave(ADDR_A);

	twiSetVal(0x38, 0); // bypass mode
	twiSetVal(0x2D, (1 << 3)); // start measurement
//	twiSetVal(0x2E, (1 << 7)); // enable Data Ready

	uint8_t buf[32];
	ret = twiReceiveMultiple(0x1D, 0x39 - 0x1d + 1, buf);
	ulen = sprintf(ubuf, "twiReceiveMultiple(0x1D, 0x39 - 0x1d + 1, buf) returned with %i (0x%02X)\r\n", ret, TW_STATUS); uartSendMultiple(ubuf, ulen);

	for (uint8_t i = 0x1d; i <= 0x39; i++) {
		ulen = sprintf(ubuf, "0x%02X\t0x%02X\r\n", i, buf[i-0x1d]); uartSendMultiple(ubuf, ulen);
	}

	while (1) {
		ret = twiReceiveMultiple(0x32, 6, buf);

		int16_t xdata, ydata, zdata;

		xdata = buf[0] + (buf[1] << 8);
		ydata = buf[2] + (buf[3] << 8);
		zdata = buf[4] + (buf[5] << 8);

		ulen = sprintf(ubuf, "X: %i, Y: %i, Z: %i\r\n", xdata, ydata, zdata); uartSendMultiple(ubuf, ulen);

		_delay_ms(1000);
	}

	twiStop();
*/
	while (1);
}

ISR (TIMER0_OVF_vect) {
	static uint8_t postscaler = 0;
	static uint8_t z_l, z_h;
	if (++postscaler >= 61) {
		postscaler = 0;
		
		z_h = twiReceive(L3G_OUT_Z_H);
		z_l = twiReceive(L3G_OUT_Z_L);
		
		z = (z_h << 8) | z_l;
		ulen = sprintf(ubuf, "%02X %02X %i\r\n", z_h, z_l, z); uartSendMultiple(ubuf, ulen);
	}
}

/*ISR (INT0_vect) {
//	uint8_t buf[6];
//	int16_t x, y, z;
//	static int32_t X = 0, Y = 0, Z = 0;

	PORTD ^= (1 << PD4);

	twiReceiveMultiple(0x28, 2, buf);
	x = (buf[1] << 8) | buf[0];

	twiReceiveMultiple(0x2a, 2, buf);
	y = (buf[1] << 8) | buf[0];

	twiReceiveMultiple(0x2c, 2, buf);
	z = (buf[1] << 8) | buf[0];

	ulen = sprintf(ubuf, "X: %i\tY: %i\tZ: %i\r\n", x, y, z); uartSendMultiple(ubuf, ulen);

}*/

uint8_t bmpReadEEPROM (void) {
	uint8_t buf[22], ret;

	twiSetSlave(ADDR_P);
	ret = twiReceiveMultiple(0xaa, 22, buf);
	twiStop();
	if (ret != 0) return 1;

	bmpAC1 = (buf[ 0] << 8) + buf[ 1];
	bmpAC2 = (buf[ 2] << 8) + buf[ 3];
	bmpAC3 = (buf[ 4] << 8) + buf[ 5];
	bmpAC4 = (buf[ 6] << 8) + buf[ 7];
	bmpAC5 = (buf[ 8] << 8) + buf[ 9];
	bmpAC6 = (buf[10] << 8) + buf[11];
	bmpB1  = (buf[12] << 8) + buf[13];
	bmpB2  = (buf[14] << 8) + buf[15];
	bmpMB  = (buf[16] << 8) + buf[17];
	bmpMC  = (buf[18] << 8) + buf[19];
	bmpMD  = (buf[20] << 8) + buf[21];

#if BMP_DEBUG_MODE == 1
	ulen = sprintf(ubuf, "AC1 = %i\r\n", bmpAC1); uartSendMultiple(ubuf, ulen);
	ulen = sprintf(ubuf, "AC2 = %i\r\n", bmpAC2); uartSendMultiple(ubuf, ulen);
	ulen = sprintf(ubuf, "AC3 = %i\r\n", bmpAC3); uartSendMultiple(ubuf, ulen);
	ulen = sprintf(ubuf, "AC4 = %u\r\n", bmpAC4); uartSendMultiple(ubuf, ulen);
	ulen = sprintf(ubuf, "AC5 = %u\r\n", bmpAC5); uartSendMultiple(ubuf, ulen);
	ulen = sprintf(ubuf, "AC6 = %u\r\n", bmpAC6); uartSendMultiple(ubuf, ulen);
	ulen = sprintf(ubuf, "B1  = %i\r\n", bmpB1);  uartSendMultiple(ubuf, ulen);
	ulen = sprintf(ubuf, "B2  = %i\r\n", bmpB2);  uartSendMultiple(ubuf, ulen);
	ulen = sprintf(ubuf, "MB  = %i\r\n", bmpMB);  uartSendMultiple(ubuf, ulen);
	ulen = sprintf(ubuf, "MC  = %i\r\n", bmpMC);  uartSendMultiple(ubuf, ulen);
	ulen = sprintf(ubuf, "MD  = %i\r\n", bmpMD);  uartSendMultiple(ubuf, ulen);
#endif

	return 0;
}

uint8_t bmpGetTempPress (uint8_t precision, int16_t *temperature, int32_t *pressure) {
	uint8_t buf[3], ret;
	precision &= 0b11; // 0..3

	twiSetSlave(ADDR_P);
	twiSetVal(0xf4, 0x2e);
	twiStop(); // yes, unfortunately this is necessary
	_delay_us(4500);
	ret = twiReceiveMultiple(0xf6, 2, buf);
	if (ret != 0) {twiStop(); return 1;}

	uint16_t ut = (buf[0] << 8) | buf[1];

#if BMP_DEBUG_MODE == 1
	ulen = sprintf(ubuf, "\r\n"); uartSendMultiple(ubuf, ulen);
	ulen = sprintf(ubuf, "buf: 0x%02X 0x%02X\r\n", buf[0], buf[1]); uartSendMultiple(ubuf, ulen);
	ulen = sprintf(ubuf, "UT  = %u\r\n", ut); uartSendMultiple(ubuf, ulen);
#endif

	twiSetVal(0xf4, 0x34 + (precision << 6));
	twiStop();
	switch (precision) {
		case 0: _delay_us(4500); break;
		case 1: _delay_us(7500); break;
		case 2: _delay_us(13500); break;
		default: _delay_us(25500);
	}
	ret = twiReceiveMultiple(0xf6, 3, buf);
	if (ret != 0) {twiStop(); return 2;}

	twiStop();

	uint32_t up = (((uint32_t)buf[0] << 16) | ((uint32_t)buf[1] << 8) | buf[2]) >> (8 - precision);

#if BMP_DEBUG_MODE == 1
	ulen = sprintf(ubuf, "buf: 0x%02X 0x%02X 0x%02X\r\n", buf[0], buf[1], buf[2]); uartSendMultiple(ubuf, ulen);
	ulen = sprintf(ubuf, "UP  = %lu\r\n", up); uartSendMultiple(ubuf, ulen);
	ulen = sprintf(ubuf, "--------------------------------\r\n"); uartSendMultiple(ubuf, ulen);
#endif

	int16_t T;
	int32_t bmpB3, bmpB5, bmpB6, bmpX1, bmpX2, bmpX3, p;
	uint32_t bmpB4, bmpB7;

	// calculate true temperature
	bmpX1 = ((ut - (int32_t)bmpAC6) * (int32_t)bmpAC5) >> 15;
	bmpX2 = ((int32_t)bmpMC << 11) / (bmpX1 + (int32_t)bmpMD);
	bmpB5 = bmpX1 + bmpX2;
	T = (bmpB5 + 8) >> 4;

#if BMP_DEBUG_MODE == 1
	ulen = sprintf(ubuf, "X1  = %li\r\n", bmpX1); uartSendMultiple(ubuf, ulen);
	ulen = sprintf(ubuf, "X2  = %li\r\n", bmpX2); uartSendMultiple(ubuf, ulen);
	ulen = sprintf(ubuf, "B5  = %li\r\n", bmpB5); uartSendMultiple(ubuf, ulen);
	ulen = sprintf(ubuf, "T   = %li\r\n", T); uartSendMultiple(ubuf, ulen);
	ulen = sprintf(ubuf, "--------------------------------\r\n"); uartSendMultiple(ubuf, ulen);
#endif


	*temperature = T;

	// calculate true pressure
	bmpB6 = bmpB5 - 4000;
	bmpX1 = ((int32_t)bmpB2 * ((bmpB6 * bmpB6) >> 12)) >> 11;
	bmpX2 = ((int32_t)bmpAC2 * bmpB6) >> 11;
	bmpX3 = bmpX1 + bmpX2;
	bmpB3 = ((((int32_t)bmpAC1 * 4 + bmpX3) << precision) + 2) / 4;

#if BMP_DEBUG_MODE == 1
	ulen = sprintf(ubuf, "B6  = %li\r\n", bmpB6); uartSendMultiple(ubuf, ulen);
	ulen = sprintf(ubuf, "X1  = %li\r\n", bmpX1); uartSendMultiple(ubuf, ulen);
	ulen = sprintf(ubuf, "X2  = %li\r\n", bmpX2); uartSendMultiple(ubuf, ulen);
	ulen = sprintf(ubuf, "X3  = %li\r\n", bmpX3); uartSendMultiple(ubuf, ulen);
	ulen = sprintf(ubuf, "B3  = %li\r\n", bmpB3); uartSendMultiple(ubuf, ulen);
#endif

	bmpX1 = ((int32_t)bmpAC3 * bmpB6) >> 13;
	bmpX2 = ((int32_t)bmpB1 * ((bmpB6 * bmpB6) >> 12)) >> 16;
	bmpX3 = (bmpX1 + bmpX2 + 2) >> 2;
	bmpB4 = ((uint32_t)bmpAC4 * (uint32_t)(bmpX3 + 32768)) >> 15;
	bmpB7 = ((uint32_t)up - bmpB3) * (uint32_t)(50000UL >> precision);

#if BMP_DEBUG_MODE == 1
	ulen = sprintf(ubuf, "X1  = %li\r\n", bmpX1); uartSendMultiple(ubuf, ulen);
	ulen = sprintf(ubuf, "X2  = %li\r\n", bmpX2); uartSendMultiple(ubuf, ulen);
	ulen = sprintf(ubuf, "X3  = %li\r\n", bmpX3); uartSendMultiple(ubuf, ulen);
	ulen = sprintf(ubuf, "B4  = %lu\r\n", bmpB4); uartSendMultiple(ubuf, ulen);
	ulen = sprintf(ubuf, "B7  = %lu\r\n", bmpB7); uartSendMultiple(ubuf, ulen);
#endif

	p = (bmpB7 < 0x80000000 ? (bmpB7 * 2) / bmpB4 : (bmpB7 / bmpB4) * 2);
	bmpX1 = (p >> 8) * (p >> 8);

#if BMP_DEBUG_MODE == 1
	ulen = sprintf(ubuf, "p   = %li\r\n", p); uartSendMultiple(ubuf, ulen);
	ulen = sprintf(ubuf, "X1  = %li\r\n", bmpX1); uartSendMultiple(ubuf, ulen);
#endif

	bmpX1 = (bmpX1 * 3038) >> 16;
	bmpX2 = (-7357 * p) >> 16;

#if BMP_DEBUG_MODE == 1
	ulen = sprintf(ubuf, "X1  = %li\r\n", bmpX1); uartSendMultiple(ubuf, ulen);
	ulen = sprintf(ubuf, "X2  = %li\r\n", bmpX2); uartSendMultiple(ubuf, ulen);
#endif

	p = p + ((bmpX1 + bmpX2 + (int32_t)3791) >> 4);

#if BMP_DEBUG_MODE == 1
	ulen = sprintf(ubuf, "p   = %li\r\n", p); uartSendMultiple(ubuf, ulen);
	ulen = sprintf(ubuf, "--------------------------------\r\n"); uartSendMultiple(ubuf, ulen);
#endif

	*pressure = p;

	return 0;
}

