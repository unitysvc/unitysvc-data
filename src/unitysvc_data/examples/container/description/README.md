+++
preset_name = "container_description"
category = "getting_started"
mime_type = "markdown"
file = "description.md"
description = "Customer guide to enrolling, starting, accessing and stopping a container service"
is_active = true
is_public = true
+++

# container / description — using container services

Shared customer guidance for every container service, alongside its application's
own setup and usage instructions. Reference it in a listing as:

```json
{
  "Using container services": {"$doc_preset": "container_description"}
}
```

The guide is plain Markdown with no template variables or service-specific URLs,
prices, resource sizes or application credentials. It describes the common
enrollment and instance lifecycle; the listing and application guide supply the
specifics. It applies to commercial services as well as at-cost catalogs and
therefore makes no claim that every seller has zero markup.

Relative topic links use `[Title](?topic=slug)`, as in `llm_description`.

## Versions

### v1 — initial release

Enrollment and channel choice, parameter defaults and application credentials,
instance entry URLs, continuous/on-demand use, runtime charges, temporary storage,
and stopping/troubleshooting.
