# LLM Tournament

A Python application for running a round-robin tournament between text contenders, evaluated by an LLM against an assessment framework.

## Overview

This application allows you to evaluate and compare text candidates (contenders) using an LLM agent. It organizes a round-robin tournament where every contender competes against every other contender, with the option for reverse matchups.

Use cases include:
- Comparing advertising slogans
- Evaluating product descriptions
- Testing different versions of copy
- Benchmarking AI-generated content
- Any scenario where you need to systematically compare text options

## Features

- Round-robin tournament with no elimination
- Configurable number of rounds per matchup
- Optional reverse matchups (A vs B and B vs A)
- Win/loss/draw records and point-based standings
- Tournament progress tracking and visualization
- Detailed match results and rationales
- JSON export of all results
- Configurable LLM models per prompt type
- Console-based UI with progress indicators
- Comprehensive logging

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/llm-tournament.git
   cd llm-tournament
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Make sure you have [Ollama](https://ollama.ai/) installed and running

## Usage

### Basic Usage

Run a tournament with the example data:

```bash
python main.py --contenders examples/contenders.json --framework examples/framework.json
```

### Command Line Options

```
usage: main.py [-h] [--config CONFIG] [--contenders CONTENDERS] [--framework FRAMEWORK] [--headless] [--output OUTPUT] [--rounds ROUNDS] [--model MODEL]

LLM Tournament Application

options:
  -h, --help            show this help message and exit
  --config CONFIG       Path to configuration file
  --contenders CONTENDERS
                        Path to contenders JSON file
  --framework FRAMEWORK
                        Path to assessment framework JSON file
  --headless            Run without UI (headless mode)
  --output OUTPUT       Path to output results file
  --rounds ROUNDS       Number of rounds per matchup
  --model MODEL         LLM model to use
```

### Configuration

The application uses a YAML configuration file (`config.yaml`) that can be customized. You can specify:
- Tournament settings (rounds, reverse matchups, point system)
- LLM provider and models
- UI settings
- Output and logging preferences

Environment variables can override configuration values with the prefix `LLM_TOURNAMENT_`. For example:
```bash
export LLM_TOURNAMENT_LLM_DEFAULT_MODEL=llama3
```

## Input Format

### Contenders

Contenders are defined in a JSON file:

```json
{
  "contenders": [
    {
      "id": "slogan-1",
      "content": "Just Do It",
      "metadata": {
        "brand": "Nike",
        "year": 1988
      }
    },
    ...
  ]
}
```

### Assessment Framework

The assessment framework is defined in a JSON file:

```json
{
  "assessment_framework": {
    "id": "ad-slogan-framework",
    "description": "Framework for evaluating advertising slogans",
    "evaluation_criteria": [
      {
        "name": "Memorability",
        "description": "How easily the slogan can be remembered",
        "weight": 0.30
      },
      ...
    ],
    "comparison_rules": [
      "Compare slogans against each criterion",
      ...
    ],
    "scoring_system": {
      "type": "points",
      "scale": {
        "min": 0,
        "max": 10
      },
      "categories": [
        {"name": "Excellent", "range": [8, 10]},
        ...
      ]
    }
  }
}
```

## Output

The tournament results are saved as a JSON file with detailed information about:
- Tournament configuration and statistics
- Complete match results with scores and rationales
- Final standings and rankings

## Customizing Prompts

Prompt templates are stored as Markdown files in the `prompts/` directory. You can customize these to adjust how the LLM evaluates contenders.

## License

[License Name](LICENSE)
