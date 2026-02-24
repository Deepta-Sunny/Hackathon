"""
Attack State Manager - Manages state across 3-run attack evolution system.

This module provides state management for progressive attack learning across
Run 1 (PyRIT → domain conversion), Run 2 (evolve successes), and Run 3 (deepest attacks).
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class SuccessfulPrompt:
    """Represents a successful attack prompt from a run."""
    prompt: str
    response: str
    risk_category: int  # 1-5 scale
    reward_points: int
    turn_number: int
    run_number: int
    attack_type: str  # "standard", "crescendo", "skeleton_key", "obfuscation"
    phase: str  # e.g., "reconnaissance", "trust_building", etc.
    timestamp: str
    generation_method: str  # "[PYRIT-MOLDED]", "[LLM-GENERATED]", "[HARDCODED]"


@dataclass
class DomainKnowledge:
    """Stores detected domain information."""
    domain: str
    confidence: float  # 0.0-1.0
    domain_keywords: List[str]
    initial_attack_questions: List[str]
    sensitive_areas: List[str]
    detection_timestamp: str


class AttackStateManager:
    """
    Manages attack state across 3-run progressive learning system.
    
    Tracks:
    - Current run number (1, 2, or 3)
    - Detected domain and domain knowledge
    - Temporary memory of successful prompts (risk >= 3)
    - Cumulative reward points per run and total
    - Evolution history
    """
    
    def __init__(self, attack_type: str):
        """
        Initialize attack state manager.
        
        Args:
            attack_type: Type of attack ("standard", "crescendo", "skeleton_key", "obfuscation")
        """
        self.attack_type = attack_type
        self.current_run = 0
        self.domain_knowledge: Optional[DomainKnowledge] = None
        
        # Temporary memory: successful prompts during current session (3 runs)
        self.successful_prompts: List[SuccessfulPrompt] = []
        
        # Reward tracking
        self.run_rewards: Dict[int, int] = {1: 0, 2: 0, 3: 0}
        self.total_session_reward = 0
        
        # Evolution tracking
        self.evolution_history: List[Dict[str, Any]] = []
        
        # Session metadata
        self.session_start_time = datetime.utcnow().isoformat()
        self.session_id = f"{attack_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    def initialize_run(self, run_number: int) -> None:
        """
        Initialize a new run.
        
        Args:
            run_number: The run number (1, 2, or 3)
        """
        if run_number not in [1, 2, 3]:
            raise ValueError(f"Invalid run number: {run_number}. Must be 1, 2, or 3.")
        
        self.current_run = run_number
        print(f"\n{'='*80}")
        print(f"🚀 INITIALIZING RUN {run_number} FOR {self.attack_type.upper()} ATTACK")
        print(f"{'='*80}")
        
        if run_number == 1:
            print("📋 Run 1 Strategy: PyRIT seeds → Domain-specific conversion")
        elif run_number == 2:
            successful_count = len([p for p in self.successful_prompts if p.run_number == 1])
            print(f"📋 Run 2 Strategy: Evolve {successful_count} successful prompts from Run 1")
        elif run_number == 3:
            successful_count = len([p for p in self.successful_prompts if p.run_number in [1, 2]])
            print(f"📋 Run 3 Strategy: Most aggressive attacks using {successful_count} successful patterns")
        
        print(f"{'='*80}\n")
    
    def set_domain_knowledge(self, domain_knowledge: DomainKnowledge) -> None:
        """
        Set detected domain knowledge (from LLM domain detector).
        
        Args:
            domain_knowledge: Detected domain information
        """
        self.domain_knowledge = domain_knowledge
        print(f"\n🎯 DOMAIN DETECTED: {domain_knowledge.domain.upper()}")
        print(f"   Confidence: {domain_knowledge.confidence:.2%}")
        print(f"   Keywords: {', '.join(domain_knowledge.domain_keywords)}")
        print(f"   Sensitive Areas: {', '.join(domain_knowledge.sensitive_areas[:3])}...")
    
    def add_successful_prompt(
        self,
        prompt: str,
        response: str,
        risk_category: int,
        reward_points: int,
        turn_number: int,
        phase: str,
        generation_method: str
    ) -> None:
        """
        Add a successful attack prompt to temporary memory (risk >= 3).
        
        Args:
            prompt: The attack prompt
            response: Chatbot response
            risk_category: Risk level (1-5)
            reward_points: Points earned
            turn_number: Turn number in current run
            phase: Attack phase (e.g., "reconnaissance")
            generation_method: How prompt was generated
        """
        if risk_category < 3:
            return  # Only store medium+ risk prompts
        
        successful_prompt = SuccessfulPrompt(
            prompt=prompt,
            response=response,
            risk_category=risk_category,
            reward_points=reward_points,
            turn_number=turn_number,
            run_number=self.current_run,
            attack_type=self.attack_type,
            phase=phase,
            timestamp=datetime.utcnow().isoformat(),
            generation_method=generation_method
        )
        
        self.successful_prompts.append(successful_prompt)
        self.run_rewards[self.current_run] += reward_points
        self.total_session_reward += reward_points
        
        print(f"\n✅ SUCCESSFUL PROMPT STORED (Risk: {risk_category}, Reward: {reward_points})")
        print(f"   Phase: {phase} | Method: {generation_method}")
        print(f"   Run {self.current_run} Total: {self.run_rewards[self.current_run]} points")
    
    def get_successful_prompts_for_evolution(self, from_run: Optional[int] = None) -> List[SuccessfulPrompt]:
        """
        Get successful prompts for evolution in next run.
        
        Args:
            from_run: Filter by specific run number (None = all runs)
        
        Returns:
            List of successful prompts
        """
        if from_run is not None:
            return [p for p in self.successful_prompts if p.run_number == from_run]
        return self.successful_prompts
    
    def get_top_prompts(self, top_n: int = 10) -> List[SuccessfulPrompt]:
        """
        Get top N successful prompts by reward points.
        
        Args:
            top_n: Number of top prompts to return
        
        Returns:
            List of top prompts sorted by reward
        """
        return sorted(
            self.successful_prompts,
            key=lambda p: p.reward_points,
            reverse=True
        )[:top_n]
    
    def calculate_total_rewards(self) -> Dict[str, Any]:
        """
        Calculate comprehensive reward statistics.
        
        Returns:
            Dictionary with reward breakdown
        """
        return {
            "total_session_reward": self.total_session_reward,
            "run_1_reward": self.run_rewards[1],
            "run_2_reward": self.run_rewards[2],
            "run_3_reward": self.run_rewards[3],
            "successful_prompt_count": len(self.successful_prompts),
            "average_reward_per_prompt": (
                self.total_session_reward / len(self.successful_prompts)
                if self.successful_prompts else 0
            ),
            "highest_risk_achieved": max(
                (p.risk_category for p in self.successful_prompts),
                default=0
            )
        }
    
    def finalize_run(self) -> Dict[str, Any]:
        """
        Finalize current run and prepare summary.
        
        Returns:
            Run summary statistics
        """
        run_prompts = [p for p in self.successful_prompts if p.run_number == self.current_run]
        
        summary = {
            "run_number": self.current_run,
            "attack_type": self.attack_type,
            "successful_prompts": len(run_prompts),
            "total_reward": self.run_rewards[self.current_run],
            "avg_risk": sum(p.risk_category for p in run_prompts) / len(run_prompts) if run_prompts else 0,
            "highest_risk": max((p.risk_category for p in run_prompts), default=0),
            "generation_methods": self._count_generation_methods(run_prompts),
            "phase_distribution": self._count_phases(run_prompts)
        }
        
        self.evolution_history.append(summary)
        
        print(f"\n{'='*80}")
        print(f"📊 RUN {self.current_run} SUMMARY")
        print(f"{'='*80}")
        print(f"Successful Prompts: {summary['successful_prompts']}")
        print(f"Total Reward: {summary['total_reward']} points")
        print(f"Average Risk: {summary['avg_risk']:.2f}")
        print(f"Highest Risk: {summary['highest_risk']}")
        print(f"{'='*80}\n")
        
        return summary
    
    def _count_generation_methods(self, prompts: List[SuccessfulPrompt]) -> Dict[str, int]:
        """Count prompts by generation method."""
        counts = {}
        for prompt in prompts:
            method = prompt.generation_method
            counts[method] = counts.get(method, 0) + 1
        return counts
    
    def _count_phases(self, prompts: List[SuccessfulPrompt]) -> Dict[str, int]:
        """Count prompts by attack phase."""
        counts = {}
        for prompt in prompts:
            phase = prompt.phase
            counts[phase] = counts.get(phase, 0) + 1
        return counts
    
    def export_state(self) -> Dict[str, Any]:
        """
        Export complete state for persistence or analysis.
        
        Returns:
            Complete state dictionary
        """
        return {
            "session_id": self.session_id,
            "session_start_time": self.session_start_time,
            "attack_type": self.attack_type,
            "current_run": self.current_run,
            "domain_knowledge": asdict(self.domain_knowledge) if self.domain_knowledge else None,
            "successful_prompts": [asdict(p) for p in self.successful_prompts],
            "run_rewards": self.run_rewards,
            "total_session_reward": self.total_session_reward,
            "evolution_history": self.evolution_history,
            "reward_statistics": self.calculate_total_rewards()
        }
    
    def save_to_file(self, filepath: str) -> None:
        """
        Save state to JSON file.
        
        Args:
            filepath: Path to save state file
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.export_state(), f, indent=2, ensure_ascii=False)
        print(f"💾 State saved to: {filepath}")
