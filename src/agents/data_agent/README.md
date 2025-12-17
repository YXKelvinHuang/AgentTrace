# Data Agent

A versatile multi-task agent built on the Adala framework for various data processing tasks.

## Features

The Data Agent provides the following capabilities:

1. **Summarization** - Condense long texts into concise summaries
2. **Question Answering** - Answer questions with optional context
3. **Entity Extraction** - Extract named entities (people, organizations, locations, etc.)
4. **Text Classification** - Categorize text into predefined labels
5. **Sentiment Analysis** - Analyze sentiment (positive, negative, neutral)
6. **Text Generation** - Generate creative text from prompts
7. **Custom Pipelines** - Chain multiple skills together for complex workflows

## Installation

### Quick Install (Recommended)

Run the automated install script from the data_agent directory:

```bash
cd src/agents/data_agent
./install.sh
```

This will automatically install all required dependencies including:
- Adala framework and all its dependencies
- pandas, openai, pydantic, rich
- guidance, litellm, instructor
- pandarallel, tenacity, label-studio-sdk
- And many more...

### Manual Installation

If you prefer to install manually:

#### 1. Install Adala

```bash
pip install git+https://github.com/HumanSignal/Adala.git
```

This installs the latest version of Adala and all its dependencies directly from GitHub.

#### 2. Set OpenAI API Key

**Option A: Using .env file (Recommended)**

Use the interactive setup script:

```bash
cd /Users/adamalsayyad/A-LOG
./setup_env.sh
```

Or manually create a `.env` file in the project root (`A-LOG/.env`):

```bash
cd A-LOG
cp .env.example .env
```

Then edit `.env` and add your API key:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

The agent will automatically load your API key from this file.

**Option B: Environment Variable**

```bash
export OPENAI_API_KEY='your-api-key-here'
```

### Verify Installation

Test that everything is installed correctly:

```bash
cd src/agents/data_agent
python3 test_basic.py
```

You should see all 4 tests pass (summarization, Q&A, sentiment, classification).

## Usage

### Basic Usage

```python
from agents.data_agent import DataAgent

# Initialize the agent
agent = DataAgent(model='gpt-4o')

# Summarize text
result = agent.summarize("Long text to summarize...")
print(result.iloc[0]['summary'])

# Answer a question
result = agent.answer_question("What is machine learning?")
print(result.iloc[0]['answer'])

# Classify text
texts = ["Text about business", "Text about science"]
result = agent.classify(texts, labels=['business', 'science', 'technology'])
print(result['category'])

# Analyze sentiment
result = agent.analyze_sentiment("This product is amazing!")
print(result.iloc[0]['sentiment'])
```

### Working with DataFrames

```python
import pandas as pd

# Process multiple texts
texts_df = pd.DataFrame({
    'text': [
        "First text to process",
        "Second text to process",
        "Third text to process"
    ]
})

# Summarize all
results = agent.summarize(texts_df)

# Analyze sentiment for all
results = agent.analyze_sentiment(texts_df)
```

### Entity Extraction

```python
# Extract entities with specific labels
text = "Apple Inc. announced new products. Tim Cook presented in California."

result = agent.extract_entities(
    text,
    labels=['PERSON', 'ORGANIZATION', 'LOCATION']
)

# Result contains entities with quote_string, label, start, and end positions
print(result.iloc[0]['entities'])
```

### Question Answering with Context

```python
context = """
The Eiffel Tower is located in Paris, France. It was completed in 1889
and stands 330 meters tall. It was designed by Gustave Eiffel.
"""

result = agent.answer_question(
    questions="Who designed the Eiffel Tower?",
    contexts=context
)

print(result.iloc[0]['answer'])
```

### Custom Multi-Step Pipelines

```python
from adala.skills import TransformSkill, ClassificationSkill

# Create a custom 3-step pipeline
pipeline_agent = agent.create_pipeline([
    # Step 1: Extract key information
    TransformSkill(
        name='extract_keywords',
        instructions='Extract the main keywords from the text (comma-separated).',
        input_template='Text: {text}',
        output_template='Keywords: {keywords}',
        field_schema={'keywords': {'type': 'string', 'description': 'Main keywords'}}
    ),

    # Step 2: Classify based on keywords
    ClassificationSkill(
        name='classify_topic',
        instructions='Classify the topic based on the text and keywords.',
        input_template='Text: {text}\nKeywords: {keywords}',
        output_template='Topic: {topic}',
        labels=['technology', 'business', 'science', 'health']
    ),

    # Step 3: Generate summary
    TransformSkill(
        name='create_summary',
        instructions='Create a one-sentence summary.',
        input_template='Text: {text}\nTopic: {topic}',
        output_template='Summary: {summary}',
        field_schema={'summary': {'type': 'string', 'description': 'One-sentence summary'}}
    )
])

# Run the pipeline
import pandas as pd
text_df = pd.DataFrame([{'text': 'Your text here...'}])
result = pipeline_agent.run(text_df)

# Access all intermediate results
print(f"Keywords: {result.iloc[0]['keywords']}")
print(f"Topic: {result.iloc[0]['topic']}")
print(f"Summary: {result.iloc[0]['summary']}")
```

## API Reference

### DataAgent

Main class for the Data Agent.

#### `__init__(model='gpt-4o', api_key=None)`

Initialize the agent.

- `model`: OpenAI model to use (default: 'gpt-4o')
- `api_key`: Optional API key (uses environment variable if not provided)

#### `summarize(texts, text_column='text')`

Summarize text(s).

- `texts`: DataFrame, list of strings, or single string
- Returns: DataFrame with 'text' and 'summary' columns

#### `answer_question(questions, contexts=None, question_column='question', context_column='context')`

Answer questions.

- `questions`: DataFrame, list of questions, or single question
- `contexts`: Optional context(s) for answering
- Returns: DataFrame with 'question' and 'answer' columns

#### `extract_entities(texts, labels=None, text_column='text')`

Extract named entities.

- `texts`: DataFrame, list of strings, or single string
- `labels`: Optional list of entity types (e.g., ['PERSON', 'ORG', 'LOC'])
- Returns: DataFrame with 'text' and 'entities' columns

#### `classify(texts, labels, instructions=None, text_column='text')`

Classify text.

- `texts`: DataFrame, list of strings, or single string
- `labels`: List of classification labels (required)
- `instructions`: Optional custom instructions
- Returns: DataFrame with 'text' and 'category' columns

#### `analyze_sentiment(texts, text_column='text')`

Analyze sentiment.

- `texts`: DataFrame, list of strings, or single string
- Returns: DataFrame with 'text' and 'sentiment' columns (positive/negative/neutral)

#### `generate_text(prompts, prompt_column='prompt')`

Generate text from prompts.

- `prompts`: DataFrame, list of prompts, or single prompt
- Returns: DataFrame with 'prompt' and 'generated_text' columns

#### `create_pipeline(skills)`

Create a custom skill pipeline.

- `skills`: List of skill instances to chain together
- Returns: Agent configured with the pipeline

## Examples

### Example 1: Content Moderation Pipeline

```python
agent = DataAgent(model='gpt-4o')

# Create moderation pipeline
moderation_agent = agent.create_pipeline([
    TransformSkill(
        name='extract_topics',
        instructions='Extract main topics discussed.',
        input_template='Content: {text}',
        output_template='Topics: {topics}',
        field_schema={'topics': {'type': 'string'}}
    ),
    ClassificationSkill(
        name='safety_check',
        instructions='Classify content safety level.',
        input_template='Content: {text}\nTopics: {topics}',
        output_template='Safety: {safety_level}',
        labels=['safe', 'review_needed', 'unsafe']
    )
])
```

### Example 2: Document Analysis

```python
import pandas as pd

# Load documents
docs_df = pd.DataFrame({
    'text': [
        "Document 1 content...",
        "Document 2 content...",
        "Document 3 content..."
    ]
})

# Analyze each document
summaries = agent.summarize(docs_df)
categories = agent.classify(docs_df, labels=['legal', 'technical', 'business'])
sentiments = agent.analyze_sentiment(docs_df)

# Combine results
results = pd.concat([summaries, categories['category'], sentiments['sentiment']], axis=1)
```

## Testing

Run the test suite:

```bash
cd src/agents/data_agent
python3 test_basic.py
```

Or run the full demo:

```bash
python3 main.py
```

## Model Options

The agent supports any OpenAI-compatible model:

```python
# Use GPT-4o (recommended, default)
agent = DataAgent(model='gpt-4o')

# Use GPT-3.5-turbo (faster, cheaper)
agent = DataAgent(model='gpt-3.5-turbo')

# Use GPT-4-turbo
agent = DataAgent(model='gpt-4-turbo')
```

## Advanced: Learning from Feedback

The underlying Adala framework supports learning from ground truth data:

```python
from adala.agents import Agent
from adala.environments import StaticEnvironment
from adala.skills import ClassificationSkill
import pandas as pd

# Prepare training data with ground truth
train_df = pd.DataFrame([
    {"text": "Great product!", "label": "positive"},
    {"text": "Terrible service", "label": "negative"},
    {"text": "It's okay", "label": "neutral"}
])

# Create agent with environment
agent = Agent(
    skills=ClassificationSkill(
        name='sentiment',
        instructions='Classify sentiment.',
        input_template='Text: {text}',
        output_template='Sentiment: {label}',
        labels=['positive', 'negative', 'neutral']
    ),
    environment=StaticEnvironment(df=train_df),
    runtimes={'openai': agent.runtime},
    default_runtime='openai'
)

# Learn from data
agent.learn(learning_iterations=3, accuracy_threshold=0.9)

# Now use the improved agent
test_df = pd.DataFrame([{"text": "Amazing experience!"}])
result = agent.run(test_df)
```

## License

Part of the A-LOG research framework.
