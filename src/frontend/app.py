import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import time
import os

# Configuration
API_BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="rrzz-rozbic-rzeczy-zrobione",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .note-card {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .tag {
        background-color: #007bff;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 12px;
        font-size: 0.8rem;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        display: inline-block;
    }
    .entity {
        background-color: #28a745;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 12px;
        font-size: 0.8rem;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        display: inline-block;
    }
    .highlight {
        background-color: #ffc107;
        color: #212529;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.9rem;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        display: inline-block;
    }
    .status-success {
        color: #28a745;
        font-weight: bold;
    }
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
    .status-processing {
        color: #ffc107;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def check_api_health() -> Dict[str, Any]:
    """Check API health status."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "error": str(e)}


def ingest_note(content: str, title: Optional[str] = None, tags: Optional[List[str]] = None) -> Dict[str, Any]:
    """Ingest a note through the API."""
    try:
        payload = {
            "content": content,
            "title": title,
            "tags": tags or []
        }
        response = requests.post(f"{API_BASE_URL}/notes", json=payload, timeout=30)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "error": str(e)}


def search_notes(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search notes through the API."""
    try:
        payload = {"query": query, "limit": limit}
        response = requests.post(f"{API_BASE_URL}/notes/search", json=payload, timeout=10)
        return response.json()
    except requests.exceptions.RequestException as e:
        return []


def get_note(note_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific note by ID."""
    try:
        response = requests.get(f"{API_BASE_URL}/notes/{note_id}", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException:
        return None


def display_note(note: Dict[str, Any]):
    """Display a note with all its metadata."""
    with st.container():
        st.markdown(f"""
        <div class="note-card">
            <h4>📝 Note ID: {note.get('note_id', 'N/A')}</h4>
            <p><strong>Content:</strong></p>
            <p>{note.get('content', 'No content')}</p>
            
            <p><strong>Tags:</strong></p>
            <div>
        """, unsafe_allow_html=True)
        
        # Display tags
        for tag in note.get('tags', []):
            st.markdown(f'<span class="tag">🏷️ {tag}</span>', unsafe_allow_html=True)
        
        st.markdown("</div><p><strong>Entities:</strong></p><div>", unsafe_allow_html=True)
        
        # Display entities
        for entity in note.get('entities', []):
            entity_type = entity.get('type', 'unknown')
            entity_value = entity.get('value', 'unknown')
            st.markdown(f'<span class="entity">🔍 {entity_type}: {entity_value}</span>', unsafe_allow_html=True)
        
        st.markdown("</div><p><strong>Highlights:</strong></p><div>", unsafe_allow_html=True)
        
        # Display highlights
        for highlight in note.get('highlights', []):
            st.markdown(f'<span class="highlight">💡 {highlight}</span>', unsafe_allow_html=True)
        
        # Status and timestamp
        status = note.get('status', 'unknown')
        status_class = 'status-success' if status == 'success' else 'status-error' if status == 'error' else 'status-processing'
        processed_at = note.get('processed_at', 'Unknown')
        
        st.markdown(f"""
        </div>
        <p><strong>Status:</strong> <span class="{status_class}">{status.upper()}</span></p>
        <p><strong>Processed:</strong> {processed_at}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()


def main():
    """Main Streamlit application."""
    st.markdown('<h1 class="main-header">📝 rrzz-rozbic-rzeczy-zrobione</h1>', unsafe_allow_html=True)
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["🏠 Home", "📝 Add Note", "🔍 Search Notes", "📊 System Status"]
    )
    
    # Check API health
    health_status = check_api_health()
    
    # Display health status in sidebar
    st.sidebar.subheader("System Status")
    if health_status.get("status") == "ok":
        st.sidebar.success("✅ API Connected")
        if health_status.get("neo4j") == "healthy":
            st.sidebar.success("✅ Neo4j Connected")
        else:
            st.sidebar.error("❌ Neo4j Issues")
    else:
        st.sidebar.error("❌ API Connection Failed")
        st.sidebar.error(f"Error: {health_status.get('error', 'Unknown error')}")
    
    # Page routing
    if page == "🏠 Home":
        show_home_page()
    elif page == "📝 Add Note":
        show_add_note_page()
    elif page == "🔍 Search Notes":
        show_search_page()
    elif page == "📊 System Status":
        show_status_page(health_status)


def show_home_page():
    """Display the home page with recent activity."""
    st.header("🏠 Welcome to Your Knowledge Graph")
    
    st.markdown("""
    This application helps you organize your thoughts and notes using AI-powered tagging, 
    entity extraction, and knowledge graph storage.
    
    ### What you can do:
    - **📝 Add Notes**: Create new notes with automatic AI processing
    - **🔍 Search**: Find notes by content, tags, or entities
    - **📊 Visualize**: Explore connections in your knowledge graph
    - **🏷️ Auto-tagging**: Get automatic tags and entity extraction
    """)
    
    # Quick stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("API Status", "✅ Connected" if check_api_health().get("status") == "ok" else "❌ Disconnected")
    
    with col2:
        st.metric("Neo4j Status", "✅ Connected" if check_api_health().get("neo4j") == "healthy" else "❌ Issues")
    
    with col3:
        st.metric("Processing Ready", "✅ Ready" if check_api_health().get("status") == "ok" else "❌ Not Ready")
    
    st.divider()
    
    # Quick note input
    st.subheader("🚀 Quick Note")
    with st.form("quick_note_form"):
        quick_content = st.text_area("Enter a quick note:", height=100)
        submitted = st.form_submit_button("📝 Add Note")
        
        if submitted and quick_content.strip():
            with st.spinner("Processing your note..."):
                result = ingest_note(quick_content)
                
                if result.get("status") == "success":
                    st.success("✅ Note processed successfully!")
                    display_note(result)
                else:
                    st.error(f"❌ Error processing note: {result.get('error', 'Unknown error')}")


def show_add_note_page():
    """Display the add note page with full form."""
    st.header("📝 Add New Note")
    
    with st.form("add_note_form"):
        st.subheader("Note Details")
        
        # Title (optional)
        title = st.text_input("Title (optional):")
        
        # Content
        content = st.text_area("Note Content:", height=200, placeholder="Enter your note here...")
        
        # Tags (optional)
        tags_input = st.text_input("Tags (comma-separated, optional):", placeholder="e.g., work, ideas, todo")
        tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()] if tags_input else []
        
        # Submit button
        submitted = st.form_submit_button("📝 Process Note")
        
        if submitted:
            if not content.strip():
                st.error("❌ Please enter some content for your note.")
            else:
                # Show processing status
                with st.spinner("🤖 Processing note with AI..."):
                    # Add a progress bar for better UX
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Simulate processing steps
                    status_text.text("📝 Saving note...")
                    progress_bar.progress(25)
                    time.sleep(0.5)
                    
                    status_text.text("🤖 Analyzing with AI...")
                    progress_bar.progress(50)
                    time.sleep(0.5)
                    
                    status_text.text("🏷️ Extracting tags and entities...")
                    progress_bar.progress(75)
                    time.sleep(0.5)
                    
                    status_text.text("💾 Storing in knowledge graph...")
                    progress_bar.progress(90)
                    
                    # Actually process the note
                    result = ingest_note(content, title, tags)
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Complete!")
                    time.sleep(1)
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Display results
                    if result.get("status") == "success":
                        st.success("🎉 Note processed successfully!")
                        
                        # Display the processed note
                        st.subheader("📋 Processed Note")
                        display_note(result)
                        
                        # Show what was extracted
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("🏷️ Extracted Tags")
                            if result.get('tags'):
                                for tag in result['tags']:
                                    st.markdown(f'<span class="tag">🏷️ {tag}</span>', unsafe_allow_html=True)
                            else:
                                st.info("No tags extracted")
                        
                        with col2:
                            st.subheader("🔍 Extracted Entities")
                            if result.get('entities'):
                                for entity in result['entities']:
                                    entity_type = entity.get('type', 'unknown')
                                    entity_value = entity.get('value', 'unknown')
                                    st.markdown(f'<span class="entity">🔍 {entity_type}: {entity_value}</span>', unsafe_allow_html=True)
                            else:
                                st.info("No entities extracted")
                        
                        # Show highlights
                        if result.get('highlights'):
                            st.subheader("💡 Key Highlights")
                            for highlight in result['highlights']:
                                st.markdown(f'<span class="highlight">💡 {highlight}</span>', unsafe_allow_html=True)
                        
                    else:
                        st.error(f"❌ Error processing note: {result.get('error', 'Unknown error')}")
                        
                        # Show error details
                        with st.expander("🔍 Error Details"):
                            st.json(result)


def show_search_page():
    """Display the search page."""
    st.header("🔍 Search Notes")
    
    # Search form
    with st.form("search_form"):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_query = st.text_input("Search query:", placeholder="Enter keywords, tags, or content to search...")
        
        with col2:
            search_limit = st.number_input("Limit results:", min_value=1, max_value=50, value=10)
        
        search_submitted = st.form_submit_button("🔍 Search")
    
    # Search results
    if search_submitted and search_query.strip():
        with st.spinner("🔍 Searching..."):
            results = search_notes(search_query, search_limit)
            
            if results:
                st.success(f"✅ Found {len(results)} notes")
                
                # Display search results
                for i, note in enumerate(results, 1):
                    with st.expander(f"📝 Note {i}: {note.get('content', 'No content')[:100]}..."):
                        display_note(note)
            else:
                st.info("🔍 No notes found matching your search criteria.")
                st.markdown("""
                **Tips for better search results:**
                - Try different keywords
                - Search for specific tags
                - Use entity names
                - Try partial matches
                """)
    
    # Recent notes section
    st.divider()
    st.subheader("📋 Recent Notes")
    
    # For now, show a placeholder since the list endpoint returns empty
    st.info("📊 Recent notes feature coming soon! Use the search function to find your notes.")


def show_status_page(health_status: Dict[str, Any]):
    """Display system status and health information."""
    st.header("📊 System Status")
    
    # Overall status
    if health_status.get("status") == "ok":
        st.success("✅ System is healthy and operational")
    else:
        st.error("❌ System has issues")
    
    # Detailed status
    st.subheader("🔧 Service Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("API Status", health_status.get("status", "unknown").upper())
        st.metric("Neo4j Status", health_status.get("neo4j", "unknown").upper())
        st.metric("Ingestion Service", health_status.get("ingestion_service", "unknown").upper())
    
    with col2:
        # Connection test
        st.subheader("🔗 Connection Test")
        if st.button("🔄 Test Connections"):
            with st.spinner("Testing connections..."):
                test_result = check_api_health()
                if test_result.get("status") == "ok":
                    st.success("✅ All connections successful!")
                else:
                    st.error(f"❌ Connection failed: {test_result.get('error', 'Unknown error')}")
    
    # System information
    st.subheader("ℹ️ System Information")
    
    with st.expander("📋 API Endpoints"):
        st.markdown("""
        **Available Endpoints:**
        - `POST /notes` - Ingest a single note
        - `POST /notes/batch` - Ingest multiple notes
        - `GET /notes/{note_id}` - Retrieve a specific note
        - `POST /notes/search` - Search notes
        - `GET /notes` - List recent notes
        - `GET /health` - Health check
        """)
    
    with st.expander("🔍 Raw Health Data"):
        st.json(health_status)
    
    # Troubleshooting
    st.subheader("🛠️ Troubleshooting")
    
    if health_status.get("status") != "ok":
        st.warning("""
        **If you're experiencing issues:**
        
        1. **Check Docker containers**: Make sure all services are running
        2. **Verify ports**: Ensure ports 8000, 7474, 8501 are available
        3. **Check logs**: Review container logs for errors
        4. **Restart services**: Try restarting the Docker containers
        
        **Common commands:**
        ```bash
        # Check container status
        docker-compose ps
        
        # View logs
        docker-compose logs
        
        # Restart services
        docker-compose restart
        ```
        """)


if __name__ == "__main__":
    main() 