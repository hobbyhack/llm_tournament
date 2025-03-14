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
- **NEW: Consistency analysis across multiple tournament runs**

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/hobbyhack/llm-tournament.git
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

```bash
python main.py --contenders examples/contenders_fb_ads_02.json --framework examples/framework_saas_fb_ad_o3.json --output ./results/gemma3_12b_test_01.json --model gemma3:12b
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

### Multiple Tournament Runs

To run multiple tournaments with different models and analyze consistency:

```bash
python run_multiple_tournaments.py --contenders examples/contenders_fb_ads_02.json --framework examples/framework_saas_fb_ad_o3.json --models gemma3:27b phi4 --runs 3 --run-analysis
```


This will:
1. Run 5 tournaments with each specified model
2. Save results to the `results` directory
3. Run consistency analysis to compare model performance

### Consistency Analysis

After running multiple tournaments, you can analyze their consistency:

```bash
python analyze_consistency.py --group-by config.llm.default_model --verbose
```

This will:
1. Analyze all tournament result files in the `results` directory
2. Group them by the LLM model used
3. Calculate consistency metrics for rankings, win rates, matchups, and scores
4. Export summary reports to the `analysis_results` directory
5. Print a comparison of which model provides the most consistent results

## Configuration

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

### Tournament Results

The tournament results are saved as a JSON file with detailed information about:
- Tournament configuration and statistics
- Complete match results with scores and rationales
- Final standings and rankings

### Consistency Analysis

The consistency analysis outputs several files:
- `consistency_summary.csv`: High-level comparison of metrics across groups
- `consistency_[group]_[timestamp].json`: Detailed metrics for each group
- `consistency_summary_[timestamp].json`: Combined summary with best-in-class comparisons

Metrics calculated include:
- **Ranking Stability**: How consistent are the final rankings across tournaments?
- **Win Rate Consistency**: How consistent are win percentages for each contender?
- **Matchup Consistency**: How often do the same pairings result in the same winner?
- **Score Consistency**: How stable are the evaluation scores across runs?

## Customizing Prompts

Prompt templates are stored as Markdown files in the `prompts/` directory. You can customize these to adjust how the LLM evaluates contenders.

## License

[MIT License](LICENSE)