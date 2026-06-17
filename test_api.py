import sys
import asyncio
from apps.api.core.security import create_access_token

token = create_access_token({"sub": "Sameer@admin.com"})
print(token)
