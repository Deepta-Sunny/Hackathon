"""
MD File Parser for Architecture Context Extraction

Reads chatbot architecture documentation from MD files and extracts
relevant context for domain detection and prompt molding.
"""

import os
from pathlib import Path
from typing import Optional


class ArchitectureLoader:
    """Loads and parses architecture documentation from MD files."""
    
    def __init__(self, md_file_path: Optional[str] = None):
        """
        Initialize the architecture loader.
        
        Args:
            md_file_path: Path to the MD file containing architecture documentation.
                         If not provided, looks for MD.txt in the current directory.
        """
        self.md_file_path = md_file_path or self._find_default_md_file()
        self.architecture_content = ""
    
    def _find_default_md_file(self) -> str:
        """Find the default MD file in the project."""
        # Check for MD.txt in current directory
        current_dir = Path(__file__).parent
        default_paths = [
            current_dir / "MD.txt",
            current_dir / "architecture.md",
            current_dir / "chatbot_architecture.md"
        ]
        
        for path in default_paths:
            if path.exists():
                return str(path)
        
        raise FileNotFoundError(
            "No architecture MD file found. Please provide md_file_path or create MD.txt"
        )
    
    def load_architecture(self) -> str:
        """
        Load architecture content from MD file.
        
        Returns:
            String containing the full architecture documentation
        """
        try:
            with open(self.md_file_path, 'r', encoding='utf-8') as f:
                self.architecture_content = f.read()
            
            print(f"[✓] Loaded architecture from: {self.md_file_path}")
            print(f"[✓] Architecture content: {len(self.architecture_content)} characters")
            
            return self.architecture_content
        
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Architecture file not found: {self.md_file_path}"
            )
        except Exception as e:
            raise Exception(f"Error loading architecture file: {e}")
    
    async def load_and_detect_domain(self, molding_engine) -> tuple[str, str]:
        """
        Load architecture and detect domain using molding engine.
        
        Args:
            molding_engine: PromptMoldingEngine instance for domain detection
            
        Returns:
            Tuple of (architecture_content, detected_domain)
        """
        # Load architecture content
        architecture = self.load_architecture()
        
        # Detect domain from architecture
        print(f"[+] Detecting domain from architecture documentation...")
        detected_domain = await molding_engine.detect_domain(architecture)
        
        return architecture, detected_domain
    
    def get_summary(self, max_chars: int = 2000) -> str:
        """
        Get a summary of the architecture for quick review.
        
        Args:
            max_chars: Maximum characters to return
            
        Returns:
            Truncated architecture summary
        """
        if not self.architecture_content:
            self.load_architecture()
        
        if len(self.architecture_content) <= max_chars:
            return self.architecture_content
        
        # Return first max_chars with ellipsis
        return self.architecture_content[:max_chars] + "\n\n[... truncated ...]"


def load_architecture_from_file(file_path: str) -> str:
    """
    Convenience function to load architecture from a file.
    
    Args:
        file_path: Path to the MD file
        
    Returns:
        Architecture content as string
    """
    loader = ArchitectureLoader(file_path)
    return loader.load_architecture()
