---
title: Building RAG Systems That Actually Work
date: 2026-04-14
category: RAG
excerpt: Lessons from shipping a production RAG pipeline to 1,000+ users — context-aware search, query refinement, and smart model routing.
read_time: 8 min read
---

Most RAG tutorials stop at "chunk your docs, embed them, retrieve top-k, feed to GPT." That gets you a demo. It does not get you a product.

Over the past year I built **Cobuddy**, a context-aware search system serving 1,000+ active users in US healthcare. Along the way I learned that the gap between a RAG demo and a RAG product is enormous — and it's almost never about the model.

Here's what actually mattered.

## 1. Context-Aware Search Beats Naive Retrieval

The default RAG pattern — embed a query, pull the top 5 chunks, send to the LLM — falls apart the moment your corpus gets large or your questions get nuanced.

What worked for us was building **two parallel indices**: one over raw document chunks, and another over pre-generated summaries and FAQs. At query time, the system searches both and merges the results before sending to the LLM.

This single change improved answer accuracy by **40%**.

> The best retrieval strategy isn't the one that finds the most relevant chunk. It's the one that gives the LLM enough context to reason correctly.

Why does this work? Because summaries capture *intent* and *structure* that individual chunks lose. A question like "What's the appeals process for denied claims?" needs context that spans multiple document sections. Summaries provide that bridge.

## 2. Query Refinement Is the Hidden Multiplier

Users type terrible queries. Short, vague, full of typos, missing context. If you pass those directly to your embedding model, you get mediocre retrieval no matter how good your index is.

We added a **hidden query-refinement step** between the user's input and the search. A lightweight LLM call that:

- Expands abbreviations and acronyms
- Adds implicit context from the conversation history
- Reformulates vague questions into specific, searchable queries

The user never sees this. They type "denied claim help" and the system searches for "What is the process for appealing a denied healthcare claim, including timelines and required documentation?"

This was cheap (a fast, small model handles it) and the retrieval quality improvement was dramatic.

## 3. Smart Routing Cuts Costs Without Cutting Quality

Not every query needs GPT-4. A simple factual lookup ("What's the phone number for Aetna?") can be handled by a much cheaper model. A complex multi-step reasoning question ("Compare the appeals processes for Aetna and UnitedHealth for out-of-network denials") genuinely needs the expensive model.

We built a **routing layer** that classifies each query by complexity and routes it to the most cost-effective model:

```python
def route_query(query, context):
    complexity = classify_complexity(query, context)
    if complexity == "simple":
        return "gpt-3.5-turbo"
    elif complexity == "moderate":
        return "gpt-4o-mini"
    else:
        return "gpt-4o"
```

The actual implementation is more nuanced (it considers the retrieved context quality too), but the principle is simple: **match model capability to task difficulty**.

Result: **60% reduction in API costs** with no measurable drop in answer quality.

## 4. Document Ingestion Is the Unsexy Bottleneck

Everyone wants to talk about the LLM. Nobody wants to talk about the ingestion pipeline. But this is where production RAG systems live or die.

Our pipeline processes **10,000+ chunks** across hundreds of documents. The challenges that don't show up in tutorials:

- **PDF layouts are adversarial.** Tables, multi-column layouts, headers/footers, watermarks — standard text extractors butcher these. We used **AI Vision** to handle the complex layouts that traditional parsers missed.
- **Chunk boundaries matter enormously.** Splitting mid-sentence or mid-paragraph destroys context. We chunk by semantic boundaries (sections, paragraphs) rather than fixed token counts.
- **Metadata is retrieval gold.** Every chunk carries its source document, section heading, page number, and document type. This metadata powers filtering and re-ranking.

## 5. What I'd Do Differently

If I were starting Cobuddy from scratch today:

- **Start with evaluation.** Build your eval set before you build your pipeline. Without a way to measure "better," you're tuning blind.
- **Log everything.** Every query, every retrieval result, every LLM response, every user action. The logs are how you find the failure modes.
- **Ship the simple version first.** Our fancy routing system came months after launch. The first version was naive RAG with good chunking. It was enough to learn what actually needed improving.

The gap between a RAG demo and a RAG product isn't the model or the framework. It's the hundred small decisions about how you process documents, refine queries, manage context, and route requests. Get those right and the LLM almost doesn't matter.
