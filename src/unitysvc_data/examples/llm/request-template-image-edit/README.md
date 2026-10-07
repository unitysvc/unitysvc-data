+++
preset_name = "llm_request_template_image_edit"
category = "request_template"
mime_type = "json"
file = "request-template-image-edit.json"
description = "Minimal image edit request for each request format"
is_active = true
is_public = true
applies_to = { capability = "image-edit" }
+++

# llm / request-template-image-edit — minimal image edit request, per request format

The default request the Test Request playground offers for services that declare
the `image-edit` capability (image to image). One document covers one capability,
which its `applies_to` names, and holds one entry per request format, each naming
the format it is written in. The playground picks the document by the service's
capability and then the first entry whose `format` is the one the customer chose
(unitysvc/unitysvc#2514). The rules every template shares are in
[CONTRIBUTING](../../../../../CONTRIBUTING.md#request-templates); the chat
template this follows is `../request-template/`.

## Body (v1)

| `format` | Wire shape | `content_type` | `path_suffix` | Derived from |
|----------|------------|----------------|---------------|--------------|
| `huggingface` | Hugging Face inference API, image to image | `multipart/form-data` | none (carries the model) | `llm_code_example_imagetoimage_requests` |

The request is a file upload: the input image as the `image` file part, with a
`prompt` and a `strength` as text fields. An entry's `body` for a
`multipart/form-data` entry holds the form's text fields, here the example's own
prompt and strength (the defaults of its `PROMPT` and `STRENGTH`), minus the model
and minus any templated parameter. The file part is not in the body: it is a file,
not a value.

The playground does not send uploads (unitysvc/unitysvc#2533). It reads
`content_type`, offers the format, and says that the request is a file upload it
does not send, rather than putting the form fields in a JSON editor that would send
them as JSON. So this document is what tells a customer why the body is blank,
instead of the generic "no template" state, and it is the request the playground
sends once it can.

## Path

**No `path_suffix`:** the example posts to
`${__version_prefix__}/models/<the service's model>`, and a `path_suffix` is one
string per capability and format, which cannot say "the service's own model". That
is the known limitation recorded for the other Hugging Face entries (embed,
video-generate; unitysvc/unitysvc#2514, noted on #2516), not something to work
around here.

## What's intentionally missing

- **No `model`.** It is in the path, not the form (see Path).
- **No `openai` entry.** No code example sends an OpenAI image edit, and a body is
  derived from an example, never written from an API's documentation.

## Title

`Default request body (image edit)`: the capability's registry label.

## Versions

### v1 — initial release

- One `huggingface` entry: a `multipart/form-data` upload whose text fields are the
  example's prompt and strength. The first entry to carry `content_type`.
