import streamlit as st
import re
import html
import json
from typing import List, Dict, Optional
from datetime import datetime
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
from math import log2

class PromptSafetyChecker:
    def __init__(self):
        # Expanded suspicious patterns organized by category
        self.suspicious_patterns = {
            "instruction_override": [
                r"\bignore\b (?:all )?(?:previous|above)? instructions\b",
                r"\bdisregard\b (?:all )?(?:previous)? (?:instructions|prompts)\b",
                r"\bforget\b (?:all )?(?:previous)? (?:instructions|prompts)\b",
                r"\bnew instruction\b:",
                r"\bsystem prompt\b:",
                r"\byou\b (?:are|will be|shall be|must be) now\b",
                r"\bact as\b",
                r"\bdo not follow\b",
                r"\boverride\b (?:previous |all )?(?:instructions|settings)\b",
                r"\bdisable\b (?:all )?(?:filters|restrictions|limitations)\b",
                r"\bbypass\b (?:all )?(?:filters|restrictions|limitations)\b",
            ],

            "system_commands": [
                r"\bsudo\b",
                r"\b/[a-z]+(?:[ -][a-z]+)*\b",  # Limit command-like patterns to avoid matches like /path/ or URL parts
                r"\b\\[a-z]+\b",
                r"\$\b[a-z]+\b",
                r"\bexecute(?:\s+(?:command|script|file))?:",
                r"\brun(?:\s+(?:command|script|file))?:",
                r"\bsystem\s*\(",
                r"\beval\s*\(",
                r"\bexec\s*\(",
            ],

            "code_injection": [
                r"```[a-zA-Z]*\n.*?\n```",  # Match code blocks more narrowly
                r"<script\b.*?>.*?</script>",
                r"\bjavascript:\b",
                r"\bdata:text/[a-z]+;base64,",
                r"\b(?:file|https?|ftp|data)://\S+",  # URLs in base64 format are rarer
                r"\b(?:require|import)\s+['\"]?\w+",          # Matches "require" and "import" in code
                r"(?m)^\s*from\s+[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z0-9_]+)*\s+import\b",  # Matches "from module import"
            ],

            "markup_injection": [
                r"<\/?[a-z][^>]*>",  # Narrow HTML matching to simple tags
                r"\[[^\]]+\]\([^\)]+\)",  # Markdown-style links
                r"\{\{[^\}]*\}\}",  # Template injection
                r"\{\%[^\%]*\%\}",  # Django/Handlebars-style injection
                r"\$\{[^\}]*\}",  # Template string injection
            ],

            "role_playing": [
                r"\byou are(?: now)?(?: a| an| the)? \w+\b",
                r"\bswitch(?: your)? (?:role|personality)(?: to)?\b",
                r"\bbehave like(?: a| an)?\b",
                r"\bpretend(?: to be| you are)\b",
                r"\brole-?play as\b",
            ],

            "escaping_attempts": [
                r"\bbase64:\b",
                r"\\x[0-9a-fA-F]{2}",
                r"\\u[0-9a-fA-F]{4}",
                r"\\[rnt]",
                r"&#x?[0-9a-fA-F]+;",
                r"%[0-9a-fA-F]{2}",
            ],

            "prompt_manipulation": [
                r"\bcontext manipulation\b",
                r"\bchange(?: your)? (?:behavior|personality|response)\b",
                r"\bmodify(?: your)? (?:output|behavior|response)\b",
                r"\breset(?: your)? (?:context|memory|state)\b",
                r"\b(?:previous|above) conversation is false\b",
                r"\b(?:previous|above) context is wrong\b",
                r"\byour(?: new)? purpose is\b",
            ],

            "data_exfiltration": [
                r"\bshow(?: me)?(?:(?: the)? system| internal| hidden| secret) (?:prompt|instructions|data|information)\b",
                r"\breveal(?: the)?(?: system| internal| hidden| secret) (?:prompt|instructions|data|information)\b",
                r"\bdisplay(?: the)?(?: system| internal| hidden| secret) (?:prompt|instructions|data|information)\b",
                r"\bwhat(?: are)?(?: your)?(?: system| internal| hidden| secret) (?:prompt|instructions|settings)\b",
            ]
}
        
        # Maximum allowed input length
        self.max_input_length = 1000
        
        # Additional security settings
        self.max_special_chars_ratio = 0.3
        self.max_repetition_ratio = 0.4
        self.max_entropy_ratio = 0.7 # entropy value >0.7 may indicate obfuscation or randomness indicating encryption or encoding.
        
        # Keep track of user inputs for rate limiting
        self.user_inputs: Dict[str, List[Dict]] = {}
        
    def calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of the text to detect potential obfuscation."""
        if not text:
            return 0
        freq = {}
        for char in text:
            freq[char] = freq.get(char, 0) + 1
        entropy = 0
        for count in freq.values():
            probability = count / len(text)
            entropy -= probability * (log2(probability))
        return entropy / 8.0  # Normalize to [0,1]
    
    def check_repetition(self, text: str) -> float:
        """Check for suspicious repetition patterns."""
        if not text:
            return 0
        chunks = [text[i:i+3] for i in range(len(text)-2)]
        unique_chunks = len(set(chunks))
        return 1 - (unique_chunks / max(len(chunks), 1))
    
    def sanitize_input(self, text: str) -> str:
        """Enhanced input sanitization."""
        # HTML escape to prevent XSS
        text = html.escape(text)
        # Remove any control characters
        text = ''.join(char for char in text if ord(char) >= 32)
        # Normalize whitespace
        text = ' '.join(text.split())
        # Remove UTF-8 invisible characters
        text = re.sub(r'[\u200B-\u200F\uFEFF]', '', text)
        return text.strip()
    
    def check_suspicious_patterns(self, text: str) -> List[Dict[str, str]]:
        """Enhanced pattern checking with categorization."""
        findings = []
        for category, patterns in self.suspicious_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    findings.append({
                        "category": category,
                        "pattern": pattern,
                        "matched_text": match.group(0),
                        "position": match.span()
                    })
        return findings
    
    def validate_input(self, text: str) -> tuple[bool, Optional[str], List[Dict]]:
        """Enhanced input validation with detailed reporting."""
        validation_results = []
        
        # Check input length
        if len(text) > self.max_input_length:
            return False, f"Input exceeds maximum length of {self.max_input_length} characters", validation_results
        
        # Check special characters ratio
        special_chars = sum(1 for c in text if not c.isalnum() and not c.isspace())
        special_chars_ratio = special_chars / len(text) if text else 0
        if special_chars_ratio > self.max_special_chars_ratio:
            validation_results.append({
                "check": "special_chars",
                "status": "failed",
                "ratio": special_chars_ratio
            })
        
        # Check repetition
        repetition_ratio = self.check_repetition(text)
        if repetition_ratio > self.max_repetition_ratio:
            validation_results.append({
                "check": "repetition",
                "status": "failed",
                "ratio": repetition_ratio
            })
        
        # Check entropy
        entropy_ratio = self.calculate_entropy(text)
        if entropy_ratio > self.max_entropy_ratio:
            validation_results.append({
                "check": "entropy",
                "status": "failed",
                "ratio": entropy_ratio
            })
        
        # Check for suspicious patterns
        findings = self.check_suspicious_patterns(text)
        if findings:
            validation_results.append({
                "check": "patterns",
                "status": "failed",
                "findings": findings
            })
            pattern_details = "\n".join([
                f"- {f['category']}: {f['matched_text']}" 
                for f in findings
            ])
            return False, f"Potential prompt injection detected:\n{pattern_details}", validation_results
        
        if validation_results:
            return False, "Input validation failed", validation_results
        
        return True, None, validation_results
    
    def generate_pattern_visualization(self, text: str, findings: List[Dict]) -> go.Figure:
        """Generate a visualization of where patterns were detected in the text."""
        if not findings:
            return None
        
        # Create a list of pattern occurrences
        pattern_locations = []
        colors = px.colors.qualitative.Set3
        color_map = {}
        current_color = 0
        
        for finding in findings:
            category = finding['category']
            if category not in color_map:
                color_map[category] = colors[current_color % len(colors)]
                current_color += 1
            
            start, end = finding['position']
            pattern_locations.append({
                'category': category,
                'start': start,
                'end': end,
                'text': finding['matched_text'],
                'color': color_map[category]
            })
        
        # Create the visualization
        fig = go.Figure()
        
        # Add the base text line
        fig.add_shape(
            type="line",
            x0=0,
            x1=len(text),
            y0=0,
            y1=0,
            line=dict(color="gray", width=2)
        )
        
        # Add markers for each pattern
        for loc in pattern_locations:
            # Add a rectangle for the pattern
            fig.add_shape(
                type="rect",
                x0=loc['start'],
                x1=loc['end'],
                y0=-0.2,
                y1=0.2,
                fillcolor=loc['color'],
                opacity=0.5,
                line_width=0,
            )
            
            # Add annotation
            fig.add_annotation(
                x=(loc['start'] + loc['end']) / 2,
                y=0.3,
                text=f"{loc['category']}<br>{loc['text']}",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor=loc['color'],
                font=dict(size=10)
            )
        
        fig.update_layout(
            title="Pattern Detection Visualization",
            showlegend=False,
            height=300,
            yaxis_range=[-0.5, 1],
            yaxis_visible=False,
            xaxis_title="Character Position"
        )
        
        return fig

    def generate_metrics_visualization(self, text: str) -> Dict[str, go.Figure]:
        """Generate visualizations for various text metrics."""
        visualizations = {}
        
        # Character distribution
        char_counts = Counter(text)
        char_df = pd.DataFrame([
            {'character': char, 'count': count}
            for char, count in char_counts.items()
        ]).sort_values('count', ascending=False)
        
        fig_chars = px.bar(
            char_df.head(20),
            x='character',
            y='count',
            title='Character Distribution (Top 20)',
            labels={'character': 'Character', 'count': 'Frequency'}
        )
        visualizations['char_dist'] = fig_chars
        
        # Metrics gauge charts
        entropy_ratio = self.calculate_entropy(text)
        repetition_ratio = self.check_repetition(text)
        special_chars = sum(1 for c in text if not c.isalnum() and not c.isspace())
        special_chars_ratio = special_chars / len(text) if text else 0
        
        metrics_data = [
            ('Entropy', entropy_ratio, self.max_entropy_ratio, 'Higher is better'),
            ('Repetition', repetition_ratio, self.max_repetition_ratio, 'Lower is better'),
            ('Special_Chars', special_chars_ratio, self.max_special_chars_ratio, 'Lower is better')
        ]
        
        for name, value, threshold, direction in metrics_data:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=value,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': f"{name} Ratio"},
                gauge={
                    'axis': {'range': [0, 1]},
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': threshold
                    },
                    'steps': [
                        {'range': [0, threshold], 'color': "lightgray"},
                        {'range': [threshold, 1], 'color': "gray"}
                    ]
                }
            ))
            fig.update_layout(height=200)
            visualizations[f'{name.lower()}_gauge'] = fig
        
        return visualizations
    
def main():
    st.title("Enhanced Secure Prompt Input System")
    
    # Initialize the safety checker
    if 'safety_checker' not in st.session_state:
        st.session_state.safety_checker = PromptSafetyChecker()
    
    # Add a description
    st.markdown("""
    This application demonstrates advanced prompt safety measures to prevent prompt injection attacks.
    It includes:
    - Enhanced pattern detection across multiple categories
    - Advanced input sanitization
    - Statistical analysis of input characteristics
    - Detailed validation reporting
    """)
    
    # User input
    user_input = st.text_area("Enter your prompt:", max_chars=1000)
    
    if st.button("Submit"):
        if user_input:
            # Sanitize input
            sanitized_input = st.session_state.safety_checker.sanitize_input(user_input)
            
            # Validate input
            is_valid, error_message, validation_results = st.session_state.safety_checker.validate_input(sanitized_input)
            
            if is_valid:
                st.success("Input validated successfully!")
                st.write("Sanitized input:", sanitized_input)
            else:
                st.error(error_message)
                
                # Display detailed validation results
                if validation_results:
                    st.expander("Validation Details").json(validation_results)
                
                st.warning("Please modify your input and try again.")
        else:
            st.warning("Please enter some text.")
    
    # Display enhanced security information
    with st.expander("Security Information"):
        st.markdown("""
        ### Enhanced Security Measures:
        1. **Advanced Input Sanitization**:
           - HTML escape
           - Control character removal
           - Whitespace normalization
           - UTF-8 invisible character removal
        
        2. **Pattern Detection Categories**:
           - Instruction override attempts
           - System command injection
           - Code injection
           - Markup injection
           - Role-playing attempts
           - Escaping attempts
           - Prompt manipulation
           - Data exfiltration attempts
        
        3. **Statistical Analysis**:
           - Special character ratio checking
           - Repetition pattern detection
           - Shannon entropy analysis
        
        4. **Additional Features**:
           - Detailed validation reporting
           - Pattern categorization
           - Position tracking of suspicious patterns
        """)

if __name__ == "__main__":
    main()
