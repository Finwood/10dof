#include <avr/io.h>
#include <avr/interrupt.h>
//#include <util/delay.h>

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

volatile int32_t X = 0, Y = 0, Z = 0;
volatile int16_t x = 0, y = 0, z = 0;

int main(void) {
	// enable INT0 for rising edge
//	EICRA |= (1 << ISC01) | (1 << ISC00);
//	EIMSK |= (1 << INT0);

	// set LED pin as output, set high
	DDRD |= (1 << PD4);
	PORTD |= (1 << PD4);

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

	while (1);
}

ISR (TIMER0_OVF_vect) {
	static uint8_t postscaler = 0;
	static uint8_t z_l, z_h;
	if (++postscaler >= 61) {
		postscaler = 0;
		PORTD ^= (1 << PD4);

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

