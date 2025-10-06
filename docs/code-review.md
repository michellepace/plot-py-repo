You are tasked with conducting a comprehensive code review of staged Python files completed by a junior developer. You need to evaluate whether these changes should be merged via pull request or reverted entirely.

Here are the staged files to evaluate:

<files>
ALL STAGED FILES `*.py`
</files>

## Context

All basic quality checks have passed:

- Ruff linting and formatting: ✅
- Pyright type checking: ✅
- All 47 tests passing: ✅

Your job is to evaluate the **value and architectural quality** of these changes against our design principles.

## Code Design Principles & Standards

**TDD-Driven Design**: Write tests first - this naturally creates better architecture:

- **Pure functions preferred**: no side effects in business logic, easier to test
- **Clear module boundaries**: easier to test and understand  
- **Single responsibility**: complex functions are hard to test

**Key Architecture Guidelines**:

- **Layer separation**: CLI → business logic → I/O
- **One module, one purpose**: Each `.py` file has a clear, focused role
- **Handle errors at boundaries**: Catch exceptions in CLI layer, not business logic
- **Type hints required**: All function signatures need type annotations
- **Descriptive naming**: Functions/variables indicate purpose clearly and consistently
- **Use pathlib**: Always use `pathlib` (not `os`) for file operations

**TDD Implementation**:

- Use pytest's `tmp_path` fixture to avoid creating test files
- Avoid mocks as they introduce unnecessary complexity
- For each test target one behavior with clear failure point
- Use focused test names that describe what's being tested

**Code Quality Standards**:

- **Naming is important!**: Function and variable names chosen to self-document clarity
- **Docstrings & Comments**: Concise, clear, fresh ➜ important for LLM comprehension

## Evaluation Framework

### 1. What Has Changed Assessment

Systematically identify what functionality has been:

- **Removed**: What existing features/capabilities were taken away?
- **Changed**: What existing functionality was modified and how?
- **Added**: What new features/capabilities were introduced?

For each change, evaluate:

- Does this add value to the user of this tool?
- Does this provide convenience for contributing engineers?
- Has there been an architectural change - beneficial or detrimental?

### 2. Quality of Change Assessment

Evaluate each file in detail against the design principles above. Look for:

- Adherence to TDD principles and architecture patterns
- Code organization and module boundaries
- Error handling patterns
- Type annotation completeness
- Naming clarity and consistency
- Use of appropriate libraries (pathlib vs os, etc.)
- Test quality and coverage of new functionality

## Required Output Format

Structure your evaluation as a detailed report with:

**Introduction**: Brief overview of the scope of changes

**What Has Changed Analysis**: Detailed prose analysis of functionality changes with clear categorization

**Quality Assessment**: File-by-file evaluation against design principles

**Four Required Tables**:

1. **Files Changed Summary** - File name, type of change, brief description
2. **Value Assessment** - Feature/change, user value (High/Medium/Low), engineering convenience (High/Medium/Low)  
3. **Design Principles Compliance** - Principle, compliance score (✅/⚠️/❌), notes
4. **Risk Assessment** - Risk area, severity (High/Medium/Low), mitigation needed

**Final Recommendation**: Clear decision with supporting rationale

Use emojis strategically for readability and organize content with appropriate headers and bullet points where beneficial.

Your final output should provide a definitive recommendation on whether to **raise a PR** or **revert all files**, along with any additional actions required. Focus on architectural soundness, adherence to principles, and genuine value delivery rather than just syntactic correctness.
