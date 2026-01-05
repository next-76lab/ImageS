import streamlit as st
from PIL import Image, ImageDraw
import io
import zipfile
import os

# Page Config
st.set_page_config(
    page_title="Image Splitter Pro",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Noto+Sans+JP:wght@400;700&display=swap');

    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #13151a 0%, #090a0c 100%);
        font-family: 'Inter', 'Noto Sans JP', sans-serif;
    }
    
    h1, h2, h3 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em;
    }

    h1 {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem !important;
        padding-bottom: 0.5rem;
    }

    /* Card/Container Style */
    .stMarkdown, .stButton, div[data-testid="stFileUploader"] {
        border-radius: 16px;
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        color: #000 !important;
        font-weight: 800 !important;
        border: none;
        padding: 0.8rem 1.5rem;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3);
        border-radius: 12px;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(79, 172, 254, 0.5);
    }

    .stButton>button:active {
        transform: translateY(1px);
        box-shadow: 0 2px 10px rgba(79, 172, 254, 0.3);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0e1014;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* File Uploader */
    div[data-testid="stFileUploader"] {
        padding: 3rem 2rem;
        border: 2px dashed rgba(79, 172, 254, 0.3);
        background-color: rgba(255, 255, 255, 0.02);
        transition: all 0.3s ease;
    }
    
    div[data-testid="stFileUploader"]:hover {
        border-color: #4facfe;
        background-color: rgba(79, 172, 254, 0.05);
    }
    
    /* Custom Classes */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    
    .instruction-text {
        color: #9ca3af;
        font-size: 1.1rem;
        line-height: 1.6;
    }
    
    .feature-tag {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        background: rgba(79, 172, 254, 0.1);
        color: #4facfe;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Helper to clean up temp files if needed, though we use memory buffers mostly.
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        st.markdown("---")
        grid_mode = st.radio(
            "分割モード (Grid Mode)",
            ("10分割 (2x5)", "9分割 (3x3)"),
            index=0,
            captions=["Instagram カルーセル用", "標準的なグリッド"]
        )
        
        st.markdown("---")
        st.markdown("""
        ### 使い方
        1. 画像をアップロード
        2. プレビューを確認
        3. 分割してダウンロード
        """)
        
        if "2x5" in grid_mode:
            rows, cols = 2, 5
        else:
            rows, cols = 3, 3

    # Main Content
    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        # Hero Section
        st.markdown("""
        <div class="glass-card">
            <span class="feature-tag">NEW v2.0</span>
            <h1>Image Splitter PRO</h1>
            <p class="instruction-text">
                画像を瞬時に美しく分割。<br>
                Instagramのカルーセル投稿や、クリエイティブなグリッドレイアウトを作成しましょう。
            </p>
        </div>
        """, unsafe_allow_html=True)

        # File Upload
        uploaded_file = st.file_uploader("ドロップまたはクリックして画像をアップロード", type=['png', 'jpg', 'jpeg', 'webp'])

        if uploaded_file:
            try:
                image = Image.open(uploaded_file)
                
                # Preview Section
                st.markdown("### 🖼️ Preview")
                
                # Create preview container
                with st.container():
                    # Create preview with grid
                    preview_img = image.copy()
                    draw = ImageDraw.Draw(preview_img)
                    width, height = preview_img.size
                    
                    # Draw vertical lines
                    item_width = width / cols
                    for c in range(1, cols):
                        x = c * item_width
                        draw.line([(x, 0), (x, height)], fill="white", width=max(2, int(width/200)))
                        draw.line([(x, 0), (x, height)], fill=(0, 0, 0, 128), width=max(1, int(width/400))) 

                    # Draw horizontal lines
                    item_height = height / rows
                    for r in range(1, rows):
                        y = r * item_height
                        draw.line([(0, y), (width, y)], fill="white", width=max(2, int(width/200)))
                        draw.line([(0, y), (width, y)], fill=(0, 0, 0, 128), width=max(1, int(width/400)))

                    st.image(preview_img, width='stretch')

                # Split Processing
                st.markdown("### 🚀 Download")
                
                # Generate ZIP on the fly
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for r in range(rows):
                        for c in range(cols):
                            left = c * item_width
                            upper = r * item_height
                            right = (c + 1) * item_width
                            lower = (r + 1) * item_height
                            
                            cropped = image.crop((left, upper, right, lower))
                            
                            img_buffer = io.BytesIO()
                            fmt = image.format if image.format else 'PNG'
                            cropped.save(img_buffer, format=fmt)
                            
                            index = r * cols + c + 1
                            ext = uploaded_file.name.split('.')[-1]
                            base_name = '.'.join(uploaded_file.name.split('.')[:-1])
                            zip_file.writestr(f"{base_name}_part_{index}.{ext}", img_buffer.getvalue())

                col_d1, col_d2, col_d3 = st.columns([1, 2, 1])
                with col_d2:
                    st.download_button(
                        label="📦 ZIPファイルをダウンロード",
                        data=zip_buffer.getvalue(),
                        file_name=f"{os.path.splitext(uploaded_file.name)[0]}_split.zip",
                        mime="application/zip",
                        type="primary"
                    )

            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
