# LDP VDD

Reference: DGT 2034175  
Version: A  
Copyright 2023 Dassault Aviation
MIT License (see LICENSE.txt)

## 1. Version Description

The Lightweight Development Platform tool (`LDP`) allows to generate the source code of an ECOA application.

The 1.0.0 version of LDP introduces those features:
* Installation and usage documentation.
* Initial version of Lightweight Development Platform tool.

## 2. Version identification
### LDP

|Product|Version|Description|
|-------|:-----:|----------:|
|LDP|v1.0.0|Initial version of Lightweight Development Platform tool.|

### Packages

|Product|Version|Description|
|-------|:-----:|----------:|
|ecoa-ldp|v1.0.0|Initial version of Lightweight Development Platform tool.|

### Documentation

|Product|Version|Description|
|-------|:-----:|----------:|
|LDP|v1.0.0|User documentation (installation and usage)|
|DGT 2021742|A|TOR-TORTC: Tool Operational Requirements and Test Cases for LDP|

## Environment / Compatibility

Linux: CentOS 7.X or higher  
Windows: 10

## Evolution

Initial version.

## Correction

Initial version.

## Requirements Coverage

Number of requirements: 42

Linux (MANDATORY):

|Fully covered|Partially covered|Not covered|Other|Total|
|:-----------:|:---------------:|:---------:|:---:|:---:|
|90.0%|10.0%|0%|0%|100%|

## Limitations / Possible problems / Known errors

### Limitations

|Requirement|Status|Linux|Windows|Comment|
|:----------|:----:|:---:|:-----:|------:|
|TOR_LDP_REQ_300|Partially covered|x|-|ECOA model with recursive assembly is not supported. Quality of Service (QoS) is not supported. Module deployment is not allowed everywhere. Modules of the same component should be deployed on the same Protection Domain.|
|TOR_LDP_REQ_440|Partially covered|x|-|The Warm start context maintenance mechanism is generated but its functioning is not proved.|
|TOR_LDP_PER_010|Partially covered|x|-|Output generation is done in less than 1 second on our examples.|
|TOR_LDP_PER_030|Partially covered|x|-|Compilation only tested on x86 architecture.|

### Possible problems

NA

### Known errors

NA

## Delivery

Via GitHub (see ECOA Website for more informations).

## Glossary

* ECOA: European Component Oriented Architecture, the standard used to design components inside a system
* LDP: Lightweight Development Platform
* NA: Not Applicable
* TOR: Tool Operational Requirements
* TORTC: Test Cases of TOR
* VDD: Version Description Document
