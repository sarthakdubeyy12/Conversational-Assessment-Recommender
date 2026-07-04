#!/usr/bin/env python3
"""
Create mock SHL catalog with realistic assessment data.

This creates a realistic catalog with proper metadata for evaluation.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path

def generate_id(name: str) -> str:
    """Generate consistent ID from name."""
    return hashlib.md5(name.encode()).hexdigest()[:16]

# Realistic SHL assessments with proper metadata
MOCK_ASSESSMENTS = [
    {
        "id": generate_id("Verify G+ Cognitive Ability"),
        "name": "Verify G+ Cognitive Ability",
        "url": "https://www.shl.com/solutions/products/assessments/verify-gplus/",
        "description": "Comprehensive cognitive ability test measuring problem-solving, logical reasoning, and decision-making skills. Industry-leading assessment for identifying candidates with high cognitive potential.",
        "category": "Cognitive Ability",
        "test_type": "Cognitive",
        "skills_measured": ["problem-solving", "logical reasoning", "analytical thinking", "decision making", "abstract reasoning"],
        "competencies": ["Critical Thinking", "Problem Solving", "Analytical Skills", "Decision Making"],
        "duration_minutes": 36,
        "question_count": 30,
        "languages": ["English", "Spanish", "French", "German", "Chinese"],
        "remote_testing": True,
        "adaptive_testing": True,
        "mobile_compatible": True,
        "job_levels": ["Entry Level", "Mid Level", "Senior Level", "Executive"],
        "suitable_roles": ["Software Engineer", "Data Analyst", "Product Manager", "Consultant", "Research Scientist"],
        "industries": ["Technology", "Finance", "Consulting", "Healthcare", "Manufacturing"],
        "product_code": "VRF-GP",
        "assessment_family": "Verify",
        "version": "2.0",
        "tags": ["cognitive", "reasoning", "problem-solving", "g-factor"],
        "difficulty_level": "Medium",
        "delivery_method": "Online",
        "metadata": {},
        "scraped_at": datetime.utcnow().isoformat(),
        "last_updated": datetime.utcnow().isoformat()
    },
    {
        "id": generate_id("Numerical Reasoning"),
        "name": "Numerical Reasoning",
        "url": "https://www.shl.com/solutions/products/assessments/numerical-reasoning/",
        "description": "Assesses ability to work with numerical data, interpret charts and graphs, and perform calculations. Essential for roles requiring data analysis and financial acumen.",
        "category": "Cognitive Ability",
        "test_type": "Numerical",
        "skills_measured": ["numerical reasoning", "data interpretation", "mathematical skills", "analytical thinking"],
        "competencies": ["Numerical Analysis", "Data Interpretation", "Quantitative Reasoning"],
        "duration_minutes": 25,
        "question_count": 20,
        "languages": ["English", "Spanish", "French", "German"],
        "remote_testing": True,
        "adaptive_testing": False,
        "mobile_compatible": True,
        "job_levels": ["Entry Level", "Mid Level", "Senior Level"],
        "suitable_roles": ["Financial Analyst", "Data Scientist", "Business Analyst", "Accountant"],
        "industries": ["Finance", "Technology", "Consulting", "Retail"],
        "product_code": "VRF-NUM",
        "assessment_family": "Verify",
        "version": "1.5",
        "tags": ["numerical", "quantitative", "data-analysis"],
        "difficulty_level": "Medium",
        "delivery_method": "Online",
        "metadata": {},
        "scraped_at": datetime.utcnow().isoformat(),
        "last_updated": datetime.utcnow().isoformat()
    },
    {
        "id": generate_id("OPQ32 Personality Assessment"),
        "name": "OPQ32 Personality Assessment",
        "url": "https://www.shl.com/solutions/products/assessments/opq/",
        "description": "Comprehensive personality questionnaire measuring 32 personality characteristics critical for workplace success. Ideal for leadership assessment and team composition.",
        "category": "Personality",
        "test_type": "Personality",
        "skills_measured": ["leadership", "communication", "teamwork", "adaptability", "emotional intelligence"],
        "competencies": ["Leadership", "Communication", "Teamwork", "Adaptability", "Influence"],
        "duration_minutes": 45,
        "question_count": 104,
        "languages": ["English", "Spanish", "French", "German", "Chinese", "Japanese"],
        "remote_testing": True,
        "adaptive_testing": False,
        "mobile_compatible": True,
        "job_levels": ["Mid Level", "Senior Level", "Executive", "Leadership"],
        "suitable_roles": ["Manager", "Director", "VP", "Team Lead", "Executive"],
        "industries": ["All Industries"],
        "product_code": "OPQ32",
        "assessment_family": "OPQ",
        "version": "3.2",
        "tags": ["personality", "leadership", "soft-skills", "behavioral"],
        "difficulty_level": "Easy",
        "delivery_method": "Online",
        "metadata": {},
        "scraped_at": datetime.utcnow().isoformat(),
        "last_updated": datetime.utcnow().isoformat()
    },
    {
        "id": generate_id("Verbal Reasoning"),
        "name": "Verbal Reasoning",
        "url": "https://www.shl.com/solutions/products/assessments/verbal-reasoning/",
        "description": "Measures ability to understand written information and evaluate arguments. Essential for roles requiring strong communication and analytical skills.",
        "category": "Cognitive Ability",
        "test_type": "Verbal",
        "skills_measured": ["verbal reasoning", "reading comprehension", "critical analysis", "communication"],
        "competencies": ["Verbal Communication", "Reading Comprehension", "Critical Thinking"],
        "duration_minutes": 25,
        "question_count": 20,
        "languages": ["English", "Spanish", "French", "German"],
        "remote_testing": True,
        "adaptive_testing": False,
        "mobile_compatible": True,
        "job_levels": ["Entry Level", "Mid Level", "Senior Level"],
        "suitable_roles": ["Writer", "Editor", "Analyst", "Consultant", "Manager"],
        "industries": ["Media", "Consulting", "Legal", "Education"],
        "product_code": "VRF-VER",
        "assessment_family": "Verify",
        "version": "1.5",
        "tags": ["verbal", "reading", "communication"],
        "difficulty_level": "Medium",
        "delivery_method": "Online",
        "metadata": {},
        "scraped_at": datetime.utcnow().isoformat(),
        "last_updated": datetime.utcnow().isoformat()
    },
    {
        "id": generate_id("Situational Judgment Test"),
        "name": "Situational Judgment Test",
        "url": "https://www.shl.com/solutions/products/assessments/sjt/",
        "description": "Evaluates judgment and decision-making in realistic workplace scenarios. Measures competencies like teamwork, customer service, and problem resolution.",
        "category": "Situational Judgment",
        "test_type": "Situational",
        "skills_measured": ["judgment", "decision-making", "customer service", "conflict resolution", "teamwork"],
        "competencies": ["Judgment", "Decision Making", "Customer Focus", "Teamwork"],
        "duration_minutes": 30,
        "question_count": 25,
        "languages": ["English", "Spanish", "French"],
        "remote_testing": True,
        "adaptive_testing": False,
        "mobile_compatible": True,
        "job_levels": ["Entry Level", "Mid Level"],
        "suitable_roles": ["Customer Service", "Sales", "Support", "Manager"],
        "industries": ["Retail", "Hospitality", "Healthcare", "Technology"],
        "product_code": "SJT-GEN",
        "assessment_family": "Situational",
        "version": "1.0",
        "tags": ["situational", "judgment", "soft-skills"],
        "difficulty_level": "Easy",
        "delivery_method": "Online",
        "metadata": {},
        "scraped_at": datetime.utcnow().isoformat(),
        "last_updated": datetime.utcnow().isoformat()
    },
    {
        "id": generate_id("Inductive Reasoning"),
        "name": "Inductive Reasoning",
        "url": "https://www.shl.com/solutions/products/assessments/inductive-reasoning/",
        "description": "Measures ability to identify patterns and solve novel problems. Key indicator of learning potential and adaptability.",
        "category": "Cognitive Ability",
        "test_type": "Inductive",
        "skills_measured": ["inductive reasoning", "pattern recognition", "abstract thinking", "problem-solving"],
        "competencies": ["Pattern Recognition", "Abstract Reasoning", "Learning Agility"],
        "duration_minutes": 20,
        "question_count": 18,
        "languages": ["English", "Spanish", "French", "German", "Chinese"],
        "remote_testing": True,
        "adaptive_testing": True,
        "mobile_compatible": True,
        "job_levels": ["Entry Level", "Mid Level", "Senior Level"],
        "suitable_roles": ["Software Engineer", "Data Scientist", "Analyst", "Researcher"],
        "industries": ["Technology", "Research", "Consulting"],
        "product_code": "IND-RSN",
        "assessment_family": "Verify",
        "version": "2.0",
        "tags": ["inductive", "reasoning", "patterns"],
        "difficulty_level": "Hard",
        "delivery_method": "Online",
        "metadata": {},
        "scraped_at": datetime.utcnow().isoformat(),
        "last_updated": datetime.utcnow().isoformat()
    }
]

def main():
    """Create mock catalog."""
    output_dir = Path("./data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "catalog.json"
    
    # Write catalog
    with open(output_file, 'w') as f:
        json.dump(MOCK_ASSESSMENTS, f, indent=2)
    
    print(f"✅ Created mock catalog with {len(MOCK_ASSESSMENTS)} assessments")
    print(f"📁 Saved to: {output_file}")
    print()
    print("Assessments:")
    for assessment in MOCK_ASSESSMENTS:
        print(f"  • {assessment['name']} ({assessment['category']})")

if __name__ == "__main__":
    main()
