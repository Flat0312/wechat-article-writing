# gzh-design author CTA override

`gzh-design` normally adds an author placeholder and a generic
“点赞、在看、转发” CTA when the source article has no explicit author. That
default is not part of the WeChat total-control output contract.

When the account has not supplied a name, bio, or CTA preference, pass the
following instruction to `gzh-design` and remove any generated default before
the five project files are finalized:

```text
author_cta: disabled
Do not add an author signature, author placeholder, or generic interaction CTA.
```

When the user has explicitly supplied an author block or CTA, pass
`author_cta: explicit` and preserve only that supplied text. In both cases,
write exactly one of these lines into `output/html-qc.md`:

```text
- author_cta: disabled
```

or:

```text
- author_cta: explicit
```

The article validator rejects missing registration. With `disabled`, it also
rejects `{{作者名}}`, `{{简介}}`, and the default three-action CTA in
`article.html` or `article-copy.html`. A placeholder or generic CTA therefore
cannot silently enter the manual-paste artifact.
