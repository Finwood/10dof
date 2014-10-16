#ifndef __TWI_H__
#define __TWI_H__

#include <util/twi.h>
#include <avr/io.h>

#define TWI_WAIT while (!(TWCR & (1 << TWINT)))

void twiInit (void);
void twiSetSlave (uint8_t addr);
uint8_t twiStart (uint8_t addr);
uint8_t twiRepStart (uint8_t addr);
uint8_t twiSend (uint8_t data);
void twiStop (void);

uint8_t twiSetVal (uint8_t regAddr, uint8_t data);
uint8_t twiReceiveMultiple (uint8_t regAddr, uint8_t count, uint8_t *buf);
uint8_t twiReceive(uint8_t regAddr);

#endif // __TWI_H__

