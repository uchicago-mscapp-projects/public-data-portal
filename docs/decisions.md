# Decisions

Documenting decisions we've made with their justifications & considered alternatives.

## File Types

Our file type field is meant to assist in searching for useful data, so we will create enum entries for common data types (CSV, XML, XLSX, etc.) that someone might filter on/prefer, but when we encounter uncommon data types or types that are not well-suited for data (PDF, HTML, DOC) we will group those as "Other". 

We will also use an "Other - Geo" to group together less common (e.g. not GeoJSON/KML/Shapefile/etc.) geo data types.

## `tags`

Capture anything that feels tag-like from upstream. For instance if upstream has:

```
  "category": "Finance",
  "tags": ["money", "banking", "industry"],
  "tags_fr": ["argent", "banque", "industrie"]
```

We would capture all seven of these words as our tags.

## Languages

Fields like `name` and `description` should favor english where possible, for UI consistency.

The alternate name/description lists can be used for translations as well as alternates in english.

## `region`, `publisher` and `subregion`

A `region` should generally be a country as defined by ISO 3166:
   <https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes>

Exceptions may include:

- European Union
- World

Those wishing to filter at a more granular level may instead:

- Use `publisher` if the data
- Use `subregion`, a free text field that can be used to identify subdivisions of a country.
  We **do not** attempt to create a hierarchy, for our purposes it is enough to say that both Illinois and Chicago are subregions of the United States.

(As discussed in 2025-07-29 meeting.)
