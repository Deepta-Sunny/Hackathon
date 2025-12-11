# Attack Strategies

This directory contains categorized attack strategies for AI chatbot red teaming.

## 📁 Structure

```
attack_strategies/
├── __init__.py              # Module exports
├── base_strategy.py         # Abstract base class
├── orchestrator.py          # Strategy coordination
├── reconnaissance.py        # Phase 1: Information gathering
├── trust_building.py        # Phase 2: Rapport establishment  
├── boundary_testing.py      # Phase 3: Security probing
└── exploitation.py          # Phase 4: Advanced attacks
```

## 🎯 Attack Phases

### Phase 1: Reconnaissance (Turns 1-6)
**Objective**: Map system components and test basic functionality

**Strategies**:
- `ReconnaissanceAttacks`: General information gathering
- `SafeReconnaissanceAttacks`: Non-aggressive testing for content-filtered environments

**Example Attacks**:
- Component discovery
- Capability mapping
- Architecture probing

### Phase 2: Trust Building (Turns 7-12)
**Objective**: Establish context and build rapport

**Strategies**:
- `TrustBuildingAttacks`: Story-based scenarios
- `ContextualTrustAttacks`: Multi-turn context manipulation

**Example Attacks**:
- Role establishment (instructor, researcher, auditor)
- Legitimate-seeming scenarios
- Gradual context escalation

### Phase 3: Boundary Testing (Turns 13-19)
**Objective**: Probe security measures with subtle exploits

**Strategies**:
- `BoundaryTestingAttacks`: General security probing
- `EncodingBypassAttacks`: Character encoding techniques
- `PromptInjectionAttacks`: Instruction manipulation

**Example Attacks**:
- Leetspeak and character substitution
- Guardrail bypass attempts
- Multi-vector injection

### Phase 4: Exploitation (Turns 20-25)
**Objective**: Execute sophisticated multi-vector attacks

**Strategies**:
- `ExploitationAttacks`: SQL injection, command injection
- `ChainedExploitationAttacks`: Combined attack vectors
- `DataExfiltrationAttacks`: Information extraction
- `PrivilegeEscalationAttacks`: Access elevation

**Example Attacks**:
- SQL injection payloads
- API exploitation
- Privilege escalation
- Data exfiltration

## 🔧 Usage

### Using the Orchestrator

```python
from attack_strategies.orchestrator import AttackStrategyOrchestrator

# Standard mode
orchestrator = AttackStrategyOrchestrator(use_safe_mode=False)
attack_plan = orchestrator.generate_attack_plan(total_turns=25)

# Safe mode (for content-filtered environments)
safe_orchestrator = AttackStrategyOrchestrator(use_safe_mode=True)
safe_plan = safe_orchestrator.generate_attack_plan(total_turns=25)

# Get description
print(orchestrator.describe_attack_plan())
```

### Using Individual Strategies

```python
from attack_strategies.reconnaissance import ReconnaissanceAttacks
from attack_strategies.exploitation import DataExfiltrationAttacks

# Get prompts from specific strategy
recon = ReconnaissanceAttacks()
prompts = recon.get_prompts()

# Create attack prompt objects
attack_prompts = recon.create_attack_prompts(start_turn=1)

# Multiple strategies
exfiltration = DataExfiltrationAttacks()
all_prompts = recon.get_prompts() + exfiltration.get_prompts()
```

### Creating Custom Strategies

```python
from attack_strategies.base_strategy import BaseAttackStrategy
from typing import List

class MyCustomAttacks(BaseAttackStrategy):
    def __init__(self):
        super().__init__()
        self.technique_name = "my_custom_attack"
        self.target_nodes = ["target1", "target2"]
        self.escalation_phase = "Phase X: Custom"
    
    def get_description(self) -> str:
        return "Description of custom attack"
    
    def get_prompts(self) -> List[str]:
        return [
            "Custom prompt 1",
            "Custom prompt 2",
            # ... more prompts
        ]
```

## 🛡️ Safe Mode

Safe mode is automatically activated when:
- Azure content filters block attack generation
- Multiple content filter violations detected (>5)
- Explicitly requested via `use_safe_mode=True`

Safe mode uses:
- Less aggressive prompts
- Focuses on legitimate functionality testing
- Avoids triggers for content safety policies

## 📊 Attack Plan Structure

The orchestrator automatically distributes 25 turns across phases:

| Phase | Turns | Strategy Focus |
|-------|-------|---------------|
| 1 | 1-6 | Reconnaissance |
| 2 | 7-12 | Trust Building |
| 3 | 13-19 | Boundary Testing |
| 4 | 20-25 | Exploitation |

## 🔄 Integration with Main System

The attack strategies are integrated into the main orchestrator:

1. **Primary Method**: LLM generates architecture-aware attacks
2. **Fallback Method**: Strategy library provides pre-defined attacks
3. **Safe Mode**: Activated when content filters block aggressive attacks

## 📝 Adding New Strategies

1. Create new file in `attack_strategies/`
2. Extend `BaseAttackStrategy`
3. Implement `get_prompts()` and `get_description()`
4. Add to `__init__.py` exports
5. Update `orchestrator.py` to include in attack plan

## ⚠️ Important Notes

- Strategies are designed for **authorized red teaming only**
- Always obtain proper authorization before testing
- Some attacks may trigger Azure OpenAI content filters
- Use safe mode for compliance-sensitive environments
- Results should be reviewed by security professionals

## 📚 References

- [MITRE ATT&CK for LLMs](https://atlas.mitre.org/)
- [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [Azure AI Content Safety](https://azure.microsoft.com/en-us/products/ai-services/ai-content-safety/)
