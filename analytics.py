import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, Any

class AnalyticsVisualizer:
    def __init__(self):
        # Enhanced color palette with better contrast
        self.color_palette = [
            '#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#5D737E',
            '#8B5A3C', '#6A994E', '#BC4749', '#F2B705', '#264653'
        ]
        
        # Common layout settings for consistency
        self.common_layout = {
            'font': dict(size=12, color='#1F2937'),  # Darker font for better visibility
            'title_font': dict(size=14, color='#111827', family='Arial, sans-serif'),  # Very dark title
            'plot_bgcolor': '#FAFBFC',
            'paper_bgcolor': 'white',
            'margin': dict(l=10, r=10, t=50, b=10)
        }
    
    def _get_hover_styling(self):
        """Get consistent hover styling for all charts."""
        return dict(
            bgcolor='rgba(0,0,0,0.9)',
            bordercolor='rgba(255,255,255,0.8)',
            font=dict(color='white', size=12, family='Arial, sans-serif')
        )
    
    def create_category_chart(self, data: pd.DataFrame, title: str) -> go.Figure:
        """Create a horizontal bar chart for categories."""
        if data.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="#374151")
            )
            fig.update_layout(
                title=dict(text=title, font=dict(size=14, color='#111827', family='Arial, sans-serif')),
                height=400,
                showlegend=False,
                **self.common_layout
            )
            return fig
        
        # Create bars with gradient colors
        fig = go.Figure()
        
        y_values = data[data.columns[0]].tolist()
        x_values = data[data.columns[1]].tolist()
        
        # Create bars with custom colors
        colors = [self.color_palette[i % len(self.color_palette)] for i in range(len(y_values))]
        
        fig.add_trace(go.Bar(
            y=y_values,
            x=x_values,
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='rgba(0,0,0,0.1)', width=1)
            ),
            text=[f"{val:,}" for val in x_values],
            textposition='outside',
            textfont=dict(size=10, color='#111827'),  # Darker text for visibility
            hovertemplate="<b style='color: white;'>%{y}</b><br>" +
                         "<span style='color: white;'>Count: %{x:,}</span>" +
                         "<extra></extra>",
            hoverlabel=self._get_hover_styling()
        ))
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=14, color='#111827', family='Arial, sans-serif')),
            height=400,
            xaxis=dict(
                title=dict(text=data.columns[1].title(), font=dict(size=12, color='#111827')),
                tickfont=dict(size=10, color='#1F2937'),  # Darker tick labels
                gridcolor='#E5E7EB',
                gridwidth=1,
                zeroline=False
            ),
            yaxis=dict(
                title=dict(font=dict(size=12, color='#111827')),
                tickfont=dict(size=10, color='#1F2937'),  # Darker tick labels
                gridcolor='#E5E7EB',
                gridwidth=1
            ),
            showlegend=False,
            hoverlabel=dict(
                bgcolor='rgba(0,0,0,0.8)',
                bordercolor='white',
                font=dict(color='white', size=12, family='Arial, sans-serif')
            ),
            **self.common_layout
        )
        
        # Reverse y-axis to show highest values at top
        fig.update_yaxes(autorange="reversed")
        
        return fig
    
    def create_ctr_chart(self, data: pd.DataFrame, title: str) -> go.Figure:
        """Create a bar chart showing CTR percentages."""
        if data.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="#374151")
            )
            fig.update_layout(
                title=dict(text=title, font=dict(size=14, color='#111827', family='Arial, sans-serif')),
                height=400,
                showlegend=False,
                **self.common_layout
            )
            return fig
        
        # Create custom color scale based on CTR values
        y_values = data['ad_category'].tolist()
        x_values = data['ctr'].tolist()
        
        # Normalize CTR values for color mapping (0-1 scale)
        max_ctr = max(x_values) if x_values else 1
        # Avoid division by zero
        if max_ctr == 0:
            normalized_ctr = [0.5 for val in x_values]  # Use neutral color if all CTRs are 0
        else:
            normalized_ctr = [val / max_ctr for val in x_values]
        
        # Create color scale from red (low) to green (high)
        colors = [f"rgba({255 - int(255 * norm)}, {int(255 * norm)}, 50, 0.8)" for norm in normalized_ctr]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=y_values,
            x=x_values,
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='rgba(0,0,0,0.2)', width=1)
            ),
            text=[f"{val:.1f}%" for val in x_values],
            textposition='outside',
            textfont=dict(size=10, color='#111827'),  # Darker text for visibility
            customdata=list(zip(data['impressions'], data['clicks'])),
            hovertemplate="<b style='color: white;'>%{y}</b><br>" +
                         "<span style='color: white;'>CTR: %{x:.2f}%</span><br>" +
                         "<span style='color: white;'>Clicks: %{customdata[1]:,}</span><br>" +
                         "<span style='color: white;'>Impressions: %{customdata[0]:,}</span><br>" +
                         "<extra></extra>",
            hoverlabel=self._get_hover_styling()
        ))
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=14, color='#111827', family='Arial, sans-serif')),
            height=400,
            xaxis=dict(
                title=dict(text="Click-through Rate (%)", font=dict(size=12, color='#111827')),
                tickfont=dict(size=10, color='#1F2937'),  # Darker tick labels
                gridcolor='#E5E7EB',
                gridwidth=1,
                zeroline=False
            ),
            yaxis=dict(
                title=dict(font=dict(size=12, color='#111827')),
                tickfont=dict(size=10, color='#1F2937'),  # Darker tick labels
                gridcolor='#E5E7EB',
                gridwidth=1
            ),
            showlegend=False,
            hoverlabel=dict(
                bgcolor='rgba(0,0,0,0.8)',
                bordercolor='white',
                font=dict(color='white', size=12, family='Arial, sans-serif')
            ),
            **self.common_layout
        )
        
        # Reverse y-axis to show highest values at top
        fig.update_yaxes(autorange="reversed")
        
        return fig
    
    def create_sentiment_distribution(self, data: pd.DataFrame, title: str = "Sentiment Distribution") -> go.Figure:
        """Create a pie chart showing sentiment distribution."""
        if data.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="gray")
            )
            fig.update_layout(
                title=title,
                height=300,
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            return fig
        
        sentiment_counts = data['user_sentiment'].value_counts()
        
        colors = {
            'Positive': '#2ca02c',
            'Neutral': '#1f77b4', 
            'Negative': '#d62728'
        }
        
        fig = go.Figure(data=[go.Pie(
            labels=sentiment_counts.index,
            values=sentiment_counts.values,
            hole=.4,
            marker_colors=[colors.get(label, '#gray') for label in sentiment_counts.index]
        )])
        
        fig.update_layout(
            title=title,
            height=300,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.1),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=12),
            title_font_size=16
        )
        
        return fig
    
    def create_device_distribution(self, data: pd.DataFrame, title: str = "Device Distribution") -> go.Figure:
        """Create a horizontal bar chart showing device distribution."""
        if data.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="gray")
            )
            fig.update_layout(
                title=title,
                height=300,
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            return fig
        
        # Handle both column names for device data
        device_col = 'user_device' if 'user_device' in data.columns else 'device_type'
        if device_col not in data.columns:
            # Return empty figure if neither column exists
            fig = go.Figure()
            fig.update_layout(
                title=dict(text=title, font=dict(size=14, color='#111827', family='Arial, sans-serif')),
                height=400,
                xaxis=dict(title="Count"),
                yaxis=dict(title="Device Type"),
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            return fig
        
        device_counts = data[device_col].value_counts().head(8)
        
        fig = px.bar(
            x=device_counts.values,
            y=device_counts.index,
            orientation='h',
            title=title,
            color_discrete_sequence=['#1f77b4']
        )
        
        fig.update_layout(
            height=300,
            xaxis_title="Count",
            yaxis_title="",
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=12),
            title_font_size=16,
            margin=dict(l=20, r=20, t=60, b=20)
        )
        
        fig.update_yaxes(autorange="reversed")
        
        return fig
    
    def create_location_map(self, data: pd.DataFrame, title: str = "Top Locations") -> go.Figure:
        """Create a simple bar chart for locations (since we don't have coordinates)."""
        if data.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="gray")
            )
            fig.update_layout(
                title=title,
                height=300,
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            return fig
        
        location_counts = data['user_location'].value_counts().head(10)
        
        fig = px.bar(
            x=location_counts.values,
            y=location_counts.index,
            orientation='h',
            title=title,
            color_discrete_sequence=['#ff7f0e']
        )
        
        fig.update_layout(
            height=300,
            xaxis_title="Count",
            yaxis_title="",
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=12),
            title_font_size=16,
            margin=dict(l=20, r=20, t=60, b=20)
        )
        
        fig.update_yaxes(autorange="reversed")
        
        return fig
