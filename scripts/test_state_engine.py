#!/usr/bin/env python3
"""
Test conversation state engine.

Demonstrates stateless state reconstruction.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.conversation.domain.entities import Message
from src.conversation.state.state_engine import ConversationStateEngine
from src.shared.logging.logger import get_logger, setup_logger

# Setup logging
setup_logger("state_test", level="INFO")
logger = get_logger(__name__)


def print_state(state, title: str):
    """Pretty print state."""
    print(f"\n{'=' * 60}")
    print(f"{title}")
    print(f"{'=' * 60}")
    print(f"Status: {state.status.value}")
    print(f"Valid: {state.is_valid}")
    print(f"\nHiring Context:")
    print(f"  Role: {state.hiring_context.role_title}")
    print(f"  Seniority: {state.hiring_context.seniority}")
    print(f"  Experience: {state.hiring_context.years_of_experience} years")
    print(f"  Skills: {', '.join(state.hiring_context.technical_skills[:5])}")
    print(f"  Leadership: {state.hiring_context.leadership_required}")
    print(f"  Cognitive: {state.hiring_context.cognitive_required}")
    print(f"\nMetadata:")
    print(f"  Completion: {state.metadata.completion_percentage:.1%}")
    print(f"  Confidence: {state.metadata.confidence_score:.2f}")
    print(f"  Inferred fields: {', '.join(list(state.metadata.inferred_fields)[:3])}")
    print(f"  Missing: {', '.join(state.metadata.missing_information[:3])}")
    if state.metadata.detected_conflicts:
        print(f"  Conflicts: {len(state.metadata.detected_conflicts)}")
        for conflict in state.metadata.detected_conflicts:
            print(f"    - {conflict}")
    print(f"\nReady for recommendations: {state.is_ready_for_recommendation()}")
    print()


def main():
    """Run test scenarios."""
    logger.info("=" * 60)
    logger.info("CONVERSATION STATE ENGINE TEST")
    logger.info("=" * 60)
    logger.info("")
    
    engine = ConversationStateEngine()
    
    # Test 1: Single message
    print("\n" + "=" * 60)
    print("TEST 1: Single hiring request")
    print("=" * 60)
    
    messages1 = [
        Message(role="user", content="I need to hire a senior Java developer")
    ]
    
    state1 = engine.reconstruct_state(messages1)
    print_state(state1, "State after: 'I need to hire a senior Java developer'")
    
    # Test 2: Multiple messages
    print("\n" + "=" * 60)
    print("TEST 2: Progressive conversation")
    print("=" * 60)
    
    messages2 = [
        Message(role="user", content="Hiring backend engineer"),
        Message(role="assistant", content="Great! What level?"),
        Message(role="user", content="Senior, with 7 years experience"),
        Message(role="assistant", content="What skills?"),
        Message(role="user", content="Python, Kubernetes, AWS, leadership"),
    ]
    
    state2 = engine.reconstruct_state(messages2)
    print_state(state2, "State after multi-turn conversation")
    
    # Test 3: Correction
    print("\n" + "=" * 60)
    print("TEST 3: User correction")
    print("=" * 60)
    
    messages3 = [
        Message(role="user", content="Need Java developer"),
        Message(role="assistant", content="Okay..."),
        Message(role="user", content="Actually, change that to Python developer"),
    ]
    
    state3 = engine.reconstruct_state(messages3)
    print_state(state3, "State after correction")
    
    # Test 4: Conflict detection
    print("\n" + "=" * 60)
    print("TEST 4: Conflicting information")
    print("=" * 60)
    
    messages4 = [
        Message(role="user", content="Junior developer with 10 years experience"),
    ]
    
    state4 = engine.reconstruct_state(messages4)
    print_state(state4, "State with conflict")
    
    # Test 5: Rich context
    print("\n" + "=" * 60)
    print("TEST 5: Rich hiring context")
    print("=" * 60)
    
    messages5 = [
        Message(
            role="user",
            content="Hiring senior software architect with 10+ years experience. "
                   "Need leadership, cognitive, and technical skills. "
                   "Python, Kubernetes, system design. Team lead role."
        ),
    ]
    
    state5 = engine.reconstruct_state(messages5)
    print_state(state5, "State with rich context")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETE")
    print("=" * 60)
    print()
    print("State engine successfully reconstructs context from messages!")
    print()
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        sys.exit(1)
