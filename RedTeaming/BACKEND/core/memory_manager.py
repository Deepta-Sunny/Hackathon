"""
Memory management for storing vulnerabilities and attack results in DuckDB.
"""

from datetime import datetime
from typing import List, Optional
from pyrit.memory import DuckDBMemory
from pyrit.models import SeedPrompt

from config import DUCKDB_PATH
from models import VulnerabilityFinding, GeneralizedPattern


class VulnerableResponseMemory:
    """
    Stores and manages vulnerability findings across attack runs.
    """
    
    def __init__(self):
        self.findings: List[VulnerabilityFinding] = []
    
    def add_finding(
        self,
        run: int,
        turn: int,
        risk_category: int,
        vulnerability_type: str,
        attack_prompt: str,
        chatbot_response: str,
        context_messages: List[dict],
        attack_technique: str,
        target_nodes: List[str],
        response_received: bool = True
    ):
        """Add a vulnerability finding."""
        finding = VulnerabilityFinding(
            run=run,
            turn=turn,
            risk_category=risk_category,
            vulnerability_type=vulnerability_type,
            attack_prompt=attack_prompt,
            chatbot_response=chatbot_response,
            context_messages=context_messages,
            attack_technique=attack_technique,
            target_nodes=target_nodes,
            response_received=response_received
        )
        self.findings.append(finding)
    
    def get_summary_for_next_run(self) -> str:
        """Generate summary of findings for next run's context."""
        if not self.findings:
            return "No previous vulnerabilities found."
        
        summary_lines = [f"DISCOVERED VULNERABILITIES ({len(self.findings)} total):"]
        
        for i, finding in enumerate(self.findings[-10:], 1):  # Last 10
            summary_lines.append(
                f"{i}. Run {finding.run}, Turn {finding.turn}: "
                f"{finding.vulnerability_type} (Risk {finding.risk_category}) - "
                f"{finding.attack_technique}"
            )
        
        return "\n".join(summary_lines)
    
    def get_by_risk_category(self, category: int) -> List[VulnerabilityFinding]:
        """Get findings by risk category."""
        return [f for f in self.findings if f.risk_category == category]
    
    def get_count_by_category(self) -> dict:
        """Get count of findings by risk category."""
        counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for finding in self.findings:
            counts[finding.risk_category] = counts.get(finding.risk_category, 0) + 1
        return counts


class DuckDBMemoryManager:
    """
    Manages DuckDB persistence for attack patterns and results.
    """
    
    def __init__(self, db_path: str = DUCKDB_PATH):
        self.db_path = db_path
        self.memory: Optional[DuckDBMemory] = None
    
    def _get_memory(self) -> DuckDBMemory:
        """Get or create DuckDB memory instance."""
        if self.memory is None:
            self.memory = DuckDBMemory(db_path=self.db_path)
        return self.memory
    
    async def save_generalized_patterns(
        self,
        patterns: List[GeneralizedPattern],
        dataset_name: str = "crescendo_3run_patterns"
    ) -> int:
        """
        Save generalized attack patterns to DuckDB.
        
        Args:
            patterns: List of GeneralizedPattern objects
            dataset_name: Dataset name for organization
            
        Returns:
            int: Number of patterns saved
        """
        if not patterns:
            return 0
        
        memory = self._get_memory()
        seed_prompts = []
        
        for idx, pattern in enumerate(patterns, 1):
            # Create structured metadata
            metadata = {
                "pattern_id": pattern.pattern_id,
                "attack_type": pattern.attack_type,
                "vulnerability_category": pattern.category,
                "risk_level": pattern.risk_level,
                "success_indicators": pattern.indicators,
                "success_count": pattern.success_count,
                "generated_from": "3_run_crescendo_assessment",
                "chatbot_architecture": "universal",
                "timestamp": datetime.now().isoformat()
            }
            
            # Create SeedPrompt
            seed_prompt = SeedPrompt(
                value=pattern.technique,
                data_type="text",
                name=f"Generalized Pattern {idx}",
                dataset_name=dataset_name,
                harm_categories=["security_testing"],
                description=pattern.description,
                authors=["ThreeRunCrescendoOrchestrator"],
                groups=["crescendo_attacks", "generalized_patterns"],
                source="pyrit_3run_assessment",
                parameters=metadata
            )
            
            seed_prompts.append(seed_prompt)
        
        # Save to DuckDB
        await memory.add_seed_prompts_to_memory_async(
            prompts=seed_prompts,
            added_by="crescendo_3run_assessment"
        )
        
        print(f"✅ Successfully saved {len(seed_prompts)} patterns to {self.db_path}")
        print(f"   • Dataset: {dataset_name}")
        print(f"   • Storage: Persistent (survives restarts)")
        
        return len(seed_prompts)
    
    def get_seed_prompts(self) -> List:
        """Retrieve all seed prompts from DuckDB."""
        memory = self._get_memory()
        try:
            return memory.get_seed_prompts()
        except AttributeError:
            # Fallback for older PyRIT versions
            return []
    
    def close(self):
        """Close database connection."""
        if self.memory:
            self.memory.dispose_engine()
            self.memory = None
