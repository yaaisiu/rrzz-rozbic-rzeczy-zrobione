# Graph Data Review Notebook Guide

This guide explains how to use the `graph_data_review.ipynb` notebook to review your graph data and prepare prompt examples.

## Purpose

The notebook helps you:
1. **Archive current graph data** - Export everything to CSV for historical record
2. **Prepare prompt examples** - Select and categorize good examples for few-shot prompting
3. **Review and edit data** - Clean up data before using it for prompt development

## Getting Started

1. **Start Neo4j**: Make sure your Neo4j database is running
   ```bash
   docker-compose up
   ```

2. **Run the notebook**: Open `notebooks/graph_data_review.ipynb` in Jupyter

3. **Execute cells sequentially** - Run each cell from top to bottom

## Key Features

### 1. Data Loading
- Automatically loads all GtdNote data with relationships
- Shows data structure and counts
- Creates DataFrame for manipulation

### 2. Data Browsing
```python
browse_rows(0, 10)  # Browse first 10 rows
browse_rows(20, 5)  # Browse 5 rows starting at index 20
```

### 3. Individual Row Editing
```python
edit_row(5)  # Show editing options for row 5

# Then use the suggested functions:
update_content(5, "Updated content")
update_summary(5, "Better summary")
mark_for_prompts(5, True)  # Include in prompt examples
set_category(5, "project")  # Categorize
```

### 4. Bulk Operations
```python
# Automatically categorize rows by tags
mark_rows_by_criteria(has_project_tag, keep=True, category='project')
mark_rows_by_criteria(has_someday_tag, keep=False)  # Exclude someday items
```

### 5. Search and Filter
```python
search_content("neo4j")  # Find rows mentioning neo4j
search_content("project")  # Find project-related rows
```

### 6. Export Functions
```python
# Export all data for archival
export_to_csv()

# Export only selected rows for prompts
export_prompt_examples()
```

## Workflow for Prompt Development

1. **Load and explore data**
   - Run the first few cells to load data
   - Use `browse_rows()` to see what you have

2. **Categorize examples**
   - Use bulk operations to auto-categorize by tags
   - Manually review and adjust categories

3. **Clean up data**
   - Remove low-quality examples: `mark_for_prompts(index, False)`
   - Fix summaries: `update_summary(index, "better summary")`

4. **Export for archival**
   - `export_to_csv()` - saves all data with timestamps

5. **Export for prompts**
   - `export_prompt_examples()` - saves only selected examples in JSON format

## Example Categories

Common categories you might use:
- `'project'` - Project-related tasks
- `'completed'` - Done tasks (good examples)
- `'reference'` - Reference information
- `'detailed'` - Long, detailed notes
- `'simple'` - Short, simple notes

## Output Files

All exports go to `../exports/` directory:
- `graph_data_export_TIMESTAMP.csv` - Full data archive
- `prompt_examples_TIMESTAMP.json` - Selected examples for prompts

## Tips

1. **Work incrementally** - Review and edit small batches
2. **Save frequently** - Use export functions to save progress
3. **Use search** - Find specific types of content quickly
4. **Check quality** - Focus on examples with good summaries and entity extraction
5. **Balance categories** - Include diverse examples in each category

## Next Steps

After exporting prompt examples:
1. Review the JSON structure in `exports/prompt_examples_*.json`
2. Use these examples to create few-shot prompts
3. Test improved prompts in a separate notebook
4. Iterate based on results 