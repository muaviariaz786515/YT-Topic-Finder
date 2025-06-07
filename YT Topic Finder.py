import streamlit as st
import json
from datetime import datetime, timedelta
from urllib.request import urlopen
from urllib.parse import urlencode, quote_plus
import urllib.error

# Page Configuration
st.set_page_config(
    page_title="YouTube Viral Topics Finder",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Professional UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #FF0000, #FF6B6B);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .filter-container {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        border-left: 4px solid #FF0000;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem;
    }
    .video-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #FF0000;
    }
    .trending-badge {
        background: linear-gradient(45deg, #FF6B6B, #FF8E53);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .viral-badge {
        background: linear-gradient(45deg, #4ECDC4, #44A08D);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    .stat-item {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        border: 2px solid #e9ecef;
    }
    .stat-number {
        font-size: 1.5rem;
        font-weight: bold;
        color: #FF0000;
    }
    .stat-label {
        font-size: 0.9rem;
        color: #6c757d;
        margin-top: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# API URLs
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# Country codes for regional filtering
COUNTRY_CODES = {
    "Global": "",
    "United States": "US",
    "United Kingdom": "GB",
    "Canada": "CA",
    "Australia": "AU",
    "India": "IN",
    "Germany": "DE",
    "France": "FR",
    "Japan": "JP",
    "Brazil": "BR",
    "Mexico": "MX",
    "Spain": "ES",
    "Italy": "IT",
    "Russia": "RU",
    "South Korea": "KR",
    "Netherlands": "NL",
    "Sweden": "SE",
    "Norway": "NO",
    "Denmark": "DK",
    "Finland": "FI"
}

def make_api_request(url, params):
    """Make API request using urllib"""
    try:
        query_string = urlencode(params, quote_via=quote_plus)
        full_url = f"{url}?{query_string}"
        
        with urlopen(full_url) as response:
            data = json.loads(response.read().decode())
            return data
    except urllib.error.HTTPError as e:
        st.error(f"API Error: {e.code} - {e.reason}")
        return None
    except Exception as e:
        st.error(f"Request Error: {str(e)}")
        return None

def format_number(num):
    """Format numbers with K, M, B suffixes"""
    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.1f}B"
    elif num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return str(num)

def calculate_viral_score(views, likes, comments):
    """Calculate viral potential score"""
    engagement_rate = (likes + comments) / max(views, 1) * 100
    viral_score = views * (1 + engagement_rate/100)
    return engagement_rate, viral_score

# Header
st.markdown("""
<div class="main-header">
    <h1>🔥 YouTube Viral Topics Finder</h1>
    <p>Discover trending content and viral topics across YouTube with advanced analytics</p>
</div>
""", unsafe_allow_html=True)

# Sidebar - Advanced Filters
with st.sidebar:
    st.markdown("## 🎯 Advanced Search Filters")
    
    # API Key Input
    api_key = st.text_input("YouTube API Key", type="password", 
                           help="Enter your YouTube Data API v3 key")
    
    if not api_key:
        st.warning("⚠️ Please enter your YouTube API key to use the tool")
        st.info("Get your free API key at: https://console.cloud.google.com/")
    
    st.markdown("---")
    
    # Search Query
    search_query = st.text_input("🔍 Search Keywords", 
                                placeholder="Enter any topic, trend, or keyword...",
                                help="Search for any topic without restrictions")
    
    # Time Range
    time_options = {
        "Past Hour": 1/24,
        "Past Day": 1,
        "Past 3 Days": 3,
        "Past Week": 7,
        "Past 2 Weeks": 14,
        "Past Month": 30,
        "Past 3 Months": 90
    }
    time_range = st.selectbox("📅 Time Range", list(time_options.keys()), index=2)
    days = time_options[time_range]
    
    # Country/Region Filter
    selected_country = st.selectbox("🌍 Region", list(COUNTRY_CODES.keys()), index=0)
    
    # Viral Metrics Thresholds
    st.markdown("### 🔥 Viral Thresholds")
    min_views = st.number_input("Minimum Views", min_value=0, value=10000, step=1000,
                               help="Videos with at least this many views")
    max_subs = st.number_input("Maximum Subscribers", min_value=0, value=100000, step=5000,
                              help="Channels with fewer subscribers (for discovery)")
    
    # Content Filters
    st.markdown("### 📊 Content Filters")
    sort_options = {
        "Most Views": "viewCount",
        "Most Recent": "date", 
        "Most Relevant": "relevance",
        "Highest Rating": "rating"
    }
    sort_by = st.selectbox("Sort By", list(sort_options.keys()), index=0)
    
    video_duration = st.selectbox("Video Duration", 
                                 ["Any", "Short (< 4 min)", "Medium (4-20 min)", "Long (> 20 min)"],
                                 index=0)
    
    max_results = st.slider("Results per Search", 5, 50, 25)

# Main Content Area
col1, col2 = st.columns([2, 1])

with col1:
    if st.button("🚀 Find Viral Topics", type="primary", use_container_width=True):
        if not search_query:
            st.error("Please enter a search keyword to find viral topics!")
        elif not api_key:
            st.error("Please enter your YouTube API Key in the sidebar!")
        else:
            try:
                with st.spinner("🔍 Searching for viral content..."):
                    # Calculate date range
                    if days < 1:
                        start_date = (datetime.utcnow() - timedelta(hours=int(days*24))).isoformat("T") + "Z"
                    else:
                        start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
                    
                    # Search parameters
                    search_params = {
                        "part": "snippet",
                        "q": search_query,
                        "type": "video",
                        "order": sort_options[sort_by],
                        "publishedAfter": start_date,
                        "maxResults": max_results,
                        "key": api_key,
                    }
                    
                    # Add regional code if selected
                    if COUNTRY_CODES[selected_country]:
                        search_params["regionCode"] = COUNTRY_CODES[selected_country]
                    
                    # Add duration filter
                    if video_duration != "Any":
                        duration_map = {
                            "Short (< 4 min)": "short",
                            "Medium (4-20 min)": "medium", 
                            "Long (> 20 min)": "long"
                        }
                        search_params["videoDuration"] = duration_map[video_duration]
                    
                    # Fetch video data
                    data = make_api_request(YOUTUBE_SEARCH_URL, search_params)
                    
                    if not data or "items" not in data or not data["items"]:
                        st.warning("No videos found for your search criteria. Try different keywords or filters.")
                    else:
                        videos = data["items"]
                        video_ids = []
                        channel_ids = []
                        
                        # Extract IDs
                        for video in videos:
                            if "id" in video and "videoId" in video["id"]:
                                video_ids.append(video["id"]["videoId"])
                            if "snippet" in video and "channelId" in video["snippet"]:
                                channel_ids.append(video["snippet"]["channelId"])
                        
                        if not video_ids:
                            st.warning("No valid videos found.")
                        else:
                            # Fetch detailed video statistics
                            stats_params = {
                                "part": "statistics,contentDetails",
                                "id": ",".join(video_ids), 
                                "key": api_key
                            }
                            stats_data = make_api_request(YOUTUBE_VIDEO_URL, stats_params)
                            
                            # Fetch channel statistics
                            channel_params = {
                                "part": "statistics,snippet",
                                "id": ",".join(list(set(channel_ids))), 
                                "key": api_key
                            }
                            channel_data = make_api_request(YOUTUBE_CHANNEL_URL, channel_params)
                            
                            if not stats_data or not channel_data:
                                st.error("Failed to fetch video/channel statistics")
                            else:
                                # Process and filter results
                                all_results = []
                                channel_stats = {}
                                
                                # Create channel lookup
                                for ch in channel_data.get("items", []):
                                    channel_stats[ch["id"]] = ch
                                
                                # Process videos
                                stats_items = stats_data.get("items", [])
                                for i, video in enumerate(videos):
                                    if i < len(stats_items):
                                        try:
                                            stat = stats_items[i]
                                            views = int(stat["statistics"].get("viewCount", 0))
                                            likes = int(stat["statistics"].get("likeCount", 0))
                                            comments = int(stat["statistics"].get("commentCount", 0))
                                            
                                            channel_id = video["snippet"]["channelId"]
                                            channel_info = channel_stats.get(channel_id, {})
                                            subs = int(channel_info.get("statistics", {}).get("subscriberCount", 0))
                                            
                                            # Apply filters
                                            if views >= min_views and (max_subs == 0 or subs <= max_subs):
                                                # Calculate metrics
                                                engagement_rate, viral_score = calculate_viral_score(views, likes, comments)
                                                
                                                # Determine viral status
                                                is_viral = views > 100000 or engagement_rate > 5
                                                is_trending = views > 50000 and views <= 100000
                                                
                                                result = {
                                                    "title": video["snippet"].get("title", "N/A"),
                                                    "description": video["snippet"].get("description", "")[:150] + "...",
                                                    "channel": video["snippet"].get("channelTitle", "N/A"),
                                                    "url": f"https://www.youtube.com/watch?v={video['id']['videoId']}",
                                                    "views": views,
                                                    "likes": likes,
                                                    "comments": comments,
                                                    "subscribers": subs,
                                                    "published": video["snippet"].get("publishedAt", ""),
                                                    "engagement_rate": round(engagement_rate, 2),
                                                    "viral_score": int(viral_score),
                                                    "is_viral": is_viral,
                                                    "is_trending": is_trending,
                                                    "thumbnail": video["snippet"]["thumbnails"]["medium"]["url"]
                                                }
                                                all_results.append(result)
                                        except (KeyError, ValueError, TypeError) as e:
                                            continue
                                
                                # Sort by viral score
                                all_results.sort(key=lambda x: x["viral_score"], reverse=True)
                                
                                if all_results:
                                    # Display metrics overview
                                    st.markdown(f"## 📊 Results Overview for '{search_query}'")
                                    
                                    total_videos = len(all_results)
                                    viral_videos = len([r for r in all_results if r["is_viral"]])
                                    trending_videos = len([r for r in all_results if r["is_trending"]])
                                    avg_engagement = sum(r["engagement_rate"] for r in all_results) / len(all_results) if all_results else 0
                                    
                                    # Custom metrics display
                                    st.markdown(f"""
                                    <div class="stats-grid">
                                        <div class="stat-item">
                                            <div class="stat-number">{total_videos}</div>
                                            <div class="stat-label">Total Videos</div>
                                        </div>
                                        <div class="stat-item">
                                            <div class="stat-number">{viral_videos}</div>
                                            <div class="stat-label">Viral Content ({viral_videos/total_videos*100:.1f}%)</div>
                                        </div>
                                        <div class="stat-item">
                                            <div class="stat-number">{trending_videos}</div>
                                            <div class="stat-label">Trending Content</div>
                                        </div>
                                        <div class="stat-item">
                                            <div class="stat-number">{avg_engagement:.2f}%</div>
                                            <div class="stat-label">Avg Engagement</div>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # Display results
                                    st.markdown("## 🔥 Viral Topics Found")
                                    
                                    for i, result in enumerate(all_results[:20]):  # Show top 20
                                        with st.container():
                                            col_thumb, col_content = st.columns([1, 4])
                                            
                                            with col_thumb:
                                                st.image(result["thumbnail"], width=120)
                                            
                                            with col_content:
                                                # Status badges
                                                badges = ""
                                                if result["is_viral"]:
                                                    badges += '<span class="viral-badge">🔥 VIRAL</span> '
                                                elif result["is_trending"]:
                                                    badges += '<span class="trending-badge">📈 TRENDING</span> '
                                                
                                                st.markdown(f"""
                                                <div class="video-card">
                                                    {badges}
                                                    <h4>{result['title']}</h4>
                                                    <p><strong>Channel:</strong> {result['channel']} ({format_number(result['subscribers'])} subscribers)</p>
                                                    <p>{result['description']}</p>
                                                    <div style="display: flex; gap: 20px; margin: 10px 0; flex-wrap: wrap;">
                                                        <span>👁️ {format_number(result['views'])} views</span>
                                                        <span>👍 {format_number(result['likes'])} likes</span>
                                                        <span>💬 {format_number(result['comments'])} comments</span>
                                                        <span>📊 {result['engagement_rate']}% engagement</span>
                                                    </div>
                                                    <a href="{result['url']}" target="_blank" style="color: #FF0000; text-decoration: none; font-weight: bold;">🎬 Watch Video</a>
                                                </div>
                                                """, unsafe_allow_html=True)
                                            
                                            st.markdown("---")
                                else:
                                    st.warning("No viral content found matching your criteria. Try adjusting the filters.")
                                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.info("Please check your API key and internet connection.")

with col2:
    st.markdown("## 💡 Pro Tips")
    st.info("""
    **🎯 Finding Viral Content:**
    • Use trending keywords and hashtags
    • Search for current events or news
    • Try seasonal or holiday topics
    • Look for emerging trends
    
    **📊 Filter Optimization:**
    • Lower subscriber counts = hidden gems
    • Recent timeframes show trending topics  
    • High engagement rates indicate viral potential
    
    **🔍 Search Strategies:**
    • Use specific niche keywords
    • Try different languages
    • Search for tutorial topics
    • Look for reaction content
    """)
    
    st.markdown("## 🚀 Features")
    st.success("""
    ✅ **Unlimited Keywords** - Search any topic  
    ✅ **Advanced Filters** - Fine-tune your search  
    ✅ **Viral Analytics** - Engagement & viral scores  
    ✅ **Global Regions** - Country-specific content  
    ✅ **Real-time Data** - Latest YouTube metrics  
    ✅ **Professional UI** - Clean, modern interface  
    ✅ **Zero Dependencies** - No external packages needed
    """)
    
    st.markdown("## 🔑 API Setup")
    st.info("""
    **Get YouTube API Key:**
    1. Go to Google Cloud Console
    2. Create/select project
    3. Enable YouTube Data API v3
    4. Create API Key credential
    5. Copy key to sidebar input
    
    **Free quota:** 10,000 units/day
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>YouTube Viral Topics Finder | Discover trending content and viral opportunities</p>
    <p><small>Built with Streamlit | Powered by YouTube Data API v3 | Zero External Dependencies</small></p>
</div>
""", unsafe_allow_html=True)
