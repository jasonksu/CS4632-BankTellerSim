CS4632 – Bank Teller Discrete-Event Simulation
Author

Jason Appolon
Department of Computer Science, Kennesaw State University
Email: jappolon@students.kennesaw.edu

Project Overview

This project models a bank teller system using discrete-event simulation (DES) principles in Python with SimPy.
Customers arrive randomly and wait in a shared queue to be served by one of several tellers.
The simulation measures performance metrics such as average wait time, queue length, teller utilization, throughput per hour, and percentile-based statistics.

The goal is to explore how arrival rate (λ), service rate (μ), and number of tellers (c) influence system performance and to compare results against analytical M/M/c queueing theory.

Implementation Summary

The system was developed across multiple milestones:

Milestone 1 – Project Foundation

Defined the problem domain and project scope

Created UML class and sequence diagrams

Conducted an initial literature review and conceptual validation

Milestone 2 – Initial Implementation

Built the initial SimPy-based simulation prototype

Tracked performance statistics and utilization

Implemented staffing sweep experiments

Incorporated instructor feedback on structure and validation

Milestone 3 – Complete Implementation and Testing

Modularized code into src/, configs/, results/, and figures/

Performed controlled experiments with multiple replications

Generated visualizations with Matplotlib

Compared simulation outcomes with expected queueing behavior

Documented testing procedure and results

Milestone 4 – Analysis and Validation

Performed sensitivity analysis for arrival rate variation

Performed service rate comparisons

Generated automated CSV and JSON summaries

Interpreted system behavior and validated consistency with theory

Milestone 5 – Final Report and Presentation

Produced final refined LaTeX report integrating previous milestones

Added visual figures and data interpretation

Recorded and submitted the final video demonstration

Published full code, configurations, report, and video in repository

Repository Structure
CS4632-BankTellerSim
│
├── src/                → Full implementation, experiment runner, and plotting script
├── configs/            → JSON configuration files for experiments
│      ├ baseline*.json
│      ├ arrival_*.json
│      └ service_*.json
│
├── results/            → Raw replications and aggregated summaries
├── figures/            → Generated plots for the report and demo presentation
│
├── CS4632_M5_Appolon_FinalReport.pdf  → Final milestone report
├── CS4632_VideoDemo.mp4               → Demonstration video
└── README.md

Example Output

Example visualization produced and used in the report:

Bank Teller Simulation: Staffing Sweep

This visualization shows how average wait time declines and utilization drops as the number of tellers increases.

Key Insights

Higher arrival rates sharply increase waiting time and congestion.

Increasing staffing reduces waiting time but decreases utilization.

System turning points appear when utilization exceeds approximately 80 percent.

Simulation results align with expected M/M/c queueing behavior, supporting model validity.

Technologies Used

Python 3.x

SimPy for discrete-event simulation

Matplotlib for visualization

JSON and CSV for configuration and data storage

LaTeX for formal documentation

Running the Simulation

Run a baseline experiment example:

python src/run_experiment.py --config configs/baseline.json


Arrival rate sensitivity experiments:

python src/run_experiment.py --config configs/arrival_10.json
python src/run_experiment.py --config configs/arrival_12.json
python src/run_experiment.py --config configs/arrival_14.json


Service rate sensitivity experiments:

python src/run_experiment.py --config configs/service_10.json
python src/run_experiment.py --config configs/service_12.json
python src/run_experiment.py --config configs/service_14.json


Visualization generation:

python src/make_plots.py


Simulation results appear under:

results/runs/
results/summary/


Figures appear in:

figures/

Version History

Milestone Description Status
M1 Project Foundation Completed
M2 Initial Implementation Completed
M3 Complete Implementation and Testing Completed
M4 Analysis and Validation Completed
M5 Final Report and Presentation Completed

Citation

Appolon, Jason. Bank Teller Discrete-Event Simulation Project.
CS4632 – Kennesaw State University, 2025.
