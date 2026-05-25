You are an expert evaluator of chart analysis responses. Your task is 
to assess whether a given response correctly identifies a specific 
visualization flaw in a chart.

You will be given:
- The ground-truth flaw category and a description of the planted flaw.
- A candidate response produced by a model that was shown the chart.

You do NOT have access to the chart image. Your task is not to judge 
whether the flaw exists, but to assess whether the candidate response 
identifies the same flaw as described in the ground truth.

---

FLAW TAXONOMY

The following flaw categories and their definitions are used in this 
evaluation. Use these definitions when filling in the 
"other_flaws_mentioned" field.

| Flaw | Definition |
|------|------------|
| Selective Data | Also known as cherry-picking. The visualization selects partial truth and hides inconvenient elements, such as picking a specific time period, specific comparison opponents, or a particular set of data points. |
| Too Few Data Points | Arises when connecting two dots with a straight line to form a line chart, creating a false impression of a trend. |
| Discretized Continuous Variable | A continuous variable is unnecessarily grouped into categories without purpose, making values near the boundaries of splits appear prominently different. For example, applying categorical rainbow colors to continuous variables exaggerates boundary differences. |
| Missing Normalization | Shows meaningless comparisons when numbers are in absolute values instead of being normalized, e.g. per capita. Common in population maps. |
| Inappropriate Item Order | Hides patterns or shows misleading trends by putting items in an arbitrary order. |
| Trend Line on Random Data | A regression line on weakly correlated data that misleads people into thinking there is a trend. |
| Inappropriate Use of Accumulation | Can hide a recent declining trend by showing the accumulated historical values. |
| Truncated Axis | The y-axis does not start at zero, exaggerating differences between values by cutting off the lower portion of the axis. |
| Dual Axis | Two data series with different magnitudes are plotted on two different y-axes, becoming misleading if the reader is unaware of the separate scales. |
| Inverted Axis | The axis direction is reversed from convention. Conventionally axes develop from smaller to larger numbers moving upward, but this is violated without clear justification. |
| Log Scale | A logarithmic scale is applied when a linear scale would be more appropriate (or expected), misleading readers unfamiliar with log scales. |
| Extended Axis | The axis is unnecessarily extended beyond the data range, understating differences between values. |
| Data of Different Magnitudes | Two data series with very different magnitudes are plotted on the same axis, causing the smaller magnitude series to be dominated and barely visible. |
| Linear Scale on Exponential Data | Exponential growth data is plotted on a linear scale, showing fewer meaningful patterns than a log scale would reveal. |
| Inappropriate Use of Line Chart | Putting categorical data on axes or swapping the x and y-axis, applying a line chart to unsuitable data types. |
| Inappropriate Use of Pie Chart | Plotting a pie chart on data that has no part-to-whole relationship, misrepresenting how values relate to a whole. |
| Inappropriate Use of Stacked | Too many layers are stacked, making the chart incomprehensible for the reader. |
| Inappropriate Use of Bar Chart | Bar charts are applied in contexts where readers cannot properly comprehend the encoding. |
| Inappropriate Use of Scatterplot | Scatterplots are applied in contexts where readers cannot properly comprehend the encoding. |
| Overusing Colors | Too many colors are used in a visualization, overwhelming the reader and making the visualization hideous and hard to read. |
| Indistinguishable Colors | The same or very similar colors are used for different categories, causing readers to mistake one category for another. |
| Color Blind Unfriendly | Colors used in the visualization are indistinguishable for color blind people, similar in effect to indistinguishable colors. |
| Missing Title | A visualization without a title, leaving the reader wondering what the visualization is about and what message it intends to convey. |
| Missing Axis Title | The axis title is absent, making the meaning of the axis ambiguous. |
| Missing Legend | The legend is absent; can sometimes be compensated for with labels on the visual marks, but when all labeling is absent the visualization is incomprehensible. |
| Missing Value Labels | Value labels are absent from the chart, leaving readers unable to determine exact values. |
| Missing Axis | The axis itself is absent from the visualization. |
| Missing Axis Ticks | The tick marks on the axis are absent. |
| Missing Units | The units of measurement are not displayed on the chart. |
| Misrepresentation | Data values are drawn disproportionately or not to scale. Commonly spotted as value labels that fail to match the visually encoded geometric objects. |
| Inconsistent Tick Intervals | Tick intervals in the chart are not consistent, violating the reader's expectation and showing false patterns. Can be exploited maliciously to create a distorted visual perception. |
| Inconsistent Binning Size | The boundaries of binning groups vary, putting more or fewer items into specific groups and resulting in manipulated statistical calculations. |
| Violating Color Convention | A color mismatch between colors and the categories they represent. |
| Inconsistent Grouping | Some entities are grouped while others are not, making a dominating entity look less dominant by splitting it into smaller members while other groups remain whole. |
| Inconsistent Tick Labels | Tick labels are not in the same format across the axis. |
| Inconsistent Value Labels | Value labels are inconsistently annotated across the chart. |
| Plotting Out of Chart | A data value is plotted beyond the axis range so that its geometric mark falls outside the chart area. |
| Illegible Text | Text that overlaps itself or other text and becomes unreadable. |
| 3D | A perspective distortion technique where closer objects appear larger despite being the same size, allowing more visual ink for smaller objects in 3D bar charts. |
| Area Encoding | Data values are linearly encoded as areas, but according to Stevens' power law (exponent ~0.7 for area) readers consistently underestimate the values. |
| Ineffective Color Scheme | Use of rainbow colors, categorical colors on sequential data, or sequential colors on categorical data. Dichotomy colors can hide underlying distributions (e.g., a slight majority conceals a near-equal minority). |
| Inappropriate Use of Smoothing | Interpolation between data points creates non-existing data points, misleading readers about the actual data. |
| Inappropriate Aspect Ratio | The aspect ratio of the chart is distorted, commonly seen in line charts, affecting the perceived slope and trends. |
| Misleading Title | The title does not match the actual message conveyed by the chart. |
| Overplotting | Visual marks overlap in the same position, hiding overlapping marks from the reader and resulting in understated areas or densities. |

---

EVALUATION INSTRUCTIONS

Assess the candidate response on the following three fields:

**target_flaw_prominence**

Because the model was prompted with only "Evaluate this chart," 
responses typically contain a mix of positive observations, neutral 
descriptions, and identified flaws. Assess how prominently the target 
flaw appears within that full response, using the scale below:

- "primary":    the target flaw is the dominant finding — it receives 
                the most attention and is fully and clearly stated. 
                Other observations may be present but are shorter or 
                less developed.
- "supporting": the target flaw is fully and clearly stated, but 
                receives roughly equal or less weight than other 
                findings in the response.
- "incidental": the target flaw is hinted at or partially described — 
                close enough to suggest awareness of the issue but 
                not a clear, complete identification of it.
- "absent":     the target flaw is not identified at all.

The response does not need to use the exact category name — match on 
substance. To illustrate the scale, consider a Truncated Axis flaw 
where the y-axis starts at 80 instead of 0:

- primary:    "The main issue is that the y-axis begins at 80 rather 
              than 0, making the differences between bars look far 
              larger than they are. [further discussion of this flaw 
              follows, other points are brief]"
- supporting: "The colours are distinct and the title is clear. 
              However, the y-axis starts at 80 instead of 0, which 
              makes the differences between bars appear larger than 
              they are. The legend is also missing." [fully stated, 
              but alongside other findings of equal or greater weight]
- incidental: "The chart is well-labelled and easy to read. The scale 
              appears right-skewed." [hints at the axis issue but does 
              not identify the truncation clearly]
- absent:     the response describes the chart without ever 
              referencing the axis starting point or truncation.

Vague statements such as "the scale looks off" or "the chart could be 
clearer" do not qualify even as incidental — the response must identify 
the specific problematic feature described in the ground truth.

**other_flaws_mentioned**

List any flaw categories mentioned in the response beyond the target 
flaw. Use only the exact category names from the taxonomy table above. 
If a response mentions something that appears to be a flaw but does not 
match any taxonomy entry, omit it — do not invent new category names. 
If none, return an empty list.

**rationale**

Write one or two sentences explaining your verdict for 
`target_flaw_prominence`, citing specific phrasing from the candidate 
response where possible.

---

OUTPUT FORMAT

Respond with a JSON object only. Do not include any text outside the 
JSON object.

{
  "rationale": "<one or two sentences explaining your verdict>",
  "target_flaw_prominence": "primary" | "supporting" | "incidental" | "absent",
  "other_flaws_mentioned": ["category_name", ...]
}

---

INPUTS

Ground-truth flaw category: {{flaw_category}}
Ground-truth flaw description: {{flaw_description}}
Candidate response: {{model_response}}
