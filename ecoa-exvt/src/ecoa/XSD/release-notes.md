# RELEASE NOTES

(Markdown format - To be used with any Markdown editor)

## Version 2.0.0

- Version associated to AS6
- Change 1.0 by 2.0 in many places

- Namespace renaming: ecoa.technology/sca => ecoa.technology/sca-extension-2.0
    
### ecoa-implementation.xsd

- Removal of attributes 'isSupervisionModule', 'activatingSvcAvailNotifs', 'enableModuleLifeCycleNotif's
- Add of 'hasUserContext' and 'hasWarmStartContext'
- Default values set to true as per meeting decision
- Renaming of attribute 'activatingErrorNotifs' by 'activatingFaultNotifs'
- Removal of attributes 'writeAccess' and 'capacity' @ writable PINFO level
- Removal of attributes 'delayMin' and 'delayMax' @ dynamic trigger instance level
- Introduce the attribute "controlled" @ dataLink element level to allow the definition
  of uncontrolled access to a given VD
- Introduce the attribute 'writeOnly' @dataWritten element to allow a writer to get a write-only copy of 
  a versioned data, thereby avoiding the platform to initialize the local copy of the data with the current value. 
- Authorize that a dataLink may not contain readers. Indeed, two writers may exchange together data.
  Useful for defining a link to a VD with no access control.
- Removal of attribute 'requestBufferSize' at OpRefServer and replacement of OpRefServer by OpRefActivatable
   - requestBufferSize was redundant with maxConcurrentRequests

### ecoa-sca-attributes and sca-core-1.1-cd06-subset-2.0

- Removal of attributes 'rank', 'promoteRankList', 'allEventsMulticasted'

### ecoa-module-behaviour-2.0.xsd

- Removal of attributes 'moduleLifeCycleNotification', 'serviceManagementNotification'

### ecoa-deployment-2.0.xsd

- Renaming of attribute 'notificationMaxNumber' by 'faultHandlerNotificationMaxNumber'
    - The attribute is now optional and defaulted to 8
- The 'computingPlatform' attribute of the executeOn element is now mandatory
- Add of WireMapping element to allow mapping of wires on logical links connecting
  different platforms
- Add of platformMessages at platform configuration level to describe the routing
  of platform domain ELI messages
- Removal of the key 'moduleLog_to_deployedModuleInstance': it is now possible again
  to define multiple module log policies for a given component instance

### ecoa-cross-platforms-view-2.0.xsd

Use the term 'view' to differentiate it from the deployment which is more oriented
to components and modules (even if it is possible to describe a multi-platforms deployment).

New XSD to describe mapping of composites onto platforms, mapping of 
wires onto logical computing platform links and binding of IDs

### ecoa-project-2.0.xsd

- Add the element 'bindings' to list IDs file
- Add an entry to identify a cross platforms view

### ecoa-logicalsystem-2.0.xsd

- Add the attribute 'ELIPlatformID' to define the ID to be used in
  in the ELI generic header (32 bits) @ computingPlatform level
- Set the attribute 'Id' of platform-level links as required
- Add a new element 'transportBinding' to logical computing platform
  level link to describe the network technology binding
    - name of the network technology
    - specific parameters for that technology
- Authorizes the definition of platforms and links without internal nodes
  or associated characteristics.
- Reorganization of the XSD to introduce uniqueness of elements through keys

### ecoa-udpbinding-2.0.xsd

Moved to the guidance sub-directory as the UDP binding is not actually a
transport binding standard.

### bug-log.xls

- File removed - no longer aligned with the current MM

## Version 1.13.1

### ecoa-types-1.0.xsd

- Add elements to cover character constants defined in hexadecimal

### sca-core-1.1-cd6-subset.xsd

- Add wireInformation element as sub-element of the wire

### ecoa-sca-attributes-1.0.xsd

- Add wireInformation complex type
- Remove CIA complex type

### ecoa-logicalsystem-1.0.xsd

- Add OS instances to define computing node OS
- Remove available schedulers at computing node level

### ecoa-implementation-1.0.xsd

- Use the common type ProgrammingLanguage to define the language used
  for the module implementation or the external interface
- Add an attribute relativePriority to the moduleInstance element

### ecoa-insertion-policy-1.0.xsd

- Add many entries in order to be coherent with the guidance

### ecoa-interface-qos-1.0.xsd

- Use now TimeDuration instead of xsd:double to avoid to define negative time

### ecoa-deployment-1.0.xsd

- Remove the choice selector in the complex type Deployment
- Update comment for the notificationMaxNumber attribute
- Remove scheduling policy choice at node level
- Remove time slice duration module at deployed module instance level

### ecoa-periodic-module-behaviour-1.0.xsd

- Remove this XSD since activation profile is now included within
  the insertion policy

### ecoa-module-behaviour-1.0.xsd

- Make it coherent with the periodic module behaviour

### ecoa-common-1.0.xsd

- Define the Steps type to define duration in number of steps
- Define the type ProgrammingLanguage to list all supported programming language

## Version 1.13.0

### ecoa-types-1.0.xsd

- Update of constants, minRange and maxRange to cover decimal and character values
    - Definitions avoid overlapping unions.
- Add the precision attribute to the simple type

### ecoa-implementation-1.0.xsd

- removal of deadline attributes in many places (module operation or module-level)
- move the attribute moduleBehaviour from ModuleImplementation to ModuleInstance
- Use of TimeDuration type whenever possible to avoid negative times
- Add attributes to indicate whether service availability or error notifications
  are activating or not
- Add attributes to indicate whether module lifecycle notifications
  are generated or not
- Rename activating attributes to be more logical from a semantic point of view

### ecoa-deployment-1.0.xsd

- Add an optional attribute moduleTimeSliceDuration to save Round-Robin attributes
- Add platformConfiguration and computingNodeConfiguration elements to introduce
  settings for scheduling policy.
  The scheduling policy is defined at node level; the attribute otherSchedulingInformation provides
  a link towards external scheduling data.

### ecoa-periodic-module-behaviour-1.0.xsd

- New file to catch realtime characteristics of a periodic module instance
- Produced as a guidance

### ecoa-module-behaviour-1.0.xsd

- Moved in a guidance directory

### ecoa-insertion-policy-1.0.xsd

- New file to save insertion constraints of a given binary component

### ecoa-bin-desc-1.0.xsd

- Introduce an attribute insertionPolicy to refer an insertion policy file.

### ecoa-logicalsystem-1.0.xsd

- Use NameId instead xs:Id in many places

### sca-implementation-composite-1.1-cd06-subset.xsd

- Introduce this SCA file to allow the definition of composites

### sca-core-1.1-cd06-subset.xsd

- Introduce the attribute promoteRankList at reference element level to allow
  the description of ranks for promoted required services.

### ecoa-sca-attributes-1.0.xsd

- Define the attribute promoteRankList allowing
  the description of ranks for promoted required services.

### ecoa-common-1.0.xsd

- Add a type TimeDuration to define positive time positions

### Examples

- Fix property values definition (no double quote apart arrays of char8)

## Version 1.12.1

### ecoa-sca-attributes-1.0.xsd

- Change the type of the rank by positiveInteger

### ecoa-types-1.0.xsd

- Replace 'predef' by 'basic'

### ecoa-implementation-1.0.xsd

- Change the type of the dynamicTrigger queue size by positiveInteger

### AbstractMetaModel

- Replace 'predef' by 'basic'
- Update datatype and supporteddatatypes diagrams

## Version 1.12.0

### ecoa-types-1.0.xsd

- Change the type of the value attribute to xsd:double to cover engineering notation

### AbstractMetaModel

- Add a diagram devoted to service operation QoS
- Remove QoS attributed from the service definition
- Update component implementation diagram

### ecoa-implementation-1.0.xsd

- Removal of the attribute activationModel associated to the element ModuleType
- Removal of the element defaultvalue associated to the element readers (dataLink)
- Use xsd:positiveInteger for fifoSize value type (instead of xsd:int)
- Add an optional attribute maxConcurrentRequests to the element requestSent with
  appropriate comment
- Change the type of the element moduleInstance to OpRefActivating since the previous
  type contains a fifoSize attribute which was redundant with maxConcurrentRequests associated 
  to the element requestSent
- Add various elements to introduce pinfo feature
- Add element 'external' to introduce driver component feature

### ecoa-bin-desc-1.0.xsd

- Use of a string to cover definition of size attributes in decimal or hexadecimal notation
- Add of the warmStartContextSize attribute

### ecoa-deployment-1.0.xsd

- Add keyref to deployment elements for managing uniqueness

### ecoa-common-1.0.xsd

- Removal of '-' in NameId
- Introduce HexOrDecValue to cover hexadecimal and decimal values

### ecoa-interface-1.0.xsd

- Add XSD unique elements to define uniquely service operations and operation parameters

### examples directories

- Adapt examples to metamodel change

### Main subdirectoriers
Change Java nature of projects to XML nature

## Version 1.11.0

### Any file

- Use the Eclipse pretty printer (spaces for tab, tab size = 2, 
  column width = 132, no whitespace at the end of an element)

### ecoa-bin-desc-1.0.xsd

- Use a string to describe the processor type to avoid to change the metamodel
  due to the use of new processor.

### ecoa-logicalsystem-1.0.xsd
- Use a string to describe the processor type to avoid to change the metamodel
  due to the use of new processor.

### xml.xsd

- Replaced by the file xml.xsd retrieved the 13th of January, 2015 
  from www.w3.org/2001/xml.xsd
  
### xml-schema.xsd

- Replaced by the file XMLSchema.xsd retrieved the 13th of January, 2015 
  from www.w3c.org/2001/XMLSchema.xsd

### catalog.xml

- Modify the file according to file renaming
- Removal of the entry for interface-behaviour

### Renaming of files related to SCA

- to clearly state that those files used in the meta-model are a subset of ECOA
- add of a disclaimer at the beginning of each file based on e-mails exchanged with OASIS 

### sca/extensions/ecoa-interface-1.0.xsd

- Removal of the optional attribute behaviour

### ecoa-interface-behaviour-1.0.xsd

- Removal of this file since the behaviour can be provided by another formalism


### ecoa-implementation-1.0.xsd

- Introduction of a timeout on the requestSend element
- Removal of the attribute immediateResponse on the requestResponse element
- Clarify definitions of requestBufferSize and maxDeferredResponses
- Introduction of the attribute isFaultHandler in relation with Fault Management

## Version 1.10.0

- Use the new project name ecoa in filenames and XML attribute/element names
- Introduction of the Papyrus diagrams to define the abstract metamodel
    - Eclipse DSL Kepler SR1 Win32 used


## Version 1.9.0

### ecoa-sca-instance-1.0.xsd
- Authorize explicitly only one implementation per instance

### ecoa-deployment-1.0.xsd
- Remove ModuleLog subelement at DeployedModuleInstance element level
- Specify that ModuleLog subelements at ComponentLog element level can be multiple (maxOccurs="unbounded")
- Add 'modulePriority' attribute to deployedModuleInstance element (between 0 and 255)
- Add 'triggerPriority' attribute to deployedTriggerInstance element (between 0 and 255)
- Remove previous log descriptions
- Add a separate logPolicy element with componentLog and moduleLog sub-elements

### General
- Add documentation for all new attributes/elements

## Version 1.9.0-alpha

### ecoa-udpbinding-1.0.xsd
- Remove 'Interim' in the root element
- Remove 'broadcastAddress' and 'receivingPort' from UDPBinding element
- Add 'receivingMulticastAddress' and 'receivingPort' to Platform element

### ecoa-implementation-1.0.xsd
- Change 'modulePriorityRanking' by 'moduleDeadline'
- Rename module 'attributes' as module 'properties'
- Add 'propertyValues' and 'propertyValue' to moduleInstance element
- Add key definitions for uniqueness of elements

### ecoa-logicalsystem-1.0.xsd
- Use xsd:string instead of xsd:ID to identify nodes within a platform

### ecoa-bin-desc-1.0.xsd

- Add attributes 'userContextSize', 'stackSize', 'heapSize' and 'checksum' to binaryModule element

### ecoa-types-1.0.xsd

- Add uint64 field to E_predef simple type
- Refinement of regular expressions to better cover constants usage

### ecoa-sca-attributes-1.0.xsd
- Removal of 'library'
- Add of 'allEventsMulticasted' as a boolean
- Add provisional attributes to define robustness required for a wire 

### sca-core-1.1-cd06.xsd
- Add 'allEventsMulticasted' to wire
- Re-enable sub-element for wire for provisional attributes
 

## Version 1.8.3

### ecoa-udpbinding-1.0.xsd

- Add the 'maxChannels' attribute to platform node to specify the 
  number of output channels

### ecoa-implementation-1.0.xsd
- Remove attribute isSupervisionModule on ModuleInstance
- Remove node 'trigger' attached to the node 'EventLink'. It has been
  deprecated by a node below 'senders'.

### ecoa-deployment-1.0.xsd
- Rename 'of' and 'on' attributes by 'finalAssembly' and 'logicalSystem'

### Gamma

### ecoa-udpbinding-1.0.xsd
- Change senderId by platformId as an integer between 0 and 15.

### Beta

### ecoa-implementation-1.0.xsd
- Add attribute isSupervisionModule on ModuleType 
- Add default value (false) for attribute isSupervisionModule on ModuleInstance
(which now becomes deprecated)
- Add abstract type 'Instance' to define attributes 'name' and 'modulePriorityRanking' only once.

###  ecoa-interface-1.0.xsd
- Add abstract type 'Operation' to define attributes 'name' and 'comment' only once.

### ecoa-logicalsystem-1.0.xsd
- Add enum value 'powerpc'

### ecoa-bin-desc-1.0.xsd
- Add 'ppc-eabi' for powerpc compiler

### ecoa-types-1.0.xsd
- Allow to use constants to define enum values
- use '%CONSTANT%' syntax in attributes min/maxRange, 
  in order to be consistent with other attributes 'maxSize' and 'value'.

### Alpha

### ecoa-implementation-1.0.xsd

- Use xsd:double for deadline attributes
- Set the attribute activationModel as an optional to be backward compatible with
  existing examples

## Version 1.8.2

### ecoa-types-1.0.xsd
- Enable the use of constant, float or integer for minRange and maxRange attributes.

### ecoa-uid-1.0.xsd
- Add an xml file to associate wires and operations to unique IDs (needed for ELI communication)

### ecoa-implementation-1.0.xsd
- DataLink readers can specify a fifoSize.
- Datalink writers cannot set an activating operation.
- Modify time attributes to handle double typed time 
  (with engineering notation, i.e 230e-3) specified in seconds.

### ecoa-types-1.0.xsd
- The extends attributes is removed.
  A clarification of the corresponding language binding is required.

### ecoa-deployment-1.0.xsd
- The target computing platform is now optional.

### ecoa-interface-behaviour-1.0.xsd
### ecoa-interface-qos-1.0.xsd
- Modify time attributes to handle double typed time 
  (with engineering notation, i.e 230e-3) specified in seconds.

### ecoa-interface-1.0.xsd
- Add a comment field on each operation

### ecoa-types-1.0.xsd
- Add a comment field on each type

### ecoa-sca-instance-1.0.xsd
- The implementation path is replaced by the logical name.

### ecoa-implementation-1.0.xsd
- The OpRefActivatingFifo fifoSize attribute is set to 8 by default.
- Forbidden referencing models that do not exist.
- Add attributes to cover the rythmic model
- Fix operation links

### ecoa-logicalsystem.xsd
- A new level added in the logical system to describe multi-platform logical
  system:
  - Rename element "logicalComputingNode" into "logicalComputingPlatform"
  - Add a root element "logicalSystem" with an id attribute containing:
    - a set of "logicalComputingPlatform"
    - a element "logicalComputingPlatformLinks" to store links between 
      "logicalComputingPlatform" with the same attributes and elements than
      "logicalComputingNodeLinks"

### deployment.xml
-  Add a reference attribute "computingPlatform" in the protection domain 
   to describe where the protection domain  execute on 
   in a multi-platform logical system


### interface-behaviour-1.0.xsd
- Introduction of a service-level behaviour

## Version 1.8.1

- Official release of 1.8.1
- Update all examples

## Version 1.8.1-delta3
- ecoa-implementation:
  - Rename attribute "immediateReply" to "immediateResponse"
  - Move attribute "immediateResponse" from operation link to ModuleType
  - Rename attribute "ReqBufferSize" into "requestBufferSize"
- ecoa-module-behaviour:
  - Replace StartOfLoop/EndOfLoop elements by an enclosing element "Loop"
  - Suppress <action> elements as they are unuseful
  
## Version 1.8.1-delta2
- ecoa-implementation:
  - New type "OpRefServer" for elements "server/moduleInstance"
  - Rename ProcessingReqBufferSize into ReqBufferSize
  - Use type xsd:positiveInteger for ReqBufferSize
  - Indentation conventions (for easier "diff"): 
    - indentation with spaces instead of tabs
    - 1 indentation = 2 spaces.

## Version 1.8.1-delta
- ecoa-implementation:
  - Comment: attributes "activating" etc. are applicable to synchronous _and_ asynchronous RR
  - Add attribute immediateReply
  - Add attribute ProcessingReqBufferSize

## Version 1.8.1-gamma2
- ecoa-implementation:
  - Move attributes 'activating' and 'fifoSize' 2 levels down: 
    from componentImplementation/*Link to componentImplementation/*Link/*/moduleInstance, so that each receiver can 
    have a different value.
  - Add <dynamicTriggerInstance> element to define a dynamic trigger
  - Add <dynamicTrigger> element in <senders> and <receivers>, to use a dynamic trigger
  - Add a new syntax for "classic" triggers (more consistent with dynamic triggers). The old syntax is still accepted.
  - Add a constraint to check that triggers, dynamicTriggers and ordinary modules have distinct names
  - Update Blake_C1.impl.xml to illustrate dynamicTriggers
  - Change type of 'period' to xsd:decimal (consistency with dynamic triggers)
  - Add a deadline per activating operation (eventReceived, requestReceived, callback, notification) at module
    type level.
  - Add the attribute 'notifying' attribute on dataRead
  - Add the attributes 'activating' and 'fifoSize' on DataLink
- ecoa-deployment:
  - Impose that all <protectionDomain>s are declared before <component>s (seems clearer)
  - Introduces option for some log entries as they might be P/F dependent
- ecoa-types: add constant
- ecoa-interface-qos:
  - add maxHandlingTime attributes for RRcallback and data notification
  
## Version 1.8.0
- Add new attributes to qualify interface QoS
- Add a first description of the module behaviour (and some examples)
- Add isSupervisionModule attribute at moduleInstance level (implementation.xml)
- Add an XSD to cover the project file
- Add version number to OS definition (logical system) and 
  componentType instance (actual schema)
- Align with final version 1.7.10
- Provide a first level of fix for sub-typing of simple types
- Fix the occurrence number of links within the logical-system.xml
- Removal of uchar8 - character is by default unsigned
- Add log configuration within the deployment

## Version 1.7.10
- Switch back to colon (':')
- Removal of the example
- Removal of QoS stuff, that will be reported to version 1.8.0
- Removal of useless sca-policy and sca-contribution files
- Add missing OS and processor types to cover UK P/F

## Version 1.7.9
- Modified ecoa-common-1.0.xsd to change syntax of LibraryName and TypeQName
  to <xsd:pattern value="([A-Za-z][A-Za-z0-9_\.]*)?[A-Za-z][A-Za-z0-9_]*"></xsd:pattern>,
  and corrected example to use XXXX.YYYY for type names throughout.
- Modified ecoa-interface-qos-1.0.xsd to incorporate changes as discussed by email,
  and added dummy QoS parameters into all example component definitions.
- Added framework to ecoa-module-behaviour-1.0.xsd,
  and added module behaviour framework into example component implementations.

## Version 1.7.8
- removal of demo1b types file 

## Version 1.7.7
- Changed TypeQName to change from ':' to '.'

## Version 1.7.6
- ecoa-interface-1.0.xsd: removal of isSynchronous attribute at
  Request-response level. This attribute is not necessary at this
  level. The specifier has only to specify if required operations can
  be done in parallel or sequentially. And there is an isSynchronous
  attribute at component implementation level.
- S1.interface.xml & S2.interface.xml: removal of the isSynchronous
  attribute

## Version 1.7.5
- ecoa-types-1.0.xsd: remove uint64 type in predef
- example:
  - Use of '.' notation within service definition
  - Return to synchronous requests-responses to avoid to break other
    example parts

## Version 1.7.4

- ecoa-common.xsd & others: 
  Add regular expressions to check the validity of names used in ECOA models (library, type, operation, module names).
- Add use="required|optional" on all attributes.
- some xsd:unique and xsd:key constraints did not work because of namespace problems.
- add new xsd:unique and xsd:key constraints.
- use the same attributes for the <xsd:schema> element in all schemas.
- use xsd: prefix instead of xs: everywhere.
- fixed typos in <xs:documentation>.

## Version 1.7.3

- Rename .composite.xml and .componentDefinition.xml by .composite and
  .componentDefinition
- deployment.xsd: Add a node deployedTriggerInstance in the deployment (example and
  xsd) (with an implicit intermediate choice node)
- ecoa-implementation-1.0.xsd:
  - Add an attribute language to the node moduleImplementation
  - Apply the rule that all operations of a given module have different
    names: renable the xs:key within ecoa-implementation-1.0.xsd
- Update the example according to previous changes



## Version 1.7.2

- Various changes in many places in order to be validated under Eclipse
  Indigo Java IDE => was obliged to rename .composite and
  .componentDefinition into .composite.xml and .componentDefinition.xml

- Still one problem and one question:
  - 'use library' have been replaced by ecoa-sca:library=""
  - xs:key unique id within ecoa-implementaiton-1.0.xsd

- Add of a catalog inside Schemas directory

- Rename .actual.composite by .impl.composite


## Version 1.7
### Problems to solve in the example

- coherency between ex1.composite and ex2.actual.composite. Remark: This could
  have an impact on ecoa-sca-instance.
- names of operations within component implementations : See red
  circles in the powerpoint
- libimport has been removed from componentType, however notion of
  "use library" inside serviceDefinition and
  componentImplementation. Can we use "use library" within
  componentType ?
- names are missing at root anchor level. It is worth adding them to
  better understand the model under edition.

### Add a file to log requests for enhancements
future-works.org
### Add a Powerpoint to explain the example
### Update of the example ('steps' directory)

- Update of example.types.xml to have a description coherent of the
  services
- Add a type (ecoa-sca:type attribute) to properties of C2 and C3
- Update values of rank of service links in order to have different values
- Use 'ecoa-sca' instead of 'ecoa' as dedicated namespace inside XML files
- Fix C1 implementation
- Add implementations for C2 and C3
- Use different names for component definitions and for component
  implementations
- Add attributes at moduleImplementation level to point out behaviours
- Fulfills bin-desc.xml for each component implementation
- redefine the QoS for a required service of C1

### Update of ecoa-implementation-1.0.xsd

- Add anchors "service" and "reference" to define new QoS for a given service
- Add the attrbute 'moduleBehaviour' at moduleImplementation level.

### Update of ecoa-sca-attributes-1.0.xsd

- Add the attribute 'type'

### Update of ecoa-sca-interface-1.0.xsd

- Add the attribute 'qos'

### bin-desc.xml

- Add the schema

## Version 1.6

2011-07-11

- Renommer ecoa-syntax.xsd ==> ecoa-interface.xsd
- Renommer le r�pertoire Initial-Assembly ==> InitialAssembly
- Renommer byte8 ==> byte
- Renommer namespace ==> library 
- [Implementation] Dans les n�uds moduleInstance et reference, remplacer instance==>instanceName, implementation==>implementationName et operation==>operationName
- [Deploiement] Dans les n�uds deployedModuleInstance, remplacer component==>componentName et moduleInstance==>instanceName
- [Ecos-types.xsd] : attention certains champs sont repass�s en NCName au lieu de ECOA:QName (ex type pour les n�uds array)
- [Implementation, Types] Harmoniser le nommage des attributs et des n�uds (enlever les _ et choisir la convention minuscule et majuscule pour la premiere lettre d'un nouveau mot)
- Traduction en anglais des annotations

- Utilisation de la notion de version pour les namespaces 

Les technos XML offrent beaucoup de possibilit�s concernant le versionnage des �l�ments:
- Classiquement, les namespaces XML contiennent un num�ro de version (souvent sous la forme d'une date).
- Il est possible de versionner �galement le sch�ma XSD (avec un attribut version="" sur le sch�ma). 
- Les sch�mas XSD sont g�n�ralement contenus dans des fichiers, qui �tre versionn�s (soit par leur nom soit par un syst�me de gestion de configuration).


Pour ECOA:
- nous avons 4-5 langages bien s�par�s : chaque fichier XML sera reli� � un langage.  
- il faut prendre en compte que les langages �volueront.
- l'important est de pouvoir associer chaque fichier XML au langage utilis� et � sa version. 
- L'utilisation de l'attribut "version" sur les sch�mas n'a pas vraiment d'int�r�t. En effet, un doc XML est associ� uniquement � un namespace, il n'est pas directement associ� � un sch�ma.

Actuellement, les namespaces ECOA contiennent un num�ro de version (ex: http://www.ecoa.technology/interface-1.0).
Les fichiers XML d'ECOA, eux doivent contenir uniquement la r�f�rence � ce namespace. Exemple:
<componentImplementation 
	xmlns="http://www.ecoa.technology/implementation-1.0">
Cela permet d'identifier, pour chaque �l�ment ECOA, � quel langage ECOA il se r�f�re, et � quelle version.

En r�sum�:
- chaque "langage ECOA" correspond � un namespace, dont le nom inclut un num�ro de version (par exemple du type "majeur.mineur", � discuter)
- tout doc XML ECOA r�f�rence (uniquement) un namespace (nom+version) 
- tout sch�ma XSD ECOA est contenu dans un fichier qui contient un num�ro de version.
- a chaque nouvelle version d'un langage ECOA, on a un nouveau son fichier xsd (contenant le nouveau sch�ma) et un nouveau namespace.

- Utilisation de "QNames" pour les librairies

Les types ECOA sont organis�s en librairies qui jouent le r�le de namespaces.
Les librairies sont nomm�s par un nom qui est un NCName, c'est-�-dire qui ne contient pas le caract�re ':'.
Par convention, ce nom peut �tre structur�, par exemple en utilisant le caract�re '.' comme pour des packages Java.
(ex: "A.B.C")

On a besoin d'utiliser des types:
- dans les d�finitions de librairies
- dans les d�finitions de services
- dans les impl�mentations de composants (interfaces de modules)

Dans ces 3 cas, pour utiliser un type T d�fini dans une lib L, il faut:
- d�clarer <use library="L"> en d�but de document XML
- r�f�rencer le type par la notation "L:T".

Afin d'�tre partag�s, l'�l�ment <use> et les types "LibraryName" et "TypeQName" sont d�finis dans le sch�ma ecoa-common.xsd, qui est inclus par les autres sch�mas ECOA. 
(Ce sch�ma n'a pas de namespace propre: ces �l�ments se retouvent donc dans tous les namespaces ECOA).

Nota: Cette strat�gie est diff�rente d'une strat�gie de "pr�fixage", 
comme par exemple dans les namespaces XML, o� � chaque utilisation, l'�l�ment est "renomm�" pour utiliser un nom court en lieu et place de son nom long. 

- Utilisation d'un catalogue XML

Chaque fichier XML mentionne uniquement un namespace XML (via une URI), et non un sch�ma.
L'association namespace-sch�ma se fait � travers un catalogue XML.

Sous Eclipse, le catalogue est modifiable par Window / Preferences / XML / XML Catalog.
Ce qui se retrouve dans le fichier [workspace_eclipse]\.metadata\.plugins\org.eclipse.wst.xml.core\user_catalog.xml.
Exemple:

<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<catalog xmlns="urn:oasis:names:tc:entity:xmlns:xml:catalog">
  <uri name="http://www.ecoa.technology/interface-1.0" uri="platform:/resource/Model_1_6/Schemas/ecoa-interface-1.0.xsd"/>
  <uri name="http://www.ecoa.technology/sca" uri="platform:/resource/Model_1_6/Schemas/sca/ecoa-sca-1.0.xsd"/>
  <uri name="http://www.ecoa.technology/implementation-1.0" uri="platform:/resource/Model_1_6/Schemas/ecoa-implementation-1.0.xsd"/>
  <uri name="http://www.ecoa.technology/logicalsystem-1.0" uri="platform:/resource/Model_1_6/Schemas/ecoa-logicalsystem-1.0.xsd"/>
  <uri name="http://docs.oasis-open.org/ns/opencsa/sca/200912" uri="platform:/resource/Model_1_6/Schemas/sca/sca-core-1.1-cd06.xsd"/>
  <uri name="http://www.ecoa.technology/types-1.0" uri="platform:/resource/Model_1_6/Schemas/ecoa-types-1.0.xsd"/>
</catalog>


## Version 1.5

2011-07-01

### use XML namespaces
Proposition: the namespaces used in ECOA should be:

- a namespace for each ECOA XSD schema, with a version number:
http://www.ecoa.technology/types-1.0
http://www.ecoa.technology/syntax-1.0  (change name to "interface" or "servicedef"?)
http://www.ecoa.technology/implementation-1.0
http://www.ecoa.technology/deployment-1.0
http://www.ecoa.technology/logicalsystem-1.0
http://www.ecoa.technology/ecoa-nodeconfiguration-1.0
So each sub-langage can evolve separately and has its own version number.

- a namespace for all ECOA-specific SCA extensions:
http://www.ecoa.technology/sca  (add version number?)

- the SCA namespaces (unmodified)
http://docs.oasis-open.org/...


### add "-sca" in these filenames:
  extensions/ecoa-sca-instance-1.0.xsd
  extensions/ecoa-sca-interface-1.0.xsd
  ecoa-sca-attributes-1.0.xsd

### remove prefix "tns:" in schema files

### rename: Types.xsd -> ecoa-types-1.0.xsd

### add -1.0 on all files

### moved standard XML stuff to xml/ directory



### ecoa-types-1.0.xsd

- ajout de Namespace pour regrouper des types
- add byte8
- rename Value to EnumValue
- add attribute "extends" on "Record"
- traduction des <xsd:documentation> en anglais
- add element <use> to specify dependencies between namespaces.

### ecoa-implementation-1.0.xsd 

- removed reference to sca namespace
- rename 'parameter' as 'input'
- rename 'in' as 'input'
- rename 'out' as 'output'
- add element <use> to specify which data type namespaces we use.

### ecoa-deployment.xsd

- move technical details to ecoa-nodeconfiguration.xsd


### ecoa-logicalsystem.xsd
new file

### ecoa-nodeconfiguration.xsd
new file


## Version 1.3

2011-06-27

### First propose of a directory tree to develop ASC

### componentType

- Add of an attribute 'name' at the top anchor.
- Uses of the 'requires' attribute to specify there is at least a QoS intent


### initial composite

- Add an attribute 'ecoa-sca:componentType' to the 'component' anchor 
to specify the componentType

Future enhancement: In pure SCA, it could be replaced by the 'constraintType' attribute but it 
implies to define the component as a constraintType instead of a 
componentType.


### component Implementation

- rename 'parameter' as 'input'
- rename 'out' as 'output'
- replace the attribute "responseTimeClasse" 
  by an anchor 'responseTimeClasse' as a child of 'moduleInstance'
  (modification of the associated XSD)

### deployment.xml

- Add  a 'on' attribute to the top anchor in order to specify the 
underlying logical system.


### actual.composite

- Remove 'providedDataLocation' anchors
- Remove 'deployment' anchors

Do we still need ecoa-instance.xml ?
We may have something like this:
<implementation.ecoa-sca path="">





