"""axiomguard: declare and check invariants ("axioms") on data and function outputs."""
from .core import Axiom, Result, Report, Verifier, AxiomViolation
from .decorators import precondition, postcondition
from . import checks

__all__ = ["Axiom", "Result", "Report", "Verifier", "AxiomViolation",
           "precondition", "postcondition", "checks"]
__version__ = "0.1.0"
