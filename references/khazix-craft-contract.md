# Khazix craft-only contract

Call `khazix-writer` only after the article style card and chapter skeleton
are locked. The total-control Skill remains the author and draft owner. The
request must ask for JSON in this shape:

```json
{
  "schema_version": "1.0",
  "source_skill": "khazix-writer",
  "mode": "craft-only",
  "suggestions": [
    {
      "kind": "transition",
      "section_ref": "section-2",
      "text": "让转场由前一节的因果后果推动。",
      "reason": "避免用连接词代替推进。"
    }
  ]
}
```

Allowed suggestion kinds are `structure`, `scene`, `analogy`, `rhythm`,
`transition`, and `self_check`. The result is advice, not article text. Run
the total-control adapter before using it:

```text
python <SKILL_ROOT>/scripts/craft_only_adapter.py <KHAZIX_JSON>
```

Reject a non-JSON response, a response containing a draft/body/article field,
or any response that imports the Khazix author identity, slogan, signature,
coarse language, fixed punctuation, fixed length, fixed structure, or fixed
ending. The normalized suggestions may be selectively rewritten into the
account voice; they may not be copied as a final draft. If the external Skill
cannot satisfy this response contract, block the craft-assistant stage and
record the downgrade instead of importing its prose.
