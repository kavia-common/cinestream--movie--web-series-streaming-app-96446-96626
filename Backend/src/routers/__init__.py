# Expose routers as package
from . import admin, auth, content, profiles, reviews, streaming, subscriptions
from . import watchlist  # noqa: F401  # imported for side-effects
