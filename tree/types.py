"""Type aliases for the tree API."""

from typing import Annotated

from pydantic import Field

# NodeId represents both node identifiers and link hrefs
# This allows us to easily change the implementation later
# (e.g., switch from strings to UUIDs, or use path-based IDs)
NodeId = Annotated[str, Field(min_length=1, max_length=255)]
