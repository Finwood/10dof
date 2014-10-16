#include "twi.h"

#define	TWI_ROLE_NONE	0b0000
#define	TWI_ROLE_MT		0b0111
#define	TWI_ROLE_MR		0b0110
#define	TWI_ROLE_ST		0b0101
#define	TWI_ROLE_SR		0b0100

uint8_t _twiRole = TWI_ROLE_NONE;

#define TWI_IS_MASTER		((_twiRole & 0b0110) == 0b0110)
#define TWI_IS_SLAVE		((_twiRole & 0b0110) == 0b0100)
#define TWI_IS_TRANSMITTER	((_twiRole & 0b0101) == 0b0101)
#define TWI_IS_RECEIVER		((_twiRole & 0b0101) == 0b0100)

void _twiSendRaw (uint8_t data);
uint8_t _twiReceiveRaw (uint8_t ack);

#define	TWI_ADDR_MASK	0xfe
uint8_t _twiActiveSlave = 0x00;

void twiInit (void) {
	// set bit rate to 100KHz, see manual p. 215
	// TWBR = (f_CPU / f_SCL - 16) / (2 * prescaler)

	TWSR = 0;
	TWBR = 72;
}

void twiSetSlave (uint8_t addr) {
	_twiActiveSlave = addr;
}

uint8_t twiStart (uint8_t addr) {
	if (_twiRole == TWI_ROLE_NONE || TWI_IS_MASTER) {
		TWCR = (1<<TWINT) | (1<<TWSTA) | (1<<TWEN); // send START
		TWI_WAIT;

		if (!(TW_STATUS == TW_START || TW_STATUS == TW_REP_START)) {
			_twiRole = TWI_ROLE_NONE;
			return 1;
		}

		// else

		_twiSendRaw (addr);

		if (!(TW_STATUS == TW_MR_SLA_ACK || TW_STATUS == TW_MT_SLA_ACK)) {
			_twiRole = TWI_ROLE_NONE;
			return 2;
		}

		// else

		_twiActiveSlave = addr & TWI_ADDR_MASK;

		if (addr & TW_READ)
			_twiRole = TWI_ROLE_MR;
		else
			_twiRole = TWI_ROLE_MT;

		return 0;

	} else return 3;
}

uint8_t twiRepStart (uint8_t addr) {
	return twiStart (addr);
}

void twiStop (void) {
	TWCR = (1 << TWINT) | (1 << TWSTO) | (1 << TWEN);
	while(TWCR & (1 << TWSTO)); // wait
	_twiRole = TWI_ROLE_NONE;
}

uint8_t twiSend (uint8_t data) {
	if (TWI_IS_TRANSMITTER) {
		_twiSendRaw (data);

		if ((_twiRole == TWI_ROLE_MT && TW_STATUS == TW_MT_DATA_ACK) || (_twiRole == TWI_ROLE_ST && TW_STATUS == TW_ST_DATA_ACK)) {
			return 0;
		} else return 2;

	} else return 1;
}

void _twiSendRaw (uint8_t data) {
	TWDR = data;
	TWCR = (1 << TWINT) | (1 << TWEN);
	TWI_WAIT;
}

uint8_t twiSetVal (uint8_t regAddr, uint8_t data) {
	uint8_t ret;

	// (repeated) start to reset any pending operations
	ret = twiStart(_twiActiveSlave + TW_WRITE);
	if (ret != 0) return (1 + (ret << 4));

	ret = twiSend(regAddr);
	if (ret != 0) return (2 + (ret << 4));

	ret = twiSend(data);
	if (ret != 0) return (3 + (ret << 4));

	// else
	return 0;
}

uint8_t _twiReceiveRaw (uint8_t ack) {
	TWCR = (1 << TWINT) | (1 << TWEN) | (ack ? (1 << TWEA) : 0);
	TWI_WAIT;
	return TWDR;
}

uint8_t twiReceive(uint8_t regAddr) {
	uint8_t buf;
	twiReceiveMultiple(regAddr, 1, &buf);
	return buf;
}

uint8_t twiReceiveMultiple (uint8_t regAddr, uint8_t count, uint8_t *buf) {
	uint8_t ret;

	// (repeated) start to reset any pending operations
	ret = twiStart(_twiActiveSlave + TW_WRITE);
	if (ret != 0) return (1 + (ret << 4));

	ret = twiSend(regAddr);
	if (ret != 0) return (2 + (ret << 4));

	ret = twiRepStart(_twiActiveSlave + TW_READ);
	if (ret != 0) return (3 + (ret << 4));

	for (uint8_t i = 0; i < count; i++) {
		buf[i] = _twiReceiveRaw(i < (count - 1));
		if (!(TW_STATUS == TW_MR_DATA_ACK || TW_STATUS == TW_MR_DATA_NACK)) return 4;
	}

	// else
	return 0;
}

