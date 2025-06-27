# Planning

A loose collection of notes from meetings.

## User Interviews  `

### Interview A--- 

- int'l student, has worked with gov. data in home country
   - expected federal data but lots is actually at state level
   - leads to focus on Chicago/IL
- feature: make it clear if it is geospatial/type of data
- how do you find data now?
    - paid ChatGPT deep research mode
    - novelty, unique data if you can learn it exists
    - create novel data, "has someone done this?"
- feature: how to link? schema for x-refs
- has used Chicago/Google data portals
- team of "data janitors", cleaning econ data published by government and republishing more useful
  - having an API is important
  

### Interview W---

- med student/CS background
- did AI project w/ Kaggle
   - pro: community, helped with references
   - con: actual data hard to work with in unexpected ways
   - con: lots of small/incomplete data
   - download->try->restart with different data loop familiar to many us
- themes:
- linking data sets to projects/other data sets
- community aspect/knowledge
- 'trade secrets' how to work w/ this data

## Alignment

(Notes from planning)

We were all fairly well aligned on the following:

- the homepage will have search, some kind of featured data set(s) and calls to explore the data in different ways, perhaps by category, or what’s new, etc.
individual dataset pages will include metadata on the source, the data itself, a large download call to action
user generated content (UGC) such as tags, comments, projects that use the data, caveats, etc. (more on this below)
- We discussed a lot of potential features worth exploring:
  - data set shopping/comparison
  - visual indicator of data set type (national/federal/state/local/etc.)
  - some kind of “score”
  - the ability to browse related data sets on different “axes” such as “same data, different year” or “same data & year, different place”
  - various kinds of faceting on search: geographic, by attributes, size, etc.

Today we discussed various ways that user-generated content will fit into the system.

- One idea was to have people create ‘projects’ as they browse the site looking for data sets. These could potentially be collaborative, shared/edited by many users. (We may decide this amount of collaboration on the site is out of scope for an MVP though.) A project would consist of saved data sets that were compared/evaluated/potentially used.  This approach could help answer the question of why a person would contribute, they are using the site to benefit themselves and these public artifacts wind up helping others see connections between data & learn what others have done with them.
- In discussing what content is most useful on a dataset page, the consensus seemed to be that Q&A made sense, but there is still a data modeling question as to if these comments/questions are associated directly with a dataset or with the publisher, or perhaps some abstract concept of a ‘family’ of data sets. This will be an important problem to address, open to creative solutions.
- We also discussed the idea of giving users a way of knowing at a glance how others felt about a data set, does it have known bugs? Is it pristine? etc. This could be a mix of automation and UGC.
- Various prior art was discussed: Amazon reviews & Q&A, Pinterest and AirBNB’s ways of presenting this content.
