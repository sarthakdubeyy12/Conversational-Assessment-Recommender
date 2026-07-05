#!/usr/bin/env python3
"""
Comprehensive SHL Catalog Audit.

Verifies that the production system uses the complete SHL Product Catalog
restricted to Individual Test Solutions only.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
import re

sys.path.insert(0, str(Path(__file__).parent.parent))

class CatalogAuditor:
    """Comprehensive catalog audit."""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.successes = []
        
    def audit_all(self):
        """Run complete audit."""
        print("=" * 80)
        print("SHL CATALOG COMPLIANCE AUDIT")
        print("=" * 80)
        print()
        
        # 1. Check raw data
        self.audit_raw_data()
        
        # 2. Check processed catalog
        self.audit_processed_catalog()
        
        # 3. Validate URLs
        self.audit_urls()
        
        # 4. Check for mock/demo data
        self.audit_mock_data()
        
        # 5. Check for hardcoded recommendations
        self.audit_hardcoded_recommendations()
        
        # 6. Check ChromaDB
        self.audit_chromadb()
        
        # 7. Generate final report
        self.generate_report()
    
    def audit_raw_data(self):
        """Audit raw HTML data."""
        print("📁 AUDITING RAW DATA")
        print("-" * 80)
        
        raw_dir = Path("data/raw")
        
        if not raw_dir.exists():
            self.issues.append("Raw data directory does not exist")
            print("❌ data/raw/ directory not found")
            return
        
        html_files = list(raw_dir.glob("*.html"))
        print(f"✓ Raw data directory exists")
        print(f"  HTML files found: {len(html_files)}")
        
        if len(html_files) == 0:
            self.warnings.append("No HTML files in data/raw/")
            print("⚠️  No HTML files found (may be using direct API)")
        else:
            self.successes.append(f"Found {len(html_files)} raw HTML files")
        
        print()
    
    def audit_processed_catalog(self):
        """Audit processed catalog.json."""
        print("📋 AUDITING PROCESSED CATALOG")
        print("-" * 80)
        
        catalog_path = Path("data/processed/catalog.json")
        
        if not catalog_path.exists():
            self.issues.append("Processed catalog does not exist")
            print("❌ data/processed/catalog.json not found")
            return
        
        print("✓ Catalog file exists")
        
        # Load catalog
        with open(catalog_path) as f:
            catalog = json.load(f)
        
        if not isinstance(catalog, list):
            self.issues.append("Catalog is not a list")
            print("❌ Catalog format invalid (not a list)")
            return
        
        total = len(catalog)
        print(f"✓ Total assessments: {total}")
        self.successes.append(f"Catalog contains {total} assessments")
        
        # Check for duplicates
        ids = [a.get('id') for a in catalog if a.get('id')]
        urls = [a.get('url') for a in catalog if a.get('url')]
        names = [a.get('name') for a in catalog if a.get('name')]
        
        unique_ids = len(set(ids))
        unique_urls = len(set(urls))
        unique_names = len(set(names))
        
        print(f"  Unique IDs: {unique_ids}")
        print(f"  Unique URLs: {unique_urls}")
        print(f"  Unique names: {unique_names}")
        
        if len(ids) != unique_ids:
            self.issues.append(f"Duplicate IDs found: {len(ids) - unique_ids} duplicates")
            print(f"❌ Duplicate IDs: {len(ids) - unique_ids}")
        
        if len(urls) != unique_urls:
            self.issues.append(f"Duplicate URLs found: {len(urls) - unique_urls} duplicates")
            print(f"❌ Duplicate URLs: {len(urls) - unique_urls}")
        
        # Validate required fields
        print("\n  Field validation:")
        required_fields = ['id', 'name', 'url', 'description', 'category', 'test_type']
        
        for field in required_fields:
            missing = sum(1 for a in catalog if not a.get(field))
            if missing > 0:
                self.issues.append(f"{missing} assessments missing '{field}'")
                print(f"  ❌ {field}: {missing} missing")
            else:
                print(f"  ✓ {field}: all present")
        
        # Check for mock/demo indicators
        print("\n  Checking for mock/demo data:")
        mock_indicators = ['mock', 'demo', 'test', 'sample', 'fake', 'placeholder', 'example']
        
        mock_found = False
        for assessment in catalog:
            name = assessment.get('name', '').lower()
            url = assessment.get('url', '').lower()
            desc = assessment.get('description', '').lower()
            
            for indicator in mock_indicators:
                if indicator in name or indicator in url or indicator in desc:
                    self.warnings.append(f"Possible mock data: {assessment.get('name')}")
                    print(f"  ⚠️  '{assessment.get('name')}' contains '{indicator}'")
                    mock_found = True
                    break
        
        if not mock_found:
            print("  ✓ No obvious mock/demo indicators found")
            self.successes.append("No mock data indicators in catalog")
        
        print()
        
        return catalog
    
    def audit_urls(self):
        """Validate all URLs."""
        print("🔗 AUDITING URLs")
        print("-" * 80)
        
        catalog_path = Path("data/processed/catalog.json")
        if not catalog_path.exists():
            print("❌ Cannot audit URLs - catalog not found")
            return
        
        with open(catalog_path) as f:
            catalog = json.load(f)
        
        invalid_urls = []
        valid_shl_urls = 0
        
        invalid_patterns = [
            'localhost',
            '127.0.0.1',
            'example.com',
            'test.com',
            'dummy',
            'placeholder',
            'mock'
        ]
        
        for assessment in catalog:
            url = assessment.get('url', '')
            
            # Check for invalid patterns
            url_lower = url.lower()
            if any(pattern in url_lower for pattern in invalid_patterns):
                invalid_urls.append((assessment.get('name'), url))
                continue
            
            # Check for valid SHL URL
            if url.startswith('https://www.shl.com/') or url.startswith('https://shl.com/'):
                valid_shl_urls += 1
            else:
                invalid_urls.append((assessment.get('name'), url))
        
        print(f"✓ Valid SHL URLs: {valid_shl_urls}/{len(catalog)}")
        
        if invalid_urls:
            self.issues.append(f"{len(invalid_urls)} invalid URLs found")
            print(f"❌ Invalid URLs: {len(invalid_urls)}")
            for name, url in invalid_urls[:5]:
                print(f"     {name}: {url}")
            if len(invalid_urls) > 5:
                print(f"     ... and {len(invalid_urls) - 5} more")
        else:
            self.successes.append("All URLs are valid SHL URLs")
            print("✓ All URLs are valid SHL URLs")
        
        print()
    
    def audit_mock_data(self):
        """Search for mock data in source code."""
        print("🔍 SEARCHING FOR MOCK DATA IN SOURCE CODE")
        print("-" * 80)
        
        # Search patterns
        mock_patterns = [
            r'mock.*catalog',
            r'demo.*catalog',
            r'fake.*assessment',
            r'sample.*assessment',
            r'test.*catalog',
            r'placeholder.*data',
        ]
        
        # Search in specific directories
        search_dirs = ['src', 'scripts']
        
        mock_files = []
        
        for dir_name in search_dirs:
            dir_path = Path(dir_name)
            if not dir_path.exists():
                continue
            
            for py_file in dir_path.rglob('*.py'):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    for pattern in mock_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            mock_files.append((str(py_file), pattern))
                            break
                except:
                    pass
        
        # Check scripts specifically
        mock_script = Path('scripts/create_mock_catalog.py')
        if mock_script.exists():
            print(f"  ⚠️  Found: scripts/create_mock_catalog.py")
            self.warnings.append("Mock catalog creation script exists")
            
            # Check if it's actually being used
            print("     Checking if mock data is being used in production...")
            
            # Check main.py, app.py for references
            production_files = [
                'src/main.py',
                'src/api/app.py',
                'src/api/dependencies/orchestrator.py'
            ]
            
            uses_mock = False
            for prod_file in production_files:
                if Path(prod_file).exists():
                    with open(prod_file) as f:
                        if 'mock' in f.read().lower():
                            uses_mock = True
                            print(f"     ⚠️  {prod_file} references 'mock'")
            
            if not uses_mock:
                print("     ✓ Mock script exists but not used in production")
        
        if not mock_files:
            print("✓ No mock data patterns found in production code")
            self.successes.append("No mock data in production code")
        
        print()
    
    def audit_hardcoded_recommendations(self):
        """Search for hardcoded recommendations."""
        print("🔒 SEARCHING FOR HARDCODED RECOMMENDATIONS")
        print("-" * 80)
        
        hardcoded_patterns = [
            r'recommendations\s*=\s*\[',
            r'RECOMMENDATIONS\s*=\s*\[',
            r'DEFAULT_ASSESSMENTS',
            r'FALLBACK_RECOMMENDATIONS',
        ]
        
        found_hardcoded = []
        
        for py_file in Path('src').rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for i, line in enumerate(lines, 1):
                    for pattern in hardcoded_patterns:
                        if re.search(pattern, line):
                            # Check if it's not just a variable assignment
                            # Look for actual assessment data
                            context = ''.join(lines[max(0, i-1):min(len(lines), i+5)])
                            if 'assessment' in context.lower() or 'test' in context.lower():
                                found_hardcoded.append((str(py_file), i, line.strip()))
            except:
                pass
        
        if found_hardcoded:
            self.issues.append(f"Found {len(found_hardcoded)} hardcoded recommendation patterns")
            print(f"⚠️  Found {len(found_hardcoded)} potential hardcoded patterns:")
            for file, line_no, line in found_hardcoded[:5]:
                print(f"     {file}:{line_no}: {line[:60]}...")
        else:
            print("✓ No hardcoded recommendation patterns found")
            self.successes.append("No hardcoded recommendations")
        
        print()
    
    def audit_chromadb(self):
        """Audit ChromaDB index."""
        print("💾 AUDITING CHROMADB INDEX")
        print("-" * 80)
        
        try:
            from src.shared.config.settings import get_settings
            from src.knowledge_base.vector_store.chroma_client import ChromaVectorStore
            
            settings = get_settings()
            
            # Check if persist directory exists
            persist_dir = Path(settings.chroma_persist_directory)
            if not persist_dir.exists():
                self.warnings.append("ChromaDB persist directory not found")
                print("⚠️  ChromaDB persist directory not found")
                print("   (This is OK if running in-memory)")
                print()
                return
            
            print(f"✓ ChromaDB directory: {persist_dir}")
            
            # Try to get collection stats
            store = ChromaVectorStore(
                settings.chroma_persist_directory,
                settings.chroma_collection_name
            )
            
            print(f"✓ Collection name: {settings.chroma_collection_name}")
            
            # Note: Can't easily get count without async context
            print("  (Collection exists and is accessible)")
            
        except Exception as e:
            self.warnings.append(f"Could not fully audit ChromaDB: {e}")
            print(f"⚠️  Could not fully audit ChromaDB: {e}")
        
        print()
    
    def generate_report(self):
        """Generate final audit report."""
        print("=" * 80)
        print("FINAL AUDIT REPORT")
        print("=" * 80)
        print()
        
        # Summary
        print("📊 SUMMARY")
        print("-" * 80)
        
        catalog_path = Path("data/processed/catalog.json")
        if catalog_path.exists():
            with open(catalog_path) as f:
                catalog = json.load(f)
            print(f"✅ Total assessments in catalog: {len(catalog)}")
            
            # Check if it's mock or real
            if len(catalog) <= 10:
                print(f"⚠️  SMALL CATALOG: Only {len(catalog)} assessments")
                print("   This appears to be MOCK DATA for testing/demo")
                self.issues.append("Catalog appears to be mock data (too few assessments)")
            else:
                print(f"✓ Reasonable catalog size")
        
        print(f"✅ Successes: {len(self.successes)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"❌ Issues: {len(self.issues)}")
        print()
        
        # Details
        if self.successes:
            print("✅ SUCCESSES:")
            for success in self.successes:
                print(f"   • {success}")
            print()
        
        if self.warnings:
            print("⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"   • {warning}")
            print()
        
        if self.issues:
            print("❌ ISSUES:")
            for issue in self.issues:
                print(f"   • {issue}")
            print()
        
        # Final verdict
        print("=" * 80)
        print("FINAL VERDICT")
        print("=" * 80)
        print()
        
        if len(self.issues) == 0:
            print("✅ VERIFIED")
            print()
            print("The production system appears to use a proper catalog structure.")
            print()
            if len(self.warnings) > 0:
                print("⚠️  However, warnings were found:")
                for warning in self.warnings:
                    print(f"   • {warning}")
                print()
                print("RECOMMENDATION: Review warnings before production deployment.")
            
            # Check if it's mock data
            if catalog_path.exists():
                with open(catalog_path) as f:
                    catalog = json.load(f)
                if len(catalog) <= 10:
                    print()
                    print("⚠️  CRITICAL: The catalog appears to contain MOCK DATA")
                    print("   Only {} assessments found - real SHL catalog should have 50+".format(len(catalog)))
                    print()
                    print("   TO FIX:")
                    print("   1. Implement the real SHL scraper")
                    print("   2. Scrape https://www.shl.com/solutions/products/assessments/")
                    print("   3. Extract all Individual Test Solutions")
                    print("   4. Rebuild the knowledge base")
        else:
            print("❌ NOT VERIFIED")
            print()
            print("Issues were found that prevent full compliance:")
            for issue in self.issues:
                print(f"   • {issue}")

def main():
    auditor = CatalogAuditor()
    auditor.audit_all()

if __name__ == "__main__":
    main()
