#!/usr/bin/env python3
"""
Catalog Demo Script - Creates sample catalog for testing.

This demonstrates the catalog structure without actually scraping SHL.
Useful for testing downstream components (Phase 3, 4, 5).
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.catalog.domain.entities import Assessment
from src.catalog.infrastructure.json_repository import JSONCatalogRepository
from src.shared.logging.logger import get_logger, setup_logger

# Setup logging
setup_logger("catalog_demo", level="INFO")
logger = get_logger(__name__)


async def main():
    """Create sample catalog."""
    logger.info("Creating sample SHL catalog...")
    
    # Sample assessments based on real SHL products
    sample_assessments = [
        Assessment(
            id="verify_g_plus",
            name="Verify G+ Assessment",
            url="https://www.shl.com/solutions/products/assessments/verify-g-plus/",
            description="General cognitive ability test measuring reasoning and problem-solving skills",
            category="Cognitive Ability",
            test_type="Reasoning",
            skills_measured=["Abstract Reasoning", "Numerical Reasoning", "Deductive Reasoning"],
            competencies=["Problem Solving", "Critical Thinking", "Analytical Skills"],
            duration_minutes=30,
            question_count=30,
            languages=["English", "Spanish", "French", "German"],
            remote_testing=True,
            adaptive_testing=True,
            mobile_compatible=True,
            job_levels=["Entry Level", "Mid Level", "Senior Level"],
            suitable_roles=["Analyst", "Manager", "Professional"],
            industries=["Technology", "Finance", "Consulting"],
            product_code="VG+",
            assessment_family="Verify",
            tags=["Cognitive", "Reasoning", "General Ability"],
            difficulty_level="Medium",
            delivery_method="Online",
            scraped_at=datetime.utcnow(),
        ),
        Assessment(
            id="opp_profile",
            name="Occupational Personality Profile (OPP)",
            url="https://www.shl.com/solutions/products/assessments/opp/",
            description="Comprehensive personality assessment measuring workplace behaviors and preferences",
            category="Personality",
            test_type="Personality Inventory",
            skills_measured=["Interpersonal Skills", "Leadership", "Teamwork"],
            competencies=["Emotional Intelligence", "Communication", "Adaptability"],
            duration_minutes=40,
            question_count=104,
            languages=["English", "Spanish", "French", "German", "Chinese"],
            remote_testing=True,
            adaptive_testing=False,
            mobile_compatible=True,
            job_levels=["All Levels"],
            suitable_roles=["Manager", "Leader", "Team Member"],
            industries=["All Industries"],
            product_code="OPP",
            assessment_family="Personality",
            tags=["Personality", "Workplace Behavior", "Competencies"],
            difficulty_level="Easy",
            delivery_method="Online",
            scraped_at=datetime.utcnow(),
        ),
        Assessment(
            id="numerical_reasoning",
            name="Numerical Reasoning Assessment",
            url="https://www.shl.com/solutions/products/assessments/numerical-reasoning/",
            description="Evaluates ability to work with numerical data and draw logical conclusions",
            category="Cognitive Ability",
            test_type="Numerical",
            skills_measured=["Numerical Analysis", "Data Interpretation", "Quantitative Reasoning"],
            competencies=["Analytical Thinking", "Decision Making"],
            duration_minutes=25,
            question_count=20,
            languages=["English", "Spanish", "French"],
            remote_testing=True,
            adaptive_testing=False,
            mobile_compatible=True,
            job_levels=["Entry Level", "Mid Level"],
            suitable_roles=["Analyst", "Financial Professional", "Data Analyst"],
            industries=["Finance", "Consulting", "Technology"],
            product_code="NUM",
            assessment_family="Verify",
            tags=["Numerical", "Reasoning", "Data Analysis"],
            difficulty_level="Medium",
            delivery_method="Online",
            scraped_at=datetime.utcnow(),
        ),
        Assessment(
            id="verbal_reasoning",
            name="Verbal Reasoning Assessment",
            url="https://www.shl.com/solutions/products/assessments/verbal-reasoning/",
            description="Measures ability to understand and analyze written information",
            category="Cognitive Ability",
            test_type="Verbal",
            skills_measured=["Reading Comprehension", "Verbal Analysis", "Critical Reading"],
            competencies=["Communication", "Critical Thinking"],
            duration_minutes=25,
            question_count=20,
            languages=["English", "Spanish", "French", "German"],
            remote_testing=True,
            adaptive_testing=False,
            mobile_compatible=True,
            job_levels=["Entry Level", "Mid Level", "Senior Level"],
            suitable_roles=["Manager", "Professional", "Consultant"],
            industries=["All Industries"],
            product_code="VER",
            assessment_family="Verify",
            tags=["Verbal", "Reasoning", "Comprehension"],
            difficulty_level="Medium",
            delivery_method="Online",
            scraped_at=datetime.utcnow(),
        ),
        Assessment(
            id="situational_judgment",
            name="Situational Judgment Test (SJT)",
            url="https://www.shl.com/solutions/products/assessments/situational-judgment/",
            description="Evaluates decision-making in workplace scenarios",
            category="Behavioral",
            test_type="Situational Judgment",
            skills_measured=["Decision Making", "Problem Solving", "Judgment"],
            competencies=["Situational Awareness", "Professional Judgment"],
            duration_minutes=30,
            question_count=15,
            languages=["English", "Spanish", "French"],
            remote_testing=True,
            adaptive_testing=False,
            mobile_compatible=True,
            job_levels=["All Levels"],
            suitable_roles=["Manager", "Supervisor", "Team Leader"],
            industries=["All Industries"],
            product_code="SJT",
            assessment_family="Behavioral",
            tags=["Situational", "Judgment", "Decision Making"],
            difficulty_level="Medium",
            delivery_method="Online",
            scraped_at=datetime.utcnow(),
        ),
    ]
    
    # Save to repository
    repository = JSONCatalogRepository("./data/processed/catalog.json")
    await repository.save(sample_assessments)
    
    logger.info(f"✅ Created sample catalog with {len(sample_assessments)} assessments")
    logger.info(f"Location: ./data/processed/catalog.json")
    
    # Print summary
    logger.info("")
    logger.info("Sample Assessments:")
    for assessment in sample_assessments:
        logger.info(f"  - {assessment.name} ({assessment.category})")
    
    logger.info("")
    logger.info("This sample catalog can be used to test:")
    logger.info("  - Phase 3: Retrieval (embeddings, vector search)")
    logger.info("  - Phase 4: Conversation (LLM integration)")
    logger.info("  - Phase 5: Recommendation (matching, ranking)")
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
