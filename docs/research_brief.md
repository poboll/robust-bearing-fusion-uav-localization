# Research Brief

## Working Title
Robust Collaborative Bearing-Only Passive Localization for UAV Swarms under Degraded Measurements

## Goal
Turn the 2022B passive localization topic into a computer-oriented SCI manuscript centered on robust collaborative bearing-only localization rather than on legacy contest heuristics.

## Current Core Story

The paper is not a rewrite of a mathematical-modeling geometry puzzle.

The real research story is:
UAV collaborative systems operating in GNSS-degraded or electromagnetically silent conditions require passive bearing-only localization, but classical geometry and least-squares pipelines fail under bias, outliers, missing observations, and poor initialization. A publishable solution should remain interpretable while improving degraded-regime stability.

## What Is Now Implemented

- consensus geometric initialization
- trimming-aware robust refinement
- residual reweighting
- optional common-bias correction
- baseline comparison with least squares, robust Huber, PSO, and SA
- degraded-regime evaluation
- ablation pipeline
- formation-generalization pipeline

## Why It Is Publishable

- the method direction matches current robust localization research better than simulated-annealing-centered stories
- the result profile is honest and useful:
  strong gains over least squares, competitive behavior against heuristics
- the framework is reproducible and lightweight
- the contribution sits in a computer/intelligent-systems framing, not only mathematical derivation

## Deliverables Already Built

- literature foundation pool
- story and outline docs
- method and experiment docs
- simulation code scaffold
- regime comparison outputs
- ablation outputs

## Immediate Publication Target

Write a manuscript whose main evidence centers on:
- biased regime robustness
- outlier regime robustness
- mixed-regime stability
- ablation-backed explanation of why the method works

The scheduling and recovery modules should remain secondary unless their experiments are strengthened.
