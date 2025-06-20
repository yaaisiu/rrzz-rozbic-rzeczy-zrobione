#!/usr/bin/env python3
"""
Neo4j Database Manager Script

This script provides functionality to:
1. Connect to Neo4j database
2. Delete all contents
3. Check if multiple named databases are supported
4. Create and manage multiple databases (if supported)
"""

import os
import sys
import logging
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Neo4jDatabaseManager:
    """Manager for Neo4j database operations."""
    
    def __init__(self, uri: str = "bolt://localhost:7687", 
                 user: str = "neo4j", password: str = "password"):
        """
        Initialize the database manager.
        
        Args:
            uri: Neo4j connection URI
            user: Neo4j username
            password: Neo4j password
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.driver: Optional[Any] = None
        
    def connect(self) -> bool:
        """Connect to Neo4j database."""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # Test connection
            if self.driver:
                with self.driver.session() as session:
                    result = session.run("RETURN 1 as test")
                    record = result.single()
                    if record and record["test"] == 1:
                        logger.info("✅ Successfully connected to Neo4j")
                        return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to Neo4j: {e}")
            return False
        return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get information about the current database."""
        if not self.driver:
            logger.error("Driver not initialized")
            return {}
            
        try:
            with self.driver.session() as session:
                # Get current database name
                result = session.run("CALL db.info() YIELD name")
                db_info = result.single()
                
                # Get Neo4j version
                version_result = session.run("CALL dbms.components() YIELD versions")
                version_info = version_result.single()
                
                # Get database statistics
                stats_result = session.run("""
                    MATCH (n) 
                    RETURN count(n) as total_nodes,
                           count(DISTINCT labels(n)) as label_types
                """)
                stats = stats_result.single()
                
                return {
                    "database_name": db_info["name"] if db_info else "unknown",
                    "version": version_info["versions"][0] if version_info and version_info["versions"] else "unknown",
                    "edition": "Community",  # Based on the error we saw earlier
                    "total_nodes": stats["total_nodes"] if stats else 0,
                    "label_types": stats["label_types"] if stats else 0
                }
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return {}
    
    def list_all_databases(self) -> List[str]:
        """List all available databases (if supported)."""
        if not self.driver:
            logger.error("Driver not initialized")
            return []
            
        try:
            with self.driver.session() as session:
                # Try to list databases (only works in Enterprise edition)
                result = session.run("SHOW DATABASES")
                databases = [record["name"] for record in result]
                return databases
        except Exception as e:
            logger.warning(f"Could not list databases (likely Community edition): {e}")
            return []
    
    def delete_all_contents(self) -> bool:
        """Delete all nodes and relationships from the database."""
        if not self.driver:
            logger.error("Driver not initialized")
            return False
            
        try:
            with self.driver.session() as session:
                # Delete all relationships first
                result = session.run("MATCH ()-[r]->() DELETE r")
                logger.info("Deleted all relationships")
                
                # Delete all nodes
                result = session.run("MATCH (n) DELETE n")
                logger.info("Deleted all nodes")
                
                # Verify deletion
                count_result = session.run("MATCH (n) RETURN count(n) as count")
                count_record = count_result.single()
                count = count_record["count"] if count_record else 0
                
                if count == 0:
                    logger.info("✅ Successfully deleted all contents from database")
                    return True
                else:
                    logger.warning(f"⚠️  Some nodes still remain: {count}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Failed to delete contents: {e}")
            return False
    
    def test_multiple_databases(self) -> Dict[str, Any]:
        """Test if multiple databases are supported and can be created."""
        results = {
            "supported": False,
            "can_create": False,
            "databases": [],
            "error": None
        }
        
        if not self.driver:
            logger.error("Driver not initialized")
            results["error"] = "Driver not initialized"
            return results
        
        try:
            # First, try to list existing databases
            existing_dbs = self.list_all_databases()
            results["databases"] = existing_dbs
            
            if existing_dbs:
                results["supported"] = True
                logger.info(f"✅ Multiple databases are supported. Found: {existing_dbs}")
                
                # Try to create a test database
                try:
                    with self.driver.session() as session:
                        test_db_name = "test_database_123"
                        session.run(f"CREATE DATABASE {test_db_name}")
                        logger.info(f"✅ Successfully created test database: {test_db_name}")
                        results["can_create"] = True
                        
                        # Clean up - drop the test database
                        session.run(f"DROP DATABASE {test_db_name}")
                        logger.info(f"✅ Cleaned up test database: {test_db_name}")
                        
                except Exception as create_error:
                    logger.warning(f"⚠️  Could not create test database: {create_error}")
                    results["error"] = str(create_error)
            else:
                logger.info("ℹ️  Multiple databases not supported in this Neo4j edition")
                
        except Exception as e:
            logger.error(f"❌ Error testing multiple databases: {e}")
            results["error"] = str(e)
            
        return results
    
    def create_sample_data(self) -> bool:
        """Create some sample data to test the database."""
        if not self.driver:
            logger.error("Driver not initialized")
            return False
            
        try:
            with self.driver.session() as session:
                # Create some test nodes and relationships
                session.run("""
                    CREATE (n1:Person {name: 'Alice', age: 30})
                    CREATE (n2:Person {name: 'Bob', age: 25})
                    CREATE (n3:Project {name: 'Test Project', status: 'active'})
                    CREATE (n1)-[:WORKS_ON]->(n3)
                    CREATE (n2)-[:WORKS_ON]->(n3)
                    CREATE (n1)-[:KNOWS]->(n2)
                """)
                
                logger.info("✅ Created sample data")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to create sample data: {e}")
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get detailed statistics about the database."""
        if not self.driver:
            logger.error("Driver not initialized")
            return {"labels": {}, "relationships": {}}
            
        try:
            with self.driver.session() as session:
                # Get node counts by label
                label_result = session.run("""
                    CALL db.labels() YIELD label
                    CALL apoc.cypher.run('MATCH (n:' + label + ') RETURN count(n) as count', {})
                    YIELD value
                    RETURN label, value.count as count
                    ORDER BY count DESC
                """)
                
                labels = {record["label"]: record["count"] for record in label_result}
                
                # Get relationship counts by type
                rel_result = session.run("""
                    CALL db.relationshipTypes() YIELD relationshipType
                    CALL apoc.cypher.run('MATCH ()-[r:' + relationshipType + ']->() RETURN count(r) as count', {})
                    YIELD value
                    RETURN relationshipType, value.count as count
                    ORDER BY count DESC
                """)
                
                relationships = {record["relationshipType"]: record["count"] for record in rel_result}
                
                return {
                    "labels": labels,
                    "relationships": relationships
                }
                
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {"labels": {}, "relationships": {}}
    
    def close(self):
        """Close the database connection."""
        if self.driver:
            self.driver.close()
            logger.info("Database connection closed")


def main():
    """Main function to run the database management operations."""
    print("🔍 Neo4j Database Manager")
    print("=" * 50)
    
    # Initialize manager
    manager = Neo4jDatabaseManager()
    
    # Connect to database
    if not manager.connect():
        print("❌ Could not connect to Neo4j. Please check if the service is running.")
        return
    
    # Get database information
    print("\n📊 Database Information:")
    db_info = manager.get_database_info()
    for key, value in db_info.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    
    # Test multiple databases
    print("\n🗄️  Multiple Database Support:")
    multi_db_results = manager.test_multiple_databases()
    print(f"  Supported: {'✅ Yes' if multi_db_results['supported'] else '❌ No'}")
    print(f"  Can Create: {'✅ Yes' if multi_db_results['can_create'] else '❌ No'}")
    if multi_db_results['databases']:
        print(f"  Existing Databases: {', '.join(multi_db_results['databases'])}")
    if multi_db_results['error']:
        print(f"  Error: {multi_db_results['error']}")
    
    # Get current database stats
    print("\n📈 Current Database Statistics:")
    stats = manager.get_database_stats()
    if stats['labels']:
        print("  Node Labels:")
        for label, count in stats['labels'].items():
            print(f"    {label}: {count}")
    if stats['relationships']:
        print("  Relationship Types:")
        for rel_type, count in stats['relationships'].items():
            print(f"    {rel_type}: {count}")
    
    # Ask user what to do
    print("\n" + "=" * 50)
    print("What would you like to do?")
    print("1. Delete all contents")
    print("2. Create sample data")
    print("3. Both (delete then create sample)")
    print("4. Just show information (exit)")
    
    try:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            print("\n🗑️  Deleting all contents...")
            if manager.delete_all_contents():
                print("✅ Successfully deleted all contents")
            else:
                print("❌ Failed to delete contents")
                
        elif choice == "2":
            print("\n📝 Creating sample data...")
            if manager.create_sample_data():
                print("✅ Successfully created sample data")
            else:
                print("❌ Failed to create sample data")
                
        elif choice == "3":
            print("\n🗑️  Deleting all contents...")
            if manager.delete_all_contents():
                print("✅ Successfully deleted all contents")
                print("\n📝 Creating sample data...")
                if manager.create_sample_data():
                    print("✅ Successfully created sample data")
                else:
                    print("❌ Failed to create sample data")
            else:
                print("❌ Failed to delete contents")
                
        elif choice == "4":
            print("ℹ️  Exiting without changes")
            
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled by user")
    
    # Close connection
    manager.close()
    print("\n✅ Database manager finished")


if __name__ == "__main__":
    main() 