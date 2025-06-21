# Dev Diary - 2025-06-21: Graph Schema Extraction

**Request ID:** (N/A - Manual session)

## Summary of Work

Today, we developed a Python script to automatically generate comprehensive documentation for our Neo4j graph schema. The primary goal was to create a reference document that would be useful for future development, particularly for tasks like text-to-Cypher generation and general onboarding.

### Key Features of the Script:

1.  **Dynamic Schema Introspection:** The script connects to the live Neo4j database and queries it directly for all existing node labels and relationship types. This ensures the documentation is always an accurate reflection of the current graph state.

2.  **Rich Content Generation:** For each node label, the script fetches and includes:
    - The total count of nodes with that label.
    - A complete list of all associated properties.
    - A markdown table with several real-data examples to provide context.

3.  **Detailed Relationship Analysis:** For each relationship type, the script includes:
    - The total count of the relationship.
    - A list of its properties (if any).
    - The specific connection patterns, showing which node labels it connects (e.g., `(:GtdNote)-[:HAS_TAG]->(:Tag)`).

4.  **Automated File Creation:** The script assembles all the gathered information into a clean, well-formatted markdown file and saves it to `documentation/graph-schema.md`. It also includes a timestamp to indicate when the documentation was last generated.

### Outcome:

The script, `scripts/generate_graph_schema_doc.py`, was created and tested iteratively. It successfully generated the `graph-schema.md` file as planned. This provides a valuable, self-updating asset for the project, created without modifying any of the existing application code. 