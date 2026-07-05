#!/usr/bin/env python3
"""
Comprehensive bottleneck profiling.

Measures latency at each stage of the pipeline to identify optimization targets.
"""

import asyncio
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.dependencies.orchestrator import get_orchestrator
from src.shared.config.settings import get_settings

async def profile_full_request():
    """Profile a complete request end-to-end."""
    print("=" * 70)
    print("BOTTLENECK PROFILING - DETAILED LATENCY BREAKDOWN")
    print("=" * 70)
    
    query = "I need to assess cognitive ability and problem-solving skills"
    
    # Get orchestrator
    start_init = time.perf_counter()
    orch = get_orchestrator()
    init_time = (time.perf_counter() - start_init) * 1000
    print(f"\n📦 Orchestrator initialization: {init_time:.2f}ms")
    
    # Execute full request with timing
    start_total = time.perf_counter()
    result = await orch.execute(query, [], '')
    total_time = (time.perf_counter() - start_total) * 1000
    
    print(f"\n⏱️  TOTAL REQUEST TIME: {total_time:.2f}ms")
    
    # Extract stage timings from execution trace
    if result.execution_trace:
        print("\n📊 STAGE-BY-STAGE BREAKDOWN:")
        print(f"   Total stages: {result.execution_trace.stages_completed}")
        
        for stage_trace in result.execution_trace.stages:
            print(f"   {stage_trace.stage.value:30s} {stage_trace.duration_ms:8.2f}ms")
    
    # Statistics from result
    if result.statistics:
        print("\n📈 ORCHESTRATOR STATISTICS:")
        stats = result.statistics
        print(f"   State reconstruction: {stats.state_reconstruction_ms:.2f}ms")
        print(f"   Intent detection:     {stats.intent_detection_ms:.2f}ms")
        print(f"   Guardrails:          {stats.guardrails_input_ms:.2f}ms")
        print(f"   Retrieval:           {stats.retrieval_ms:.2f}ms")
        print(f"   Recommendation:      {stats.recommendation_ms:.2f}ms")
        print(f"   Total:               {stats.total_duration_ms:.2f}ms")
    
    # Retrieval details
    if result.retrieval_result:
        print("\n🔍 RETRIEVAL PIPELINE DETAILS:")
        ret_stats = result.retrieval_result.statistics
        print(f"   Query build:         {ret_stats.query_build_ms:.2f}ms")
        print(f"   Retrieval:           {ret_stats.retrieval_ms:.2f}ms")
        print(f"   Filtering:           {ret_stats.filtering_ms:.2f}ms")
        print(f"   Ranking:             {ret_stats.ranking_ms:.2f}ms")
        print(f"   Deduplication:       {ret_stats.deduplication_ms:.2f}ms")
        print(f"   Compression:         {ret_stats.compression_ms:.2f}ms")
        print(f"   Total retrieval:     {ret_stats.total_latency_ms:.2f}ms")
        print(f"\n   Chunks retrieved:    {ret_stats.chunks_retrieved}")
        print(f"   Chunks filtered:     {ret_stats.chunks_filtered}")
        print(f"   Chunks final:        {ret_stats.chunks_final}")
        print(f"   Assessments final:   {ret_stats.assessments_final}")
    
    # Recommendation details
    if result.recommendation_result:
        print("\n🎯 RECOMMENDATION ENGINE DETAILS:")
        rec_stats = result.recommendation_result.statistics
        print(f"   Processing time:     {rec_stats.processing_time_ms:.2f}ms")
        print(f"   Candidates received: {rec_stats.candidates_received}")
        print(f"   Candidates filtered: {rec_stats.candidates_filtered}")
        print(f"   Recommendations:     {rec_stats.recommendations_generated}")
    
    print("\n" + "=" * 70)
    print("BOTTLENECK ANALYSIS")
    print("=" * 70)
    
    # Identify top bottlenecks
    if result.statistics:
        stages = [
            ("State reconstruction", result.statistics.state_reconstruction_ms),
            ("Intent detection", result.statistics.intent_detection_ms),
            ("Guardrails", result.statistics.guardrails_input_ms),
            ("Retrieval", result.statistics.retrieval_ms),
            ("Recommendation", result.statistics.recommendation_ms),
        ]
        
        # Sort by time
        stages.sort(key=lambda x: x[1], reverse=True)
        
        print("\n🔴 TOP BOTTLENECKS (slowest first):")
        for i, (name, duration) in enumerate(stages[:3], 1):
            pct = (duration / result.statistics.total_duration_ms) * 100
            print(f"   {i}. {name:25s} {duration:8.2f}ms ({pct:5.1f}%)")
    
    # Identify optimization opportunities
    print("\n💡 OPTIMIZATION OPPORTUNITIES:")
    
    if result.retrieval_result:
        ret_stats = result.retrieval_result.statistics
        
        # Check for slow retrieval
        if ret_stats.retrieval_ms > 100:
            print(f"   ⚠️  Retrieval latency high: {ret_stats.retrieval_ms:.2f}ms")
            print("      → Optimize: embedding cache, batch queries, reduce top_k")
        
        # Check for excessive chunks
        if ret_stats.chunks_retrieved > 50:
            print(f"   ⚠️  Too many chunks retrieved: {ret_stats.chunks_retrieved}")
            print("      → Optimize: metadata filtering, adaptive top-k")
        
        # Check compression overhead
        if ret_stats.compression_ms > 50:
            print(f"   ⚠️  Compression overhead: {ret_stats.compression_ms:.2f}ms")
            print("      → Optimize: reduce chunk size, smarter compression")
    
    if result.recommendation_result:
        rec_stats = result.recommendation_result.statistics
        
        # Check for slow recommendation processing
        if rec_stats.processing_time_ms > 100:
            print(f"   ⚠️  Recommendation processing slow: {rec_stats.processing_time_ms:.2f}ms")
            print("      → Optimize: caching, parallel ranking")
    
    # Check total latency
    if total_time > 500:
        print(f"   ⚠️  Total latency exceeds target: {total_time:.2f}ms > 500ms")
        print("      → Target: < 500ms average, < 1000ms P95")
    
    print("\n" + "=" * 70)
    
    return {
        'total_time': total_time,
        'init_time': init_time,
        'retrieval_time': result.retrieval_result.statistics.total_latency_ms if result.retrieval_result else 0,
        'recommendation_time': result.recommendation_result.statistics.processing_time_ms if result.recommendation_result else 0,
        'result': result
    }

async def profile_multiple_requests(n=5):
    """Profile multiple requests to get statistical data."""
    print(f"\n🔄 Running {n} requests for statistical profiling...\n")
    
    times = []
    for i in range(n):
        print(f"Request {i+1}/{n}...", end=" ")
        start = time.perf_counter()
        orch = get_orchestrator()
        result = await orch.execute("I need to assess cognitive ability and problem-solving skills", [], '')
        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)
        print(f"{elapsed:.2f}ms")
    
    print(f"\n📊 STATISTICAL SUMMARY ({n} requests):")
    print(f"   Min:     {min(times):.2f}ms")
    print(f"   Max:     {max(times):.2f}ms")
    print(f"   Mean:    {sum(times)/len(times):.2f}ms")
    print(f"   Median:  {sorted(times)[len(times)//2]:.2f}ms")
    
    return times

async def main():
    # Single detailed profile
    await profile_full_request()
    
    # Statistical profile
    await profile_multiple_requests(5)

if __name__ == "__main__":
    asyncio.run(main())
