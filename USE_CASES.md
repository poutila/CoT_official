# Chain-of-Thought (CoT) Use Cases in Software Development

## Table of Contents

1. [Code Review & Analysis](#code-review--analysis)
2. [Refactoring & Architecture](#refactoring--architecture)
3. [Debugging & Troubleshooting](#debugging--troubleshooting)
4. [API Design & Changes](#api-design--changes)
5. [Security Analysis](#security-analysis)
6. [Performance Optimization](#performance-optimization)
7. [Documentation Generation](#documentation-generation)
8. [Dependency Management](#dependency-management)
9. [Test Generation & Coverage](#test-generation--coverage)
10. [CI/CD Pipeline Decisions](#cicd-pipeline-decisions)
11. [Code Generation](#code-generation)
12. [Migration Planning](#migration-planning)

## Code Review & Analysis

### Use Case: Identifying Code Smells

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

### Decision: Refactor the UserService class due to Single Responsibility Principle violation

#### Risk Assessment:
- **Change Type**: Refactor class structure
- **Risk Level**: Medium
- **Impact Scope**: Module (auth package)
- **Reversibility**: Moderate effort

#### Evidence Collection:
1. **Source**: `user_service.py:45-250`
   **Quote**: "class UserService: # Handles user CRUD, auth, emails, logging"
   **Relevance**: Comment indicates multiple responsibilities
   **Timestamp**: Modified: 2024-01-25T10:00:00Z
   **Freshness**: current (0.99)

2. **Source**: `user_service.py:150-180`
   **Quote**: "def send_welcome_email(self, user): ..."
   **Relevance**: Email functionality should be separate service

3. **Source**: `SOLID_principles.md:12`
   **Quote**: "Each class should have one reason to change"
   **Relevance**: Architecture guideline mandates separation

#### Analysis:
- **Primary rationale**: Class handles 4 distinct responsibilities
- **Alternative considered**: Keep as-is with better documentation
- **Alternative rejected because**: Violates documented architecture principles

#### Action:
→ Therefore, I will: Split UserService into UserCRUD, AuthService, EmailService, and UserLogger
```

### Use Case: Detecting Potential Bugs

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

### Decision: Fix potential null pointer exception in payment processor

#### Risk Assessment:
- **Change Type**: Add defensive programming check
- **Risk Level**: High (payment processing)
- **Impact Scope**: Critical business logic
- **Reversibility**: Easy

#### Evidence Collection:
1. **Source**: `payment_processor.py:67`
   **Quote**: "amount = order.items[0].price * order.items[0].quantity"
   **Relevance**: Assumes items array is never empty

2. **Source**: `order_service.py:34`
   **Quote**: "return Order(items=[])"  # Empty orders allowed
   **Relevance**: Proves empty orders are possible

3. **Source**: `crash_log_2024-01-20.txt:45`
   **Quote**: "IndexError: list index out of range at payment_processor.py:67"
   **Relevance**: Production crash confirms the issue

#### Action:
→ Therefore, I will: Add validation to check if order.items is empty before accessing
```

## Refactoring & Architecture

### Use Case: Microservice Extraction

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

### Decision: Extract notification system into separate microservice

#### Risk Assessment:
- **Change Type**: Architectural restructuring
- **Risk Level**: Critical
- **Impact Scope**: System-wide
- **Reversibility**: Difficult

#### Evidence Collection:
1. **Source**: `system_metrics.json:234`
   **Quote**: "notification_queue_size: 45000, avg_delay: 12min"
   **Relevance**: Performance bottleneck identified

2. **Source**: `architecture_review.md:89`
   **Quote**: "Notification system causes 70% of monolith scaling events"
   **Relevance**: Scaling issues documented

3. **Source**: `team_roadmap.md:15`
   **Quote**: "Q2 Goal: Improve notification delivery to <1min"
   **Relevance**: Business requirement for improvement

4. **Source**: `notification_module.py:1-500`
   **Quote**: "# No dependencies on core business logic"
   **Relevance**: Clean separation already exists

#### Analysis:
- **Primary rationale**: Performance + scaling + clean boundaries
- **Alternative considered**: Optimize within monolith
- **Alternative rejected because**: Metrics show optimization insufficient

#### Action:
→ Therefore, I will: Create notification-service with dedicated queue and workers
```

### Use Case: Design Pattern Implementation

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

### Decision: Implement Repository pattern for data access layer

#### Risk Assessment:
- **Change Type**: Add abstraction layer
- **Risk Level**: Medium
- **Impact Scope**: All database operations
- **Reversibility**: Moderate

#### Evidence Collection:
1. **Source**: `user_controller.py:45-67`
   **Quote**: "users = db.execute('SELECT * FROM users WHERE ...')"
   **Relevance**: Direct SQL in controllers

2. **Source**: `product_controller.py:89-102`
   **Quote**: "products = db.execute('SELECT * FROM products ...')"
   **Relevance**: Pattern repeated across controllers

3. **Source**: `testing_guidelines.md:23`
   **Quote**: "Controllers must be testable without database"
   **Relevance**: Current structure prevents unit testing

#### Action:
→ Therefore, I will: Create UserRepository, ProductRepository with interfaces
```

## Debugging & Troubleshooting

### Use Case: Memory Leak Investigation

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

### Decision: Fix memory leak caused by event listener accumulation

#### Risk Assessment:
- **Change Type**: Fix resource cleanup
- **Risk Level**: High
- **Impact Scope**: Application stability
- **Reversibility**: Easy

#### Evidence Collection:
1. **Source**: `heap_dump_analysis.txt:156`
   **Quote**: "EventEmitter: 47,293 listeners for 'data' event"
   **Relevance**: Abnormal listener count

2. **Source**: `websocket_handler.py:78`
   **Quote**: "socket.on('data', self.handle_data)"
   **Relevance**: Listener added without cleanup

3. **Source**: `websocket_handler.py:95-120`
   **Quote**: "def disconnect(self): socket.close()"
   **Relevance**: No listener removal on disconnect

#### Analysis:
- **Primary rationale**: Listeners accumulate without cleanup
- **Alternative considered**: Increase memory limits
- **Alternative rejected because**: Doesn't fix root cause

#### Action:
→ Therefore, I will: Add socket.off('data', self.handle_data) in disconnect()
```

### Use Case: Race Condition Detection

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

### Decision: Add mutex lock to prevent race condition in inventory update

#### Risk Assessment:
- **Change Type**: Add synchronization
- **Risk Level**: Critical (data integrity)
- **Impact Scope**: Inventory management
- **Reversibility**: Easy

#### Evidence Collection:
1. **Source**: `inventory_service.py:234`
   **Quote**: "current = get_stock(item_id); set_stock(item_id, current - quantity)"
   **Relevance**: Non-atomic read-modify-write

2. **Source**: `error_log_2024-01-25.log:567`
   **Quote**: "Stock went negative: item_id=123, stock=-2"
   **Relevance**: Race condition symptoms in production

3. **Source**: `concurrency_test.py:45`
   **Quote**: "FAILED: Parallel updates cause negative inventory"
   **Relevance**: Test reproduces the issue

#### Action:
→ Therefore, I will: Wrap inventory updates in distributed lock using Redis
```

## API Design & Changes

### Use Case: Breaking API Change Assessment

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

### Decision: DEFERRED - Cannot safely change API response format

#### Risk Assessment:
- **Change Type**: Modify API response structure
- **Risk Level**: Critical
- **Impact Scope**: All API consumers
- **Reversibility**: Irreversible for live clients

#### Evidence Collection:
1. **Source**: `api_analytics.json:89`
   **Quote**: "active_api_consumers: 2,847"
   **Relevance**: Large number of potentially affected clients

2. **Source**: `api_changelog.md:12`
   **Quote**: "Last breaking change: 2019-03-15"
   **Relevance**: 5-year stability expectation established

#### Analysis:
⚠️ DEFERRED: Breaking change too risky
- Available evidence: Many active consumers, long stability period
- Missing evidence: Client version distribution, migration capability
- Recommended action: 
  1. Add new versioned endpoint (/v2/users)
  2. Deprecate old endpoint with 12-month notice
  3. Provide migration guide
```

### Use Case: GraphQL Schema Evolution

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

### Decision: Add nullable field to GraphQL schema for backward compatibility

#### Risk Assessment:
- **Change Type**: Schema extension
- **Risk Level**: Low
- **Impact Scope**: GraphQL API
- **Reversibility**: Cannot remove field later

#### Evidence Collection:
1. **Source**: `schema.graphql:45`
   **Quote**: "type User { id: ID!, name: String!, email: String! }"
   **Relevance**: Current schema structure

2. **Source**: `graphql_best_practices.md:23`
   **Quote**: "New fields must be nullable to maintain compatibility"
   **Relevance**: Documented schema evolution policy

3. **Source**: `feature_request.md:67`
   **Quote**: "Add user avatar URL to API response"
   **Relevance**: Business requirement

#### Action:
→ Therefore, I will: Add avatarUrl: String field (nullable) to User type
```

## Security Analysis

### Use Case: SQL Injection Prevention

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

### Decision: Replace string concatenation with parameterized queries

#### Risk Assessment:
- **Change Type**: Security fix
- **Risk Level**: Critical
- **Impact Scope**: All database queries
- **Reversibility**: Easy

#### Evidence Collection:
1. **Source**: `user_search.py:34`
   **Quote**: "query = f\"SELECT * FROM users WHERE name = '{search_term}'\""
   **Relevance**: Direct string interpolation in SQL

2. **Source**: `security_scan_report.json:156`
   **Quote**: "CRITICAL: SQL injection vulnerability in user_search.py:34"
   **Relevance**: Automated scan confirms vulnerability

3. **Source**: `OWASP_guidelines.md:12`
   **Quote**: "Always use parameterized queries or prepared statements"
   **Relevance**: Security standard requirement

4. **Source**: `penetration_test_2024.pdf:page-45`
   **Quote**: "Successfully injected '; DROP TABLE users;--"
   **Relevance**: Vulnerability exploited in pentest

#### Action:
→ Therefore, I will: Use cursor.execute(query, params) with parameter binding
```

### Use Case: Authentication Flow Analysis

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

### Decision: Implement refresh token rotation for enhanced security

#### Risk Assessment:
- **Change Type**: Auth flow modification
- **Risk Level**: High
- **Impact Scope**: All authenticated users
- **Reversibility**: Requires migration

#### Evidence Collection:
1. **Source**: `auth_service.py:89`
   **Quote**: "refresh_token = generate_token(); # Never expires"
   **Relevance**: Tokens don't rotate, security risk

2. **Source**: `security_audit_2024.md:34`
   **Quote**: "Recommendation: Implement refresh token rotation"
   **Relevance**: External audit finding

3. **Source**: `oauth2_spec.txt:567`
   **Quote**: "Refresh tokens SHOULD expire or be rotated"
   **Relevance**: Industry standard recommendation

#### Action:
→ Therefore, I will: Implement token rotation on each refresh with 7-day expiry
```

## Performance Optimization

### Use Case: Database Query Optimization

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

### Decision: Add composite index to improve query performance

#### Risk Assessment:
- **Change Type**: Database schema change
- **Risk Level**: Medium
- **Impact Scope**: Read performance
- **Reversibility**: Easy (drop index)

#### Evidence Collection:
1. **Source**: `slow_query_log.txt:234`
   **Quote**: "Query time: 8.5s - SELECT * FROM orders WHERE user_id=? AND status=?"
   **Relevance**: Slow query identified

2. **Source**: `explain_plan.txt:12`
   **Quote**: "Full table scan on orders (2.5M rows)"
   **Relevance**: Missing index causes full scan

3. **Source**: `db_metrics.json:89`
   **Quote**: "orders_by_user_status: called 50k times/day"
   **Relevance**: High-frequency query

#### Analysis:
- **Primary rationale**: 8.5s * 50k calls = 118 hours CPU/day
- **Alternative considered**: Query result caching
- **Alternative rejected because**: Data changes frequently

#### Action:
→ Therefore, I will: CREATE INDEX idx_orders_user_status ON orders(user_id, status)
```

### Use Case: Caching Strategy Implementation

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

### Decision: Implement Redis caching for product catalog API

#### Risk Assessment:
- **Change Type**: Add caching layer
- **Risk Level**: Medium
- **Impact Scope**: API performance
- **Reversibility**: Easy (disable cache)

#### Evidence Collection:
1. **Source**: `api_metrics.json:145`
   **Quote**: "GET /products avg_response_time: 850ms"
   **Relevance**: Slow response time

2. **Source**: `product_service.py:67-89`
   **Quote**: "products = db.query('SELECT * FROM products JOIN ...')"
   **Relevance**: Complex query with 5 table joins

3. **Source**: `product_update_log.csv:analysis`
   **Quote**: "Avg update frequency: 2.3 times/day per product"
   **Relevance**: Low change rate makes caching viable

4. **Source**: `sla_requirements.md:23`
   **Quote**: "API response time must be <200ms for 95th percentile"
   **Relevance**: Performance requirement not met

#### Action:
→ Therefore, I will: Add Redis cache with 1-hour TTL for product queries
```

## Documentation Generation

### Use Case: API Documentation from Code

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

### Decision: Generate OpenAPI spec from Flask route decorators

#### Risk Assessment:
- **Change Type**: Documentation generation
- **Risk Level**: Low
- **Impact Scope**: Developer experience
- **Reversibility**: Easy

#### Evidence Collection:
1. **Source**: `api_routes.py:45-67`
   **Quote**: "@app.route('/users/<int:id>', methods=['GET', 'PUT', 'DELETE'])"
   **Relevance**: Route definitions available in code

2. **Source**: `api_routes.py:68-75`
   **Quote**: "def get_user(id: int) -> dict: '''Returns user by ID'''"
   **Relevance**: Type hints and docstrings present

3. **Source**: `developer_survey.md:34`
   **Quote**: "83% of developers report API docs are outdated"
   **Relevance**: Documentation maintenance issue

#### Analysis:
- **Primary rationale**: Auto-generation ensures docs stay current
- **Alternative considered**: Manual documentation
- **Alternative rejected because**: History shows manual docs go stale

#### Action:
→ Therefore, I will: Use flask-apispec to generate OpenAPI from decorators
```

### Use Case: Code Comments for Complex Logic

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

### Decision: Add explanatory comments to the rate limiting algorithm

#### Risk Assessment:
- **Change Type**: Add documentation
- **Risk Level**: Low
- **Impact Scope**: Code maintainability
- **Reversibility**: Easy

#### Evidence Collection:
1. **Source**: `rate_limiter.py:45-89`
   **Quote**: "tokens = min(capacity, tokens + (now - last) * rate)"
   **Relevance**: Token bucket algorithm not obvious

2. **Source**: `code_review_notes.md:234`
   **Quote**: "Three developers asked about rate limiter logic"
   **Relevance**: Complexity indicator

3. **Source**: `onboarding_feedback.md:56`
   **Quote**: "Rate limiter took 2 days to understand"
   **Relevance**: Onboarding friction point

#### Action:
→ Therefore, I will: Add detailed comments explaining token bucket algorithm
```

## Dependency Management

### Use Case: Security Vulnerability Resolution

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

### Decision: Upgrade lodash to patch critical security vulnerability

#### Risk Assessment:
- **Change Type**: Dependency update
- **Risk Level**: High (security critical)
- **Impact Scope**: All components using lodash
- **Reversibility**: Easy (revert version)

#### Evidence Collection:
1. **Source**: `npm_audit.json:45`
   **Quote**: "lodash@4.17.11 - Critical: Prototype pollution (CVE-2019-10744)"
   **Relevance**: Known vulnerability

2. **Source**: `package-lock.json:234`
   **Quote**: "lodash: { version: '4.17.11' }"
   **Relevance**: Confirms vulnerable version in use

3. **Source**: `security_policy.md:12`
   **Quote**: "Critical vulnerabilities must be patched within 48 hours"
   **Relevance**: Compliance requirement

4. **Source**: `test_results.json:567`
   **Quote**: "All tests passed with lodash@4.17.21"
   **Relevance**: Upgrade tested successfully

#### Action:
→ Therefore, I will: Upgrade lodash to 4.17.21 immediately
```

### Use Case: Dependency Conflict Resolution

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

### Decision: DEFERRED - Cannot upgrade React due to dependency conflicts

#### Risk Assessment:
- **Change Type**: Major version upgrade
- **Risk Level**: High
- **Impact Scope**: Entire frontend
- **Reversibility**: Difficult

#### Evidence Collection:
1. **Source**: `npm_ls_output.txt:89`
   **Quote**: "UNMET PEER DEPENDENCY react@18.0.0"
   **Relevance**: Version conflict detected

2. **Source**: `package.json:45-50`
   **Quote**: "react-widgets: ^4.0.0 // requires react@^16.0.0"
   **Relevance**: Blocking dependency identified

#### Analysis:
⚠️ DEFERRED: Dependency conflict prevents upgrade
- Available evidence: react-widgets incompatible with React 18
- Missing evidence: Alternative widget libraries, upgrade path
- Recommended action: 
  1. Research react-widgets alternatives
  2. Test with react-widgets@5.0.0-beta
  3. Create staged migration plan
```

## Test Generation & Coverage

### Use Case: Unit Test Generation for Uncovered Code

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

### Decision: Generate unit tests for PaymentCalculator class

#### Risk Assessment:
- **Change Type**: Add test coverage
- **Risk Level**: Low
- **Impact Scope**: Test suite only
- **Reversibility**: Easy

#### Evidence Collection:
1. **Source**: `coverage_report.html:234`
   **Quote**: "PaymentCalculator.py: 23% coverage (17/74 lines)"
   **Relevance**: Critical code with low coverage

2. **Source**: `payment_calculator.py:45-67`
   **Quote**: "def calculate_tax(self, amount, region): ..."
   **Relevance**: Complex tax logic needs testing

3. **Source**: `bug_report_2024-01.md:34`
   **Quote**: "Tax calculation error for EU customers"
   **Relevance**: Bugs found in untested code

4. **Source**: `testing_standards.md:12`
   **Quote**: "Payment code requires 90% coverage minimum"
   **Relevance**: Coverage requirement not met

#### Action:
→ Therefore, I will: Generate comprehensive unit tests for all PaymentCalculator methods
```

### Use Case: Integration Test Strategy

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

### Decision: Create integration tests for order processing pipeline

#### Risk Assessment:
- **Change Type**: Add integration tests
- **Risk Level**: Low
- **Impact Scope**: Test environment
- **Reversibility**: Easy

#### Evidence Collection:
1. **Source**: `incident_report_2024-01-15.md:23`
   **Quote**: "Order stuck between payment and fulfillment services"
   **Relevance**: Integration point failure

2. **Source**: `service_dependencies.json:89`
   **Quote**: "order-service → [payment-service, inventory-service, shipping-service]"
   **Relevance**: Complex service interactions

3. **Source**: `test_inventory.txt:analysis`
   **Quote**: "0 integration tests for order pipeline"
   **Relevance**: Gap in test coverage

#### Action:
→ Therefore, I will: Create end-to-end tests simulating complete order flow
```

## CI/CD Pipeline Decisions

### Use Case: Deployment Strategy Selection

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

### Decision: Implement blue-green deployment for zero-downtime releases

#### Risk Assessment:
- **Change Type**: Deployment process change
- **Risk Level**: Medium
- **Impact Scope**: Production deployments
- **Reversibility**: Easy (revert to old process)

#### Evidence Collection:
1. **Source**: `deployment_metrics.json:34`
   **Quote**: "avg_downtime_per_deploy: 3.5 minutes"
   **Relevance**: Current process has downtime

2. **Source**: `sla_agreement.pdf:page-12`
   **Quote**: "99.9% uptime requirement (43 minutes/month max)"
   **Relevance**: Downtime budget being consumed by deploys

3. **Source**: `infrastructure_capacity.yaml:23`
   **Quote**: "available_instances: 8, current_usage: 3"
   **Relevance**: Capacity exists for blue-green

4. **Source**: `customer_complaints.csv:analysis`
   **Quote**: "37% of complaints mention 'site unavailable during update'"
   **Relevance**: Business impact of downtime

#### Action:
→ Therefore, I will: Configure blue-green deployment with automated health checks
```

### Use Case: Build Optimization

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

### Decision: Implement Docker layer caching to speed up builds

#### Risk Assessment:
- **Change Type**: Build process optimization
- **Risk Level**: Low
- **Impact Scope**: CI pipeline
- **Reversibility**: Easy

#### Evidence Collection:
1. **Source**: `ci_metrics.json:156`
   **Quote**: "avg_build_time: 27 minutes"
   **Relevance**: Slow builds impacting productivity

2. **Source**: `dockerfile:1-30`
   **Quote**: "COPY package*.json ./ \n RUN npm install \n COPY . ."
   **Relevance**: Dependencies reinstalled every build

3. **Source**: `build_logs/analysis.txt:45`
   **Quote**: "npm install: 18 minutes (no changes detected)"
   **Relevance**: Wasted time on unchanged dependencies

#### Action:
→ Therefore, I will: Reorder Dockerfile to copy package files first, code last
```

## Code Generation

### Use Case: Boilerplate Generation

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

### Decision: Generate CRUD endpoints for new Product model

#### Risk Assessment:
- **Change Type**: Generate new code
- **Risk Level**: Low
- **Impact Scope**: New module only
- **Reversibility**: Easy

#### Evidence Collection:
1. **Source**: `models/product.py:1-25`
   **Quote**: "class Product(db.Model): id, name, price, description"
   **Relevance**: Model structure defines CRUD needs

2. **Source**: `api_patterns.md:34`
   **Quote**: "All models must expose standard REST endpoints"
   **Relevance**: Architectural requirement

3. **Source**: `api_routes/user.py:45-189`
   **Quote**: "Standard CRUD implementation example"
   **Relevance**: Pattern to follow for consistency

#### Action:
→ Therefore, I will: Generate GET/POST/PUT/DELETE endpoints following user.py pattern
```

### Use Case: Test Data Generation

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

### Decision: Generate comprehensive test fixtures for e-commerce testing

#### Risk Assessment:
- **Change Type**: Create test data
- **Risk Level**: Low
- **Impact Scope**: Test environment only
- **Reversibility**: Easy

#### Evidence Collection:
1. **Source**: `test_requirements.md:23`
   **Quote**: "Tests must cover: normal, edge, and error cases"
   **Relevance**: Comprehensive data needed

2. **Source**: `models/order.py:45-67`
   **Quote**: "Order statuses: pending, paid, shipped, delivered, cancelled"
   **Relevance**: All states need test coverage

3. **Source**: `test_data/current_fixtures.json:1-10`
   **Quote**: "orders: [{status: 'pending'}, {status: 'pending'}]"
   **Relevance**: Only one status currently tested

#### Action:
→ Therefore, I will: Generate fixtures covering all order states and edge cases
```

## Migration Planning

### Use Case: Database Migration Strategy

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

### Decision: Use phased migration from MySQL to PostgreSQL

#### Risk Assessment:
- **Change Type**: Database platform change
- **Risk Level**: Critical
- **Impact Scope**: Entire application
- **Reversibility**: Very difficult

#### Evidence Collection:
1. **Source**: `database_metrics.json:234`
   **Quote**: "mysql_limitations_hit: ['json_support', 'full_text_search', 'arrays']"
   **Relevance**: Technical limitations driving migration

2. **Source**: `data_analysis.sql:results`
   **Quote**: "Total data size: 2.3TB, Daily transactions: 1.2M"
   **Relevance**: Large scale requires careful planning

3. **Source**: `architecture_decision_record_042.md:45`
   **Quote**: "Approved: Migrate to PostgreSQL for advanced features"
   **Relevance**: Decision already approved

4. **Source**: `customer_sla.pdf:page-8`
   **Quote**: "Maximum allowed downtime: 5 minutes/month"
   **Relevance**: Cannot do stop-the-world migration

#### Analysis:
- **Primary rationale**: Zero-downtime requirement + data scale
- **Alternative considered**: Big-bang migration
- **Alternative rejected because**: 48-hour downtime unacceptable

#### Action:
→ Therefore, I will: Implement dual-write strategy with gradual cutover
```

### Use Case: Framework Upgrade Path

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

### Decision: Create incremental upgrade path from Django 2.2 to 4.2

#### Risk Assessment:
- **Change Type**: Framework major version upgrade
- **Risk Level**: High
- **Impact Scope**: Entire application
- **Reversibility**: Moderate

#### Evidence Collection:
1. **Source**: `requirements.txt:3`
   **Quote**: "Django==2.2.28"
   **Relevance**: Current version near end-of-life

2. **Source**: `django_deprecation_warnings.log:count`
   **Quote**: "Total deprecation warnings: 847"
   **Relevance**: Significant code changes needed

3. **Source**: `django_release_notes_3.0.txt:breaking`
   **Quote**: "Python 2 support removed, new migrations format"
   **Relevance**: Breaking changes in 3.0

4. **Source**: `test_suite_results.json:django3.2`
   **Quote**: "Failed tests: 234/1879"
   **Relevance**: Cannot jump directly to 3.2

#### Analysis:
- **Primary rationale**: Too many breaking changes for direct upgrade
- **Alternative considered**: Direct 2.2 → 4.2 upgrade
- **Alternative rejected because**: 234 test failures indicate high risk

#### Action:
→ Therefore, I will: Plan incremental upgrades: 2.2 → 3.0 → 3.2 → 4.0 → 4.2
```

## Best Practices

### When to Use CoT

1. **Always Use For**:
   - Production code changes
   - Security-related decisions
   - Architecture modifications
   - API changes
   - Performance optimizations
   - Complex debugging

2. **Optional For**:
   - Documentation updates
   - Test additions
   - Minor refactoring
   - Development environment changes

3. **Not Needed For**:
   - Typo fixes
   - Comment updates
   - Formatting changes
   - Variable renames (unless breaking)

### Integration with Development Workflow

1. **Code Review Integration**:
   ```bash
   # Generate CoT for PR
   git diff main..feature | cot-analyze --output pr-reasoning.md
   ```

2. **IDE Integration**:
   ```python
   # VS Code extension example
   @command('cot.analyze')
   def analyze_selection(selection):
       return cot_reasoner.analyze(selection)
   ```

3. **CI/CD Integration**:
   ```yaml
   # GitHub Actions example
   - name: CoT Analysis
     uses: cot-standard/analyze-action@v1
     with:
       files: ${{ github.changed_files }}
       risk-threshold: medium
   ```

### Common Patterns

1. **Evidence Hierarchy**:
   - Production metrics > Test results
   - Current code > Documentation
   - Recent data > Historical data

2. **Risk Assessment**:
   - User-facing changes = Higher risk
   - Data changes = Critical risk
   - Internal refactoring = Lower risk

3. **Deferral Triggers**:
   - Insufficient evidence
   - Conflicting requirements
   - Unknown dependencies
   - Missing stakeholder input

---

*These use cases demonstrate practical applications of CoT v7.0.0 in software development. For more examples, see the `examples/` directory.*