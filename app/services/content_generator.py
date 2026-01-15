import json
from typing import List, Dict, Any, Optional
from app.services.vector_store import get_retriever
from app.services.prompts import build_prompt_for_content_generation
from app.core.llm import llm
from langchain_core.runnables import RunnablePassthrough
import requests
from app.services.cloudinary_service import upload_image_to_cloudinary
from app.core.config import settings

def traverse_hierarchy(nodes: List[Dict[str, Any]], level: int = 1, parent_topic: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Recursive function to traverse hierarchy topics and flatten them.
    Equivalent to the provided n8n Javascript logic.
    """
    result = []
    
    for node in nodes:
        # Replicating the logic: importantPoints joined by ", " (and trailing comma in orig JS, but standard join here)
        # JS: node.importantPoints.reduce((acc, curr) => acc+curr+", ", "") -> results in "p1, p2, "
        # We will iterate and replicate the exact string format if strict adherence is needed, 
        # but typically clean comma separation is better. 
        # However, to be safe with "convert it", I will do standard join.
        important_points_list = node.get("importantPoints", [])
        if isinstance(important_points_list, list):
             important_points = ", ".join(str(p) for p in important_points_list)
        else:
             important_points = str(important_points_list) if important_points_list else ""

        # Using keys as defined in the user's snippet
        flat_node = {
            "topic": node.get("topic"),
            "level": level,
            "color": node.get("color"),
            "importantPoints": important_points,
            "parentTopic": parent_topic,
            "isImagePresent": node.get("isImagePresent"), # Key from user snippet: isImagePresent
            "imagePrompt": node.get("imagePrompt"),
            "imageDescription": node.get("imageDescription"),
            "imagePath": node.get("imagePath"),
            "node_ref": node  # Keep reference to original node for in-place updates
        }
        result.append(flat_node)

        subtopics = node.get("subtopics", [])
        if subtopics:
            result.extend(traverse_hierarchy(subtopics, level + 1, node.get("topic")))
            
    return result

def process_hierarchy(hierarchy_data: Any) -> List[Dict[str, Any]]:
    """
    Process the hierarchy data (can be JSON string or list).
    """
    if isinstance(hierarchy_data, str):
        try:
            nodes = json.loads(hierarchy_data)
        except json.JSONDecodeError:
            return []
    else:
        nodes = hierarchy_data

    if not isinstance(nodes, list):
        # If it's a dict wrapping the list or something else, handle it? 
        # The user said "items[0].json.hierarchy" which implies hierarchy is the list or object containing it.
        # Assuming hierarchy IS the list of nodes based on "traverse(hierarchy)".
        return []

    return traverse_hierarchy(nodes)

def generate_image_and_upload(prompt: str, topic: str) -> Optional[str]:
    """
    Generates an image via OpenAI DALL-E and stores it in Cloudinary.
    """
    try:
        url = "https://api.openai.com/v1/images/generations"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}"
        }
        payload = {
            "model": "gpt-image-1.5",
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024"
        }
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        image_url = response.json()["data"][0]["url"]
        
        # Download image
        img_response = requests.get(image_url)
        img_response.raise_for_status()
        
        # Upload to Cloudinary
        filename = f"{topic.replace(' ', '_').lower()}.png"
        result = upload_image_to_cloudinary(img_response.content, filename, folder="study_buddy")
        return result.get("url")
    except Exception as e:
        print(f"Error generating or uploading image for topic '{topic}': {e}")
        return None

def generate_html_content(hierarchy_data: Any, document_id: str) -> tuple[str, Any]:
    """
    Generates HTML content for the entire hierarchy by iterating through nodes,
    retrieving context using RAG, and generating HTML sections using LLM.
    Updates hierarchy_data with generated image paths.
    """
    # handle case where hierarchy_data is a string
    if isinstance(hierarchy_data, str):
        try:
            nodes_tree = json.loads(hierarchy_data)
        except json.JSONDecodeError:
            nodes_tree = []
    else:
        nodes_tree = hierarchy_data

    flat_nodes = traverse_hierarchy(nodes_tree)
    accumulated_html = ""
    
    # helper for formatting docs
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # Get retriever for the specific document
    retriever = get_retriever(namespace=document_id)
    
    # Get the prompt template
    prompt_template = build_prompt_for_content_generation()
    
    # The chain: Prompt -> LLM
    chain = prompt_template | llm

    for node in flat_nodes:
        topic = node.get("topic", "")
        important_points = node.get("importantPoints", "")
        parent_topic = node.get("parentTopic", "") or ""
        level = node.get("level", 1)
        
        # Image Logic
        is_image_present = node.get("isImagePresent")
        image_path = node.get("imagePath")
        image_prompt = node.get("imagePrompt") or topic
        
        if is_image_present and not image_path:
            # Generate and upload image
            new_image_url = generate_image_and_upload(image_prompt, topic)
            if new_image_url:
                image_path = new_image_url
                # Update original node in tree
                node["node_ref"]["imagePath"] = new_image_url
        
        image_url_to_pass = image_path if image_path else "null"

        # 1. Generate Query for RAG
        rag_query = (
            f"Explain: {topic}\n"
            f"Important Points should not miss: {important_points}\n"
            f"Explain its role in: {parent_topic}"
        )

        # 2. Retrieve Context
        retrieved_docs = retriever.invoke(rag_query)
        context_str = format_docs(retrieved_docs)

        # 3. Invoke LLM Chain
        response = chain.invoke({
            "context": context_str,
            "topic": topic,
            "level": level,
            "importantPoints": important_points,
            "parentTopic": parent_topic,
            "imageUrl": image_url_to_pass
        })
        
        # 4. Accumulate HTML
        if response.content:
            accumulated_html += response.content.strip()

    return accumulated_html, nodes_tree
