#ifndef __UART_H__
#define __UART_H__

#include <avr/io.h>
#include <avr/interrupt.h>

#define BAUD 38400
#include <util/setbaud.h>

#define UART_BUFFERSIZE 256

void uartInit (void);
void uartSend (char data);
void uartSendMultiple (char *data, uint8_t count);
void uartSendMultipleWithCallback (char *data, uint8_t count, void (*cbFunc)(void));

#endif // __UART_H__

