#include "uart.h"

uint8_t uartWriteBuf[UART_BUFFERSIZE];
volatile uint8_t uartIdxPending = 0, uartIdxCurrent = 0;

uint8_t _uartSendByte (void);
void _uartAppendBuffer (char data);

void (*_uartCallbackFunc)(void) = 0;

void uartInit (void) {
	// set USART Baud Rate Register as defined in <util/setbaud.h>, see Manual p.175
	UBRR0H = UBRRH_VALUE;
	UBRR0L = UBRRL_VALUE;

	// double speed mode, if necessary
	UCSR0A |= (USE_2X << U2X0);

	// enable Rx and Tx, interrupt on Tx complete
	UCSR0B = (1 << RXEN0) | (1 << TXEN0) | (0 << RXCIE0) | (1 << TXCIE0) | (0 << UDRIE0);

	// 8N1
	UCSR0C = (0 << USBS0) | (1 << UCSZ00) |(1 << UCSZ01);
}

void uartSend (char data) {
	uartSendMultiple(&data, 1);
}

void uartSendMultiple (char *data, uint8_t count) {
	uartSendMultipleWithCallback(data, count, 0);
}

void uartSendMultipleWithCallback (char *data, uint8_t count, void (*cbFunc)(void)) {
	for (uint8_t i = 0; i < count; i++)
		_uartAppendBuffer(data[i]);
	_uartCallbackFunc = cbFunc;
	_uartSendByte();
}

void _uartAppendBuffer (char data) {
	uartWriteBuf[uartIdxPending] = data;
	uartIdxPending = (uartIdxPending + 1) % UART_BUFFERSIZE;
}

uint8_t _uartSendByte (void) {
	if (uartIdxPending != uartIdxCurrent) {
		UDR0 = uartWriteBuf[uartIdxCurrent];
		uartIdxCurrent = (uartIdxCurrent + 1) % UART_BUFFERSIZE;
		return 1;
	} else {
		return 0;
	}
}

// UART Transfer Complete
ISR (USART_TX_vect) {
	if (!_uartSendByte()) {
		if (_uartCallbackFunc) _uartCallbackFunc();
	}
}


