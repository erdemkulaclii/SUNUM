# GDELT (GKG 2.0) and Keyword-Based News Retrieval: Validity, Biases, and Validation Best Practices for the Doppelgänger Coverage Study

> **How the citations were checked (read first).** Crossref (api.crossref.org), doi.org and blog.gdeltproject.org were **blocked** in this research session (DNS/proxy refusal), so DOIs could not be resolved directly. Each citation has one of these tags:
> - **[V]** the DOI or bibliographic data was confirmed in this session by a search result or repository page (URL given).
> - **[M]** the DOI comes from my prior knowledge. It is high confidence but was **not re-verified in this session**. Check it at doi.org before final submission.
> - **[?]** uncertain. Must be checked.
> To verify the [M] items, allow api.crossref.org / doi.org in the session's network settings.

---

## 1. Documented limitations of GDELT (GKG/Events/DOC): coverage bias, duplication, geocoding, translation, source-list drift

### Takeaway
Peer-reviewed evaluations agree on three points. GDELT's raw output has low precision for event-level claims. It contains large numbers of duplicates. Its source base is unrepresentative (English/US-heavy) and changes over time. GDELT is therefore defensible as a *media-attention* index (what got published, by which outlets, and when), as long as the study is explicit about the sampling frame and validates its filters. It should not be read as a measure of real-world events or of "global" coverage.

### Cited Findings
**Core evaluations**
- Wang, Kennedy, Lazer & Ramakrishnan (2016), "Growing pains for global monitoring of societal events," *Science* 353(6307), 1502–1503. The paper compared GDELT and ICEWS protest events with a hand-curated gold standard. **Only 21% of GDELT's reported protest events referred to real protests.** ICEWS was more accurate but reported the same event more than once, which inflated counts. The two systems rarely agreed on which protests occurred. — [Northeastern news release](https://news.northeastern.edu/2016/09/29/study-using-big-data-to-monitor-societal-events-shows-promise-but-the-coding-tech-needs-work); [NetSI abstract page](https://www.networkscienceinstitute.org/publications/growing-pains-for-global-monitoring-of-societal-events). DOI **10.1126/science.aaf6758 [M]**: the volume, issue and pages were confirmed, but the DOI string itself was not shown in the search results.
- Hammond & Weidmann (2014), "Using machine-coded event data for the micro-level study of political violence," *Research & Politics* 1(2). The paper benchmarks GDELT against two hand-coded conflict datasets for micro-level (subnational) analysis. Its well-known conclusion is that GDELT is usable at coarse spatial and temporal aggregation, but geolocation is biased toward capitals and major cities and is weak at fine resolution. Note that this summary of findings comes from my knowledge; the search results confirmed only the scope. DOI **10.1177/2053168014539924 [V]** — [KOPS Konstanz record](https://kops.uni-konstanz.de/entities/publication/cd1512fc-1853-4302-9829-cb83f47cbbcb)
- Kwak & An (2016), "Two Tales of the World: Comparison of Widely Used World News Datasets GDELT and EventRegistry," *Proc. ICWSM* 10(1), 619–622 (poster). The paper found **significant differences in scale and in news sources** between GDELT and EventRegistry, but **high similarity in news geography**. GDELT indexes far more documents and also draws on broadcast and print, whereas ER relies mainly on RSS. The authors advise using either dataset "with caution." — [AAAI OJS page](https://ojs.aaai.org/index.php/ICWSM/article/view/14763); [arXiv 1603.01979](https://arxiv.org/pdf/1603.01979). DOI likely **10.1609/icwsm.v10i1.14763 [?]**, inferred from the OJS article ID and not confirmed.
- Kwak & An (2014), "A first look at global news coverage of disasters by using the GDELT dataset," *SocInfo 2014*, LNCS 8851, Springer. DOI **10.1007/978-3-319-13734-6_22 [M]**. The companion arXiv paper, "Understanding News Geography and Major Determinants of Global News Coverage of Disasters," uses the GKG to study which countries' disasters get covered by which countries' media. — [arXiv 1410.3710](https://arxiv.org/pdf/1410.3710)
- Hoffmann, Santos, Neumayer & Mercea (2022), "Lifting the Veil on the Use of Big Data News Repositories: A Documentation and Critical Discussion of a Protest Event Analysis," *Communication Methods and Measures* 16(4), 283–302. The authors document the "many hidden or partly hidden preparatory steps" needed to extract protest events from GDELT. They argue that ready-made GDELT data *can be made more valid but should not be accepted at face value*. The article is open access and is the closest methodological template for this study: it documents every filtering step. DOI **10.1080/19312458.2022.2128099 [V]** — [City Univ. open-access PDF](https://openaccess.city.ac.uk/28866/1/Hoffmann_Lifting%20the%20Veil%20on%20the%20Use%20of%20Big%20Data%20News%20Repositories%20A%20Documentation%20and%20Critical%20Discussion%20of%20A%20Protest%20Event%20Analysis.pdf)
- Leetaru & Schrodt (2013), "GDELT: Global data on events, location, and tone, 1979–2012," paper presented at the ISA Annual Convention. This is a conference paper with **no DOI**; cite it as a convention paper. (No URL verified this session.)
- Ward, Beger, Cutler, Dickenson, Dorff & Radford (2013), "Comparing GDELT and ICEWS Event Data," *Analysis* 21(1), 267–297. **[M/?]** This is a non-mainstream outlet with no known DOI, so verify the bibliographic details. It is usually cited for the finding that GDELT records far more events than ICEWS and that many of them are duplicates or noise.
- Raleigh, Kishi & Linke (2023), "Political instability patterns are obscured by conflict dataset scope conditions, sources, and coding choices," *Humanities and Social Sciences Communications* 10, art. 74. DOI **10.1057/s41599-023-01559-4 [M]**. ACLED authors criticise automated, media-scraped datasets (GDELT, ICEWS) for duplication, misclassification and source-driven bias.
- Day, Pinckney & Chenoweth (2015), "Collecting data on nonviolent action: Lessons learned and ways forward," *Journal of Peace Research* 52(1), 129–133. DOI **10.1177/0022343314533985 [M]**. The paper reports serious validity problems when GDELT is used for protest/nonviolent-action data.
- Weidmann (2016), "A closer look at reporting bias in conflict event data," *AJPS* 60(1), 206–218. DOI **10.1111/ajps.12196 [M]**. Media-based event data under-report in areas with weak media/communications coverage. Use this as the general "reporting bias" citation.
- A *PSRM* article, "The prevalence and severity of underreporting bias in machine- and human-coded data," directly compares machine- and human-coded event data on under-reporting. — [Cambridge Core abstract](https://resolve-he.cambridge.org/core/journals/political-science-research-and-methods/article/abs/prevalence-and-severity-of-underreporting-bias-in-machine-and-humancoded-data/E7B648ECA1E52DDAA4BF79CB622F520A) (authors and DOI not captured **[?]**)
- A 2022 PeaceRep report on GDELT notes that "questions remain regarding the quality and possible bias of GDELT data" and recommends benchmarking automated coding against human coding. — [PeaceRep GDELT report (PDF)](https://peacerep.org/wp-content/uploads/2022/07/GDELT-Report-Digital.pdf)

**Source-country field (relevant to the US 373 / DE 29 / IT 13 split)**
- GDELT's source-country lookup is **not** based on the domain TLD or on registration data. It is inferred from **which locations an outlet mentions most often across the GKG**, on the assumption that outlets cover nearby places more than distant ones. The original English list covered **13,155 English-language websites**, coded with FIPS10-4 country codes. GDELT explains that TLDs are uninformative because few outlets use country TLDs. The method was later run on all coverage in the **65 languages GDELT live-translates**. GDELT calls it "a reasonable approximation" and gives caveats for low-volume and non-geographically-focused outlets. — [GDELT blog: "Mapping the Media: A Geographic Lookup of GDELT's Sources"](https://blog.gdeltproject.org/?p=4818); [GDELT blog: Multilingual Source-Country Crossreferencing Dataset](https://blog.gdeltproject.org/?p=1647); [GDELT blog: 2015–2021 update with BigQuery SQL](https://blog.gdeltproject.org/?p=14261). These are summarised from search snippets; the blog itself could not be fetched.
- A secondary OSINT document wrongly describes the field as inferred from domain registration/TLD. GDELT's own blog contradicts this, so cite the GDELT blog. — [GDELT blog p=4818](https://blog.gdeltproject.org/?p=4818)
- Kwak & An (2016) show that GDELT's and EventRegistry's *source* lists differ sharply even when the geography of coverage is similar. Source-country counts therefore depend on the dataset's crawl, not on the real-world media population. — [AAAI OJS](https://ojs.aaai.org/index.php/ICWSM/article/view/14763)

### Inferences
- **The source-country lookup is circular for this study.** An outlet coded "US" is one that mentions US places a lot. Large US-based aggregators and international English outlets (e.g., Yahoo/MSN-style portals, wire-reprint sites) will be coded US even when their audience is global. "Source country" should therefore be described as *GDELT-inferred outlet geography*, not as "national media coverage." The lookup also dates from 2018 and is static. Outlets created or reorganised after it was built will be missing (NA) or misassigned. **Report the share of the 511 articles whose domain had no lookup match.**
- **Translation pipeline.** GDELT's translingual stream machine-translates non-English text into English before GKG extraction. A keyword rule applied to the translated *title/URL* is affected in two ways. URLs stay in the original language, so English terms in a German URL will not match. Translated titles depend on how the MT system renders "Doppelgänger." In German, "Doppelgänger" is a native word, so R1 may *over*-match generic German uses of the word. **Report precision separately for the English and translingual streams.**
- **Source-list drift.** GDELT's monitored source list grows and changes continuously. Because the study window is only three weeks, within-window drift is probably small. Comparisons with other periods or campaigns would need normalisation by total volume per period (this study already does that).
- **Geocoding.** Hammond & Weidmann's capital/major-city bias matters only if the study uses GKG V2Locations ("mentioned location"). This study uses source country, so geocoding error is a secondary issue. Say so explicitly, so that reviewers do not apply the event-data critiques to a design they do not fit.
- **Positioning sentence for the paper:** "Following Hoffmann et al. (2022), we treat GDELT not as a census of world media but as a large, documented, but non-random sampling frame of online news. We therefore (i) document every filtering step, (ii) validate the keyword filter for precision and recall, and (iii) normalise by GDELT's own per-country volume rather than by population."

### Gaps
- I could not open GDELT's official GKG 2.0 codebook or the translingual announcement in this session (blog.gdeltproject.org was blocked). Cite them directly: the GDELT GKG 2.0 Codebook (V2.1) and the "GDELT Translingual" blog post (2015).
- I did not retrieve the exact full-text figures from Ward et al. (2013) or Hammond & Weidmann (2014).
- I did not find a published, quantified estimate of GDELT duplication *specifically in the GKG* (as opposed to the Events table).

---

## 2. Validating keyword-based retrieval: precision AND recall, sampling, sample size, inter-coder reliability

### Takeaway
The standard in communication research (Stryker et al. 2006) is to report **both precision and recall** for any database search string. Precision alone (90.6% on n=32) does not establish validity; recall is the larger gap. The study's 511 articles collapse to only 145 distinct titles, so precision can be measured as a **census** of all 145 titles at low cost. Recall can be estimated from data the study already has (overlap between R1 and R2) and from an inexpensive "near-miss" sample.

### Cited Findings
- Stryker, Wray, Hornik & Yanovitzky (2006), "Validation of Database Search Terms for Content Analysis: The Case of Cancer News Coverage," *Journalism & Mass Communication Quarterly* 83(2), 413–430. The paper argues that sampling error in database-driven content analysis has been "largely ignored." It scores search phrases on **recall** ("ability to accurately call up items of interest") and **precision** ("ability to avoid extraneous items"). DOI **10.1177/107769900608300212 [V]**: the DOI appears in the indexing URL. — [Pollux record](https://www.pollux-fid.de/r/cr-10.1177/107769900608300212)
- Salton's classic IR text defines recall as the proportion of relevant material actually retrieved, and notes that recall and precision tend to vary inversely. Use this to justify reporting both. — [Salton (1986) PDF](https://eurospider.ch/images/pddfs-ect/salton-text-retrieval-systems-1986.pdf.pdf)
- King, Lam & Roberts (2017), "Computer-Assisted Keyword and Document Set Discovery from Unstructured Text," *AJPS* 61(4), 971–988. Human-chosen keyword lists are idiosyncratic and miss many relevant documents (people choose different keywords for the same concept). The paper offers an algorithm to expand keywords from a seed "reference set" and a "search set." DOI **10.1111/ajps.12291 [M]**
- Grimmer & Stewart (2013), "Text as Data: The Promise and Pitfalls of Automatic Content Analysis Methods for Political Texts," *Political Analysis* 21(3), 267–297. Its four principles include "validate, validate, validate." Dictionary methods must be validated *in the specific corpus*, because dictionaries do not transfer across domains. DOI **10.1093/pan/mps028 [M]**
- Krippendorff (2004), "Reliability in content analysis: Some common misconceptions and recommendations," *Human Communication Research* 30(3), 411–433. Suggested thresholds: α ≥ .800 for firm conclusions, and .667 ≤ α < .800 for tentative conclusions only. DOI **10.1111/j.1468-2958.2004.tb00738.x [M]**
- Hayes & Krippendorff (2007), "Answering the call for a standard reliability measure for coding data," *Communication Methods and Measures* 1(1), 77–89. Introduces the KALPHA macro and recommends α over κ and percent agreement. DOI **10.1080/19312450709336664 [M]**
- Lombard, Snyder-Duch & Bracken (2002), "Content analysis in mass communication: Assessment and reporting of intercoder reliability," *Human Communication Research* 28(4), 587–604. Requires ICR to be reported with a named index, the subsample size and selection method, and coder training. Percent agreement alone is insufficient. DOI **10.1111/j.1468-2958.2002.tb00826.x [M]**

### Inferences (concrete, numeric, implementable)
All numbers below are my own calculations, using standard formulas.

**A. Check of the current figure.** 29/32 = 90.6%. The Wilson 95% CI is [75.8%, 96.8%], which matches the presentation. The CI is about 21 points wide, which is too wide to be a strong validity claim.

**B. Sample size for precision.** The normal approximation is n = z²·p(1−p)/E², with z = 1.96.
| Target half-width E | assume p = 0.906 | conservative p = 0.5 |
|---|---|---|
| ±10 pp | 33 | 97 |
| ±5 pp | **131** | **385** |
| ±3 pp | 364 | 1,068 |

With the finite-population correction n' = n/(1 + (n−1)/N):
- For the **N = 145 distinct titles**, ±5 pp needs about **70** titles (p = .906) or about **106** titles (p = .5).
- For the **N = 511 articles**, ±5 pp needs about **105** articles (p = .906) or about **220** articles (p = .5).
- **Recommendation: code all 145 distinct titles (a census).** Title-level precision then has no sampling error. Article-level precision is the share of the 511 articles whose title was coded relevant, i.e., title verdicts weighted by reprint count. Report both: "title-level precision" and "article-level (reprint-weighted) precision."

**C. Recall: three feasible estimators, in order of rigour.**
1. **External reference set (gold standard).** Build an independent list of relevant articles for 20 Sep–11 Oct 2022 from a different retrieval system. Options: the GDELT DOC 2.0 API full-text search for "Doppelganger"/"Doppelgänger" (it searches article text, not only title/URL); Media Cloud; or Factiva/Nexis Uni with an independent query. Possible seeds include outlets that cited Meta's 27 Sep 2022 takedown report. Restrict the reference set to URLs that are present in the scanned GKG files, so that *retrieval* failure is separated from *GDELT coverage* failure. Then recall = |reference ∩ retrieved| / |reference|. For a ±10 pp CI at recall ≈ 0.8, you need about 62 reference articles; for ±5 pp, about 246.
2. **Near-miss ("null set") sampling.** Take GKG records in the window that pass a *looser* rule but fail R1/R2 (e.g., Meta/Facebook AND Russia in the title/URL, but without the network/fake/disinformation terms; or "Doppelganger" without the Russia context). Draw a random sample of n from this pool of size N_pool and code it. Then:
   - estimated false negatives: FN̂ = N_pool × (relevant in sample / n)
   - estimated recall: TP / (TP + FN̂)
   - If **0** relevant items are found in n, the "rule of three" gives a 95% upper bound on the pool prevalence of about 3/n. For example, n = 150 bounds the prevalence at ≤ 2%. This mirrors Stryker et al.'s logic and King et al.'s search-set idea.
3. **Capture–recapture using R1 and R2 (no new coding needed).** Treat R1 and R2 as two "captures" of the same set of relevant articles, after the precision filter has removed false positives.
   - Chapman estimator: N̂ = (n₁+1)(n₂+1)/(m+1) − 1, where m is the overlap.
   - Recall of R1 ∪ R2 = (n₁ + n₂ − m)/N̂.
   - **Caveat:** the method assumes the two rules capture articles independently. R1 and R2 probably both favour high-salience stories (positive dependence), which **underestimates N̂ and therefore overestimates recall**. Present it as an *upper bound* on recall and pair it with estimator 1 or 2.

**D. Inter-coder reliability.**
- Have a **second, independent human coder** code the relevance of all 145 titles (or at least a random subset of ≥ 50), blind to the first coder's and the AI's labels, using a written codebook. The codebook should define "relevant" as being about the Russian "Doppelgänger" operation or Meta's Sept-2022 takedown of it.
- Report Krippendorff's α (nominal), plus Cohen's κ and raw agreement for transparency.
- Thresholds: α ≥ .80 is acceptable; .667–.80 is tentative.
- Resolve disagreements by discussion and report the final adjudicated precision.

**E. Report precision by rule and by stream:** R1-only, R2-only, R1∩R2, and English vs. translingual. This shows *which* rule is driving any errors.

### Gaps
- I did not retrieve the exact numeric precision and recall that Stryker et al. reported for their cancer search strings, or their recommended thresholds. Read the full paper to cite specific values.
- I did not locate the full text of Lombard et al. (2002) in this session. Their often-cited guideline that a reliability subsample should be "≥50 units or ≥10% of the sample" comes from my memory and needs verification before it is cited.

---

## 3. Wire-service syndication and duplicate content in news-volume measures

### Takeaway
Of the 511 retrieved URLs, only 145 have distinct titles, so roughly 72% are reprints. For a media-attention study, this is a substantive finding (amplification through wire syndication), not just noise. Measures should be reported at **three levels**: URLs (exposure/volume), distinct stories (editorial production), and distinct outlets. Near-duplicate detection (shingling) should be used, not exact-title matching alone.

### Cited Findings
- Nicholls (2019), "Detecting Textual Reuse in News Stories, At Scale," *International Journal of Communication* 13. The paper uses **n-gram shingling** to detect shared text across news articles. It separates newswire copy, PR material, outlet-to-outlet copying and incidental overlap. It finds that wire reliance is robust but lower than earlier studies suggested. It also notes that much wire copy is **unattributed**, so it cannot be detected without cross-referencing the wires. — [IJoC article](https://ijoc.org/index.php/ijoc/article/view/9904); [PDF](https://ijoc.org/index.php/ijoc/article/download/9904/2777)
- Lewis, Williams & Franklin (2008), as quoted in Nicholls (2019): 30% of published UK press items were wholly dependent on agency copy. — [Nicholls 2019, IJoC](https://ijoc.org/index.php/ijoc/article/view/9904)
- Cagé, Hervé & Viaud built a large French online-news dataset that includes AFP and used plagiarism-detection methods to measure article originality. They found heavy copying. — [NBER conference paper PDF](https://conference.nber.org/conf_papers/f89940/f89940.pdf)
- Kuntur et al. (LREC 2026) studied cross-lingual reuse. Reuse appears in 52% of Slovenian Press Agency articles. Much of it is **non-literal**, so simple lexical matching misses it. This matters for the translingual stream. — [ACL Anthology author page](https://aclanthology.org/people/soveatin-kuntur/unverified/)
- Boumans, Trilling, Vliegenthart & Boomgaarden (2018), "The agency makes the (online) news world go round: The impact of news agency content on print and online news," *International Journal of Communication* 12. This is one of the few large-scale measurements of news agency reliance, as cited by Nicholls (2019). — [Nicholls 2019 citing it](https://ijoc.org/index.php/ijoc/article/view/9904). No DOI (IJoC). **[M]**
- Welbers, van Atteveldt, Kleinnijenhuis & Ruigrok (2018), "A gatekeeper among gatekeepers: News agency influence in print and online newspapers in the Netherlands," *Journalism Studies* 19(3), 315–333. DOI **10.1080/1461670X.2016.1190663 [M]**
- Wang et al. (2016) showed that duplication (the same event reported more than once) inflates counts in automated systems. — [Northeastern release](https://news.northeastern.edu/2016/09/29/study-using-big-data-to-monitor-societal-events-shows-promise-but-the-coding-tech-needs-work)

### Inferences (implementable pipeline)
1. **Normalise titles.** Lowercase, strip the outlet suffix (" - AP News", " | Reuters"), strip punctuation, and Unicode-normalise (NFKC) so that "Doppelgänger" and "Doppelganger" are treated the same.
2. **Detect near-duplicates.** Compute character 5-gram or word 3-gram shingles on the title (and on body text if it is fetched) and use MinHash/LSH. Cluster pairs with Jaccard ≥ 0.8 for titles, or ≥ 0.5 for body text. Report how sensitive the cluster count is to the threshold, e.g., at 0.6, 0.7, 0.8 and 0.9. Each cluster is a "story."
3. **Attribute the wire source.** Tag each cluster by origin (AP, Reuters, AFP, dpa, ANSA, original reporting) using bylines or URL patterns, or by fetching the text. Report the share of the 511 URLs that are AP reprints.
4. **Report three counts per country and day:** URLs, distinct stories, and distinct outlets (registered domains). Also report a concentration index (e.g., the Herfindahl index of URLs across stories) to quantify syndication-driven amplification.
5. **Interpretation.** The US advantage in raw URLs (373) is likely driven partly by local US newspaper sites that carry the AP feed. Re-run the cross-country comparison using **distinct stories** and **distinct outlets**. If the US–Germany gap shrinks a lot, the claim should read: "US exposure is driven by wire syndication rather than by more independent editorial attention."

### Gaps
- I found no study that quantifies AP/Reuters syndication *inside GDELT* specifically. This is an opportunity: the study can report its own 145/511 ratio as a descriptive contribution.
- I did not verify Boumans et al. (2018)'s numeric findings.

---

## 4. Normalising coverage across countries; source country vs. mentioned location vs. audience; news-flow theory

### Takeaway
Per-capita normalisation is inappropriate for GDELT. Volume reflects GDELT's crawl, not population or readership. The study's current metric (matches per 100,000 scanned GDELT records from the same source country) is the right **within-frame** normalisation. It should be presented as "relative salience within each country's GDELT-monitored output," with CIs, and paired with story-level and outlet-level versions. Interpretation should draw on news-flow theory, which treats US/German attention to a Russia-related story as a function of elite-nation status, proximity and relevance.

### Cited Findings
- GDELT's source-country field is inferred from outlet *location mentions*, not from audience or ownership. It is an approximation, with caveats for low-volume and non-geographic outlets. — [GDELT blog p=4818](https://blog.gdeltproject.org/?p=4818); [GDELT blog p=1647](https://blog.gdeltproject.org/?p=1647)
- Kwak & An (2016) found that GDELT and EventRegistry differ greatly in indexed volume and active sources, yet produce "extremely similar" news geographies. **Ratios and shares** therefore travel across datasets better than raw counts do. — [AAAI OJS](https://ojs.aaai.org/index.php/ICWSM/article/view/14763); [later arXiv summary](https://arxiv.org/pdf/1802.06437)
- An & Kwak / Kwak & An, "What We Read, What We Search: Media Attention and Public Attention Among 193 Countries," used GDELT to compare media attention with public (search) attention across countries. This is a model for linking source geography with audience interest. — [arXiv 1802.06437](https://arxiv.org/pdf/1802.06437)
- "The Drivers of Global News Spreading Patterns" uses GDELT to model how stories spread across countries' media. It is useful for framing cross-national diffusion. — [arXiv 2305.13769](https://arxiv.org/pdf/2305.13769)
- Kwak & An's disaster-coverage work uses the GKG to identify the determinants of which countries' events get covered by which media. It operationalises "news geography." — [arXiv 1410.3710](https://arxiv.org/pdf/1410.3710)
- Galtung & Ruge (1965), "The structure of foreign news," *Journal of Peace Research* 2(1), 64–90. News values include reference to elite nations, cultural proximity, meaningfulness and negativity. DOI **10.1177/002234336500200104 [M]**
- Wu (2000), "Systemic determinants of international news coverage: A comparison of 38 countries," *Journal of Communication* 50(2), 110–130. Trade volume and the presence of international news agencies are the strongest predictors of coverage. The US is the most covered country, and wire agencies structure flows. DOI **10.1111/j.1460-2466.2000.tb02844.x [M]**
- Chang (1998), "All countries not created equal to be news: World system and international communication," *Communication Research* 25(5), 528–563. DOI **10.1177/009365098025005004 [M]**
- Weidmann (2016) on reporting bias: coverage depends on media infrastructure, not only on newsworthiness. — DOI 10.1111/ajps.12196 **[M]**

### Inferences
- **Three concepts must be kept apart in the text:**
  - **source country**, meaning GDELT-inferred outlet geography: "where the outlet appears to be based";
  - **mentioned location**, from GKG V2Locations: "what places the story is about";
  - **audience**, which GDELT does not measure at all.

  The current results are about the first concept only.
- **Normalisation recommendation:**
  - (a) Keep "matches per 100k GKG records from that source country." This is within-frame salience, the same logic as GDELT's own volume-normalisation practice.
  - (b) Add CIs. For US, 373/1,468k gives 25.4 per 100k. Use a Poisson or Wilson CI on the proportion and test US vs. DE with a rate-ratio test. The current figures (25.4 vs. 15.4) imply a rate ratio of about 1.65, and the CI should be reported.
  - (c) Compute the same rate on **distinct stories** and on **distinct outlets**.
  - (d) Do **not** use per-capita figures. If an audience-weighted figure is desired, weight outlets by an external reach measure (e.g., Tranco/Similarweb rank), labelled as exploratory.
- **Interpretation through news-flow theory.** High US volume fits Wu (2000), where agency presence (AP) drives flows, and Galtung & Ruge, where elite-nation actors are involved (Meta is a US company). Germany's high *relative* rate fits proximity and relevance: German outlets (e.g., Der Spiegel, Bild, t-online) were among those impersonated in the Doppelgänger operation. Confirm this detail with the Doppelgänger literature notes prepared in parallel.

### Gaps
- I did not retrieve GDELT's official "normalization files" documentation (the blog was blocked). Cite GDELT's own description of its per-country/per-day total-volume files directly.
- The denominators per country (e.g., the US record count) are not in my notes. I inferred about 1.47M US records from 373/25.4×100k; check this against the study's own table.

---

## 5. LLM/AI-assisted coding: validity evidence and reporting standards when one coder is AI-assisted

### Takeaway
LLMs can match or exceed crowd workers on relevance annotation (Gilardi et al. 2023). The literature is equally clear that **LLM labels must be validated task by task against human labels** (Pangakis et al. 2023; Törnberg 2024). A study whose only coder is AI-assisted does not meet current content-analysis standards. The minimum fix is one blind, independent human coder, reliability statistics, and a full disclosure of the LLM setup.

### Cited Findings
- Gilardi, Alizadeh & Kubli (2023), "ChatGPT outperforms crowd workers for text-annotation tasks," *PNAS* 120(30), e2305016120. The study covered four datasets of tweets and news articles (n = 6,183), with tasks including relevance, stance, topics and frames. Zero-shot ChatGPT accuracy was about 25 pp above MTurk crowd workers on average. Its intercoder agreement exceeded that of both crowd workers and trained annotators. The cost was about $0.003 per annotation. DOI **10.1073/pnas.2305016120 [V]** — [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC10372638)
- Pangakis, Wolken & Fasching (2023), "Automated Annotation with Generative AI Requires Validation," arXiv:2306.00176. The authors replicated 27 annotation tasks across 11 datasets with GPT-4. Performance is "promising but highly contingent on both the dataset and the type of annotation task," so validation against human labels is needed for each task. Consistency scores across repeated runs help flag edge cases. — [arXiv](https://arxiv.org/abs/2306.00176v1)
- Pangakis & Wolken (ICWSM 2025), "Keeping Humans in the Loop: Human-Centered Automated Annotation with Generative AI." Label quality is generally high, but there is significant variation across tasks even within a dataset. "Grounding automated annotation in validation labels generated by humans is essential." — [AAAI OJS](https://ojs.aaai.org/index.php/ICWSM/article/view/35883); [arXiv 2409.09467](https://arxiv.org/abs/2409.09467v2)
- Törnberg (2024), "Best Practices for Text Annotation with Large Language Models," *Sociologica* 18(2), 67–85. The paper sets standards for reliable, reproducible and ethical LLM annotation. They cover model selection (preferring open models), prompt engineering, structured prompting, **prompt-stability analysis**, **rigorous validation against human labels**, and ethical and legal issues. The arXiv version calls the field an "academic Wild West." — [Sociologica article](https://sociologica.unibo.it/article/view/19461); [arXiv 2402.05129](https://www.arxiv.org/pdf/2402.05129)
- Törnberg (2023), "ChatGPT-4 outperforms experts and crowd workers in annotating political Twitter messages with zero-shot learning," arXiv:2304.06588. **[M]** (preprint)
- Törnberg, "How to use LLMs for Text Analysis" (arXiv 2307.13106), a practical guide. — [arXiv](https://arxiv.org/pdf/2307.13106)
- Ziems et al. (2024), "Can Large Language Models Transform Computational Social Science?," *Computational Linguistics* 50(1), 237–291. DOI **10.1162/coli_a_00502 [M]**. The authors find that LLMs are good at some classification tasks and weaker at others, and recommend using them as an aid to human annotators.
- Reiss (2023), "Testing the Reliability of ChatGPT for Text Annotation and Classification: A Cautionary Remark," arXiv:2304.11085. **[M]** It finds that outputs vary across runs and prompt wordings.

### Inferences (minimum reporting checklist for this study)
1. **Disclose the AI-assisted coder:** model name and version, access date, interface (API or chat), temperature, the exact prompt (in an appendix), the label set, and whether the human saw the AI suggestion before deciding.
2. **Stability:** run the LLM classification at least 3 times, or with 2 prompt paraphrases, and report self-agreement (α). This follows Törnberg (2024) and the Pangakis et al. consistency scores.
3. **Human validation:** have one independent human coder, blind to the AI output, code the same units. Report α and κ for human vs. human-with-AI, and for human vs. raw LLM.
4. **Name the coding status honestly:** "single coder with LLM assistance; reliability assessed against an independent human coder on n = X units (α = …)."
5. **Precision is the right AI task.** Relevance classification of 145 headlines is close to the "relevance" task where Gilardi et al. found strong LLM performance. That supports the approach, but it does not replace validation.

### Gaps
- I found no formal, journal-mandated reporting standard for LLM-assisted content analysis, comparable to CONSORT. The closest are Törnberg (2024) and the Pangakis et al. workflow. Say so.

---

## 6. Studies using GDELT to study coverage of disinformation and influence operations

### Takeaway
I found **no peer-reviewed study that uses the GKG specifically to measure news coverage of a named influence operation** such as Doppelgänger. The literature uses GDELT for related questions: media bias and structural breaks around the Russia–Ukraine war, and state-media amplification. This gap can be framed as a contribution, while being careful not to overclaim novelty.

### Cited Findings
- An *AIB Insights* article, "Media in the Geopolitical Crossfire: Identification and Novel Data Sources for IB Research," proposes using GDELT to detect structural breaks that indicate interference or bias in media coverage. It cross-checks with Google Trends and applies the approach to 2022 coverage of Russia's invasion of Ukraine. — [AIB Insights](https://insights.aib.world/article/66442-media-in-the-geopolitical-crossfire-identification-and-novel-data-sources-for-ib-research)
- The GDELT blog reports a Simon Fraser University study that used GDELT TV data and found that **Russia Today covered the 2022 Freedom Convoy protests more than any other foreign outlet**. This is an influence/amplification use case, reported via GDELT's blog and not peer-reviewed as cited. — [GDELT blog](https://blog.gdeltproject.org/global-news-russia-today-covered-freedom-convoy-protests-more-than-any-foreign-outlet-research/amp/)
- The GDELT blog also lists a UCD study using GDELT to examine whether Confucius Institutes influence media coverage of China. This is also blog-reported. — [GDELT blog search result](https://blog.gdeltproject.org/?p=14831)
- The GDELT blog tracked TV mentions of "disinformation" on CNN, MSNBC and Fox, with sharp increases after 2016. — [GDELT blog](https://blog.gdeltproject.org/?p=5922)
- GDELT is cited as a data source in Harvard's *Network Propaganda* (Benkler, Faris & Roberts 2018) context. — [GDELT blog](https://blog.gdeltproject.org/harvard-network-propaganda-manipulation-disinformation-and-radicalization-in-american-politics/amp/)

### Inferences
- The 96.3% concentration on 27–28 Sep 2022 is consistent with a **single-trigger news event**: Meta's public takedown announcement, and the EU DisinfoLab report released around the same time. That is a typical "event-driven attention spike." The measure therefore captures *coverage of the takedown announcement*, not coverage of the operation over its lifetime. State this in the scope conditions, and confirm the announcement date with the parallel Doppelgänger notes.
- Suggested framing: "To our knowledge, no published study has used the raw GKG archive to trace international coverage of a specific attributed influence-operation takedown. Existing GDELT work on disinformation focuses on structural breaks (AIB Insights 2023) or state-media amplification (GDELT TV analyses)."

### Gaps
- My search effort was limited (about 15 tool calls). There may be ICWSM or *Journal of Quantitative Description* papers using GDELT for state-media or influence-operation coverage that I did not find. Before claiming novelty, run a targeted Google Scholar search for "GDELT" together with "influence operation", "IRA", "RT", "Sputnik" or "disinformation".
- Meta's adversarial threat report and the EU DisinfoLab "Doppelganger" report (both Sept 2022) belong to the parallel Doppelgänger-literature notes and are not covered here.

---

## Summary: priority upgrades (ranked by value per effort)
1. **Census-code all 145 distinct titles** with two coders, one of whom is a blind human. Report title-level and reprint-weighted precision, and Krippendorff's α. (Section 2B/D)
2. **Estimate recall:**
   - Chapman capture–recapture from R1/R2 overlap, as an upper bound;
   - a near-miss sample of about 150 records, using the rule of three if no relevant items are found;
   - optionally, an external reference set from the GDELT DOC API full-text search or from Nexis. (Section 2C)
3. **Run deduplication at three levels:** URL, story (MinHash clusters), and outlet. Repeat the US/DE/IT comparison on stories and outlets. Report the AP share. (Section 3)
4. **Add CIs and a rate-ratio test** to the per-100k rates. Rename "source country" to "GDELT-inferred outlet country" and report the NA share. (Section 4)
5. **Disclose the LLM setup** using the Törnberg (2024) checklist. (Section 5)
6. **Add citations for the critiques:** Hoffmann et al. (2022) [V], Wang et al. (2016), Stryker et al. (2006) [V], Grimmer & Stewart (2013), King et al. (2017), Krippendorff (2004), Gilardi et al. (2023) [V], Törnberg (2024) [V], Nicholls (2019) [V], and Wu (2000) / Galtung & Ruge (1965).
