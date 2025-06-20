### **Plan: Incremental Graph Ingestion with Content Hashing**

#### **Objective:**

Modify the data ingestion pipeline to only process new or changed notes. This will be achieved by storing a content hash for each note in the Neo4j graph and comparing it against the current file content.

### ---

**Step 1: Modify file\_parser.py to Generate Content Hashes**

**File:** src/backend/file\_parser.py

Action:  
Update the file parser to calculate a unique hash for each line of content and include it in the Note object.

1. **Import the hashlib module.**  
2. **Modify the Note NamedTuple** to include a content\_hash field.  
3. **Update the parse\_line function** to calculate a SHA256 hash of the raw line before stripping tags and add it to the Note object.

Python

\# src/backend/file\_parser.py

import re  
from typing import List, NamedTuple  
import hashlib \# 1\. IMPORT HASHLIB

\# 2\. UPDATE THE NOTE NAMEDTUPLE  
class Note(NamedTuple):  
    content: str  
    indentation: int  
    tags: List\[str\]  
    line\_number: int  
    date\_str: str  
    content\_hash: str \# ADD THIS FIELD

def get\_indentation(line: str) \-\> int:  
    """Calculates the indentation level of a line based on leading spaces."""  
    return len(line) \- len(line.lstrip(' '))

\# 3\. UPDATE PARSE\_LINE  
def parse\_line(line: str, line\_number: int, current\_date: str) \-\> Note:  
    """Parses a single line into a Note object."""  
    indentation \= get\_indentation(line)  
    content \= line.strip()  
    tags \= re.findall(r"\#(\\w+)", content)  
    \# Remove tags from content  
    content\_without\_tags \= re.sub(r"\\s\*\#\\w+", "", content).strip()  
    \# Calculate hash from the original stripped line content  
    content\_hash \= hashlib.sha256(content.encode('utf-8')).hexdigest()  
    return Note(  
        content=content\_without\_tags,  
        indentation=indentation,  
        tags=tags,  
        line\_number=line\_number,  
        date\_str=current\_date,  
        content\_hash=content\_hash \# ADD HASH TO NOTE  
    )

def parse\_file(file\_path: str) \-\> List\[Note\]:  
    """Reads a file and parses it into a list of Note objects."""  
    notes: List\[Note\] \= \[\]  
    current\_date\_str \= "unknown"  
    \# Regex to find lines like "dd.mm" or "dd.mm."  
    date\_pattern \= re.compile(r"^\\s\*(\\d{1,2}\\.\\d{1,2})\\.?\\s\*$")

    with open(file\_path, 'r') as f:  
        for i, line in enumerate(f):  
            \# Check if the line is a date  
            match \= date\_pattern.match(line)  
            if match:  
                current\_date\_str \= match.group(1)  
                continue  \# Skip adding the date line as a note itself

            if line.strip():  \# Ignore empty lines  
                notes.append(parse\_line(line.rstrip('\\n'), i \+ 1, current\_date\_str))  
    return notes

### ---

**Step 2: Overhaul graph\_ingestion\_service.py for Caching Logic**

**File:** src/backend/graph\_ingestion\_service.py

Action:  
This is the main part of the implementation. We will replace the "delete-and-recreate" logic with an "update-in-place" logic.

1. **Remove clear\_gtd\_notes method.** It will be replaced by a more precise cleanup function.  
2. **Modify ingest\_notes method.** This method will now contain the core caching logic. It will compare hashes and only process notes that are new or have been modified. It will also store the content\_hash on the graph node.  
3. **Add a new \_cleanup\_deleted\_notes method.** This will run after processing to remove notes from the graph that are no longer in the source file.  
4. **Update the main ingest\_gtd\_file orchestrator method** to call the new and modified methods in the correct order.

Python

\# src/backend/graph\_ingestion\_service.py

import logging  
import json  
import re  
from typing import List, Dict, Any

from src.backend.file\_parser import parse\_file, Note  
from src.graph.neo4j\_client import Neo4jClient  
from src.llm.base import BaseLLM

logger \= logging.getLogger(\_\_name\_\_)

class GraphIngestionService:  
    def \_\_init\_\_(self, neo4j\_client: Neo4jClient, llm\_client: BaseLLM):  
        self.client \= neo4j\_client  
        self.llm\_client \= llm\_client

    \# 1\. THE clear\_gtd\_notes METHOD IS REMOVED.

    def \_get\_llm\_metadata(self, note: Note) \-\> Dict\[str, Any\]:  
        """Gets metadata for a note from the LLM."""  
        prompt \= f"""  
        Analyze the following note content and extract structured metadata.  
        The content is: "{note.content}"  
        Respond with a JSON object containing:  
        \- "entities": a list of named entities. Each entity should be an object with "name" and "type" (e.g., "Person", "Project", "Technology").  
        \- "summary": a one-sentence summary of the note.  
          
        Example response for "Discuss budget with @john for \#project-alpha":  
        {{  
          "entities": \[  
            {{"name": "John", "type": "Person"}},  
            {{"name": "Project Alpha", "type": "Project"}}  
          \],  
          "summary": "A task to discuss the budget for Project Alpha with John."  
        }}

        Your response must be only the JSON object.  
        Note content: "{note.content}"  
        """  
        llm\_response\_str \= self.llm\_client.generate(prompt)  
          
        try:  
            \# Use regex to find the JSON block, even if it's wrapped in markdown  
            json\_match \= re.search(r'{.\*}', llm\_response\_str, re.DOTALL)  
            if json\_match:  
                json\_str \= json\_match.group(0)  
                return json.loads(json\_str)  
            else:  
                logger.warning(f"Could not find a JSON object in the LLM response for line {note.line\_number}: {llm\_response\_str}")  
                return {}  
        except json.JSONDecodeError:  
            logger.warning(f"Failed to parse LLM response as JSON for line {note.line\_number}, even after cleaning: {llm\_response\_str}")  
            return {}

    \# 2\. MODIFY ingest\_notes  
    def ingest\_notes(self, notes: List\[Note\]) \-\> List\[str\]:  
        """  
        Ingests a list of notes using caching. Only new or modified notes are processed by the LLM.  
        """  
        \# Fetch existing notes and their hashes from the graph  
        query\_existing \= "MATCH (n:GtdNote) RETURN n.line\_number AS line\_number, n.content\_hash AS content\_hash"  
        existing\_notes\_raw \= self.client.execute\_query(query\_existing)  
        existing\_notes \= {item\['line\_number'\]: item\['content\_hash'\] for item in existing\_notes\_raw}

        notes\_to\_process: List\[Note\] \= \[\]  
        for note in notes:  
            if note.line\_number not in existing\_notes or existing\_notes\[note.line\_number\] \!= note.content\_hash:  
                notes\_to\_process.append(note)  
          
        logger.info(f"Found {len(notes)} total notes. Processing {len(notes\_to\_process)} new or modified notes.")

        node\_ids: List\[str\] \= \[\]  
        if not notes\_to\_process:  
            logger.info("No new or modified notes to process.")  
            return \[\]

        for i, note in enumerate(notes\_to\_process):  
            logger.info(f"\[{i+1}/{len(notes\_to\_process)}\] Processing note from {note.date\_str} (line {note.line\_number})")

            llm\_metadata \= self.\_get\_llm\_metadata(note)

            query \= """  
            MERGE (d:Day {date: $date\_str})  
            MERGE (n:GtdNote {line\_number: $line\_number})  
            ON CREATE SET   
                n.content \= $content,   
                n.content\_hash \= $content\_hash,  
                n.llm\_summary \= $llm\_summary,   
                n.created\_at \= datetime()  
            ON MATCH SET   
                n.content \= $content,   
                n.content\_hash \= $content\_hash,  
                n.llm\_summary \= $llm\_summary,   
                n.updated\_at \= datetime()  
            MERGE (n)-\[:RECORDED\_ON\]-\>(d)  
            WITH n, $tags as tags, $entities as entities  
            OPTIONAL MATCH (n)-\[r:HAS\_TAG\]-\>() DELETE r  
            OPTIONAL MATCH (n)-\[r2:MENTIONS\]-\>() DELETE r2  
            WITH n, tags, entities  
            FOREACH (tag\_name IN tags |  
                MERGE (t:Tag {name: tag\_name})  
                MERGE (n)-\[:HAS\_TAG\]-\>(t)  
            )  
            FOREACH (entity IN entities |  
                MERGE (e:Entity {name: entity.name})  
                ON CREATE SET e.type \= entity.type  
                MERGE (n)-\[:MENTIONS\]-\>(e)  
            )  
            RETURN elementId(n) as node\_id  
            """  
            params \= {  
                "date\_str": note.date\_str,  
                "line\_number": note.line\_number,  
                "content": note.content,  
                "content\_hash": note.content\_hash,  
                "llm\_summary": llm\_metadata.get("summary", ""),  
                "tags": note.tags,  
                "entities": llm\_metadata.get("entities", \[\])  
            }  
            result \= self.client.execute\_query(query, params)  
            if result:  
                node\_ids.append(result\[0\]\['node\_id'\])  
          
        logger.info(f"Finished processing {len(notes\_to\_process)} notes.")  
        return node\_ids

    \# 3\. ADD \_cleanup\_deleted\_notes  
    def \_cleanup\_deleted\_notes(self, notes: List\[Note\]):  
        """Removes notes from the graph that are no longer in the source file."""  
        if not notes:  
            return

        current\_line\_numbers \= \[note.line\_number for note in notes\]  
        logger.info(f"Cleaning up notes that are no longer in the source file.")  
          
        \# Delete notes no longer present  
        query\_delete \= "MATCH (n:GtdNote) WHERE NOT n.line\_number IN $line\_numbers DETACH DELETE n"  
        self.client.execute\_query(query\_delete, {"line\_numbers": current\_line\_numbers})  
          
        \# Delete orphaned tags, entities, and days  
        query\_orphans \= """  
        MATCH (n)  
        WHERE (n:Tag OR n:Entity OR n:Day) AND NOT (n)--()  
        DELETE n  
        """  
        self.client.execute\_query(query\_orphans)  
        logger.info("Successfully cleaned up deleted and orphaned nodes.")

    def build\_hierarchy(self, notes: List\[Note\]):  
        """Builds HAS\_CHILD relationships based on indentation."""  
        logger.info("Building note hierarchy.")  
        \# This requires node elementIds, which are not stable. A better way is to match on line\_number.  
        parent\_stack \= \[\]  \# Stack of (indentation, line\_number)

        for note in notes:  
            while parent\_stack and parent\_stack\[-1\]\[0\] \>= note.indentation:  
                parent\_stack.pop()

            if parent\_stack:  
                parent\_line\_number \= parent\_stack\[-1\]\[1\]  
                query \= """  
                MATCH (parent:GtdNote {line\_number: $parent\_line\_number})  
                MATCH (child:GtdNote {line\_number: $child\_line\_number})  
                MERGE (parent)-\[:HAS\_CHILD\]-\>(child)  
                """  
                params \= {"parent\_line\_number": parent\_line\_number, "child\_line\_number": note.line\_number}  
                self.client.execute\_query(query, params)

            parent\_stack.append((note.indentation, note.line\_number))  
        logger.info("Successfully built note hierarchy.")

    \# 4\. UPDATE ingest\_gtd\_file  
    def ingest\_gtd\_file(self, file\_path: str):  
        """  
        Parses a gtd file and incrementally updates the graph.  
        """  
        logger.info(f"Starting ingestion for file: {file\_path}")  
        \# 1\. Parse the file  
        notes \= parse\_file(file\_path)

        \# 2\. Ingest new and modified notes  
        self.ingest\_notes(notes)

        \# 3\. Clean up notes that were deleted from the file  
        self.\_cleanup\_deleted\_notes(notes)

        \# 4\. Rebuild the entire hierarchy to ensure correctness  
        if notes:  
            \# First, clear all existing hierarchy relationships  
            self.client.execute\_query("MATCH ()-\[r:HAS\_CHILD\]-\>() DELETE r")  
            self.build\_hierarchy(notes)  
          
        logger.info(f"Finished ingestion for file: {file\_path}")  
