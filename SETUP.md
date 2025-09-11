# Arcade AI Interview Challenge - Setup Guide

This document provides step-by-step instructions to set up and run the Arcade AI Interview Challenge project.

## 1. Clone the Repository

Begin by cloning the repository to your local machine:

```bash
git clone <repository_url>
cd <repository_directory>
```

Replace `<repository_url>` and `<repository_directory>` with the appropriate URL and folder name.

## 2. Create and Activate a Virtual Environment

It is recommended to use a virtual environment to manage project dependencies.

- **On macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

- **On Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

## 3. Install Dependencies

Install the required Python packages using the provided `requirements.txt` file:

```bash
pip install -r requirements.txt
```

## 4. Configure Environment Variables

To securely manage your OpenAI API key, configure environment variables as follows:

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Open `.env` in a text editor and set your `OPENAI_API_KEY` value:

```
OPENAI_API_KEY=your_openai_api_key_here
```

Make sure to replace `your_openai_api_key_here` with your actual API key.

## 5. Run the Analyzer

Execute the analyzer script with the provided flow data:

```bash
python -m src.analyzer_ai --flow flow.json
```

This command processes the flow data and generates outputs.

## 6. Generated Outputs

After running the analyzer, the following files will be created:

- `out/report.md`: A comprehensive markdown report summarizing the analyzed flow.
- `out/social.png`: A professionally designed social media image representing the flow.

## 7. Caching

To optimize API usage and reduce costs, the project implements caching:

- Cached AI responses are stored in `.cache/ai.jsonl`.
- This cache helps avoid redundant API calls during development and testing.

## 8. Project Implementation Summary

This repository implements a robust pipeline to analyze Arcade flow recordings using AI multimodal APIs. Key features include:

- AI-driven extraction of user actions and UI element interactions from flow data.
- Generation of clear, human-friendly summaries describing user intent.
- Automated creation of social media images that visually represent the flow.
- Efficient caching mechanisms to manage API usage and costs.
- Modular, maintainable code structure enabling extensibility and reuse.

This setup enables seamless analysis and reporting of Arcade flows, demonstrating effective integration of AI capabilities in user interaction analysis.