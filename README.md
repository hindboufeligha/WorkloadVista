# WorkloadVista
**A compute infrastructure observability and resource analytics platform built using historical cluster workload traces.**

**WorkloadVista** aims to provide an interactive platform for exploring, analysing, and visualising compute resource usage across machines and instances in large-scale computing systems.

The project uses historical workload traces to investigate resource utilisation patterns, examine temporal behaviour, and develop insights into infrastructure workloads.


## Objectives

- Explore CPU and memory utilisation across machines and instances. 
- Analyse workload behaviour over time.
- Provide interactive visualisations of resource usage and workload characteristics.
- Develop a structured data pipeline for processing large-scale workload traces;
- Expose workload metrics through a REST API.
- Build a dashboard for querying and exploring workload data.

## Tech Stack

|---|---|
| Data engineering and analysis | Python, Pandas, NumPy |
| Backend | Java, Spring Boot |
| Database | PostgreSQL |
| Frontend | React, TypeScript, Vite |
| Visualisation | Recharts |
| Containerisation | Docker, Docker Compose |
| Testing | pytest, JUnit 5, Vitest, Playwright |
| CI | GitHub Actions |

The tech stack represents the planned architecture The implementation will evolve as the project develops.


## Data Source

WorkloadVista initially uses **Google Borg Cluster Traces v3 (2019)**, a publicly available dataset containing workload and resource usage information from Google's Borg cluster management system.

We initially focus on the `instance_usage` table from **Trace B** for the initial development.

- **Source**: [Google Cluster Data repository](https://github.com/google/cluster-data).

- **Dataset Documentation**: [ClusterData2019](https://github.com/google/cluster-data/blob/master/ClusterData2019.md)

- **Dataset licence**: [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)

The dataset's licensing and attributon requirements are separate from the **WorkloadVista** source code license.

## Current Progress

### Data Engineering: Initial Preparation Piepline

The initial data preparation workflow has been implemented Python scripts.

- Inspected the Trace B `instance_usage` dataset.
- Profiled the distinct machines.
- Selected five distinct machines using unifrom random sampling without replacement (seed: 42).
- Extracted all available records for the selected machines. 
- Validated the extracted sample against the original machine record counts.

**Current development sample**: 2457 records across five machines.

The pipeline supports configurable local data directories and configurable machine selection parameters.


### Planned Development

- EDA and data quality assessment.
- Definition of the analytical data model.
- Data transformation and PostgreSQL ingestion.
- Backend REST API development.
- Interactive frontend dashboard.
- Automated testing and deployment.

## Repository Structure

```text
WorkloadVista/
├── docs/
│   ├── data/
├── data-engineering/
│   ├── scripts/
│   ├── analysis/
│   └── tests/
├── backend/
├── frontend/
├── infrastructure/
└── .github/
```

The repository structure will expand as additional components are implemented.


## Data Availability

The original dataset and extracted CSV samples are maintained separately from the source repository. Large raw data files and generated artifacts are not committed to GitHub.

To reproduce the data preparation workflow, obtain the dataset from the official Google Cluster Data repository and follow the instructions in `data-engineering/README.md`.


## Licence

The **WorkloadVista** source code is licenced under the Apache License 2.0. See [LICENSE](LICENSE).

The Google Borg Cluster Traces dataset is subject to its own licence and attribution requirements.