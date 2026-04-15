# PHAN Proposal: MasqFit + Breathesafe Next-Phase Plan

## Overview

MasqFit and Breathesafe are an open-source mask recommendation and fit-data platform designed to help more people identify respirators that fit their faces well. The practical public-health problem is straightforward: a high-filtration mask only delivers strong protection if it fits the specific user, yet most people do not know which mask model and size are likely to fit them. Formal fit testing is highly valuable, but it is not broadly accessible at the population scale. The opportunity for MasqFit is therefore not to replace fit testing, but to make fit guidance far more scalable, more data-driven, and easier to improve over time.

I propose a two-year next phase focused on scale, validation, and model quality. The core goal is to increase the number of people who end up with a well-fitting respirator by giving them better mask recommendations, making those recommendations available on more devices, and improving the system as more fit outcomes are contributed. PHAN’s value as a partner would be to help move this from a promising technical platform into a measurable public-health intervention.

## Why This Matters

For environmental interventions, PHAN often looks for direct building-level metrics such as clean air delivery or illness reduction. MasqFit is different, but it can still be evaluated using credible proxy metrics tied to protection. We already know that respirator fit materially affects inward leakage and therefore affects protection. For this project, the most appropriate impact metrics are likely to be adoption and fit-success metrics rather than direct illness outcomes in the short term.

The key proxy logic is:

- if more people use the tool,
- and the tool helps a larger share of them identify a mask that actually fits,
- then more people will receive the protection associated with wearing a well-fitting respirator.

That is why scalability matters so much here. A modest improvement in mask-selection quality, if delivered to a large number of people, can have meaningful public-health value.

## Proposed Work Over the Next Two Years

### 1. Improve Fit Prediction Accuracy

The first line of work is to improve recommendation quality by collecting more data and building better models.

This includes:

- building partnerships with mask manufacturers, mask blocs, and community fit testers to collect more facial measurements paired with fit-testing results;
- reaching out to manufacturers for fit testing data, breathability data, and, where possible, facial-measurement-linked fit data;
- cleaning and ingesting external data sources such as Fit Test the Planet;
- incorporating strap tension into predictions by estimating strap length, force or pressure, and qualitative tightness;
- experimenting with mask-style-specific facial measurements so that the model can better account for differences among bifold, duckbill, boat, and other styles;
- supporting fit-test-only contribution pathways so users can contribute useful outcome data even if they do not want to share facial measurements.

This work should make the model more accurate, more sample efficient, and more privacy-compatible.

### 2. Run Validation Studies

The second line of work is validation. Internally, the current implementation appears to have roughly a 90% probability that at least one mask in the top three recommendations will fit. That is promising, but PHAN and other external partners will reasonably want stronger prospective evidence.

I propose two validation efforts:

- an independent MasqFit-led study in which participants receive top-three recommendations, rank them qualitatively, and then validate the most promising candidate using PortaCount fit testing;
- a more formal validation study designed with help from CDC NIOSH NPPTL, who indicated interest in helping with study design and validation.

These studies would test whether app-guided recommendations outperform unguided self-selection and would provide the strongest evidence that MasqFit delivers real-world value.

### 3. Build the Android Version

The third line of work is platform expansion. Today, MasqFit is strongest on iOS because Apple’s TrueDepth hardware provides a good facial measurement pipeline. Android is the largest scale opportunity and the largest technical gap.

The Android work has two parts:

- building an Android app that is stylistically and functionally consistent with the iOS version;
- developing a camera-only computer vision pipeline that can extract a facial mesh comparable enough to ARKit output that downstream modeling can remain similar across platforms.

If this is successful, MasqFit can move from an iOS-limited tool to a much more scalable cross-platform system.

## External Collaboration Opportunities

The recent CDC NIOSH NPPTL meeting clarified that MasqFit is complementary to their own upcoming app. Their current focus is adults and N95 masks, while MasqFit can focus more broadly on children, non-NIOSH-certified masks that nonetheless perform well, and the broader recommendation problem rather than only NIOSH-panel measurement.

Potential collaboration opportunities include:

- validation-study design support from NPPTL;
- access to headform facial measurements and fit-testing data for benchmarking;
- possible future use of public fit-testing datasets if IRB and data-sharing hurdles are resolved;
- manufacturer partnerships for fit, breathability, and mask-geometry data.

These collaborations reduce technical risk and improve scientific credibility.

## Staffing Needed

To execute this next phase well, I expect the project will need:

- a machine learning / computer vision engineer to develop Android camera-only face-mesh extraction comparable to ARKit;
- a machine learning engineer to improve the existing prediction approach using fit-testing and facial-measurement data;
- a software engineer to build the Android app and maintain cross-platform product features;
- a data collection manager to coordinate partnerships, participant scheduling, and data acquisition;
- a fit tester to run field data collection and structured validation studies.

This combination supports both technical progress and the operational work needed to create the dataset that the models depend on.

## Proposed KPIs and Outcomes

Because direct illness tracking may be too slow, noisy, and resource-intensive for the next phase, I propose using a combination of proxy protection metrics and scale metrics:

- number of active users served across iOS and Android;
- number of new fit-testing records collected;
- number of records collected from children, large-face users, and elastomeric users;
- number of fit-test-only contributions submitted without facial measurements;
- proportion of users for whom at least one top-three recommendation passes fit testing;
- improvement in recommendation performance relative to baseline models;
- Android facial-measurement agreement versus reference methods;
- number of partner organizations contributing data or participating in deployment.

The most important outcome is a higher share of users ending up in well-fitting respirators, delivered at much larger scale.

## What Funding Would Enable

PHAN funding would support a focused two-year implementation and validation phase: building Android support, collecting substantially more fit data, improving the recommender, and running the studies needed to show that MasqFit improves mask selection in practice. In short, the funding would not just support software development. It would support a full public-health intervention pipeline: product, data, validation, and deployment.

If successful, this next phase would produce a cross-platform, open-source fit-guidance system with stronger evidence, broader coverage, and a realistic pathway to large-scale adoption.
