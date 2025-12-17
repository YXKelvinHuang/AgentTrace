"""
Data Agent: A versatile multi-task agent built on the Adala framework.

This agent can perform various data processing tasks including:
- Text summarization
- Question answering
- Entity extraction
- Text classification
- Sentiment analysis
- Data generation

The agent uses Adala's skill system to compose and execute these tasks
either independently or in sequences.
"""

import os
import pandas as pd
from typing import Optional, List, Union
from pathlib import Path

# Load environment variables from .env file
# remember to remove key
def load_env():
    """Load environment variables from .env file in project root."""
    env_path = Path(__file__).parent.parent.parent.parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Load .env on import
load_env()

from adala.agents import Agent
from adala.skills import (
    TransformSkill,
    ClassificationSkill,
    LinearSkillSet
)
from adala.skills.collection.summarization import SummarizationSkill
from adala.skills.collection.qa import QuestionAnsweringSkill
from adala.skills.collection.entity_extraction import EntityExtraction
from adala.skills.collection.text_generation import TextGenerationSkill
from adala.runtimes import OpenAIChatRuntime


class DataAgent:
    """
    A versatile data processing agent with multiple task capabilities.

    This agent can perform:
    - Summarization: Condense long texts
    - Q&A: Answer questions about text
    - Entity Extraction: Extract named entities
    - Classification: Categorize text
    - Sentiment Analysis: Determine sentiment
    - Text Generation: Generate new text

    Attributes:
        model (str): The OpenAI model to use
        api_key (Optional[str]): OpenAI API key
    """

    def __init__(
        self,
        model: str = 'gpt-4o',
        api_key: Optional[str] = None
    ):
        """
        Initialize the Data Agent.

        Args:
            model: OpenAI model name (default: 'gpt-4o')
            api_key: OpenAI API key (uses env var if not provided)
        """
        self.model = model

        # Configure runtime
        runtime_config = {'model': model}
        if api_key:
            runtime_config['api_key'] = api_key

        self.runtime = OpenAIChatRuntime(**runtime_config)

    def summarize(
        self,
        texts: Union[pd.DataFrame, List[str], str],
        text_column: str = 'text'
    ) -> pd.DataFrame:
        """
        Summarize text(s).

        Args:
            texts: DataFrame with text column, list of strings, or single string
            text_column: Name of the text column in DataFrame

        Returns:
            DataFrame with 'text' and 'summary' columns
        """
        df = self._prepare_input(texts, text_column)

        agent = Agent(
            skills=SummarizationSkill(
                name='summarization',
                instructions='Provide a concise summary of the text.',
                input_template='Text: {text}',
                output_template='Summary: {summary}'
            ),
            runtimes={'openai': self.runtime},
            default_runtime='openai'
        )

        return agent.run(df)

    def answer_question(
        self,
        questions: Union[pd.DataFrame, List[str], str],
        contexts: Optional[Union[List[str], str]] = None,
        question_column: str = 'question',
        context_column: str = 'context'
    ) -> pd.DataFrame:
        """
        Answer questions, optionally using provided context.

        Args:
            questions: DataFrame, list of questions, or single question
            contexts: Optional context(s) for answering
            question_column: Name of question column in DataFrame
            context_column: Name of context column in DataFrame

        Returns:
            DataFrame with 'question' and 'answer' columns
        """
        # Prepare input
        if isinstance(questions, pd.DataFrame):
            df = questions
        elif isinstance(questions, list):
            df = pd.DataFrame({question_column: questions})
            if contexts:
                df[context_column] = contexts if isinstance(contexts, list) else [contexts] * len(questions)
        else:  # single string
            df = pd.DataFrame([{question_column: questions}])
            if contexts:
                df[context_column] = contexts

        # Rename to standard names
        df = df.rename(columns={question_column: 'question'})
        if context_column in df.columns:
            df = df.rename(columns={context_column: 'context'})
            input_template = 'Context: {context}\n\nQuestion: {question}'
        else:
            input_template = 'Question: {question}'

        agent = Agent(
            skills=QuestionAnsweringSkill(
                name='qa',
                instructions='Answer the question clearly and concisely.',
                input_template=input_template,
                output_template='Answer: {answer}'
            ),
            runtimes={'openai': self.runtime},
            default_runtime='openai'
        )

        return agent.run(df)

    def extract_entities(
        self,
        texts: Union[pd.DataFrame, List[str], str],
        labels: Optional[List[str]] = None,
        text_column: str = 'text'
    ) -> pd.DataFrame:
        """
        Extract named entities from text.

        Args:
            texts: DataFrame with text column, list of strings, or single string
            labels: Optional list of entity labels to extract (e.g., ['PERSON', 'ORG', 'LOC'])
            text_column: Name of the text column in DataFrame

        Returns:
            DataFrame with 'text' and 'entities' columns
        """
        df = self._prepare_input(texts, text_column)

        agent = Agent(
            skills=EntityExtraction(
                name='entity_extraction',
                input_template='Extract entities from the text.\n\nText: {text}',
                output_template='Entities: {entities}',
                labels=labels
            ),
            runtimes={'openai': self.runtime},
            default_runtime='openai'
        )

        return agent.run(df)

    def classify(
        self,
        texts: Union[pd.DataFrame, List[str], str],
        labels: List[str],
        instructions: Optional[str] = None,
        text_column: str = 'text'
    ) -> pd.DataFrame:
        """
        Classify text into predefined categories.

        Args:
            texts: DataFrame with text column, list of strings, or single string
            labels: List of possible classification labels
            instructions: Optional custom classification instructions
            text_column: Name of the text column in DataFrame

        Returns:
            DataFrame with 'text' and 'category' columns
        """
        df = self._prepare_input(texts, text_column)

        if not instructions:
            instructions = f'Classify the text into one of these categories: {", ".join(labels)}'

        agent = Agent(
            skills=ClassificationSkill(
                name='classification',
                instructions=instructions,
                input_template='Text: {text}',
                output_template='Category: {category}',
                labels=labels
            ),
            runtimes={'openai': self.runtime},
            default_runtime='openai'
        )

        return agent.run(df)

    def analyze_sentiment(
        self,
        texts: Union[pd.DataFrame, List[str], str],
        text_column: str = 'text'
    ) -> pd.DataFrame:
        """
        Analyze sentiment of text (positive, negative, neutral).

        Args:
            texts: DataFrame with text column, list of strings, or single string
            text_column: Name of the text column in DataFrame

        Returns:
            DataFrame with 'text' and 'sentiment' columns
        """
        df = self._prepare_input(texts, text_column)

        agent = Agent(
            skills=ClassificationSkill(
                name='sentiment',
                instructions='Analyze the sentiment of the text.',
                input_template='Text: {text}',
                output_template='Sentiment: {sentiment}',
                labels=['positive', 'negative', 'neutral']
            ),
            runtimes={'openai': self.runtime},
            default_runtime='openai'
        )

        return agent.run(df)

    def generate_text(
        self,
        prompts: Union[pd.DataFrame, List[str], str],
        prompt_column: str = 'prompt'
    ) -> pd.DataFrame:
        """
        Generate text based on prompts.

        Args:
            prompts: DataFrame, list of prompts, or single prompt
            prompt_column: Name of prompt column in DataFrame

        Returns:
            DataFrame with 'prompt' and 'generated_text' columns
        """
        df = self._prepare_input(prompts, prompt_column, 'prompt')

        agent = Agent(
            skills=TextGenerationSkill(
                name='text_generation',
                instructions='Generate creative and relevant text based on the prompt.',
                input_template='Prompt: {prompt}',
                output_template='Generated: {generated_text}'
            ),
            runtimes={'openai': self.runtime},
            default_runtime='openai'
        )

        return agent.run(df)

    def create_pipeline(
        self,
        skills: List[TransformSkill]
    ) -> Agent:
        """
        Create a custom pipeline of skills.

        Args:
            skills: List of skill instances to chain together

        Returns:
            Agent configured with the skill pipeline
        """
        agent = Agent(
            skills=LinearSkillSet(skills=skills),
            runtimes={'openai': self.runtime},
            default_runtime='openai'
        )
        return agent

    def _prepare_input(
        self,
        data: Union[pd.DataFrame, List[str], str],
        column_name: str,
        target_column: str = 'text'
    ) -> pd.DataFrame:
        """
        Convert various input formats to DataFrame.

        Args:
            data: Input data (DataFrame, list, or string)
            column_name: Name of the column in DataFrame
            target_column: Target column name for conversion

        Returns:
            Standardized DataFrame
        """
        if isinstance(data, pd.DataFrame):
            if column_name in data.columns and column_name != target_column:
                return data.rename(columns={column_name: target_column})
            return data
        elif isinstance(data, list):
            return pd.DataFrame({target_column: data})
        else:  # single string
            return pd.DataFrame([{target_column: data}])


def demo_basic_tasks():
    """Demonstrate basic single-task capabilities."""
    print("="*80)
    print("DATA AGENT DEMO: Basic Tasks")
    print("="*80)

    agent = DataAgent(model='gpt-4o')

    # 1. Summarization
    print("\n--- Task 1: Summarization ---")
    text = """
    Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to
    the natural intelligence displayed by humans and animals. Leading AI textbooks define
    the field as the study of "intelligent agents": any device that perceives its environment
    and takes actions that maximize its chance of successfully achieving its goals.
    """
    result = agent.summarize(text)
    print(f"Original: {text.strip()[:80]}...")
    print(f"Summary: {result.iloc[0]['summary']}")

    # 2. Question Answering
    print("\n--- Task 2: Question Answering ---")
    question = "What is the capital of France?"
    result = agent.answer_question(question)
    print(f"Q: {question}")
    print(f"A: {result.iloc[0]['answer']}")

    # 3. Sentiment Analysis
    print("\n--- Task 3: Sentiment Analysis ---")
    texts = [
        "This product is amazing! Best purchase ever!",
        "Terrible experience. Very disappointed.",
        "It's okay, nothing special."
    ]
    results = agent.analyze_sentiment(texts)
    for idx, row in results.iterrows():
        print(f"Text: {row['text'][:50]}...")
        print(f"Sentiment: {row['sentiment']}\n")

    # 4. Classification
    print("\n--- Task 4: Text Classification ---")
    texts = [
        "The stock market rose 5% today on positive earnings reports.",
        "Scientists discovered a new species in the Amazon rainforest.",
        "The new smartphone features a better camera and longer battery life."
    ]
    labels = ['business', 'science', 'technology', 'sports', 'politics']
    results = agent.classify(texts, labels=labels)
    for idx, row in results.iterrows():
        print(f"Text: {row['text'][:60]}...")
        print(f"Category: {row['category']}\n")


def demo_pipeline():
    """Demonstrate multi-step pipeline."""
    print("\n" + "="*80)
    print("DATA AGENT DEMO: Multi-Step Pipeline")
    print("="*80)

    agent = DataAgent(model='gpt-4o')

    # Create a custom pipeline: Extract topic -> Classify -> Summarize
    print("\nCreating 3-step pipeline:")
    print("  1. Extract main topic")
    print("  2. Classify content type")
    print("  3. Generate summary")

    pipeline_agent = agent.create_pipeline([
        TransformSkill(
            name='topic_extraction',
            instructions='Extract the main topic or subject of the text in 2-3 words.',
            input_template='Text: {text}',
            output_template='Topic: {topic}',
            field_schema={'topic': {'type': 'string', 'description': 'Main topic in 2-3 words'}}
        ),
        ClassificationSkill(
            name='content_type',
            instructions='Classify the content type.',
            input_template='Text: {text}\nTopic: {topic}',
            output_template='Type: {content_type}',
            labels=['news', 'tutorial', 'opinion', 'research']
        ),
        TransformSkill(
            name='summary',
            instructions='Create a brief one-sentence summary.',
            input_template='Text: {text}',
            output_template='Summary: {summary}',
            field_schema={'summary': {'type': 'string', 'description': 'One-sentence summary'}}
        )
    ])

    text = """
    Machine learning engineers are increasingly using automated tools to speed up model
    development. These tools help with hyperparameter tuning, feature engineering, and
    model selection, allowing engineers to focus on higher-level architecture decisions.
    """

    df = pd.DataFrame([{'text': text}])
    result = pipeline_agent.run(df)

    print(f"\nOriginal text: {text.strip()[:100]}...")
    print(f"\nExtracted topic: {result.iloc[0]['topic']}")
    print(f"Content type: {result.iloc[0]['content_type']}")
    print(f"Summary: {result.iloc[0]['summary']}")


def main():
    """Run all demonstrations."""
    print("\n╔════════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                            ║")
    print("║                      DATA AGENT DEMONSTRATION                              ║")
    print("║                    Multi-Task Adala Agent                                  ║")
    print("║                                                                            ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝\n")

    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  WARNING: OPENAI_API_KEY not set!")
        print("   Set it with: export OPENAI_API_KEY='your-key-here'")
        return

    try:
        demo_basic_tasks()
        demo_pipeline()

        print("\n" + "="*80)
        print("Demo complete!")
        print("="*80)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
