#!/usr/bin/env python3
"""Test database connection."""
import asyncio

import asyncpg


async def test_connection():
    """Test PostgreSQL connection."""
    try:
        # Try to connect to the database
        conn = await asyncpg.connect("postgresql://gost@localhost:5432/duelbot")
        print("✅ Database connection successful!")
        
        # Test a simple query
        result = await conn.fetchval("SELECT version()")
        print(f"PostgreSQL version: {result}")
        
        await conn.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_connection())
