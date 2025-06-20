#!/usr/bin/env python3
"""
Simple Neo4j Database Cleaner

Quick script to delete all contents from Neo4j database.
"""

import logging
from neo4j import GraphDatabase

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def clean_neo4j_database():
    """Delete all contents from Neo4j database."""
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "password"
    
    try:
        # Connect to Neo4j
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        with driver.session() as session:
            # Get count before deletion
            count_result = session.run("MATCH (n) RETURN count(n) as count")
            count_record = count_result.single()
            count_before = count_record["count"] if count_record else 0
            logger.info(f"Found {count_before} nodes before deletion")
            
            if count_before == 0:
                logger.info("Database is already empty")
                return True
            
            # Delete all relationships first
            rel_result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            rel_record = rel_result.single()
            rel_count = rel_record["count"] if rel_record else 0
            logger.info(f"Found {rel_count} relationships")
            
            session.run("MATCH ()-[r]->() DELETE r")
            logger.info("Deleted all relationships")
            
            # Delete all nodes
            session.run("MATCH (n) DELETE n")
            logger.info("Deleted all nodes")
            
            # Verify deletion
            count_after_result = session.run("MATCH (n) RETURN count(n) as count")
            count_after_record = count_after_result.single()
            count_after = count_after_record["count"] if count_after_record else 0
            
            if count_after == 0:
                logger.info("✅ Successfully deleted all contents from database")
                return True
            else:
                logger.warning(f"⚠️  Some nodes still remain: {count_after}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Failed to clean database: {e}")
        return False
    finally:
        if 'driver' in locals():
            driver.close()


def test_database_creation():
    """Test if we can create multiple databases."""
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "password"
    
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        with driver.session() as session:
            # List databases
            result = session.run("SHOW DATABASES")
            databases = [record["name"] for record in result]
            logger.info(f"Available databases: {databases}")
            
            # Check if we can create databases
            try:
                session.run("CREATE DATABASE test_db")
                logger.info("✅ Can create databases")
                # Clean up
                session.run("DROP DATABASE test_db")
                return True
            except Exception as e:
                logger.info(f"❌ Cannot create databases: {e}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Failed to test database creation: {e}")
        return False
    finally:
        if 'driver' in locals():
            driver.close()


if __name__ == "__main__":
    print("🧹 Neo4j Database Cleaner")
    print("=" * 40)
    
    # Test database creation first
    print("\n🗄️  Testing multiple database support:")
    can_create = test_database_creation()
    
    # Clean the database
    print("\n🗑️  Cleaning database:")
    success = clean_neo4j_database()
    
    if success:
        print("\n✅ Database cleaning completed successfully")
    else:
        print("\n❌ Database cleaning failed") 