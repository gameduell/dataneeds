# Declares Data

Decalre is about a declerative approch to data processing. Instead of
describing exactly __how__ to load and process your data, you define a
descriptive repository of your data sources and then only have to describe
__what__ data you need to load. Exporting of data can be handled the same way by
Declares, using definitions of data sinks.

Moreover Declare can apply many transformations, like references to other
objects in different sources or automatic accomulations when required for
your data request.

Finally, a pool of computatinal ressources can be allocated to Declare, making
Declare a distributed, scalable data processing tool.

Meta-classes inside Declare:

 * Types:       primitive types and constraints
 * Records:     define record for structured data
 * Entities:    identifiable/referancable objects in your system
 * Requests:    request to specific data content
 * Formats:     data format definition, can be hierachal
 * Sources:     declarations of you data sources
 * Sinks:       declarations of data sinks
 * Repository:  store for definitions of types, entities, sources and sinks
 * Processors:  data processing with declaritive in- and output


## Types

Data have types, allowing to do different things with them. For example you can
add hours to a timestamp, but not to an integer. Types keep track of this.

There are primitive types in Declares, like String or Int, but also more
advanced types like Timestamps, Tuples or Categoricals. And you can define your
own Types.


## Entitis

Entities are the things you talk about in your domain, that can be users,
events that are happening on your platform or an account.

To combine different information, entities should be referrable, identified
by key-fields.


## Records

Normally data is stored as records, grouping together related information.

In Declares records are defined referencing fields of entites and other
records.

/ There's an Event class that is both Entity and the primitive record of itself. /

## Formats

A format descripes how data entries are stored.

For example if you have a timestamp, you can represent in many ways, a unix
timestamp in milliseconds or a human readable string in UTC timezone. Now this
can be combined with an event-name and user-id to build up a record of events.
These records also have a format, for example json or csv, where all fields may
have formats on there own. And this can be combine into a big Bzip2ed file or a
pickled list, so formats most likely are hierachal.


# Definition Grammer

## Struct Definition
 * __attributes__ to __type instances__
```
class AStruct(Struct):
    attr1 = AType()
    attr2 = OtherType()
```

## Entity Definition
 * __attributes__ with __type instances__
 * __references__ to other __entity instances__
```
class AEntity(Entity):
    attr1 = AType()
    attr2 = OtherType()
    attr3 = AStruct()
    ...
    ref1 = OtherEntity()
    ref2 = YetAnotherEntity()
    ...
    # TODO Cardinalities
```

## Record Definition
 * __attributes* referring to __attributes of entity classes__
 * __inner__ defines with __type instances__ to other __record instances__
 * __references__ as __keys of entity classes__

```
class ARecord(Record):
    attr1 = AEntity.attr1
    attr2 = AEntity.attr2
    inner1 = AType() >> InnerRecord()
    inner2 = OtherInnerRecord()

    ref1 = AEntity.ref1.an_id
    ref2_key1 = ~AEntity.ref2.key1
    ref2_key2 = ~AEntity.ref2.key2

class BRecord(ARecord):
    attr1 = BEntity.attr1
    attr2 = (AType() >> BEntity.attr2)
    inner1 = SpecificInnerRecord()
```

## Event Definition
Like entities, but define a naive record accordingly. Inners can also be bound
to Structs and Entities, creating a naive Record for them.
```
class AEvent(Record, Entity):
    attr1 = AType()
    attr2 = Type2()
    inner1 = AType() >> InnerStruct()
    inner2 = OtherInnerRecord()

    ref1 = AEntity.ref1.an_id
    ref2_key1 = ~AEntity.ref2.key1
    ref2_key2 = ~AEntity.ref2.key2
```

## Format Definition
 * __format record DAG__
```
class AInput:
    (Files(...)
     >> Sep(',')
     >> ARecord())
```

# Towards Dask

Were starting with the Format Definition:

```
(Files(...)
 >> Sep(',')
 >> ARecord())
```

For the dask.bag backend, we have now that `Files(...)` gives a bag of lines,
and Sep can transform a bag of lines into a bag of tuples,
which has a naive interpretation as a record.

So we can generate a bag of ARecort-entries ...
