/**
* @file ECOA_simple_types_serialization.h
* @brief ECOA types serialization
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#if !defined(_ECOA_SIMPLE_TYPES_SERIALIZATION_H_)
#define _ECOA_SIMPLE_TYPES_SERIALIZATION_H_

#if defined(__cplusplus)
extern "C" {
#endif /* __cplusplus */

#include <stdint.h>
#include <ECOA.h>

uint64_t htonll(uint64_t n);
uint64_t ntohll(uint64_t n);

/* Type ECOA__char8 */
void serialize_ECOA__char8(const ECOA__char8 data, void *buffer, uint32_t max_size, uint32_t *added_size);
void deserialize_ECOA__char8(ECOA__char8 *data, void *buffer, uint32_t length);

/* Type ECOA__boolean8 */
void serialize_ECOA__boolean8(const ECOA__boolean8 data, void *buffer, uint32_t max_size, uint32_t *added_size);
void deserialize_ECOA__boolean8(ECOA__boolean8 *data, void *buffer, uint32_t length);

/* Type ECOA__byte */
void serialize_ECOA__byte(const ECOA__byte data, void *buffer, uint32_t max_size, uint32_t *added_size);
void deserialize_ECOA__byte(ECOA__byte *data, void *buffer, uint32_t length);

/* Type ECOA__int8 */
void serialize_ECOA__int8(const ECOA__int8 data, void *buffer, uint32_t max_size, uint32_t *added_size);
void deserialize_ECOA__int8(ECOA__int8 *data, void *buffer, uint32_t length);

/* Type ECOA__int16 */
void serialize_ECOA__int16(const ECOA__int16 data, void *buffer, uint32_t max_size, uint32_t *added_size);
void deserialize_ECOA__int16(ECOA__int16 *data, void *buffer, uint32_t length);

/* Type ECOA__int32 */
void serialize_ECOA__int32(const ECOA__int32 data, void *buffer, uint32_t max_size, uint32_t *added_size);
void deserialize_ECOA__int32(ECOA__int32 *data, void *buffer, uint32_t length);

#if defined(ECOA_64BIT_SUPPORT)
/* Type ECOA__int64 */
void serialize_ECOA__int64(const ECOA__int64 data, void *buffer, uint32_t max_size, uint32_t *added_size);
void deserialize_ECOA__int64(ECOA__int64 *data, void *buffer, uint32_t length);
#endif

/* Type ECOA__uint8 */
void serialize_ECOA__uint8(const ECOA__uint8 data, void *buffer, uint32_t max_size, uint32_t *added_size);
void deserialize_ECOA__uint8(ECOA__uint8 *data, void *buffer, uint32_t length);

/* Type ECOA__uint16 */
void serialize_ECOA__uint16(const ECOA__uint16 data, void *buffer, uint32_t max_size, uint32_t *added_size);
void deserialize_ECOA__uint16(ECOA__uint16 *data, void *buffer, uint32_t length);

/* Type ECOA__uint32 */
void serialize_ECOA__uint32(const ECOA__uint32 data, void *buffer, uint32_t max_size, uint32_t *added_size);
void deserialize_ECOA__uint32(ECOA__uint32 *data, void *buffer, uint32_t length);

#if defined(ECOA_64BIT_SUPPORT)
/* Type ECOA__uint64 */
void serialize_ECOA__uint64(const ECOA__uint64 data, void *buffer, uint32_t max_size, uint32_t *added_size);
void deserialize_ECOA__uint64(ECOA__uint64 *data, void *buffer, uint32_t length);

/* Type ECOA__double64 */
void serialize_ECOA__double64(const ECOA__double64 data, void *buffer, uint32_t max_size, uint32_t *added_size);
void deserialize_ECOA__double64(ECOA__double64 *data, void *buffer, uint32_t length);
#endif

/* Type ECOA__float32 */
void serialize_ECOA__float32(const ECOA__float32 data, void *buffer, uint32_t max_size, uint32_t *added_size);
void deserialize_ECOA__float32(ECOA__float32 *data, void *buffer, uint32_t length);


/* Type ECOA__log */
void serialize_ECOA__log(const ECOA__log* data, void *buffer, uint32_t max_size, uint32_t *added_size);
void deserialize_ECOA__log(ECOA__log *data, void *buffer, uint32_t length);
uint32_t max_size_of_ECOA__log(void);
uint32_t current_size_of_ECOA__log(const ECOA__log *data);

/* Type ECOA__pinfo_filename */
void serialize_ECOA__pinfo_filename(const ECOA__pinfo_filename* data, void *buffer, uint32_t max_size, uint32_t *added_size);
void deserialize_ECOA__pinfo_filename(ECOA__pinfo_filename *data, void *buffer, uint32_t length);
uint32_t max_size_of_ECOA__pinfo_filename(void);
uint32_t current_size_of_ECOA__pinfo_filename(const ECOA__pinfo_filename *data);

/* Type ECOA__hr_time */
void serialize_ECOA__hr_time(const ECOA__hr_time* data, void *buffer, uint32_t max_size, uint32_t *added_size);
void deserialize_ECOA__hr_time(ECOA__hr_time *data, void *buffer, uint32_t length);
uint32_t size_of_ECOA__hr_time(void);

/* Type global_time */
void serialize_ECOA__global_time(const ECOA__global_time* data, void *buffer, uint32_t max_size, uint32_t *added_size);
void deserialize_ECOA__global_time(ECOA__global_time *data, void *buffer, uint32_t length);
uint32_t size_of_ECOA__global_time(void);

/* Type ECOA__duration */
void serialize_ECOA__duration(const ECOA__duration* data, void *buffer, uint32_t max_size, uint32_t *added_size);
void deserialize_ECOA__duration(ECOA__duration *data, void *buffer, uint32_t length);
uint32_t size_of_ECOA__duration(void);

#if defined(__cplusplus)
}
#endif /* __cplusplus */

#endif /* _ECOA_SIMPLE_TYPES_SERIALIZATION_H_ */
