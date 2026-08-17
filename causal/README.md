# EconoCausal - Causal DAG

## Overview

This module contains the Week 1 causal inference implementation for the
EconoCausal project.

The purpose of this module is to define the causal relationship between:

- Treatment: `discount`
- Outcome: `purchase`
- Confounders: customer characteristics that influence both treatment and outcome

The causal graph is created using Microsoft's DoWhy library.

The DAG is also visualized using NetworkX and Matplotlib and saved as a JPG
image for documentation and review.

---

## Business Question

> What is the causal effect of giving a customer a discount on their
> probability of purchasing?

The goal is not simply to determine whether customers who receive discounts
purchase more.

Instead, the project aims to estimate whether the discount itself causes
an increase in the probability of purchase after accounting for confounding
customer characteristics.

---

## Dataset

The DAG uses the cleaned retail campaign dataset:

```text
data/mockretaildatacleaned.csv