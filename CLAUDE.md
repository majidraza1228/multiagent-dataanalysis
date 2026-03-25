# Code Review Guidelines

## Focus Areas
- Security vulnerabilities (SQL injection, XSS, auth bypass)
- Performance issues in data processing pipelines
- Error handling in API routes
- Test coverage for critical paths

## Project Context
- This is a Python FastAPI project with pandas data analysis
- We use pytest for testing
- All eval framework code must maintain backward compatibility

## Conventions
- Always use type hints
- Database queries must use parameterized statements
- API routes must have proper error handling
