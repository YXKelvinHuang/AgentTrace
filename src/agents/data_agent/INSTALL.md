# Installation Guide for Data Agent

## Prerequisites

- Python 3.10 or higher
- OpenAI API key

## Quick Install

### Option 1: Use the automated install script (Recommended)

```bash
cd src/agents/data_agent
./install.sh
```

This will automatically install Adala and all dependencies from GitHub.

### Option 2: Install Adala manually

```bash
pip install git+https://github.com/HumanSignal/Adala.git
```

This will install all required dependencies including:
- pandas
- openai
- pydantic
- rich
- guidance
- litellm
- instructor
- pandarallel
- tenacity
- label-studio-sdk
- and many more...

## Set OpenAI API Key

**Recommended: Use .env file**

1. Copy the example file:
```bash
cd /Users/adamalsayyad/A-LOG
cp .env.example .env
```

2. Edit `.env` and add your key:
```bash
nano .env  # or use any text editor
```

3. Add your API key:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

The agent automatically loads the API key from this file.

**Alternative: Environment Variable**

```bash
export OPENAI_API_KEY='your-api-key-here'
```

## Verify Installation

Test that everything is installed correctly:

```bash
cd src/agents/data_agent
python3 test_basic.py
```

## Troubleshooting

### "No module named 'adala'"
Make sure you installed Adala:
```bash
pip install git+https://github.com/HumanSignal/Adala.git
```

Or use the install script:
```bash
cd src/agents/data_agent
./install.sh
```

### "No module named 'pandarallel'" or other dependencies
Install Adala with all dependencies:
```bash
pip install git+https://github.com/HumanSignal/Adala.git
```

### "OpenAI API key not found"
Set your API key:
```bash
export OPENAI_API_KEY='sk-...'
```

### Import errors from pandas or other packages
Try upgrading pip and reinstalling:
```bash
pip install --upgrade pip
pip install --upgrade pandas openai pydantic
```

## Running the Test

Once everything is installed:

```bash
cd src/agents/data_agent
python3 test_basic.py
```

You should see output showing the agent processing text through its 5-step pipeline.
