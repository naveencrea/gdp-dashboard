import streamlit as st
import pandas as pd
import io
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Google Shopping Title Optimizer",
    page_icon="🛒",
    layout="wide"
)

# Title rules
TITLE_RULES = {
    'max_length': 150,
    'optimal_min': 70,
    'optimal_max': 150,
    'avoid_words': ['sale', 'free shipping', 'best', 'cheap', 'buy now', 'new', 'hot', '!']
}

def analyze_title_quality(title):
    """Analyze title quality and return score and issues"""
    issues = []
    score = 100
    
    # Length check
    if len(title) > TITLE_RULES['max_length']:
        issues.append(f"Exceeds {TITLE_RULES['max_length']} chars ({len(title)})")
        score -= 30
    elif len(title) < TITLE_RULES['optimal_min']:
        issues.append(f"Under optimal length ({len(title)} < 70)")
        score -= 10
    
    # Check for banned words
    title_lower = title.lower()
    for word in TITLE_RULES['avoid_words']:
        if word in title_lower:
            issues.append(f'Contains "{word}"')
            score -= 15
    
    # Check capitalization
    if title.isupper() and len(title) > 10:
        issues.append("Avoid ALL CAPS")
        score -= 10
    
    # Check for excessive symbols
    if '!' in title:
        issues.append("Remove exclamation marks")
        score -= 5
    
    return max(score, 0), issues

def generate_title_variants(product):
    """Generate 5 title variants based on Google best practices"""
    variants = []
    
    brand = product.get('brand', '')
    title = product.get('title', '')
    color = product.get('color', '')
    size = product.get('size', '')
    material = product.get('material', '')
    product_type = product.get('product_type', '') or product.get('google_product_category', '')
    
    # Variant 1: Brand First (Google Recommended)
    if brand and title:
        parts = [brand, title]
        if color:
            parts.append(color)
        if size:
            parts.append(size)
        v1_title = ' - '.join(parts)[:150]
        score, issues = analyze_title_quality(v1_title)
        variants.append({
            'formula': 'Brand First',
            'title': v1_title,
            'description': 'Google recommended structure',
            'score': score,
            'issues': '; '.join(issues) if issues else 'None',
            'length': len(v1_title)
        })
    
    # Variant 2: Product First
    if title and brand:
        parts = [title, brand]
        if color:
            parts.append(color)
        if size:
            parts.append(size)
        v2_title = ' - '.join(parts)[:150]
        score, issues = analyze_title_quality(v2_title)
        variants.append({
            'formula': 'Product First',
            'title': v2_title,
            'description': 'Product name leading',
            'score': score,
            'issues': '; '.join(issues) if issues else 'None',
            'length': len(v2_title)
        })
    
    # Variant 3: Attribute Rich
    parts = []
    if brand:
        parts.append(brand)
    if product_type:
        parts.append(product_type)
    if color:
        parts.append(color)
    if size:
        parts.append(size)
    if material:
        parts.append(material)
    
    if len(parts) >= 3:
        v3_title = ' - '.join(parts)[:150]
        score, issues = analyze_title_quality(v3_title)
        variants.append({
            'formula': 'Attribute Rich',
            'title': v3_title,
            'description': 'Maximum attributes',
            'score': score,
            'issues': '; '.join(issues) if issues else 'None',
            'length': len(v3_title)
        })
    
    # Variant 4: Compact (Pipe separator)
    if brand and title:
        parts = [brand, title]
        if color:
            parts.append(color)
        if size:
            parts.append(size)
        v4_title = ' | '.join(parts)[:150]
        score, issues = analyze_title_quality(v4_title)
        variants.append({
            'formula': 'Compact',
            'title': v4_title,
            'description': 'Space-efficient format',
            'score': score,
            'issues': '; '.join(issues) if issues else 'None',
            'length': len(v4_title)
        })
    
    # Variant 5: Natural Language
    if brand and title:
        natural = f"{brand} {title}"
        if color:
            natural += f" in {color}"
        if size:
            natural += f", {size}"
        v5_title = natural[:150]
        score, issues = analyze_title_quality(v5_title)
        variants.append({
            'formula': 'SEO Natural',
            'title': v5_title,
            'description': 'Natural language format',
            'score': score,
            'issues': '; '.join(issues) if issues else 'None',
            'length': len(v5_title)
        })
    
    return variants

# Initialize session state
if 'products' not in st.session_state:
    st.session_state.products = None
if 'variants' not in st.session_state:
    st.session_state.variants = {}
if 'test_data' not in st.session_state:
    st.session_state.test_data = {}

# Header
st.title("🛒 Google Shopping Title Optimizer")
st.markdown("Scientific A/B testing based on Google best practices")

# Stats row
col1, col2, col3 = st.columns(3)
with col1:
    product_count = len(st.session_state.products) if st.session_state.products is not None else 0
    st.metric("Products Loaded", product_count)
with col2:
    variant_count = sum(len(v) for v in st.session_state.variants.values())
    st.metric("Variants Generated", variant_count)
with col3:
    st.metric("Testing Formulas", 5)

# Info box
st.info("📘 **Best Practices Applied:** 150 char max, Brand-first priority, No promotional terms, Multiple formula testing")

# File upload
uploaded_file = st.file_uploader("Upload Product Feed (CSV or TSV)", type=['csv', 'tsv', 'txt'])

if uploaded_file is not None:
    try:
        # Detect separator
        content = uploaded_file.read().decode('utf-8')
        separator = '\t' if '\t' in content.split('\n')[0] else ','
        
        # Read CSV
        df = pd.read_csv(io.StringIO(content), sep=separator)
        df.columns = df.columns.str.strip().str.lower()
        
        # Add ID if not present
        if 'id' not in df.columns:
            df['id'] = [f'product_{i+1}' for i in range(len(df))]
        
        st.session_state.products = df
        st.success(f"✅ Loaded {len(df)} products")
        
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")

# Display products
if st.session_state.products is not None:
    st.markdown("---")
    st.subheader("Product Catalog")
    
    for idx, row in st.session_state.products.iterrows():
        product_id = row.get('id', f'product_{idx}')
        
        with st.expander(f"📦 {row.get('title', 'Untitled Product')} (ID: {product_id})"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Brand:** {row.get('brand', 'N/A')}")
                st.markdown(f"**Product Type:** {row.get('product_type', 'N/A')}")
                st.markdown(f"**Color:** {row.get('color', 'N/A')} | **Size:** {row.get('size', 'N/A')}")
            
            with col2:
                if st.button("🔄 Generate Variants", key=f"gen_{product_id}"):
                    variants = generate_title_variants(row.to_dict())
                    st.session_state.variants[product_id] = variants
                    # Initialize test data
                    st.session_state.test_data[product_id] = {
                        v['formula']: {'impressions': 0, 'clicks': 0, 'conversions': 0}
                        for v in variants
                    }
                    st.rerun()
            
            # Display variants if generated
            if product_id in st.session_state.variants:
                st.markdown("### 📊 Title Variants & A/B Testing")
                
                for variant in st.session_state.variants[product_id]:
                    formula = variant['formula']
                    
                    # Score color
                    if variant['score'] >= 90:
                        score_color = "🟢"
                    elif variant['score'] >= 70:
                        score_color = "🟡"
                    else:
                        score_color = "🔴"
                    
                    st.markdown(f"**{score_color} {formula}** (Score: {variant['score']}/100)")
                    st.markdown(f"_{variant['description']} | Length: {variant['length']}_")
                    st.code(variant['title'], language=None)
                    
                    if variant['issues'] != 'None':
                        st.warning(f"⚠️ Issues: {variant['issues']}")
                    
                    # Test metrics input
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        impressions = st.number_input(
                            "Impressions",
                            min_value=0,
                            value=st.session_state.test_data.get(product_id, {}).get(formula, {}).get('impressions', 0),
                            key=f"imp_{product_id}_{formula}"
                        )
                    
                    with col2:
                        clicks = st.number_input(
                            "Clicks",
                            min_value=0,
                            value=st.session_state.test_data.get(product_id, {}).get(formula, {}).get('clicks', 0),
                            key=f"click_{product_id}_{formula}"
                        )
                    
                    with col3:
                        ctr = (clicks / impressions * 100) if impressions > 0 else 0
                        st.metric("CTR %", f"{ctr:.2f}")
                    
                    with col4:
                        conversions = st.number_input(
                            "Conversions",
                            min_value=0,
                            value=st.session_state.test_data.get(product_id, {}).get(formula, {}).get('conversions', 0),
                            key=f"conv_{product_id}_{formula}"
                        )
                    
                    # Update test data
                    if product_id not in st.session_state.test_data:
                        st.session_state.test_data[product_id] = {}
                    st.session_state.test_data[product_id][formula] = {
                        'impressions': impressions,
                        'clicks': clicks,
                        'ctr': ctr,
                        'conversions': conversions
                    }
                    
                    st.markdown("---")
                
                # Show winner
                test_data = st.session_state.test_data.get(product_id, {})
                if test_data:
                    max_ctr = 0
                    winner = None
                    for formula, data in test_data.items():
                        if data['ctr'] > max_ctr:
                            max_ctr = data['ctr']
                            winner = formula
                    
                    if winner and max_ctr > 0:
                        st.success(f"🏆 **Winner:** {winner} (CTR: {max_ctr:.2f}%)")

# Export button
if st.session_state.variants:
    st.markdown("---")
    if st.button("📥 Export All Results"):
        export_data = []
        
        for product_id, variants in st.session_state.variants.items():
            product = st.session_state.products[st.session_state.products['id'] == product_id].iloc[0]
            
            for variant in variants:
                test_data = st.session_state.test_data.get(product_id, {}).get(variant['formula'], {})
                
                export_data.append({
                    'product_id': product_id,
                    'original_title': product.get('title', ''),
                    'formula': variant['formula'],
                    'new_title': variant['title'],
                    'quality_score': variant['score'],
                    'issues': variant['issues'],
                    'length': variant['length'],
                    'impressions': test_data.get('impressions', 0),
                    'clicks': test_data.get('clicks', 0),
                    'ctr': test_data.get('ctr', 0),
                    'conversions': test_data.get('conversions', 0)
                })
        
        df_export = pd.DataFrame(export_data)
        
        # Convert to TSV
        tsv = df_export.to_csv(sep='\t', index=False)
        
        st.download_button(
            label="Download TSV",
            data=tsv,
            file_name=f"shopping_titles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsv",
            mime="text/tab-separated-values"
        )
        
        st.success("✅ Ready to download!")
