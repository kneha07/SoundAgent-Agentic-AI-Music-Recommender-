import os
from dataclasses import dataclass
from typing import Dict, List

from .recommender import load_songs
from .system import RecommendationAgent


@dataclass
class EvaluationCase:
    request: str
    expected_mood: str
    expected_context: str
    min_confidence: float


def run_evaluation(csv_path: str) -> None:
    songs = load_songs(csv_path)
    agent = RecommendationAgent(songs)

    cases = [
        EvaluationCase(
            request='Recommend upbeat party music for a happy listener who loves electronic pop and bright energy.',
            expected_mood='happy',
            expected_context='party',
            min_confidence=0.70,
        ),
        EvaluationCase(
            request='I want calm study songs with a chill mood and dreamy textures for coffee work.',
            expected_mood='chill',
            expected_context='study',
            min_confidence=0.65,
        ),
        EvaluationCase(
            request='Give me intense workout tracks with strong rock or pop energy and aggressive mood tags.',
            expected_mood='intense',
            expected_context='workout',
            min_confidence=0.70,
        ),
        EvaluationCase(
            request='Find sad but powerful night music that is emotional and vocal-heavy.',
            expected_mood='sad',
            expected_context='night',
            min_confidence=0.65,
        ),
    ]

    results: List[Dict] = []
    for case in cases:
        recommendation = agent.recommend_for_text(case.request, k=5)
        top_song = recommendation.recommendations[0][0] if recommendation.recommendations else None
        mood_ok = top_song and top_song['mood'] == case.expected_mood
        context_ok = top_song and top_song['listening_context'] == case.expected_context
        confidence_ok = recommendation.confidence >= case.min_confidence

        results.append({
            'request': case.request,
            'top_song': top_song['title'] if top_song else 'None',
            'mood_ok': mood_ok,
            'context_ok': context_ok,
            'confidence': recommendation.confidence,
            'confidence_ok': confidence_ok,
        })

    passed = sum(1 for result in results if result['mood_ok'] and result['context_ok'] and result['confidence_ok'])

    print('RELIABILITY EVALUATION SUMMARY')
    print('--------------------------------')
    for idx, result in enumerate(results, start=1):
        print(f"Case {idx}: {result['request']}")
        print(f"  Top song: {result['top_song']}")
        print(f"  Mood match: {result['mood_ok']} | Context match: {result['context_ok']} | Confidence: {result['confidence']:.2f} | Passed: {result['confidence_ok']}")
        print()

    print(f"{passed}/{len(results)} cases fully passed the reliability check.")
    print('Note: This is a synthetic test harness for model reliability and intent alignment.')


if __name__ == '__main__':
    root_dir = os.path.join(os.path.dirname(__file__), '..')
    csv_path = os.path.join(root_dir, 'data', 'songs.csv')
    run_evaluation(csv_path)
