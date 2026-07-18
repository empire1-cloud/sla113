# Validation receipt

Validated before publication:

```text
python3 -m py_compile firekirin-engine/art_pipeline/*.py
python3 -m json.tool firekirin-engine/art_pipeline/aztec_roster.json
python3 -m json.tool firekirin-engine/art_pipeline/aztec_static_assets.json
python3 -m unittest discover -s firekirin-engine/art_pipeline/tests -v
```

Expected unit-test coverage:

- packed cell indices are independent of sparse source manifest indices
- aspect ratio is preserved when sprites are normalized into grid cells
- the Empire coin extractor prefers the compact coin over separated wordmark letters
- aggregate SLA113 animation groups use each creature's declared engine animation key

Dry-run validation makes no API calls:

```text
python3 firekirin-engine/art_pipeline/generate_sprites.py --validate-only
python3 firekirin-engine/art_pipeline/generate_static_art.py --dry-run
```
