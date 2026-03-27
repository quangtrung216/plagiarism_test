"""
Highlight service for plagiarism detection and visualization.
"""

import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from difflib import SequenceMatcher


class HighlightService:
    """
    Service for highlighting similar text segments and generating context.
    """
    
    def __init__(self):
        """Initialize the highlight service."""
        self.logger = logging.getLogger(__name__)
    
    def highlight_similar_words(
        self, 
        query_sentence: str, 
        matched_sentence: str,
        similarity_threshold: float = 0.7
    ) -> Tuple[str, str]:
        """
        Highlight similar words between two sentences.
        
        Args:
            query_sentence: The query sentence
            matched_sentence: The matched sentence
            similarity_threshold: Threshold for word similarity
            
        Returns:
            Tuple of (highlighted_query, highlighted_matched)
        """
        try:
            # Tokenize sentences into words
            query_words = query_sentence.split()
            matched_words = matched_sentence.split()
            
            # Find similar word pairs
            similar_pairs = self._find_similar_word_pairs(
                query_words, matched_words, similarity_threshold
            )
            
            # Highlight in query sentence
            highlighted_query = self._highlight_words(query_words, similar_pairs, 'query')
            
            # Highlight in matched sentence  
            highlighted_matched = self._highlight_words(matched_words, similar_pairs, 'matched')
            
            return highlighted_query, highlighted_matched
            
        except Exception as e:
            self.logger.error(f"Error highlighting similar words: {e}")
            return query_sentence, matched_sentence
    
    def highlight_sentence_segments(
        self, 
        query_sentence: str, 
        matched_sentence: str,
        similarity_score: float
    ) -> Tuple[str, str]:
        """
        Highlight similar segments between sentences based on similarity score.
        
        Args:
            query_sentence: The query sentence
            matched_sentence: The matched sentence
            similarity_score: Overall similarity score
            
        Returns:
            Tuple of (highlighted_query, highlighted_matched)
        """
        try:
            if similarity_score >= 0.9:
                # Very high similarity - highlight entire sentences
                highlighted_query = f"<mark>{query_sentence}</mark>"
                highlighted_matched = f"<mark>{matched_sentence}</mark>"
            elif similarity_score >= 0.7:
                # High similarity - use word-level highlighting
                return self.highlight_similar_words(query_sentence, matched_sentence, 0.6)
            else:
                # Lower similarity - use phrase-level highlighting
                return self._highlight_similar_phrases(query_sentence, matched_sentence)
                
        except Exception as e:
            self.logger.error(f"Error highlighting sentence segments: {e}")
            return query_sentence, matched_sentence
    
    def get_sentence_context(
        self, 
        sentences: List[str], 
        target_index: int, 
        context_size: int = 2
    ) -> Dict[str, List[str]]:
        """
        Get context around a target sentence.
        
        Args:
            sentences: List of all sentences in document
            target_index: Index of the target sentence
            context_size: Number of sentences before and after
            
        Returns:
            Dictionary with 'before', 'target', and 'after' sentences
        """
        try:
            start_before = max(0, target_index - context_size)
            end_before = target_index
            
            start_after = target_index + 1
            end_after = min(len(sentences), target_index + context_size + 1)
            
            return {
                'before': sentences[start_before:end_before],
                'target': [sentences[target_index]] if target_index < len(sentences) else [],
                'after': sentences[start_after:end_after]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting sentence context: {e}")
            return {'before': [], 'target': [], 'after': []}
    
    def generate_highlighted_html(
        self, 
        query_sentence: str, 
        matched_sentence: str,
        similarity_score: float,
        context_before: List[str] = None,
        context_after: List[str] = None,
        matched_context_before: List[str] = None,
        matched_context_after: List[str] = None
    ) -> Dict[str, str]:
        """
        Generate HTML with highlighted similarities and context.
        
        Args:
            query_sentence: The query sentence
            matched_sentence: The matched sentence
            similarity_score: Similarity score
            context_before: Context before query sentence
            context_after: Context after query sentence
            matched_context_before: Context before matched sentence
            matched_context_after: Context after matched sentence
            
        Returns:
            Dictionary with HTML content for query and matched sections
        """
        try:
            # Highlight main sentences
            highlighted_query, highlighted_matched = self.highlight_sentence_segments(
                query_sentence, matched_sentence, similarity_score
            )
            
            # Build HTML for query section
            query_html = "<div class='query-section'>"
            if context_before:
                query_html += "<div class='context-before'>"
                query_html += " ".join(context_before)
                query_html += "</div>"
            
            query_html += f"<div class='main-sentence'>{highlighted_query}</div>"
            
            if context_after:
                query_html += "<div class='context-after'>"
                query_html += " ".join(context_after)
                query_html += "</div>"
            
            query_html += "</div>"
            
            # Build HTML for matched section
            matched_html = "<div class='matched-section'>"
            if matched_context_before:
                matched_html += "<div class='context-before'>"
                matched_html += " ".join(matched_context_before)
                matched_html += "</div>"
            
            matched_html += f"<div class='main-sentence'>{highlighted_matched}</div>"
            
            if matched_context_after:
                matched_html += "<div class='context-after'>"
                matched_html += " ".join(matched_context_after)
                matched_html += "</div>"
            
            matched_html += "</div>"
            
            return {
                'query_html': query_html,
                'matched_html': matched_html,
                'similarity_score': similarity_score
            }
            
        except Exception as e:
            self.logger.error(f"Error generating highlighted HTML: {e}")
            return {
                'query_html': query_sentence,
                'matched_html': matched_sentence,
                'similarity_score': similarity_score
            }
    
    def _find_similar_word_pairs(
        self, 
        query_words: List[str], 
        matched_words: List[str],
        threshold: float
    ) -> List[Tuple[int, int, float]]:
        """
        Find pairs of similar words between two word lists.
        
        Args:
            query_words: Words from query sentence
            matched_words: Words from matched sentence
            threshold: Similarity threshold
            
        Returns:
            List of tuples (query_index, matched_index, similarity)
        """
        similar_pairs = []
        
        for i, query_word in enumerate(query_words):
            for j, matched_word in enumerate(matched_words):
                similarity = self._word_similarity(query_word, matched_word)
                if similarity >= threshold:
                    similar_pairs.append((i, j, similarity))
        
        # Filter to keep best matches (avoid multiple matches for same word)
        filtered_pairs = []
        used_query_indices = set()
        used_matched_indices = set()
        
        # Sort by similarity descending
        similar_pairs.sort(key=lambda x: x[2], reverse=True)
        
        for query_idx, matched_idx, similarity in similar_pairs:
            if query_idx not in used_query_indices and matched_idx not in used_matched_indices:
                filtered_pairs.append((query_idx, matched_idx, similarity))
                used_query_indices.add(query_idx)
                used_matched_indices.add(matched_idx)
        
        return filtered_pairs
    
    def _word_similarity(self, word1: str, word2: str) -> float:
        """Calculate similarity between two words."""
        if word1.lower() == word2.lower():
            return 1.0
        
        # Use SequenceMatcher for similarity
        return SequenceMatcher(None, word1.lower(), word2.lower()).ratio()
    
    def _highlight_words(
        self, 
        words: List[str], 
        similar_pairs: List[Tuple[int, int, float]],
        side: str
    ) -> str:
        """Highlight words in a sentence based on similar pairs."""
        if side == 'query':
            indices_to_highlight = {pair[0] for pair in similar_pairs}
        else:  # matched
            indices_to_highlight = {pair[1] for pair in similar_pairs}
        
        highlighted_words = []
        for i, word in enumerate(words):
            if i in indices_to_highlight:
                highlighted_words.append(f"<mark>{word}</mark>")
            else:
                highlighted_words.append(word)
        
        return " ".join(highlighted_words)
    
    def _highlight_similar_phrases(
        self, 
        query_sentence: str, 
        matched_sentence: str
    ) -> Tuple[str, str]:
        """Highlight similar phrases between sentences."""
        try:
            # Use SequenceMatcher to find matching blocks
            matcher = SequenceMatcher(None, query_sentence, matched_sentence)
            
            highlighted_query = ""
            highlighted_matched = ""
            
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == 'equal':
                    # Highlight matching parts
                    query_part = query_sentence[i1:i2]
                    matched_part = matched_sentence[j1:j2]
                    highlighted_query += f"<mark>{query_part}</mark>"
                    highlighted_matched += f"<mark>{matched_part}</mark>"
                elif tag == 'replace':
                    # Different parts - no highlighting
                    highlighted_query += query_sentence[i1:i2]
                    highlighted_matched += matched_sentence[j1:j2]
                elif tag == 'delete':
                    # Part only in query
                    highlighted_query += f"<del>{query_sentence[i1:i2]}</del>"
                elif tag == 'insert':
                    # Part only in matched
                    highlighted_matched += f"<ins>{matched_sentence[j1:j2]}</ins>"
            
            return highlighted_query, highlighted_matched
            
        except Exception as e:
            self.logger.error(f"Error highlighting similar phrases: {e}")
            return query_sentence, matched_sentence
    
    def generate_diff_view(
        self, 
        query_sentence: str, 
        matched_sentence: str
    ) -> Dict[str, str]:
        """
        Generate a diff view between two sentences.
        
        Args:
            query_sentence: The query sentence
            matched_sentence: The matched sentence
            
        Returns:
            Dictionary with diff information
        """
        try:
            matcher = SequenceMatcher(None, query_sentence, matched_sentence)
            
            query_parts = []
            matched_parts = []
            
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                query_part = query_sentence[i1:i2]
                matched_part = matched_sentence[j1:j2]
                
                if tag == 'equal':
                    query_parts.append({'text': query_part, 'type': 'equal'})
                    matched_parts.append({'text': matched_part, 'type': 'equal'})
                elif tag == 'replace':
                    query_parts.append({'text': query_part, 'type': 'deleted'})
                    matched_parts.append({'text': matched_part, 'type': 'inserted'})
                elif tag == 'delete':
                    query_parts.append({'text': query_part, 'type': 'deleted'})
                elif tag == 'insert':
                    matched_parts.append({'text': matched_part, 'type': 'inserted'})
            
            return {
                'query_parts': query_parts,
                'matched_parts': matched_parts,
                'similarity_ratio': matcher.ratio()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating diff view: {e}")
            return {
                'query_parts': [{'text': query_sentence, 'type': 'equal'}],
                'matched_parts': [{'text': matched_sentence, 'type': 'equal'}],
                'similarity_ratio': 0.0
            }
    
    def create_plagiarism_report(
        self, 
        plagiarism_results: List[Dict[str, Any]],
        include_context: bool = True,
        context_size: int = 2
    ) -> Dict[str, Any]:
        """
        Create a comprehensive plagiarism report with highlighting.
        
        Args:
            plagiarism_results: List of plagiarism matches
            include_context: Whether to include context sentences
            context_size: Number of context sentences
            
        Returns:
            Dictionary containing the plagiarism report
        """
        try:
            report = {
                'summary': {
                    'total_matches': len(plagiarism_results),
                    'high_similarity_matches': len([r for r in plagiarism_results if r['similarity_score'] >= 0.9]),
                    'medium_similarity_matches': len([r for r in plagiarism_results if 0.7 <= r['similarity_score'] < 0.9]),
                    'low_similarity_matches': len([r for r in plagiarism_results if r['similarity_score'] < 0.7]),
                    'max_similarity': max([r['similarity_score'] for r in plagiarism_results]) if plagiarism_results else 0,
                    'average_similarity': sum([r['similarity_score'] for r in plagiarism_results]) / len(plagiarism_results) if plagiarism_results else 0
                },
                'matches': []
            }
            
            for match in plagiarism_results:
                # Generate highlighting
                highlighted_query, highlighted_matched = self.highlight_sentence_segments(
                    match['query_original'], 
                    match['matched_original'],
                    match['similarity_score']
                )
                
                # Generate diff view
                diff_view = self.generate_diff_view(
                    match['query_original'],
                    match['matched_original']
                )
                
                match_report = {
                    'match_id': match['id'],
                    'similarity_score': match['similarity_score'],
                    'match_type': match['match_type'],
                    'query_document': match.get('query_original', ''),
                    'matched_document_name': match.get('matched_document_name', ''),
                    'highlighted_query': highlighted_query,
                    'highlighted_matched': highlighted_matched,
                    'diff_view': diff_view
                }
                
                # Add context if requested
                if include_context:
                    match_report.update({
                        'context_before_query': match.get('context_before_query', ''),
                        'context_after_query': match.get('context_after_query', ''),
                        'context_before_matched': match.get('context_before_matched', ''),
                        'context_after_matched': match.get('context_after_matched', '')
                    })
                
                report['matches'].append(match_report)
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error creating plagiarism report: {e}")
            return {'summary': {}, 'matches': []}
