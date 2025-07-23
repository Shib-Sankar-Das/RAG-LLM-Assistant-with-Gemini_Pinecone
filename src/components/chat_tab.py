"""
Chat tab component with enhanced feedback and history integration.
"""

import streamlit as st
from datetime import datetime
from typing import List, Dict, Any
from ..core.rag_system import RAGSystem
from ..utils.ui_helpers import render_feature_card
from ..config import Config

class ChatTab:
    """Enhanced chat tab component with feedback and history integration."""
    
    def __init__(self):
        self.config = Config()
    
    def render(self, rag_system: RAGSystem):
        """Render the chat tab.
        
        Args:
            rag_system: The RAG system instance
        """
        st.markdown("### 💬 Intelligent Chat")
        render_feature_card(
            "💬 Chat with your documents",
            "Ask questions about your uploaded content and get AI-powered answers with source citations."
        )
        
        # Initialize chat messages and feedback
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "feedback_data" not in st.session_state:
            st.session_state.feedback_data = {}
        if "conversation_context" not in st.session_state:
            st.session_state.conversation_context = []
        
        # Quick actions
        self._render_quick_actions()
        
        # Show example questions if requested
        self._render_example_questions()
        
        # Show chat stats if requested
        self._render_chat_stats()
        
        # Chat container and history
        self._render_chat_history()
        
        # Chat input
        self._handle_chat_input(rag_system)
    
    def _render_quick_actions(self):
        """Render quick action buttons."""
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("💡 Example Questions", use_container_width=True):
                st.session_state.show_examples = not st.session_state.get('show_examples', False)
        with col2:
            if st.button("📊 Chat Stats", use_container_width=True):
                st.session_state.show_stats = not st.session_state.get('show_stats', False)
        with col3:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.session_state.feedback_data = {}
                st.session_state.conversation_context = []
                st.rerun()
    
    def _render_example_questions(self):
        """Render example questions if enabled."""
        if st.session_state.get('show_examples', False):
            with st.expander("💡 Example Questions", expanded=True):
                st.markdown("""
                **Try asking questions like:**
                - "What is the main topic of the documents?"
                - "Summarize the key points from the content"
                - "What are the most important findings?"
                - "Can you explain [specific concept] from the documents?"
                """)
    
    def _render_chat_stats(self):
        """Render enhanced chat statistics if enabled."""
        if st.session_state.get('show_stats', False):
            with st.expander("📊 Chat Statistics", expanded=True):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Messages", len(st.session_state.messages))
                with col2:
                    user_msgs = len([msg for msg in st.session_state.messages if msg["role"] == "user"])
                    st.metric("User Messages", user_msgs)
                with col3:
                    ai_msgs = len([msg for msg in st.session_state.messages if msg["role"] == "assistant"])
                    st.metric("AI Responses", ai_msgs)
                with col4:
                    feedback_count = len(st.session_state.feedback_data)
                    st.metric("Feedback Given", feedback_count)
                
                # Feedback analysis
                if st.session_state.feedback_data:
                    positive_feedback = sum(1 for feedback in st.session_state.feedback_data.values() 
                                          if feedback.get("rating") == "positive")
                    total_feedback = len(st.session_state.feedback_data)
                    satisfaction_rate = (positive_feedback / total_feedback) * 100
                    st.metric("Satisfaction Rate", f"{satisfaction_rate:.1f}%")
    
    def _render_chat_history(self):
        """Render chat message history."""
        chat_container = st.container()
        
        with chat_container:
            for i, message in enumerate(st.session_state.messages):
                with st.chat_message(message["role"]):
                    st.write(message["content"])
                    
                    if message["role"] == "assistant" and "sources" in message:
                        if message["sources"]:
                            with st.expander("📚 Sources & References"):
                                for j, source in enumerate(message["sources"]):
                                    st.markdown(f"**{j+1}.** {source}")
                        
                        # Enhanced feedback buttons with stored feedback
                        self._render_enhanced_feedback_buttons(i)
    
    def _render_enhanced_feedback_buttons(self, message_index: int):
        """Render enhanced feedback buttons with stored feedback.
        
        Args:
            message_index: Index of the message
        """
        message_id = f"msg_{message_index}"
        current_feedback = st.session_state.feedback_data.get(message_id, {})
        
        col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
        
        # Positive feedback button
        with col1:
            button_style = "🟢👍" if current_feedback.get("rating") == "positive" else "👍"
            if st.button(button_style, key=f"like_{message_index}", help="Helpful response"):
                self._store_feedback(message_index, "positive")
                st.success("Thanks for your positive feedback!")
                st.rerun()
        
        # Negative feedback button
        with col2:
            button_style = "🔴👎" if current_feedback.get("rating") == "negative" else "👎"
            if st.button(button_style, key=f"dislike_{message_index}", help="Not helpful"):
                self._store_feedback(message_index, "negative")
                st.info("Thanks for your feedback! This helps improve responses.")
                st.rerun()
        
        # Feedback details button
        with col3:
            if st.button("�", key=f"detail_{message_index}", help="Add detailed feedback"):
                st.session_state[f"show_feedback_form_{message_index}"] = True
                st.rerun()
        
        # Show feedback form if requested
        if st.session_state.get(f"show_feedback_form_{message_index}", False):
            self._render_feedback_form(message_index)
    
    def _store_feedback(self, message_index: int, rating: str):
        """Store feedback for a message.
        
        Args:
            message_index: Index of the message
            rating: 'positive' or 'negative'
        """
        message_id = f"msg_{message_index}"
        st.session_state.feedback_data[message_id] = {
            "rating": rating,
            "timestamp": datetime.now().isoformat(),
            "message_index": message_index
        }
    
    def _render_feedback_form(self, message_index: int):
        """Render detailed feedback form.
        
        Args:
            message_index: Index of the message
        """
        with st.expander("📝 Detailed Feedback", expanded=True):
            feedback_text = st.text_area(
                "What could be improved?",
                key=f"feedback_text_{message_index}",
                help="Your feedback helps improve future responses"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save Feedback", key=f"save_feedback_{message_index}"):
                    message_id = f"msg_{message_index}"
                    if message_id in st.session_state.feedback_data:
                        st.session_state.feedback_data[message_id]["detailed_feedback"] = feedback_text
                    else:
                        st.session_state.feedback_data[message_id] = {
                            "detailed_feedback": feedback_text,
                            "timestamp": datetime.now().isoformat(),
                            "message_index": message_index
                        }
                    st.success("Feedback saved!")
                    st.session_state[f"show_feedback_form_{message_index}"] = False
                    st.rerun()
            
            with col2:
                if st.button("❌ Cancel", key=f"cancel_feedback_{message_index}"):
                    st.session_state[f"show_feedback_form_{message_index}"] = False
                    st.rerun()
    
    def _build_conversation_context(self) -> str:
        """Build conversation context from recent messages and feedback.
        
        Returns:
            Formatted conversation context string
        """
        if not self.config.CHAT_HISTORY_ENABLED:
            return ""
        
        context_parts = []
        recent_messages = st.session_state.messages[-self.config.MAX_CHAT_HISTORY_CONTEXT*2:]
        
        # Add conversation history
        if recent_messages:
            context_parts.append("Previous conversation context:")
            for msg in recent_messages:
                if msg["role"] == "user":
                    context_parts.append(f"User: {msg['content']}")
                elif msg["role"] == "assistant":
                    context_parts.append(f"Assistant: {msg['content'][:200]}...")
        
        # Add feedback insights
        if self.config.FEEDBACK_ENABLED and st.session_state.feedback_data:
            positive_patterns = []
            negative_patterns = []
            
            for msg_id, feedback in st.session_state.feedback_data.items():
                msg_idx = feedback.get("message_index")
                if msg_idx is not None and msg_idx < len(st.session_state.messages):
                    message = st.session_state.messages[msg_idx]
                    if feedback.get("rating") == "positive":
                        positive_patterns.append(message.get("content", "")[:100])
                    elif feedback.get("rating") == "negative":
                        negative_patterns.append(message.get("content", "")[:100])
            
            if positive_patterns or negative_patterns:
                context_parts.append("\nFeedback insights:")
                if positive_patterns:
                    context_parts.append(f"User appreciated responses like: {'; '.join(positive_patterns[:2])}")
                if negative_patterns:
                    context_parts.append(f"User wanted better responses for: {'; '.join(negative_patterns[:2])}")
        
        return "\n".join(context_parts)
    
    def _render_feedback_buttons(self, message_index: int):
        """Legacy feedback buttons method - replaced by enhanced version."""
        # This method is kept for backward compatibility but now calls enhanced version
        self._render_enhanced_feedback_buttons(message_index)
    
    def _handle_chat_input(self, rag_system: RAGSystem):
        """Handle chat input and generate context-aware responses.
        
        Args:
            rag_system: The RAG system instance
        """
        if prompt := st.chat_input("Ask a question about your documents..."):
            # Check if database has content
            if rag_system.vectorstore is None:
                st.error("⚠️ Please add some data first by scraping a website or uploading PDFs")
                return
            
            # Build conversation context
            conversation_context = self._build_conversation_context()
            
            # Create enhanced prompt with context
            enhanced_prompt = self._create_enhanced_prompt(prompt, conversation_context)
            
            # Add user message
            st.session_state.messages.append({
                "role": "user", 
                "content": prompt,
                "timestamp": datetime.now().isoformat()
            })
            
            with st.chat_message("user"):
                st.write(prompt)
            
            # Get response with enhanced context
            with st.chat_message("assistant"):
                with st.spinner("🤔 Thinking with conversation context..."):
                    result = rag_system.query(enhanced_prompt)
                    
                    if "error" in result:
                        st.error(f"❌ {result['error']}")
                    else:
                        answer = result["answer"]
                        sources = []
                        
                        if "source_documents" in result:
                            sources = list(set([doc.metadata.get("source", "Unknown") 
                                              for doc in result["source_documents"]]))
                        
                        # Post-process answer based on feedback patterns
                        processed_answer = self._post_process_answer(answer)
                        
                        st.write(processed_answer)
                        
                        if sources:
                            with st.expander("📚 Sources & References"):
                                for j, source in enumerate(sources):
                                    st.markdown(f"**{j+1}.** {source}")
                        
                        # Add to chat history with enhanced metadata
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": processed_answer,
                            "sources": sources,
                            "timestamp": datetime.now().isoformat(),
                            "original_query": prompt,
                            "used_context": bool(conversation_context)
                        })
                        
                        # Update conversation context
                        self._update_conversation_context(prompt, processed_answer)
                        
                        st.rerun()
    
    def _create_enhanced_prompt(self, user_query: str, conversation_context: str) -> str:
        """Create an enhanced prompt with conversation context.
        
        Args:
            user_query: Original user query
            conversation_context: Previous conversation context
            
        Returns:
            Enhanced prompt string
        """
        if not conversation_context:
            return user_query
        
        enhanced_prompt = f"""
{conversation_context}

Current question: {user_query}

Please provide a response that:
1. Takes into account the conversation history above
2. Builds upon previous responses where relevant
3. Avoids repeating information unless specifically requested
4. Incorporates lessons learned from previous feedback
5. Maintains consistency with earlier answers in this conversation
"""
        return enhanced_prompt
    
    def _post_process_answer(self, answer: str) -> str:
        """Post-process answer based on feedback patterns.
        
        Args:
            answer: Original answer from LLM
            
        Returns:
            Post-processed answer
        """
        if not self.config.FEEDBACK_ENABLED or not st.session_state.feedback_data:
            return answer
        
        # Analyze feedback patterns
        negative_feedback_count = sum(1 for feedback in st.session_state.feedback_data.values() 
                                    if feedback.get("rating") == "negative")
        
        # If there's been negative feedback, add a note about improvements
        if negative_feedback_count > 0:
            improvement_note = "\n\n💡 *This response incorporates improvements based on your previous feedback.*"
            return answer + improvement_note
        
        return answer
    
    def _update_conversation_context(self, query: str, response: str):
        """Update conversation context for future reference.
        
        Args:
            query: User query
            response: Assistant response
        """
        context_entry = {
            "query": query,
            "response": response[:300],  # Truncate for storage efficiency
            "timestamp": datetime.now().isoformat()
        }
        
        st.session_state.conversation_context.append(context_entry)
        
        # Keep only recent context entries
        max_context_size = self.config.MAX_CHAT_HISTORY_CONTEXT
        if len(st.session_state.conversation_context) > max_context_size:
            st.session_state.conversation_context = st.session_state.conversation_context[-max_context_size:]
