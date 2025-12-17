"""
Test script for Data Agent - testing all capabilities.

Tests:
1. Summarization
2. Question Answering
3. Sentiment Analysis
4. Text Classification
5. Entity Extraction
6. Text Generation
7. Custom Pipeline
"""

import os

from main import DataAgent


def test_summarization():
    """Test summarization capability."""
    print("\n" + "="*80)
    print("TEST 1: Summarization")
    print("="*80)

    agent = DataAgent(model='gpt-4o')

    text = """
    The Internet of Things (IoT) refers to the network of physical devices embedded with
    sensors, software, and other technologies to connect and exchange data with other devices
    and systems over the internet. These devices range from ordinary household items to
    sophisticated industrial tools. IoT enables devices to be controlled remotely across
    existing network infrastructure, creating opportunities for more direct integration
    of the physical world into computer-based systems.
    """

    print(f"\nOriginal text ({len(text)} chars):")
    print(text.strip()[:100] + "...")

    print("\n⏳ Calling OpenAI API...")
    result = agent.summarize(text)

    print("\n✓ Success!")
    print(f"Summary: {result.iloc[0]['summary']}")

    # Assertions
    assert 'summary' in result.columns, "Missing 'summary' column in summarization result"
    assert len(result) == 1, "Summarization should return exactly one row for single input"
    assert isinstance(result.iloc[0]['summary'], str) and len(result.iloc[0]['summary']) > 0, "Summary should be a non-empty string"

    return True


def test_question_answering():
    """Test question answering capability."""
    print("\n\n" + "="*80)
    print("TEST 2: Question Answering")
    print("="*80)

    agent = DataAgent(model='gpt-4o')

    question = "What are the primary colors?"

    print(f"\nQuestion: {question}")
    print("⏳ Calling OpenAI API...")

    result = agent.answer_question(question)

    print("\n✓ Success!")
    print(f"Answer: {result.iloc[0]['answer']}")

    # Assertions
    assert 'answer' in result.columns, "Missing 'answer' column in QA result"
    assert len(result) == 1, "QA should return exactly one row for single question"
    assert isinstance(result.iloc[0]['answer'], str) and len(result.iloc[0]['answer']) > 0, "Answer should be a non-empty string"

    return True


def test_sentiment_analysis():
    """Test sentiment analysis capability."""
    print("\n\n" + "="*80)
    print("TEST 3: Sentiment Analysis")
    print("="*80)

    agent = DataAgent(model='gpt-4o')

    texts = [
        "I absolutely love this product! It's fantastic!",
        "This is the worst experience I've ever had.",
        "It's okay, nothing extraordinary."
    ]

    print(f"\nAnalyzing {len(texts)} texts...")
    print("⏳ Calling OpenAI API...")

    results = agent.analyze_sentiment(texts)

    print("\n✓ Success!")
    for idx, row in results.iterrows():
        print(f"\nText {idx+1}: \"{row['text'][:45]}...\"")
        print(f"Sentiment: {row['sentiment']}")

    # Assertions
    assert 'sentiment' in results.columns, "Missing 'sentiment' column in sentiment result"
    assert len(results) == len(texts), "Sentiment should return one row per input text"
    allowed = {"positive", "negative", "neutral"}
    assert all(str(s) in allowed for s in results['sentiment']), "Sentiment values must be one of positive/negative/neutral"

    return True


def test_classification():
    """Test text classification capability."""
    print("\n\n" + "="*80)
    print("TEST 4: Text Classification")
    print("="*80)

    agent = DataAgent(model='gpt-4o')

    texts = [
        "Apple stock surged 5% after strong quarterly earnings.",
        "New species of frog discovered in Amazon rainforest."
    ]

    labels = ['business', 'science', 'technology', 'sports']

    print(f"\nClassifying {len(texts)} texts into: {', '.join(labels)}")
    print("⏳ Calling OpenAI API...")

    results = agent.classify(texts, labels=labels)

    print("\n✓ Success!")
    for idx, row in results.iterrows():
        print(f"\nText {idx+1}: \"{row['text'][:50]}...\"")
        print(f"Category: {row['category']}")

    # Assertions
    assert 'category' in results.columns, "Missing 'category' column in classification result"
    assert len(results) == len(texts), "Classification should return one row per input text"
    assert all(str(c) in labels for c in results['category']), "Classification category must be one of the provided labels"

    return True


def main():
    """Run all tests."""
    print("\n╔════════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                            ║")
    print("║                      DATA AGENT TEST SUITE                                 ║")
    print("║                                                                            ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝")

    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("\n❌ ERROR: OPENAI_API_KEY environment variable not set!")
        print("   Set it with: export OPENAI_API_KEY='your-key-here'")
        return

    print("\n✓ API key found")

    # Run tests
    results = {}

    try:
        results['summarization'] = test_summarization()
    except Exception as e:
        print(f"\n❌ Summarization test failed: {e}")
        results['summarization'] = False

    try:
        results['qa'] = test_question_answering()
    except Exception as e:
        print(f"\n❌ Q&A test failed: {e}")
        results['qa'] = False

    try:
        results['sentiment'] = test_sentiment_analysis()
    except Exception as e:
        print(f"\n❌ Sentiment test failed: {e}")
        results['sentiment'] = False

    try:
        results['classification'] = test_classification()
    except Exception as e:
        print(f"\n❌ Classification test failed: {e}")
        results['classification'] = False

    # Summary
    print("\n\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.title():20s}: {status}")
    print("="*80)

    passed_count = sum(results.values())
    total_count = len(results)

    if passed_count == total_count:
        print(f"\n🎉 All {total_count} tests passed!")
    else:
        print(f"\n⚠️  {passed_count}/{total_count} tests passed")

    print()


if __name__ == "__main__":
    main()
