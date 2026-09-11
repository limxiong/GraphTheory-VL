# Recorded paper results

Rates are percentages. The Hard20 Original rows are included in Challenge62 Original, so their positions are not added twice.

| Subset | Model | Input | Acc@1 | MeanAcc | Pass@4 | Stable@4 |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| Hard20 | gpt-5.6-luna | original | 10.00 | 5.00 | 15.00 | 0.00 |
| Hard20 | gpt-5.6-luna | text_only | 0.00 | 0.00 | 0.00 | 0.00 |
| Hard20 | gemini-3.6-flash | original | 5.00 | 2.50 | 5.00 | 0.00 |
| Hard20 | gemini-3.6-flash | text_only | 0.00 | 0.00 | 0.00 | 0.00 |
| Hard20 | claude-opus-4-8 | original | 0.00 | 1.25 | 5.00 | 0.00 |
| Hard20 | claude-opus-4-8 | text_only | 5.00 | 5.00 | 5.00 | 5.00 |
| Challenge62 | gpt-5.6-luna | original | 33.87 | 31.85 | 54.84 | 12.90 |
| Challenge62 | gemini-3.6-flash | original | 27.42 | 28.63 | 43.55 | 14.52 |
| Challenge62 | claude-opus-4-8 | original | 9.68 | 10.89 | 22.58 | 1.61 |

The 984 positions include 983 complete archived responses and one user-reported Incorrect decision without a complete local answer body. Labels measure agreement with the requested target. The text-only scores do not imply that the missing diagram can be inferred from the text.

See [paper_metrics.json](paper_metrics.json) for the saved confidence intervals and paired comparisons. The separate response archive contains the available answer bodies and judgment records.
