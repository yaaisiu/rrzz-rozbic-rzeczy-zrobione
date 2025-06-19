# Neo4j Browser Connection Guide

## 🔐 **Neo4j Credentials**

**URL**: http://localhost:7474  
**Username**: `neo4j`  
**Password**: `password`

---

## 🌐 **How to Connect**

1. **Open Neo4j Browser**: Navigate to http://localhost:7474 in your web browser

2. **Connection Form**: You'll see a connection form with these fields:
   - **Connect URL**: `neo4j://localhost:7687` (should be pre-filled)
   - **Username**: Enter `neo4j`
   - **Password**: Enter `password`

3. **Click "Connect"**

---

## 📊 **Database Status**

✅ **Database**: `neo4j` (default database)  
✅ **Nodes**: 33 nodes currently stored  
✅ **Data**: Notes and related entities are present  

---

## 🔍 **Sample Queries to Try**

Once connected, you can run these queries in the Neo4j Browser:

### 1. **Count All Nodes**
```cypher
MATCH (n) 
RETURN count(n) as total_nodes
```

### 2. **Show All Note Types**
```cypher
MATCH (n) 
RETURN DISTINCT labels(n) as node_types
```

### 3. **View Recent Notes**
```cypher
MATCH (n:Note) 
RETURN n.content, n.note_id, n.processed_at 
ORDER BY n.processed_at DESC 
LIMIT 5
```

### 4. **Explore Note Relationships**
```cypher
MATCH (n:Note)-[r]-(m) 
RETURN n, r, m 
LIMIT 20
```

### 5. **Find Notes with Tags**
```cypher
MATCH (n:Note)-[:HAS_TAG]->(t:Tag) 
RETURN n.content, collect(t.name) as tags
```

### 6. **Visual Graph View**
```cypher
MATCH (n:Note)-[r]-(m)
RETURN n, r, m
LIMIT 50
```

---

## 🎯 **Sample Data Found**

Your database currently contains notes like:
- "I need to finish the Python project by Friday..."
- "Meeting with John tomorrow at 2 PM..."
- "Remember to buy groceries: milk, bread, eggs..."

---

## 🛠️ **Troubleshooting**

### If Connection Fails:

1. **Check Service Status**:
   ```bash
   docker-compose ps
   ```

2. **Verify Neo4j is Running**:
   ```bash
   curl http://localhost:7474
   ```

3. **Check Neo4j Logs**:
   ```bash
   docker-compose logs neo4j --tail=10
   ```

4. **Test Direct Connection**:
   ```bash
   docker exec -it rrzz-rozbic-rzeczy-zrobione-neo4j-1 cypher-shell -u neo4j -p password
   ```

### Common Issues:

- **"Authentication failed"**: Make sure you're using `neo4j` / `password`
- **"Connection refused"**: Check if Neo4j container is running
- **"No data visible"**: Try the sample queries above to verify data exists

---

## 🎨 **Neo4j Browser Features**

Once connected, you can:

- **Run Cypher queries** in the command bar
- **Visualize graphs** with interactive node/relationship diagrams  
- **Explore data** by clicking on nodes and relationships
- **Export results** as JSON, CSV, or images
- **Save queries** for later use
- **View database schema** and statistics

---

## 📝 **Quick Start Commands**

After connecting, try these commands in order:

1. `:help` - Show help information
2. `:schema` - View database schema
3. `MATCH (n) RETURN n LIMIT 25` - See your data
4. `:play start` - Interactive tutorial

---

## 🚀 **Next Steps**

1. Connect to Neo4j Browser using the credentials above
2. Run the sample queries to explore your data
3. Try adding more notes through the Streamlit frontend (http://localhost:8501)
4. Watch how the graph grows as you add more content!

---

## 📞 **Support**

If you still can't connect:
- Verify all Docker containers are running: `docker-compose ps`
- Check the SYSTEM_STATUS_REPORT.md for troubleshooting commands
- The credentials are definitely: `neo4j` / `password` 