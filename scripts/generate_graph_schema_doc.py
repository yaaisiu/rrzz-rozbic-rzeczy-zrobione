import sys
import os
import logging
from typing import List, Dict, Any
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph.neo4j_client import Neo4jClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_schema(client: Neo4jClient) -> Dict[str, Any]:
    """Fetches node labels and relationship types from the graph."""
    schema_data = {}
    try:
        logging.info("Fetching node labels...")
        labels_query = "CALL db.labels() YIELD label"
        labels_result = client.execute_query(labels_query)
        schema_data['labels'] = [item['label'] for item in labels_result]
        logging.info(f"Found labels: {schema_data['labels']}")

        logging.info("Fetching relationship types...")
        rel_types_query = "CALL db.relationshipTypes() YIELD relationshipType"
        rel_types_result = client.execute_query(rel_types_query)
        schema_data['relationship_types'] = [item['relationshipType'] for item in rel_types_result]
        logging.info(f"Found relationship types: {schema_data['relationship_types']}")
        
    except Exception as e:
        logging.error(f"An error occurred while fetching schema: {e}")
        return {}
        
    return schema_data

def get_node_examples(client: Neo4jClient, label: str, properties: List[str]) -> List[Dict[str, Any]]:
    """Fetches a few example nodes for a given label."""
    if not properties:
        return []
    try:
        # We need to return each property explicitly to ensure order
        return_clause = ", ".join([f"n.`{prop}` AS `{prop}`" for prop in properties])
        examples_query = f"MATCH (n:`{label}`) RETURN {return_clause} LIMIT 3"
        return client.execute_query(examples_query)
    except Exception as e:
        logging.error(f"Could not fetch examples for label {label}: {e}")
        return []

def format_value(value: Any, max_length: int = 50) -> str:
    """Formats a value for display in a markdown table, truncating if necessary."""
    if value is None:
        return ""
    
    # Convert Neo4j temporal types to string if they exist
    if hasattr(value, 'iso_format'):
        value = value.iso_format()
        
    str_value = str(value).replace("\n", " ").replace("|", "\\|")
    
    if len(str_value) > max_length:
        return str_value[:max_length-3] + "..."
    return str_value

def generate_node_schema_markdown(client: Neo4jClient, labels: List[str]) -> str:
    """Generates markdown documentation for each node label."""
    markdown_lines = ["# Graph Schema: Nodes", ""]
    
    for label in labels:
        try:
            logging.info(f"Processing label: {label}")
            
            # Get node count
            count_query = f"MATCH (n:`{label}`) RETURN count(n) AS count"
            count_result = client.execute_query(count_query)
            count = count_result[0]['count'] if count_result else 0
            
            # Get properties
            # We sample a few nodes to get a representative set of properties
            props_query = f"""
                MATCH (n:`{label}`) 
                WITH n LIMIT 100
                UNWIND keys(n) AS key
                RETURN collect(distinct key) AS properties
            """
            props_result = client.execute_query(props_query)
            properties = props_result[0]['properties'] if props_result else []
            
            markdown_lines.append(f"## `:{label}`")
            markdown_lines.append(f"- **Count:** {count}")
            markdown_lines.append("- **Properties:**")
            for prop in sorted(properties):
                markdown_lines.append(f"  - `{prop}`")
            markdown_lines.append("")

            # Add examples
            examples = get_node_examples(client, label, properties)
            if examples:
                sorted_props = sorted(properties)
                header = "| " + " | ".join(sorted_props) + " |"
                separator = "| " + " | ".join(["---"] * len(sorted_props)) + " |"
                markdown_lines.append("**Examples:**")
                markdown_lines.append(header)
                markdown_lines.append(separator)
                for example in examples:
                    row = "| " + " | ".join([format_value(example.get(prop)) for prop in sorted_props]) + " |"
                    markdown_lines.append(row)
                markdown_lines.append("")

        except Exception as e:
            logging.error(f"Failed to generate schema for label {label}: {e}")
            markdown_lines.append(f"## `:{label}`")
            markdown_lines.append(f"- Error generating schema for this label.")
            markdown_lines.append("")

    return "\n".join(markdown_lines)

def generate_relationship_schema_markdown(client: Neo4jClient, rel_types: List[str]) -> str:
    """Generates markdown documentation for each relationship type."""
    markdown_lines = ["# Graph Schema: Relationships", ""]

    for rel_type in rel_types:
        try:
            logging.info(f"Processing relationship type: {rel_type}")

            # Get relationship count
            count_query = f"MATCH ()-[r:`{rel_type}`]->() RETURN count(r) as count"
            count_result = client.execute_query(count_query)
            count = count_result[0]['count'] if count_result else 0

            # Get properties
            props_query = f"""
                MATCH ()-[r:`{rel_type}`]->()
                WITH r LIMIT 100
                UNWIND keys(r) AS key
                RETURN collect(distinct key) AS properties
            """
            props_result = client.execute_query(props_query)
            properties = props_result[0]['properties'] if props_result else []
            
            # Get connection patterns
            patterns_query = f"""
                MATCH (a)-[r:`{rel_type}`]->(b)
                RETURN DISTINCT labels(a) AS start_labels, labels(b) AS end_labels
                LIMIT 10
            """
            patterns_result = client.execute_query(patterns_query)
            patterns = [
                f"(`:{':'.join(p['start_labels'])}`)-[:`{rel_type}`]->(`:{':'.join(p['end_labels'])}`)"
                for p in patterns_result
            ]

            markdown_lines.append(f"## `[:{rel_type}]`")
            markdown_lines.append(f"- **Count:** {count}")
            markdown_lines.append("- **Properties:**")
            if properties:
                for prop in sorted(properties):
                    markdown_lines.append(f"  - `{prop}`")
            else:
                markdown_lines.append("  - (No properties)")
            markdown_lines.append("- **Connection Patterns:**")
            if patterns:
                for pattern in patterns:
                    markdown_lines.append(f"  - {pattern}")
            else:
                markdown_lines.append("  - (No patterns found)")
            markdown_lines.append("")

        except Exception as e:
            logging.error(f"Failed to generate schema for relationship {rel_type}: {e}")
            markdown_lines.append(f"## `[:{rel_type}]`")
            markdown_lines.append(f"- Error generating schema for this relationship.")
            markdown_lines.append("")
    
    return "\n".join(markdown_lines)

def main():
    """Main function to generate the graph schema documentation."""
    logging.info("Starting graph schema documentation generation...")
    client = None
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'documentation',
        'graph-schema.md'
    )

    try:
        client = Neo4jClient()
        
        schema = fetch_schema(client)
        if not schema:
            logging.error("Could not fetch schema. Aborting.")
            return

        node_markdown = generate_node_schema_markdown(client, schema['labels'])
        rel_markdown = generate_relationship_schema_markdown(client, schema['relationship_types'])

        # Combine all parts into the final document
        final_markdown = [
            "# Knowledge Graph Schema",
            "",
            "This document outlines the schema of the knowledge graph, including node labels, their properties, and relationship types.",
            "It is auto-generated by the `scripts/generate_graph_schema_doc.py` script.",
            f"**Last generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            "",
            node_markdown,
            "",
            "---",
            "",
            rel_markdown
        ]

        # Write to file
        with open(output_path, 'w') as f:
            f.write("\n".join(final_markdown))

        logging.info(f"Successfully generated and saved graph schema to {output_path}")

    except Exception as e:
        logging.error(f"An error occurred during the process: {e}")
    finally:
        if client:
            client.close()
            logging.info("Neo4j connection closed.")

if __name__ == "__main__":
    main() 