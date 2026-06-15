---
name: django-expert
description: Expert Django backend development guidance. Use when creating Django models, views, serializers, or APIs; debugging ORM queries or migrations; optimizing database performance; implementing authentication; writing tests; or working with Django REST Framework. Follows Django best practices and modern patterns.
---

# Django Expert

## Overview

This skill provides expert guidance for Django backend development with comprehensive coverage of models, views, Django REST Framework, forms, authentication, testing, and performance optimization. It follows official Django best practices and modern Python conventions to help you build robust, maintainable applications.

**Key Capabilities:**
- Model design with optimal ORM patterns
- View implementation (FBV, CBV, DRF viewsets)
- Django REST Framework API development
- Query optimization and performance tuning
- Authentication and permissions
- Testing strategies and patterns
- Security best practices

## When to Use

Invoke this skill when you encounter these triggers:

**Model & Database Work:**
- "Create a Django model for..."
- "Optimize this queryset/database query"
- "Generate migrations for..."
- "Design database schema for..."
- "Fix N+1 query problem"

**View & API Development:**
- "Create an API endpoint for..."
- "Build a Django view that..."
- "Implement DRF serializer/viewset"
- "Add filtering/pagination to API"

**Authentication & Security:**
- "Implement authentication/permissions"
- "Create custom user model"
- "Secure this endpoint/view"

**Testing & Quality:**
- "Write tests for this Django app"
- "Debug this Django error/issue"
- "Review Django code for issues"

**Clean Code & Refactoring:**
- "Refactor this for clean code"
- "Apply SOLID principles to..."
- "Improve readability/maintainability of this view/model/serializer"
- "This function is too long, break it up"
- "Move this logic out of the view into a service"

**Performance & Optimization:**
- "This Django view is slow"
- "Optimize database queries"
- "Add caching to..."

**Production Deployment:**
- "Deploy Django to production"
- "Configure Django for production"
- "Set up HTTPS/SSL for Django"
- "Production settings checklist"
- "Configure production database/cache"

## Instructions

Follow this workflow when handling Django development requests:

### 1. Analyze the Request and Gather Context

**Identify the task type:**
- Model design (database schema, relationships, migrations)
- View/API development (FBV, CBV, DRF viewsets, serializers)
- Query optimization (N+1 problems, database performance)
- Authentication/permissions (user models, access control)
- Testing (unit tests, integration tests, fixtures)
- Security review (CSRF, XSS, SQL injection, permissions)
- Production deployment (settings, HTTPS, database, caching, monitoring)
- Template rendering (Django templates, context processors)

**Leverage available context:**
- If `django-ai-boost` MCP server is available, use it to understand project structure and existing patterns
- Read relevant existing code to understand conventions
- Check Django version for compatibility considerations

### 2. Load Relevant Reference Documentation

Based on the task type, reference the appropriate bundled documentation:

- **Models/ORM work** -> `references/models-and-orm.md`
  - Model design patterns and field choices
  - Relationship configurations (ForeignKey, ManyToMany)
  - Custom managers and QuerySet methods
  - Migration strategies

- **View/API development** -> `references/views-and-urls.md` + `references/drf-guidelines.md`
  - FBV vs CBV decision criteria
  - DRF serializers, viewsets, and routers
  - URL configuration patterns
  - Middleware and request/response handling

- **Performance issues** -> `references/performance-optimization.md`
  - Query optimization techniques (select_related, prefetch_related)
  - Caching strategies (Redis, Memcached, database caching)
  - Database indexing and query profiling
  - Connection pooling and async patterns

- **Production deployment** -> `references/production-deployment.md`
  - Critical settings (DEBUG, SECRET_KEY, ALLOWED_HOSTS)
  - HTTPS and SSL/TLS configuration
  - Database and cache configuration
  - Static/media file serving
  - Error monitoring and logging
  - Deployment process and health checks

- **Security concerns** -> `references/security-checklist.md`
  - CSRF/XSS/SQL injection prevention
  - Authentication and authorization patterns
  - Secure configuration practices
  - Input validation and sanitization

- **Testing tasks** -> `references/testing-strategies.md`
  - Test structure and organization
  - Fixtures and factories
  - Mocking external dependencies
  - Coverage and CI/CD integration

- **Clean code / refactoring** -> `references/clean-code.md`
  - Naming conventions and readability
  - Function/class size and single responsibility
  - SOLID principles applied to Django (thin views, service layer)
  - Avoiding duplication and magic values
  - Type hints and docstring conventions

### 3. Implement Following Django Best Practices

**Architecture Application (Service Layer):**
You MUST respect the strict dependency flow of the project's architecture:
1.  **Router/URLs:** Routes HTTP requests to the appropriate View/ViewSet.
2.  **Views/Serializers:** Handle HTTP request/response formatting, payload validation (via DRF), and permissions. They MUST NOT contain business logic.
3.  **Service Layer (`services.py`):** Contains the core business logic. Views depend on Services. Services depend on Models.
4.  **Models/ORM (`models.py` / `managers.py`):** Handle data definition and database interactions.

**Clean code standards** (see `references/clean-code.md` for full guidance):
- Follow PEP 8 and Django coding style; format with `black`/`ruff`
- **MUST:** Keep functions/classes small and focused on a Single Responsibility (SRP). Extract helpers for repeated logic (DRY).
- **MUST:** Keep views and serializers "thin". Business logic MUST be placed in `services.py` or custom model managers.
- **MUST:** Use intention-revealing names for variables, functions, and classes. Avoid abbreviations.
- **MUST:** Avoid magic numbers/strings. Extract them to constants, `TextChoices`, or `IntegerChoices`.
- **MUST:** Document your code. Write clear Docstrings for all classes, public API methods, and services describing their purpose, args, and returns.
- **MUST:** Handle errors gracefully with specific exceptions; never use bare `except:`.
- **SHOULD:** Follow PEP 8 and Django coding style; format code mentally assuming `black`/`ruff` will be used.
- **SHOULD:** Add Python type hints (`->`, `str`, `int`, etc.) for non-trivial functions and public APIs to improve developer experience.
- **SHOULD:** Avoid deep nesting. Prefer early returns / guard clauses over nested if/else statements.

**Django-specific patterns:**
- Use Django forms/serializers for validation
- Use Django's built-in security features (CSRF tokens, auth decorators)
**Django-specific patterns:**
- **MUST:** Use `select_related()` for FK/OneToOne and `prefetch_related()` for reverse FK/M2M to avoid N+1 query problems.
- **SHOULD:** Leverage class-based views and mixins for code reuse when applicable.
- **MUST:** Never edit applied migrations manually; follow standard workflow.

**API development (DRF):**
- Use ModelSerializer for standard CRUD operations
- Implement proper pagination and filtering
- Use appropriate permission classes
- Follow RESTful conventions for endpoints
- Version APIs when making breaking changes

### 4. Validate and Test

Before presenting the solution:

**Code review:**
- Check for N+1 query problems (use Django Debug Toolbar mentally)
- Verify proper error handling and edge cases
- Ensure security best practices are followed
- Confirm migrations are clean and reversible
- Check clean code: naming, function size, duplication, magic values (see `references/clean-code.md`)

**Testing considerations:**
- Suggest or write appropriate tests for new functionality
- Verify test coverage for critical paths
- Check that fixtures/factories are maintainable

**Performance check:**
- Review database queries for efficiency
- Consider caching opportunities
- Verify proper use of database indexes

## Bundled Resources

**references/** - Comprehensive Django documentation loaded into context as needed

These reference files provide detailed guidance beyond this SKILL.md overview:

- **`references/models-and-orm.md`** (~11k words)
  - Model field types and best practices
  - Relationship configurations (ForeignKey, OneToOne, ManyToMany)
  - Custom managers and QuerySet methods
  - Migration patterns and common pitfalls
  - Database-level constraints and indexes

- **`references/views-and-urls.md`** (~17k words)
  - Function-based vs class-based view trade-offs
  - CBV mixins and inheritance patterns
  - URL routing and reverse resolution
  - Middleware implementation
  - Request/response lifecycle

- **`references/drf-guidelines.md`** (~18k words)
  - Serializer patterns (ModelSerializer, nested serializers)
  - ViewSet and router configurations
  - Pagination, filtering, and search
  - Authentication and permission classes
  - API versioning strategies
  - Performance optimization for APIs

- **`references/testing-strategies.md`** (~18k words)
  - Test organization and structure
  - Factory patterns vs fixtures
  - Testing views, models, and serializers
  - Mocking external services
  - Test database optimization
  - CI/CD integration

- **`references/security-checklist.md`** (~12k words)
  - CSRF protection implementation
  - XSS prevention techniques
  - SQL injection defense
  - Authentication best practices
  - Permission and authorization patterns
  - Secure settings configuration

- **`references/performance-optimization.md`** (~14k words)
  - Query optimization (select_related, prefetch_related, only, defer)
  - Database indexing strategies
  - Caching layers (Redis, Memcached, database cache)
  - Database connection pooling
  - Profiling and monitoring tools
  - Async views and background tasks

- **`references/production-deployment.md`** (~20k words)
  - Critical settings (DEBUG, SECRET_KEY, ALLOWED_HOSTS)
  - Database configuration and connection pooling
  - HTTPS/SSL configuration and security headers
  - Static and media file serving
  - Caching with Redis/Memcached
  - Email configuration for production
  - Error monitoring with Sentry
  - Logging and health checks
  - Zero-downtime deployment strategies

- **`references/examples.md`** - Practical implementation examples
  - Model design with custom managers
  - N+1 query optimization
  - DRF API endpoint implementation
  - Writing Django tests

- **`references/clean-code.md`** - Clean code principles for Django/Python
  - Naming conventions and readability
  - Function and class size, single responsibility
  - SOLID principles applied to Django (service layer pattern)
  - Avoiding duplication and magic values
  - Type hints, docstrings, and error handling

## Additional Notes

**Django Version Compatibility:**
- Consider LTS releases (4.2, 5.2) for production
- Check deprecation warnings when upgrading
- Use `django-upgrade` tool for automated migration

**Common Pitfalls to Avoid:**
- Circular imports (use lazy references)
- Missing `related_name` on relationships
- Forgetting database indexes on frequently queried fields
- Using `get()` without exception handling
- N+1 queries in templates and serializers

### 5. Quality Checklist (Final Output)

At the end of every response, you must provide a concise quality checklist using ✅ (Green/Pass) or ❌ (Red/Fail or Needs Attention) evaluating the provided solution against these core requirements:

- ✅/❌ **MUST: Clean Code & SRP:** Functions/classes are small, single-purpose, and use descriptive names without magic numbers.
- ✅/❌ **MUST: Architecture (Service Layer):** Business logic is strictly isolated in services, keeping views/serializers thin.
- ✅/❌ **MUST: Performance & ORM:** Avoids N+1 queries (uses `select_related`/`prefetch_related` appropriately).
- ✅/❌ **MUST: Security & Validation:** Inputs are validated and secure access controls/permissions are applied.
- ✅/❌ **SHOULD: Documentation & Typing:** Code includes clear Docstrings and appropriate Python type hints.