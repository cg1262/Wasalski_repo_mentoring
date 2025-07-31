# Data Integration Platform

## Overview

This project contains a collection of ETL (Extract, Transform, Load) and ELT (Extract, Load, Transform) pipelines designed to integrate data from various sources into a centralized data platform. The platform enables comprehensive data analysis, monitoring, and reporting across multiple tools and services. All code for this project is stored and executed inside Snowflake, leveraging Snowflake's compute and storage capabilities for efficient data processing.

## Components

### ELT Pipelines

- **elt_checkmarx**: Data integration for Checkmarx security scanning tool
- **elt_jira**: Data integration for Jira project management
- **elt_mend**: Data integration for Mend (formerly WhiteSource) software composition analysis
- **elt_newrelic**: Data integration for New Relic application performance monitoring

### ETL Pipelines

- **etl_azure_costmanager**: Cost management data from Azure
- **etl_azure_defender**: Security insights from Azure Defender
- **etl_azure_devops**: Development metrics from Azure DevOps
- **etl_sonarcloud**: Code quality metrics from SonarCloud

### Additional Components

- **monitoring_pbi**: Power BI monitoring dashboards
- **operational_notebooks**: Jupyter notebooks for operational tasks
- **pipelines**: Pipeline definitions and orchestration
- **share_deltadirect**: Shared Delta Lake direct access components

## Getting Started

### Prerequisites

- Snowflake account with appropriate access privileges
- Python 3.8+ (for local development and testing)
- Access to the respective data sources (API keys, credentials)
- Appropriate Snowflake warehouse sizing for your data processing needs

### Installation

1. Clone this repository for local development and reference
2. Deploy the code to Snowflake using one of the following methods:
   - Snowflake's native Git integration
   - Snowflake SQL worksheets
   - CI/CD pipeline with Snowflake integration
3. Configure Snowflake connections to external data sources
4. Set up Snowflake tasks for scheduling pipeline execution

```bash# For local development and testinggit clone <repository-url>
cd <repository-name>
# Follow setup instructions in each component directory
```

## Usage

Each pipeline component has its own configuration and execution instructions. Refer to the README files within each directory for specific usage details.

### Example

```bash
cd elt_jira
# Follow the specific instructions for the Jira ELT pipeline
```

## Architecture

This platform follows a modern data architecture pattern:

1. **Extract**: Data is extracted from source systems via APIs or direct connections.
2. **Load/Transform**: Depending on the pipeline type (ETL or ELT), data is either transformed before loading or loaded first and then transformed.
3. **Storage**: Data is stored in a structured format, likely using SnowFlake.
4. **Analysis**: Data is made available for analysis through Power BI or other analytics tools

## Contact

[Provide contact information for the project maintainers]

## Snowflake connect:

Name: METRICS_REPO
	•	Origin: https://dev.azure.com/Phlexglobal/DevOps/_git/DevOps.Data.Python
	•	API Integration: METRICS_REPO_API_INTEGRATION
	•	Git Credentials: METRICS.AIRBYTE.METRICS_REPO_SECRET