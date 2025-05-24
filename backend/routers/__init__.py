# Import routers
# Only import routers that correspond to model tables or core functionality
from . import auth
from . import roles
from . import permissions
from . import users
from . import units
from . import training_packages
from . import qualifications
from . import skillsets
from . import assessments
from . import user_progress
from . import achievements
from . import badges

# It's generally better to have the main app include these routers
# directly, rather than re-exporting them here, to avoid potential
# circular dependencies if routers import from each other via this __init__.

# If you intend for other modules to import these directly from the 'routers' package,
# you can list them in __all__, but this is often not necessary if your FastAPI app
# (e.g., in main.py) includes them directly from their respective modules.
# Example: app.include_router(users.router)

# For now, to minimize changes while diagnosing, we'll keep the direct imports
# but be mindful that this can be a source of circular dependencies.
# If errors persist, the next step would be to remove these imports
# and have main.py import each router module directly.
