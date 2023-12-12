# EXVT VDD

Reference: DGT 2034177  
Version: A  
Copyright 2023 Dassault Aviation
MIT License (see LICENSE.txt)

## 1. Version Description

The ECOA XML Validation Tool (`EXVT`) allows to validate an ECOA project.

The 1.0.0 version of EXVT introduces those features:
* Installation and usage documentation.
* Initial version of ECOA XML Validation Tool.

## 2. Version identification
### EXVT

|Product|Version|Description|
|-------|:-----:|----------:|
|EXVT|v1.0.0|Initial version of ECOA XML Validation Tool.|

### Packages

|Product|Version|Description|
|-------|:-----:|----------:|
|ecoa-exvt|v1.0.0|Initial version of ECOA XML Validation Tool.|

### Documentation

|Product|Version|Description|
|-------|:-----:|----------:|
|EXVT|v1.0.0|User documentation (installation and usage)|
|DGT 2025319|A|TOR-TORTC: Tool Operational Requirements and Test Cases for EXVT|

## Environment / Compatibility

Linux: CentOS 7.X or higher
Windows: 10 build 1909 or higher

ECOA Architecture Specifications Version 6

## Evolution

Initial version.

## Correction

Initial version.

## Requirements Coverage

Number of requirements: 21

Linux (MANDATORY):

|Fully covered|Partially covered|Not covered|Other|Total|
|:-----------:|:---------------:|:---------:|:---:|:---:|
|81.0%|14.3%|0%|4.8%|100%|

Windows (DESIRABLE):

The proper functioning of the tool has not been fully tested on Windows.

## Limitations / Possible problems / Known errors

### Limitations

|Requirement|Status|Linux|Windows|Comment|
|:----------|:----:|:---:|:-----:|------:|
|TOR_EXVT_REQ_011|Not applicable|x||Windows requirement.|
|TOR_EXVT_REQ_200|Partially covered|x|-|ECOA model with recursive assembly is not supported.|
|TOR_EXVT_PER_100|Partially covered|x|-|Validation is done in less than 1 second on our examples.|
|TOR_EXVT_PER_110|Partially covered|x|-|Validation in less than 2 Gbytes of RAM is not proved.|

### Possible problems

NA

### Known errors

NA

## Delivery

Via GitHub (see ECOA Website for more informations).

## Glossary

* ECOA: European Component Oriented Architecture, the standard used to design components inside a system
* EXVT: ECOA XML Validation Tool
* NA: Not Applicable
* TOR: Tool Operational Requirements
* TORTC: Test Cases of TOR
* VDD: Version Description Document
