# Agent Notes: Code Style & Design Principles

## Key Takeaways from Phase 1

### Minimalism First
- Strip away unnecessary abstractions
- Models represent **state**, not transport/protocol concerns
- Only create something if it has clear, irreducible value
- Question: "Do we really need this?" before adding complexity

### Flexibility Over Rigidity
- Use flexible types (`dict[str, Link]`) instead of rigid classes with predefined fields
- Allow extension without modification
- Let frameworks handle what they're designed for (FastAPI for request/response shaping)
- Don't lock into specific structures prematurely

### Semantic Clarity
- No "clever" naming conventions (avoid unnecessary underscores)
- Field names should match their conceptual purpose directly
- If it contains links, call it `links`, not `_links`
- Use type aliases (`NodeId`) to make domain concepts explicit

### Separation of Concerns
- **Models** = domain state only
- **Request/response shaping** = framework's responsibility
- **Operations** = described by endpoints, not node metadata
- **HTTP methods** = implicit from endpoints, not in link data

### Code Organization
- **Absolute imports only**: `from tree.X import Y`
- No relative imports: `from ..X import Y`
- Makes dependencies explicit and refactoring safer

### Type Safety
- Create type aliases for domain concepts
- Enables safe refactoring (change in one place)
- Provides validation at domain boundaries
- Documents intent through the type system

### Testing Philosophy
- Test validation and edge cases, not implementation details
- Cover boundary conditions
- Ensure field constraints work as expected
- Comprehensive coverage on what matters

## Design Philosophy

**Essential Complexity Only**

Consistently push toward:
- **Less** boilerplate
- **More** flexibility
- **Clearer** semantics
- **Simpler** mental models

The code should do exactly what's needed, nothing more, and make its intent obvious to readers.

## Anti-Patterns to Avoid

1. **Over-engineering**: Creating wrapper classes when dicts suffice
2. **Premature abstraction**: Rigid schemas before understanding needs
3. **Framework fighting**: Duplicating what FastAPI already provides
4. **Data pollution**: Adding metadata that belongs in other layers
5. **Relative imports**: Hiding dependencies behind `..`
6. **Aesthetic prefixes**: Underscores that don't add semantic value

## Phase 1 Final State

**4 clean models:**
- `Node` - Core tree state
- `Context` + `Breadcrumb` - Zipper position
- `Link` - Navigation (href + title only)
- `NodeId` - Type-safe ID alias

**Infrastructure:**
- 52 tests with 100% model coverage
- Pre-commit hooks (ruff, mypy, general checks)
- GitHub Actions CI
- Makefile for common tasks
- Strict type checking enabled
