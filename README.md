# CS4632 – Bank Teller Discrete-Event Simulation

### Author  
**Jason Appolon**  
Department of Computer Science, Kennesaw State University  
Email: jappolon@students.kennesaw.edu  

---

## Project Overview  
This project models a bank teller system using discrete-event simulation (DES) in Python with SimPy.  
Customers arrive randomly, join a shared queue, and are served by one of several tellers.  
Performance metrics include average wait time, queue length, teller utilization, throughput per hour, and time-in-system.

The objective is to study how arrival rate (λ), service rate (μ), and number of tellers (c) affect system congestion and whether simulation results match analytical M/M/c theory.

---

## Implementation Summary  

### Milestone 1 – Project Foundation
- Defined the simulation problem  
- Built UML class and sequence diagrams  
- Conducted literature foundation and design planning  

### Milestone 2 – Initial Implementation
- Implemented the first working SimPy model  
- Added utilization tracking and output summarization  
- Introduced staffing sweep experimentation  
- Incorporated model correctness feedback  

### Milestone 3 – Complete Implementation and Testing
- Structured repository into `src/`, `configs/`, `results/`, and `figures/`  
- Ran multiple experiments with controlled replication  
- Produced visualizations (staffing sweep plots)  
- Compared results with expected queueing behavior  

### Milestone 4 – Analysis and Validation
- Performed sensitivity testing on arrival and service rates  
- Produced structured outputs and summaries  
- Interpreted trends and compared against theory  

### Milestone 5 – Final Report and Presentation
- Completed refined report with integrated figures  
- Recorded demonstration video  
- Delivered final repository containing code, results, report, and video  

---

## Repository Structure

```plaintext
CS4632-BankTellerSim
│
├── src/                → Final modular implementation
├── configs/            → JSON experiment configurations
├── results/            → Raw replications and summaries
├── figures/            → Generated experiment visuals
│
├── CS4632_M5_Appolon_FinalReport.pdf   → Final written report
├── CS4632_VideoDemo.mp4                → Project demonstration video
└── README.md
```

---

## Example Output  

**Bank Teller Simulation: Staffing Sweep**

![Staffing Sweep Figure](figures/staffing_sweep.png)

This figure shows how average wait time falls as tellers increase while utilization declines — demonstrating capacity trade-offs.

---

## Key Insights
- Higher arrival rates produce sharply increasing wait times  
- Adding staffing reduces delay but lowers utilization  
- System behavior aligns with M/M/c queueing theory predictions  
- Significant changes occur when utilization exceeds roughly 80%

---

## Technologies Used
- Python 3.x  
- SimPy for discrete-event modeling  
- Matplotlib for visualization  
- JSON / CSV for configuration and result storage  
- LaTeX for academic documentation  

---

## Running the Simulation  

### Run a baseline experiment
```
python src/run_experiment.py --config configs/baseline.json
```

### Run arrival-rate sensitivity tests
```
python src/run_experiment.py --config configs/arrival_10.json
python src/run_experiment.py --config configs/arrival_12.json
python src/run_experiment.py --config configs/arrival_14.json
```

### Run service-rate sensitivity tests
```
python src/run_experiment.py --config configs/service_10.json
python src/run_experiment.py --config configs/service_12.json
python src/run_experiment.py --config configs/service_14.json
```

### Generate visuals
```
python src/make_plots.py
```

Results are stored under:

```
results/
figures/
```

---

## Version History  

Milestone | Description | Status  
--- | --- | ---  
M1 | Project Foundation | Completed  
M2 | Initial Implementation | Completed  
M3 | Complete Implementation & Testing | Completed  
M4 | Analysis & Validation | Completed  
M5 | Final Report & Presentation | Completed  

---

## Citation  
Appolon, Jason. Bank Teller Discrete-Event Simulation Project.  
CS4632 – Kennesaw State University, 2025.
