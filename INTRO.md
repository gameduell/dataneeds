Declares Data
===


Decalre is about a declerative approch to data processing. Instead of
describing exactly *how* to load and process your data, you define a
descriptive repository of your data sources and then only have to describe
*what* data you need to load. Exporting of data can be handled the same way by
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


Types
---

Data have types, allowing to do different things with them. For example you can
add hours to a timestamp, but not to an integer. Types keep track of this.

There are primitive types in Declares, like String or Int, but also more
advanced types like Timestamps, Tuples or Categoricals. And you can define your
own Types.


Entitis
---

Entities are the things you talk about in your domain, that can be users,
events that are happening on your platform or an account.

To combine different information, entities should be referrable, identified
by key-fields.


Records
---

Normally data is stored as records, grouping together related information.

In Declares records are defined referencing fields of entites and other
records.

/ There's an Event class that is both Entity and the primitive record of itself. /

Formats
---

A format descripes how data entries are stored.

For example if you have a timestamp, you can represent in many ways, a unix
timestamp in milliseconds or a human readable string in UTC timezone. Now this
can be combined with an event-name and user-id to build up a record of events.
These records also have a format, for example json or csv, where all fields may
have formats on there own. And this can be combine into a big Bzip2ed file or a
pickled list, so formats most likely are hierachal.


Bla
===

```
class Entity1(Entity):
    attr1 = Type1()
    attr2 = Type2()
    ...
    ref1 = Entity1()
    ref2 = Entity2()
    ...
    # TODO Cardinalities


class Record1(Record):
    attr1 = dc.Format() >> Entity1.attr1
    attr2 = dc.Format() >> Entity1.attr2

    ref1 = Entity1.ref1.id1
    ref2 = Entity1.ref2.id1

    # FIXME Record vs Format
```

