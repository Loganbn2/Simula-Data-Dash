import pandas as pd
import numpy as np
try:
    from faker import Faker
    FAKER_AVAILABLE = True
except ImportError:
    FAKER_AVAILABLE = False
import random
from datetime import datetime, timedelta

class DataGenerator:
    def __init__(self, seed=42):
        """Initialize the data generator with a seed for reproducibility."""
        if FAKER_AVAILABLE:
            self.fake = Faker()
            Faker.seed(seed)
        else:
            self.fake = None
        random.seed(seed)
        np.random.seed(seed)
        
        # Predefined categories and responses for more realistic data
        self.message_categories = [
            'Technical Support', 'Product Inquiry', 'Billing Question', 
            'General Information', 'Complaint', 'Feature Request',
            'Account Help', 'Troubleshooting', 'Sales Inquiry', 'Feedback',
            'Integration Help', 'API Questions', 'Documentation Request',
            'Bug Report', 'Performance Issue', 'Security Question'
        ]
        
        self.ad_categories = [
            'Software Tools', 'Cloud Services', 'Marketing Tools', 
            'Development Frameworks', 'Security Solutions', 'Analytics Platforms',
            'CRM Software', 'Productivity Apps', 'Design Tools', 'AI/ML Services',
            'Database Solutions', 'DevOps Tools', 'Mobile Apps', 'E-commerce',
            'Communication Tools', 'Project Management'
        ]
        
        self.devices = [
            'iPhone 15', 'iPhone 14', 'iPhone 13', 'Samsung Galaxy S24', 
            'Samsung Galaxy S23', 'MacBook Pro', 'MacBook Air', 'Windows Laptop',
            'iPad Pro', 'iPad Air', 'Surface Pro', 'Chrome OS', 'Android Tablet',
            'Desktop Windows', 'Desktop Mac', 'Linux Desktop'
        ]
        
        self.locations = [
            'New York, NY', 'Los Angeles, CA', 'Chicago, IL', 'Houston, TX',
            'Phoenix, AZ', 'Philadelphia, PA', 'San Antonio, TX', 'San Diego, CA',
            'Dallas, TX', 'San Jose, CA', 'Austin, TX', 'Jacksonville, FL',
            'Fort Worth, TX', 'Columbus, OH', 'Charlotte, NC', 'San Francisco, CA',
            'Indianapolis, IN', 'Seattle, WA', 'Denver, CO', 'Washington, DC',
            'Boston, MA', 'Nashville, TN', 'Detroit, MI', 'Portland, OR',
            'Memphis, TN', 'Louisville, KY', 'Baltimore, MD', 'Milwaukee, WI'
        ]
        
        self.sample_questions = [
            "How do I reset my password?",
            "What are your pricing plans?",
            "Can you help me integrate your API?",
            "I'm having trouble with the login process",
            "What features are included in the pro plan?",
            "How do I export my data?",
            "Is there a mobile app available?",
            "Can I get a refund for my subscription?",
            "How do I contact technical support?",
            "What security measures do you have in place?",
            "How can I upgrade my account?",
            "Are there any training resources available?",
            "Can I customize the dashboard?",
            "What integrations do you support?",
            "How do I delete my account?",
            "Is there a free trial available?",
            "Can you help me with setup?",
            "What's the difference between plans?",
            "How do I invite team members?",
            "Can I change my email address?"
        ]
        
        self.sample_responses = [
            "I can help you with that. Please check your email for password reset instructions.",
            "Our pricing starts at $9.99/month for the basic plan. Would you like me to explain the features?",
            "I'd be happy to help with API integration. Here's a link to our documentation.",
            "Let me troubleshoot this login issue with you. Can you tell me what error you're seeing?",
            "The pro plan includes advanced analytics, priority support, and custom integrations.",
            "You can export your data from the Settings > Data Export section.",
            "Yes, we have mobile apps for both iOS and Android available in the app stores.",
            "Refunds are processed within 5-7 business days. I'll initiate that for you.",
            "You can reach our technical support team at support@company.com or through live chat.",
            "We use enterprise-grade encryption and comply with SOC 2 Type II standards.",
            "I can help you upgrade your account. Which plan would you like to switch to?",
            "We offer comprehensive training materials and video tutorials in our help center.",
            "Yes, you can customize your dashboard layout and widgets from the settings panel.",
            "We integrate with over 50 popular tools including Slack, Salesforce, and Google Workspace.",
            "Account deletion can be done from Account Settings > Privacy > Delete Account.",
            "Yes, we offer a 14-day free trial with full access to all features.",
            "I'll guide you through the setup process step by step. Let's start with configuration.",
            "Here's a comparison chart showing the differences between our Basic, Pro, and Enterprise plans.",
            "Team members can be invited from the Team Management section in your dashboard.",
            "You can update your email address in Account Settings > Profile Information."
        ]
        
        self.ad_messages = [
            "Boost your productivity with our AI-powered automation tools - 30% off this month!",
            "Secure your data with enterprise-grade cloud storage - Free trial available!",
            "Transform your marketing strategy with advanced analytics - Get started today!",
            "Build faster with our developer-friendly API platform - Documentation included!",
            "Protect your business with comprehensive cybersecurity solutions - Learn more!",
            "Streamline your workflow with intelligent project management - Free for teams under 5!",
            "Scale your business with professional CRM software - No setup fees!",
            "Create stunning designs with our intuitive design platform - Templates included!",
            "Optimize your performance with real-time monitoring tools - Start monitoring now!",
            "Connect your team with seamless communication tools - Video calls included!",
            "Manage your inventory with smart tracking solutions - Barcode scanning available!",
            "Accelerate development with automated testing frameworks - Integration ready!",
            "Enhance customer experience with AI chatbot solutions - 24/7 support included!",
            "Simplify accounting with cloud-based financial tools - Tax reporting features!",
            "Increase sales with targeted email marketing campaigns - A/B testing included!"
        ]
    
    def generate_sample_data(self, num_records=1000):
        """Generate sample chat analytics data."""
        data = []
        
        for i in range(num_records):
            # Generate realistic timestamp (last 90 days)
            start_date = datetime.now() - timedelta(days=90)
            random_date = start_date + timedelta(
                days=random.randint(0, 90),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            # Select random elements
            category = random.choice(self.message_categories)
            user_message = random.choice(self.sample_questions)
            model_response = random.choice(self.sample_responses)
            
            # Generate sentiment based on category (some categories are more likely to be negative)
            if category in ['Complaint', 'Bug Report', 'Performance Issue']:
                sentiment_weights = [0.2, 0.3, 0.5]  # Lower positive sentiment
            elif category in ['Product Inquiry', 'Sales Inquiry', 'General Information']:
                sentiment_weights = [0.6, 0.3, 0.1]  # Higher positive sentiment
            else:
                sentiment_weights = [0.4, 0.4, 0.2]  # Balanced sentiment
            
            user_sentiment = np.random.choice(
                ['Positive', 'Neutral', 'Negative'], 
                p=sentiment_weights
            )
            
            # Generate ad data
            ad_category = random.choice(self.ad_categories)
            ad_message = random.choice(self.ad_messages)
            
            # Ad click probability based on sentiment and category alignment
            base_ctr = 0.05  # 5% base CTR
            if user_sentiment == 'Positive':
                click_probability = base_ctr * 2
            elif user_sentiment == 'Negative':
                click_probability = base_ctr * 0.5
            else:
                click_probability = base_ctr
            
            # Boost CTR for relevant categories
            if (category == 'Technical Support' and 'Tools' in ad_category) or \
               (category == 'Product Inquiry' and 'Software' in ad_category):
                click_probability *= 1.5
            
            ad_clicked = random.random() < click_probability
            
            # Generate user info
            user_location = random.choice(self.locations)
            user_device = random.choice(self.devices)
            
            # Add some variation to messages to make them more unique
            if random.random() < 0.3:  # 30% chance to add specific details
                user_message += f" I'm using {user_device.split()[0]} and located in {user_location.split(',')[0]}."
            
            record = {
                'timestamp': random_date,
                'user_message': user_message,
                'model_response': model_response,
                'user_sentiment': user_sentiment,
                'ad_message': ad_message,
                'ad_clicked': ad_clicked,
                'message_category': category,
                'ad_category': ad_category,
                'user_location': user_location,
                'user_device': user_device
            }
            
            data.append(record)
        
        df = pd.DataFrame(data)
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        return df
    
    def add_seasonal_patterns(self, df):
        """Add seasonal patterns to the data (optional enhancement)."""
        # Add day of week and hour patterns
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['hour'] = df['timestamp'].dt.hour
        
        # Business hours have higher activity
        business_hours_mask = (df['hour'] >= 9) & (df['hour'] <= 17)
        df.loc[business_hours_mask, 'ad_clicked'] = df.loc[business_hours_mask, 'ad_clicked'] | (np.random.random(business_hours_mask.sum()) < 0.02)
        
        return df
    
    def export_to_csv(self, df, filename="sample_chat_data.csv"):
        """Export the generated data to CSV."""
        df.to_csv(filename, index=False)
        print(f"Data exported to {filename}")
        
    def get_data_summary(self, df):
        """Get a summary of the generated data."""
        summary = {
            'total_records': len(df),
            'date_range': f"{df['timestamp'].min()} to {df['timestamp'].max()}",
            'unique_categories': df['message_category'].nunique(),
            'unique_locations': df['user_location'].nunique(),
            'unique_devices': df['user_device'].nunique(),
            'overall_ctr': f"{(df['ad_clicked'].sum() / len(df) * 100):.2f}%",
            'sentiment_distribution': df['user_sentiment'].value_counts().to_dict()
        }
        return summary

# Usage example
if __name__ == "__main__":
    generator = DataGenerator()
    sample_data = generator.generate_sample_data(1000)
    
    print("Sample data generated successfully!")
    print("\nData Summary:")
    summary = generator.get_data_summary(sample_data)
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    # Export to CSV
    generator.export_to_csv(sample_data, "chat_analytics_sample.csv")
