/**
* @file ECOA_simple_types_serialization.c
* @brief ECOA types serialization
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#include <string.h>
#include <stdint.h>

#include "ECOA.h"
#include "ECOA_simple_types_serialization.h"

/* OD BEGIN
#ifdef __linux__ *//******************* linux ******************/
#if defined(__linux__)

#include <endian.h>
#include <arpa/inet.h>
#define	_LITTLE_ENDIAN __LITTLE_ENDIAN
#define	_BIG_ENDIAN __BIG_ENDIAN
#define	_BYTE_ORDER	__BYTE_ORDER

#else /******************* windows ******************/
#include <winsock2.h>

// define some missing macros on windows :
#define _LITTLE_ENDIAN  1
#define _BIG_ENDIAN     0
#define _BYTE_ORDER _LITTLE_ENDIAN
#endif /****** end of linux/winsows ********/

#if _BYTE_ORDER == _BIG_ENDIAN


uint64_t htonll(uint64_t n) {
	return n;
}

uint64_t ntohll(uint64_t n) {
	return n;
}


#elif _BYTE_ORDER == _LITTLE_ENDIAN

uint64_t htonll(uint64_t n) {
   return (((uint64_t)htonl((uint32_t)n)) << 32) + htonl((uint32_t)(n >> 32));
}

uint64_t ntohll(uint64_t n) {
   return (((uint64_t)ntohl((uint32_t)n)) << 32) + ntohl((uint32_t)(n >> 32));
}


#else
#error /* In case of different endianess directives */
#endif

/* Type ECOA__char8 */
void serialize_ECOA__char8(const ECOA__char8 data, void *buffer, uint32_t max_size, uint32_t *added_size) {
	ECOA__char8 local_data;
	if (max_size >= sizeof(ECOA__char8)) {
		local_data = (data);
		memcpy(buffer, &local_data, sizeof(ECOA__char8));
		*added_size = sizeof(ECOA__char8);
	} else {
		*added_size = 0;
	}
}
void deserialize_ECOA__char8(ECOA__char8 *data, void *buffer, uint32_t length) {
	ECOA__char8 local_data;
	if (length >= sizeof(ECOA__char8)) {
		memcpy(&local_data, buffer, sizeof(ECOA__char8));
		*data = (local_data);
	} else {
		*data = (char)0x00;
	}
}

/* Type ECOA__boolean8 */
void serialize_ECOA__boolean8(const ECOA__boolean8 data, void *buffer, uint32_t max_size, uint32_t *added_size) {
	ECOA__boolean8 local_data;
	if (max_size >= sizeof(ECOA__boolean8)) {
		local_data = (data);
		memcpy(buffer, &local_data, sizeof(ECOA__boolean8));
		*added_size = sizeof(ECOA__boolean8);
	} else {
		*added_size = 0;
	}
}
void deserialize_ECOA__boolean8(ECOA__boolean8 *data, void *buffer, uint32_t length) {
	ECOA__boolean8 local_data;
	if (length >= sizeof(ECOA__boolean8)) {
		memcpy(&local_data, buffer, sizeof(ECOA__boolean8));
		*data = (local_data);
	} else {
		*data = 0;
	}
}

/* Type ECOA__byte */
void serialize_ECOA__byte(const ECOA__byte data, void *buffer, uint32_t max_size,
		uint32_t *added_size) {
	ECOA__byte local_data;
	if (max_size >= sizeof(ECOA__byte)) {
		local_data = (data);
		memcpy(buffer, &local_data, sizeof(ECOA__byte));
		*added_size = sizeof(ECOA__byte);
	} else {
		*added_size = 0;
	}
}
void deserialize_ECOA__byte(ECOA__byte *data, void *buffer, uint32_t length) {
	ECOA__byte local_data;
	if (length >= sizeof(ECOA__byte)) {
		memcpy(&local_data, buffer, sizeof(ECOA__byte));
		*data = (local_data);
	} else {
		*data = 0x00;
	}
}

/* Type ECOA__int8 */
void serialize_ECOA__int8(const ECOA__int8 data, void *buffer, uint32_t max_size,
		uint32_t *added_size) {
	ECOA__int8 local_data;
	if (max_size >= sizeof(ECOA__int8)) {
		local_data = (data);
		memcpy(buffer, &local_data, sizeof(ECOA__int8));
		*added_size = sizeof(ECOA__int8);
	} else {
		*added_size = 0;
	}
}
void deserialize_ECOA__int8(ECOA__int8 *data, void *buffer, uint32_t length) {
	ECOA__int8 local_data;
	if (length >= sizeof(ECOA__int8)) {
		memcpy(&local_data, buffer, sizeof(ECOA__int8));
		*data = (local_data);
	} else {
		*data = 0;
	}
}

/* Type ECOA__int16 */
void serialize_ECOA__int16(const ECOA__int16 data, void *buffer, uint32_t max_size,
		uint32_t *added_size) {
	ECOA__int16 local_data;
	if (max_size >= sizeof(ECOA__int16)) {
		local_data = htons(data);
		memcpy(buffer, &local_data, sizeof(ECOA__int16));
		*added_size = sizeof(ECOA__int16);
	} else {
		*added_size = 0;
	}
}
void deserialize_ECOA__int16(ECOA__int16 *data, void *buffer, uint32_t length) {
	ECOA__int16 local_data;
	if (length >= sizeof(ECOA__int16)) {
		memcpy(&local_data, buffer, sizeof(ECOA__int16));
		*data = ntohs(local_data);
	} else {
		*data = 0;
	}
}

/* Type ECOA__int32 */
void serialize_ECOA__int32(const ECOA__int32 data, void *buffer, uint32_t max_size,
		uint32_t *added_size) {
	ECOA__int32 local_data;
	if (max_size >= sizeof(ECOA__int32)) {
		local_data = htonl(data);
		memcpy(buffer, &local_data, sizeof(ECOA__int32));
		*added_size = sizeof(ECOA__int32);
	} else {
		*added_size = 0;
	}
}
void deserialize_ECOA__int32(ECOA__int32 *data, void *buffer, uint32_t length) {
	ECOA__int32 local_data;
	if (length >= sizeof(ECOA__int32)) {
		memcpy(&local_data, buffer, sizeof(ECOA__int32));
		*data = ntohl(local_data);
	} else {
		*data = 0;
	}
}

#if defined(ECOA_64BIT_SUPPORT)
/* Type ECOA__int64 */
void serialize_ECOA__int64(const ECOA__int64 data, void *buffer, uint32_t max_size, uint32_t *added_size) {
	ECOA__int64 local_data;
	if (max_size >= sizeof(ECOA__int64)) {
		local_data = htonll(data);
		memcpy(buffer, &local_data, sizeof(ECOA__int64));
		*added_size = sizeof(ECOA__int64);
	}
	else {
		*added_size = 0;
	}
}
void deserialize_ECOA__int64(ECOA__int64 *data, void *buffer, uint32_t length) {
	ECOA__int64 local_data;
	if (length >= sizeof(ECOA__int64)) {
		memcpy(&local_data, buffer, sizeof(ECOA__int64));
		*data = ntohll(local_data);
	}
	else {
		*data = 0;
	}
}
#endif

/* Type ECOA__uint8 */
void serialize_ECOA__uint8(const ECOA__uint8 data, void *buffer, uint32_t max_size,
		uint32_t *added_size) {
	ECOA__uint8 local_data;
	if (max_size >= sizeof(ECOA__uint8)) {
		local_data = (data);
		memcpy(buffer, &local_data, sizeof(ECOA__uint8));
		*added_size = sizeof(ECOA__uint8);
	} else {
		*added_size = 0;
	}
}
void deserialize_ECOA__uint8(ECOA__uint8 *data, void *buffer, uint32_t length) {
	ECOA__uint8 local_data;
	if (length >= sizeof(ECOA__uint8)) {
		memcpy(&local_data, buffer, sizeof(ECOA__uint8));
		*data = (local_data);
	} else {
		*data = 0;
	}
}

/* Type ECOA__uint16 */
void serialize_ECOA__uint16(const ECOA__uint16 data, void *buffer, uint32_t max_size,
		uint32_t *added_size) {
	ECOA__uint16 local_data;
	if (max_size >= sizeof(ECOA__uint16)) {
		local_data = htons(data);
		memcpy(buffer, &local_data, sizeof(ECOA__uint16));
		*added_size = sizeof(ECOA__uint16);
	} else {
		*added_size = 0;
	}
}
void deserialize_ECOA__uint16(ECOA__uint16 *data, void *buffer, uint32_t length) {
	ECOA__uint16 local_data;
	if (length >= sizeof(ECOA__uint16)) {
		memcpy(&local_data, buffer, sizeof(ECOA__uint16));
		*data = ntohs(local_data);
	} else {
		*data = 0;
	}
}

/* Type ECOA__uint32 */
void serialize_ECOA__uint32(const ECOA__uint32 data, void *buffer, uint32_t max_size,
		uint32_t *added_size) {
	ECOA__uint32 local_data;
	if (max_size >= sizeof(ECOA__uint32)) {
		local_data = htonl(data);
		memcpy(buffer, &local_data, sizeof(ECOA__uint32));
		*added_size = sizeof(ECOA__uint32);
	} else {
		*added_size = 0;
	}
}
void deserialize_ECOA__uint32(ECOA__uint32 *data, void *buffer, uint32_t length) {
	ECOA__uint32 local_data;
	if (length >= sizeof(ECOA__uint32)) {
		memcpy(&local_data, buffer, sizeof(ECOA__uint32));
		*data = ntohl(local_data);
	} else {
		*data = 0;
	}
}

#if defined(ECOA_64BIT_SUPPORT)
/* Type ECOA__uint64 */
void serialize_ECOA__uint64(const ECOA__uint64 data, void *buffer, uint32_t max_size, uint32_t *added_size) {
	ECOA__uint64 local_data;
	if (max_size >= sizeof(ECOA__uint64)) {
		local_data = htonll(data);
		memcpy(buffer, &local_data, sizeof(ECOA__uint64));
		*added_size = sizeof(ECOA__uint64);
	}
	else {
		*added_size = 0;
	}
}
void deserialize_ECOA__uint64(ECOA__uint64 *data, void *buffer, uint32_t length) {
	ECOA__uint64 local_data;
	if (length >= sizeof(ECOA__uint64)) {
		memcpy(&local_data, buffer, sizeof(ECOA__uint64));
		*data = ntohll(local_data);
	}
	else {
		*data = 0;
	}
}
#endif

/* Type ECOA__float32 */
void serialize_ECOA__float32(const ECOA__float32 data, void *buffer, uint32_t max_size,
		uint32_t *added_size) {
	ECOA__uint32 local_data;
	if (max_size >= sizeof(ECOA__float32)) {
		local_data = htonl(*(ECOA__uint32*)&data);
		memcpy(buffer, &local_data, sizeof(ECOA__uint32));
		*added_size = sizeof(ECOA__uint32);
	} else {
		*added_size = 0;
	}
}
void deserialize_ECOA__float32(ECOA__float32 *data, void *buffer, uint32_t length) {
	ECOA__uint32 local_data;
	if (length >= sizeof(ECOA__float32)) {
		memcpy(&local_data, buffer, sizeof(ECOA__uint32));
		local_data = ntohl(local_data);
		*data = *(ECOA__float32*) &local_data;
	} else {
		*data = 0.0;
	}
}

#if defined(ECOA_64BIT_SUPPORT)
/* Type ECOA__double64 */
void serialize_ECOA__double64(const ECOA__double64 data, void *buffer, uint32_t max_size,
		uint32_t *added_size) {
	ECOA__uint64 local_data;
	if (max_size >= sizeof(ECOA__uint64)) {
		local_data = htonll(*(ECOA__uint64*)&data);
		memcpy(buffer, &local_data, sizeof(ECOA__uint64));
		*added_size = sizeof(ECOA__uint64);
	} else {
		*added_size = 0;
	}
}
void deserialize_ECOA__double64(ECOA__double64 *data, void *buffer, uint32_t length) {
	ECOA__uint64 local_data;
	if (length >= sizeof(ECOA__uint64)) {
		memcpy(&local_data, buffer, sizeof(ECOA__uint64));
		local_data = ntohll(local_data);
		*data = *(ECOA__double64*) &local_data;
	} else {
		*data = 0.0;
	}
}
#endif



/* Type ECOA__log */
void serialize_ECOA__log(const ECOA__log *data, void *buffer, uint32_t max_size, uint32_t *added_size)
{
	uint32_t item_added_size = 0;
	void *index = buffer;
	if(max_size >= current_size_of_ECOA__log(data)) {
		serialize_ECOA__uint32(data->current_size, index, sizeof(ECOA__uint32), &item_added_size);
		index = index + sizeof(ECOA__uint32);
		memcpy(index, data->data, data->current_size);
		*added_size = current_size_of_ECOA__log(data);
	}
}
void deserialize_ECOA__log(ECOA__log *data, void *buffer, uint32_t length)
{
	void *index = buffer;
	if(length >= max_size_of_ECOA__log()) {
		deserialize_ECOA__uint32(&data->current_size, index, sizeof(ECOA__uint32));
		if(data->current_size > ECOA__LOG_MAXSIZE) {
			data->current_size = ECOA__LOG_MAXSIZE;
		}
		index = index + sizeof(ECOA__uint32);
		memcpy(data->data, index, data->current_size);
	}
}
uint32_t max_size_of_ECOA__log(void)
{
	uint32_t size = 0;
	size = (sizeof(ECOA__uint8) * ECOA__LOG_MAXSIZE) + sizeof(ECOA__uint32);
	return size;
}
uint32_t current_size_of_ECOA__log(const ECOA__log*data)
{
	uint32_t size = 0;
	size = (sizeof(ECOA__uint8) * data->current_size) + sizeof(ECOA__uint32);
	return size;
}


void serialize_ECOA__pinfo_filename(const ECOA__pinfo_filename *data, void *buffer, uint32_t max_size, uint32_t *added_size)
{
	uint32_t item_added_size = 0;
	char* index = buffer;
	if(max_size >= current_size_of_ECOA__pinfo_filename(data)) {
		serialize_ECOA__uint32(data->current_size, index, sizeof(ECOA__uint32), &item_added_size);
		index = index + sizeof(ECOA__uint32);
		memcpy(index, data->data, data->current_size);
		*added_size = current_size_of_ECOA__pinfo_filename(data);
	}
}
void deserialize_ECOA__pinfo_filename(ECOA__pinfo_filename *data, void *buffer, uint32_t length)
{
	char* index = buffer;
	if(length >= max_size_of_ECOA__pinfo_filename()) {
		deserialize_ECOA__uint32(&data->current_size, index, sizeof(ECOA__uint32));
		index = index + sizeof(ECOA__uint32);
		if(data->current_size > ECOA__PINFO_FILENAME_MAXSIZE) {
			data->current_size = ECOA__PINFO_FILENAME_MAXSIZE;
		}
		memcpy(data->data, index, data->current_size);
	}
}
uint32_t max_size_of_ECOA__pinfo_filename(void)
{
	uint32_t size = 0;
	size = (sizeof(ECOA__uint8) * ECOA__PINFO_FILENAME_MAXSIZE) + sizeof(ECOA__uint32);
	return size;
}
uint32_t current_size_of_ECOA__pinfo_filename(const ECOA__pinfo_filename*data)
{
	uint32_t size = 0;
	size = (sizeof(ECOA__uint8) * data->current_size) + sizeof(ECOA__uint32);
	return size;
}


/* Type ECOA__hr_time */
void serialize_ECOA__hr_time(const ECOA__hr_time *data, void *buffer, uint32_t max_size, uint32_t *added_size)
{
	uint32_t added_field_size = 0;
	char* index = buffer;
	if(max_size >= size_of_ECOA__hr_time()) {
		serialize_ECOA__uint32((data->seconds), index, sizeof(ECOA__uint32), &added_field_size);
		index = index + sizeof(ECOA__uint32);
		serialize_ECOA__uint32((data->nanoseconds), index, sizeof(ECOA__uint32), &added_field_size);
		*added_size = size_of_ECOA__hr_time();
	}
}
void deserialize_ECOA__hr_time(ECOA__hr_time *data, void *buffer, uint32_t length)
{
	char* index = buffer;
	if(length >= size_of_ECOA__hr_time()) {
		deserialize_ECOA__uint32(&(data->seconds), index, length);
		index = index + sizeof(ECOA__uint32);
		deserialize_ECOA__uint32(&(data->nanoseconds), index, length);
	}
}
uint32_t size_of_ECOA__hr_time(void)
{
	uint32_t size = 2*sizeof(ECOA__uint32);
	return size;
}

/* Type ECOA__global_time */
void serialize_ECOA__global_time(const ECOA__global_time *data, void *buffer, uint32_t max_size, uint32_t *added_size)
{
	void *index = buffer;
	uint32_t max_field_size = 0;
	uint32_t added_field_size = 0;
	if(max_size >= size_of_ECOA__global_time()) {
		max_field_size = sizeof(ECOA__uint32);
		serialize_ECOA__uint32((data->seconds), index, max_field_size, &added_field_size);
		index = index + added_field_size;
		serialize_ECOA__uint32((data->nanoseconds), index, max_field_size, &added_field_size);
		*added_size = size_of_ECOA__global_time();
	}
}
void deserialize_ECOA__global_time(ECOA__global_time *data, void *buffer, uint32_t length)
{
	void *index = buffer;
	if(length >= size_of_ECOA__global_time()) {
		deserialize_ECOA__uint32(&(data->seconds), index, length);
		index = index + sizeof(ECOA__uint32);
		deserialize_ECOA__uint32(&(data->nanoseconds), index, length);
	}
}
uint32_t size_of_ECOA__global_time(void)
{
	uint32_t size = 2*sizeof(ECOA__uint32);
	return size;
}

/* Type ECOA__duration */
void serialize_ECOA__duration(const ECOA__duration *data, void *buffer, uint32_t max_size, uint32_t *added_size)
{
	void *index = buffer;
	uint32_t max_field_size = 0;
	uint32_t added_field_size = 0;
	if(max_size >= size_of_ECOA__duration()) {
		max_field_size = sizeof(ECOA__uint32);
		serialize_ECOA__uint32((data->seconds), index, max_field_size, &added_field_size);
		index = index + added_field_size;
		serialize_ECOA__uint32((data->nanoseconds), index, max_field_size, &added_field_size);
		*added_size = size_of_ECOA__duration();
	}
}
void deserialize_ECOA__duration(ECOA__duration *data, void *buffer, uint32_t length)
{
	void *index = buffer;
	if(length >= size_of_ECOA__duration()) {
		deserialize_ECOA__uint32(&(data->seconds), index, length);
		index = index + sizeof(ECOA__uint32);
		deserialize_ECOA__uint32(&(data->nanoseconds), index, length);
	}
}
uint32_t size_of_ECOA__duration(void)
{
	uint32_t size = 2*sizeof(ECOA__uint32);
	return size;
}
