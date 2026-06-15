# Clean Code for Django & Python

Clean code is code that is easy to read, easy to change, and does what it says.
This guide applies general clean code principles (Robert C. Martin's "Clean Code",
PEP 8) specifically to Django projects.

## 1. Meaningful Names

Names should reveal intent. A reader shouldn't need to open the implementation
to understand what something is for.

```python
# ❌ BAD: unclear, abbreviated names
def calc(o, d):
    t = o.p * (1 - d)
    return t

# ✅ GOOD: intention-revealing names
def calculate_discounted_total(order: Order, discount_rate: float) -> Decimal:
    return order.price * (1 - discount_rate)
```

**Guidelines:**
- Use pronounceable, searchable names (`user_count`, not `uc`).
- Booleans should read as predicates: `is_active`, `has_permission`, `can_edit`.
- Avoid encoding type info in names (`user_list` -> just `users`).
- Be consistent: if you call it `user` in one place, don't call it `usr` or
  `account` elsewhere for the same concept.
- Django model field names should match domain language used by the team and
  product (e.g. `published_at`, not `pub_dt`).

## 2. Functions and Methods

### Do One Thing

A function should do one thing, do it well, and do nothing else. If you need
"and" to describe what a function does, it probably should be split.

```python
# ❌ BAD: validates, saves, sends email, and logs - four responsibilities
def create_order(data, user):
    if not data.get("items"):
        raise ValueError("Order must have items")
    order = Order.objects.create(user=user, total=data["total"])
    for item in data["items"]:
        OrderItem.objects.create(order=order, **item)
    send_mail("Order confirmation", "...", "noreply@example.com", [user.email])
    logger.info(f"Order {order.id} created")
    return order

# ✅ GOOD: each function has a single responsibility
def validate_order_data(data: dict) -> None:
    if not data.get("items"):
        raise ValueError("Order must have items")

def create_order(data: dict, user: User) -> Order:
    validate_order_data(data)
    order = Order.objects.create(user=user, total=data["total"])
    OrderItem.objects.bulk_create(
        OrderItem(order=order, **item) for item in data["items"]
    )
    return order

def place_order(data: dict, user: User) -> Order:
    """Orchestrates order creation, notification, and logging."""
    order = create_order(data, user)
    send_order_confirmation(order)
    logger.info("Order created", extra={"order_id": order.id})
    return order
```

### Keep Functions Small

A good rule of thumb: if a function doesn't fit on your screen, it's a
candidate for extraction. Long functions usually hide multiple responsibilities.

```python
# ❌ BAD: 40-line view doing everything inline
def checkout_view(request):
    # ... 10 lines validating cart
    # ... 10 lines calculating totals and discounts
    # ... 10 lines creating order and payment record
    # ... 10 lines sending emails and redirecting
    ...

# ✅ GOOD: view delegates to small, named steps
def checkout_view(request):
    cart = get_cart_or_404(request)
    totals = calculate_order_totals(cart)
    order = create_order_from_cart(cart, totals, user=request.user)
    send_order_confirmation(order)
    return redirect("order_detail", pk=order.pk)
```

### Limit Arguments

Functions with many positional arguments are hard to call correctly and hard
to extend.

```python
# ❌ BAD: too many positional args, easy to mix up
def create_user(email, first_name, last_name, is_staff, is_active, role, dept):
    ...

# ✅ GOOD: group related data, use keyword-only args or a dataclass
@dataclass
class NewUserData:
    email: str
    first_name: str
    last_name: str
    role: str
    department: str

def create_user(data: NewUserData, *, is_staff: bool = False) -> User:
    ...
```

### Avoid Side Effects in "Query-Like" Functions

A function named `get_x` or `is_x` shouldn't mutate state. If it must, name it
accordingly (`fetch_and_mark_read`, `create_or_update_profile`).

## 3. Don't Repeat Yourself (DRY)

If the same logic appears in three or more places, extract it - into a
function, a model method/manager, a mixin, or a template tag. But don't
over-abstract two superficially similar blocks that may evolve differently
("premature DRY" can be worse than duplication).

```python
# ❌ BAD: same availability check duplicated across views/serializers
if product.stock > 0 and product.is_active and not product.is_discontinued:
    ...

# ✅ GOOD: encapsulated where the concept lives
class Product(models.Model):
    ...
    @property
    def is_available(self) -> bool:
        return self.stock > 0 and self.is_active and not self.is_discontinued
```

## 4. Avoid Magic Numbers and Strings

Unexplained literals make code fragile and hard to understand.

```python
# ❌ BAD: what does 3 mean? what does "A" mean?
if order.status == "A" and order.retries < 3:
    ...

# ✅ GOOD: named constants / Django choices
class OrderStatus(models.TextChoices):
    ACTIVE = "A", "Active"
    CANCELLED = "C", "Cancelled"

MAX_RETRY_ATTEMPTS = 3

if order.status == OrderStatus.ACTIVE and order.retries < MAX_RETRY_ATTEMPTS:
    ...
```

## 5. Comments and Docstrings

Prefer self-explanatory code over comments that explain *what* the code does.
Use comments to explain *why*, when the reasoning isn't obvious from the code.

```python
# ❌ BAD: comment restates the code
# increment retries by 1
order.retries += 1

# ✅ GOOD: comment explains non-obvious reasoning
# Stripe requires idempotency keys to avoid double-charging on retries
payment_intent = stripe.PaymentIntent.create(idempotency_key=order.idempotency_key, ...)
```

**Docstring conventions:**
- Every public function/class/module that isn't trivially named should have a
  docstring describing purpose, parameters, and return value.
- Use a consistent style (Google or NumPy docstring format) across the project.
- Don't leave commented-out code in commits - delete it; version control
  remembers it for you.

```python
def calculate_shipping_cost(order: Order, destination: Address) -> Decimal:
    """Calculate shipping cost for an order.

    Args:
        order: The order being shipped, used for weight and dimensions.
        destination: Destination address, used for zone-based pricing.

    Returns:
        The shipping cost as a Decimal in the store's currency.
    """
    ...
```

## 6. Error Handling

Fail fast and be explicit about what can go wrong.

```python
# ❌ BAD: swallows all errors, hides bugs
try:
    process_payment(order)
except Exception:
    pass

# ✅ GOOD: catch specific exceptions, handle or re-raise meaningfully
try:
    process_payment(order)
except PaymentDeclinedError as exc:
    logger.warning("Payment declined", extra={"order_id": order.id, "reason": str(exc)})
    raise

# ✅ GOOD: guard clauses instead of deep nesting
def publish_post(post: Post, user: User) -> None:
    if post.author != user:
        raise PermissionDenied("Only the author can publish this post")
    if not post.content:
        raise ValueError("Cannot publish an empty post")

    post.is_published = True
    post.save(update_fields=["is_published"])
```

## 7. SOLID Principles Applied to Django

### Single Responsibility Principle (SRP) - Service Layer Pattern

Views, serializers, and models each have a natural responsibility. When
business logic grows beyond "save this object", extract it into a **service**
layer (plain functions or classes in `services.py`) instead of stuffing it
into views or `save()` overrides.

```python
# ✅ GOOD: thin view, model stays focused on data, service holds business logic
# services.py
def transfer_funds(*, from_account: Account, to_account: Account, amount: Decimal) -> None:
    """Move funds between accounts atomically."""
    if amount <= 0:
        raise ValueError("Transfer amount must be positive")

    with transaction.atomic():
        from_account.balance = F("balance") - amount
        from_account.save(update_fields=["balance"])
        to_account.balance = F("balance") + amount
        to_account.save(update_fields=["balance"])

# views.py
class TransferView(APIView):
    def post(self, request):
        serializer = TransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        transfer_funds(**serializer.validated_data)
        return Response(status=status.HTTP_204_NO_CONTENT)
```

This keeps each layer testable in isolation: the service can be unit-tested
without HTTP, and the view test only needs to confirm it calls the service
correctly.

### Open/Closed & Dependency Inversion

Depend on abstractions (interfaces/protocols) for things that vary, like
notification channels or payment providers, so new implementations can be
added without modifying existing code.

```python
# ✅ GOOD: notifier is swappable without touching calling code
class Notifier(Protocol):
    def send(self, user: User, message: str) -> None: ...

class EmailNotifier:
    def send(self, user: User, message: str) -> None:
        send_mail("Notification", message, "noreply@example.com", [user.email])

def notify_order_shipped(order: Order, notifier: Notifier) -> None:
    notifier.send(order.user, f"Your order {order.id} has shipped!")
```

## 8. Type Hints

Type hints document intent and let tools (mypy, IDEs) catch mistakes early.
Add them at minimum to function signatures of services, utilities, and
non-trivial model/serializer methods.

```python
# ✅ GOOD
def get_active_subscriptions(user: User) -> QuerySet["Subscription"]:
    return user.subscriptions.filter(status=Subscription.Status.ACTIVE)
```

## 9. Formatting and Tooling

Consistent formatting removes an entire class of code review comments and
diffs. Automate it:

```bash
pip install black ruff isort
```

```toml
# pyproject.toml
[tool.black]
line-length = 88

[tool.ruff]
line-length = 88
select = ["E", "F", "I", "UP", "B"]

[tool.isort]
profile = "black"
```

**Pre-commit hook example:**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.4.2
    hooks:
      - id: black
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.4
    hooks:
      - id: ruff
```

## Clean Code Checklist

When reviewing or writing Django code, check:

✅ Names reveal intent (no `data`, `tmp`, `obj2`, single-letter vars except loop counters)
✅ Functions/methods do one thing and fit comfortably on screen
✅ Views and serializers are thin; business logic lives in services/managers
✅ No duplicated logic across 3+ places (DRY) without over-abstracting
✅ No magic numbers/strings - use constants, enums, or `TextChoices`
✅ Comments explain *why*, not *what*; no commented-out code left behind
✅ Public functions/classes have docstrings
✅ Specific exceptions are caught and handled; no bare `except:`
✅ Type hints on service/utility functions and complex signatures
✅ Code formatted with `black`/`ruff` and passes linting in CI

---

**Remember**: Clean code is optimized for the next person reading it -
including future you. When in doubt, prioritize clarity over cleverness.
