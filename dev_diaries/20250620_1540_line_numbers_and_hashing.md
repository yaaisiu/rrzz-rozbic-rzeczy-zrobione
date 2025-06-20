### Dev Diary: Implementing a Resilient, Hash-Based Ingestion Pipeline

**Date:** 2025-06-20 15:40

#### **Objective:**
Overhaul the data ingestion pipeline to be more efficient and resilient to changes in the source `gtd.txt` file. The goal was to eliminate unnecessary re-processing of notes by the LLM.

---

#### **The Journey**

##### **1. The Initial Problem:**
The original pipeline was a "delete-and-recreate" model. Every time it ran, it wiped the entire graph and re-ingested every single note from scratch. This was incredibly inefficient, especially as the notes file grew, leading to slow processing times and wasted LLM calls.

##### **2. First Iteration: Caching with Line Numbers**
Our first attempt at a solution was to introduce a caching mechanism. The plan was:
-   Add a `content_hash` (a SHA256 hash of the line's content) to each note during parsing.
-   Store this hash along with the `line_number` in the Neo4j graph.
-   On subsequent runs, only process notes where the hash for a given line number had changed.

This worked for simple additions and in-place edits but had a critical flaw: it relied on the `line_number` as a stable identifier. If a line was inserted or deleted in the middle of the file, all subsequent line numbers would shift, causing the system to mistakenly treat every following note as "modified" and re-process them.

##### **3. The Final Solution: A Truly Resilient, Hash-Centric Pipeline**
Recognizing the limitation of using line numbers, we re-engineered the entire process to use the `content_hash` as the **single source of truth** for a note's identity.

**Key Architectural Changes:**

1.  **Unique Constraint:** We programmatically added a unique constraint on the `content_hash` property for all `:GtdNote` nodes in Neo4j. This enforces data integrity and makes lookups by hash extremely fast.
2.  **State Comparison:** The new pipeline now starts by comparing the set of all content hashes in the `gtd.txt` file with the set of all content hashes stored in the graph. This allows it to immediately determine:
    *   **New Notes:** Hashes in the file but not in the graph.
    *   **Deleted Notes:** Hashes in the graph but not in the file.
    *   **Existing Notes:** Hashes present in both.
3.  **Targeted Operations:**
    *   **New notes** are processed by the LLM and added to the graph.
    *   **Deleted notes** are removed from the graph in a single batch operation.
    *   **Existing notes** are **not** re-processed. Instead, their `line_number` property is updated in a separate, efficient batch query to reflect any potential reordering.
4.  **Hierarchy Rebuild:** After all additions, updates, and deletions are complete, the parent-child hierarchy is rebuilt from scratch to ensure it accurately reflects the final state of the notes file.

---

#### **Outcome:**
The ingestion pipeline is now highly efficient and robust. It correctly handles additions, deletions, and reordering of notes, minimizing LLM calls and processing time by only ever working on the precise set of notes that have actually changed. This marks a significant improvement in the project's architecture and usability. 