# ASCTG VDD

Reference: DGT 2034171  
Version: B  
Copyright 2023 Dassault Aviation
MIT License (see LICENSE.txt)

## 1. Version Description

The Application Software Components Test Generator (`ASCTG`) allows to
generate a component harness replacing all components that are not under test.

The 1.0.0 version of ASCTG introduces those features:
* Installation and usage documentation.
* Initial version of ASC Test Generator.

## 2. Version identification
### ASCTG

|Product|Version|Description|
|-------|:-----:|----------:|
|ASCTG|v1.0.0|Initial version of ASC Test Generator.|

### Packages

|Product|Version|Description|
|-------|:-----:|----------:|
|ecoa-asctg|v1.0.0|Initial version of ASC Test Generator.|

### Documentation

|Product|Version|Description|
|-------|:-----:|----------:|
|ASCTG|v1.0.0|User documentation (installation and usage)|
|DGT 2021741|A|TOR-TORTC: Tool Operational Requirements and Test Cases for ASCTG|

## Environment / Compatibility

Linux: CentOS 7.x or equivalent  
Windows: 10 or higher

ECOA Architecture Specifications Version 6

## Evolution

|Version|Version date|Summary of changes|
|:-----:|:----------:|-----------------:|
|A|May 16, 2023|Initial version.|
|B|August 25, 2023|Correction of the requirements coverage for Linux. Removed TOR_ASCTG_REQ_320 requirement in "Limitations" section.|

## Correction

Initial version.

## Requirements Coverage

Number of requirements: 45

Linux (MANDATORY):

|Fully covered|Partially covered|Not covered|Other|Total|
|:-----------:|:---------------:|:---------:|:---:|:---:|
|88.9%|6.7%|0%|4.4%|100%|

Windows (DESIRABLE):

The proper functioning of the tool has not been fully tested on Windows.

## Limitations / Possible problems / Known errors

### Limitations

|Requirement|Status|Linux|Windows|Comment|
|:----------|:----:|:---:|:-----:|------:|
|TOR_ASCTG_REQ_111|Not applicable|x||Windows requirement.|
|TOR_ASCTG_REQ_121|Not applicable|x||Windows requirement.|
|TOR_ASCTG_REQ_300|Partially covered|x|-|ECOA model with recursive assembly is not supported.|
|TOR_ASCTG_PER_100|Partially covered|x|-|Output generation is done in less than 1 second on our examples.|
|TOR_ASCTG_PER_110|Partially covered|x|-|Output generation with less than 2 Gbytes of RAM is not proved.|

### Possible problems

NA

### Known errors

NA

## Delivery

Via GitHub (see ECOA Website for more informations).

## Glossary

* ASC: Application Software Components
* ASCTG: Application Software Component Test Generator
* ECOA: European Component Oriented Architecture, the standard used to design components inside a system
* NA: Not Applicable
* TOR: Tool Operational Requirements
* TORTC: Test Cases of TOR
* VDD: Version Description Document
