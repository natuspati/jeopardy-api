import contextvars

is_concurrent = contextvars.ContextVar("is_concurrent", default=False)
