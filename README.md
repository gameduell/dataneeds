# Data Needs

Data Needs is a declarative approch to data processing: Instead of describing exactly how to load and process your data, you declare once what data you have and then your data needs are served using these declarations.

That why you can load and store data from and to your system without caring about every indivdual step, with many transformations applyed automatically: references to other objects in different sources are resolved or accomulations are clalculated on the fly when required for your data request.

Finally, a pool of computatinal ressources can be managed by declarative, making it a distributed scalable data processing tool.

Meta-classes inside Data Needs:

- Types: primitive types and constraints
- Records: define record for structured data
- Entities: identifiable/referancable objects in your system
- Requests: request to specific data content
- Formats: data format definition, can be hierachal
- Sources: declarations of you data sources
- Sinks: declarations of data sinks
- Repository: store for definitions of types, entities, sources and sinks
- Processors: data processing with declaritive in- and output

## Types

Data have types, allowing to do different things with them. For example you can add hours to a timestamp, but not to an integer. Types keep track of this.

There are primitive types in Data Needs, like String or Int, but also more advanced types like Timestamps, Tuples or Categoricals. And you can define your own Types.

## Entitis

Entities are the things you talk about in your domain, that can be users, events that are happening on your platform or an account.

To combine different information, entities should be referrable, identified by key-fields.

## Records

Normally data is stored as records, grouping together related information.

In Data Needs records are defined referencing fields of entites and other records.

/ There's an Event class that is both Entity and the primitive record of itself. /

## Formats

A format descripes how data entries are stored.

For example if you have a timestamp, you can represent in many ways, a unix timestamp in milliseconds or a human readable string in UTC timezone. Now this can be combined with an event-name and user-id to build up a record of events. These records also have a format, for example json or csv, where all fields may have formats on there own. And this can be combine into a big Bzip2ed file or a pickled list, so formats most likely are hierachal.

# Definition Grammer

## Struct Definition

- **attributes** to **type instances**

  ```python
  class AStruct(Struct):
    attr1 = AType()
    attr2 = OtherType()
  ```

## Entity Definition

- **attributes** with **type instances**
- **references** to other **entity instances**

  ```python
  class AEntity(Entity):
    attr1 = AType()
    attr2 = OtherType()
    attr3 = AStruct()
    ...
    ref1 = OtherEntity()
    @relate
    def ref2(lower=1, upper=...)
      return YetAnotherEntity()
    ...
  ```

## Record Definition

- **attributes** referring to **attributes of entity classes**
- **inner** defines with **type instances** to other **record instances**
- **references** as **keys of entity classes**

```python
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

## Unified Definition

- define **entity** and naive **record** the same time.

```python
class AEvent(Record, Entity):
    attr1 = AType()
    attr2 = OneFormat() >> OtherType()
    inner1 = AType() >> InnerStruct()
    inner2 = OtherInnerRecord()

    ref1 = AEntity.ref1.an_id
    ref2_key1 = ~AEntity.ref2.key1
    ref2_key2 = ~AEntity.ref2.key2
```

## Format Definition

- **format record DAG**

  ```python
  class AInput:
   (Files(...)
    >> Sep(',')
    >> ARecord())
  ```

# Towards Dask

Were starting with the Format Definition:

```python
(Files(...)
 >> Sep(',')
 >> ARecord())
```

For the dask.bag backend, we have now that `Files(...)` gives a bag of lines, and Sep can transform a bag of lines into a bag of tuples, which has a naive interpretation as a record.

So we can generate a bag of ARecort-entries ...
