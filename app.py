import streamlit as st
import pandas as pd
import unicodedata
import io

# --- 1. إعدادات الصفحة (الهوية الجديدة) ---
st.set_page_config(page_title="تطابق | Tatabaq", layout="wide", page_icon="🎯")

# --- 2. التصميم (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Cairo', sans-serif; 
    }
    
    /* تنسيق البطاقات */
    .upload-card { 
        background-color: #ffffff; 
        color: #000000; 
        border-radius: 12px; 
        padding: 20px; 
        border: 1px solid #e0e0e0; 
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    .upload-card h3 { color: #333; margin: 0; font-size: 1.1rem; }
    
    .stButton > button { background-color: #2980b9; color: white; border-radius: 8px; font-weight: bold; width: 100%; border: none; padding: 0.6rem; }
    .stButton > button:hover { background-color: #3498db; }
    
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;}
    
    .block-container {
        padding-bottom: 70px;
    }

    /* --- التوقيع الثابت (Fixed Footer) --- */
    .fixed-footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #2c3e50;
        color: white;
        text-align: center;
        padding: 10px;
        font-family: 'Cairo', sans-serif;
        font-size: 14px;
        z-index: 9999;
        border-top: 3px solid #3498db;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
    }
    .fixed-footer span {
        font-weight: bold;
        color: #3498db;
    }

    /* --- تنسيق الجدول المخصص (HTML) --- */
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        font-size: 0.95em;
        border-radius: 8px 8px 0 0;
        overflow: hidden;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.05);
    }
    .custom-table thead tr {
        background-color: #2c3e50;
        color: #ffffff;
        text-align: center !important;
        font-weight: bold;
    }
    .custom-table th, .custom-table td {
        padding: 12px 15px;
        text-align: center !important;
        border-bottom: 1px solid #dddddd;
    }
    .custom-table tbody tr {
        border-bottom: 1px solid #dddddd;
    }
    .custom-table tbody tr:last-of-type {
        border-bottom: 2px solid #2c3e50;
    }
        /* إخفاء زر Deploy */
    .stDeployButton {display:none;}
    /* إخفاء الشريط العلوي بالكامل والقائمة الجانبية */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- التوقيع ---
st.markdown("""
<div class="fixed-footer">
    Developed by <span>Aymen N. Hamad</span> © 2026 | Tatabaq Tool
</div>
""", unsafe_allow_html=True)

# --- 3. دوال المعالجة ---
def clean_text(text):
    if pd.isna(text) or str(text).strip() == "": return ""
    text = str(text).strip()
    text = unicodedata.normalize('NFKD', text)
    text = "".join([c for c in text if not unicodedata.combining(c)])
    text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    text = text.replace("ة", "ه").replace("ى", "ي")
    text = text.replace(" ", "")
    return text

def smart_format(val):
    if pd.isna(val) or val == "-" or str(val).strip() == "": return "-"
    try:
        num = float(val)
        if num.is_integer(): return str(int(num))
        else: return str(num)
    except: return str(val)

def to_excel_styled(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='تقرير تطابق')
        wb = writer.book
        ws = writer.sheets['تقرير تطابق']
        
        fmt_head = wb.add_format({'bold': True, 'fg_color': '#2c3e50', 'font_color': 'white', 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        fmt_green = wb.add_format({'bg_color': '#c3e6cb', 'font_color': '#155724', 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        fmt_red = wb.add_format({'bg_color': '#f5c6cb', 'font_color': '#721c24', 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        fmt_yellow = wb.add_format({'bg_color': '#ffeeba', 'font_color': '#856404', 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        fmt_center = wb.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter'})

        ws.right_to_left()
        for i, col in enumerate(df.columns):
            ws.write(0, i, col, fmt_head)
            ws.set_column(i, i, 22, fmt_center)
            
        last = len(df.columns) - 1
        ws.conditional_format(1, last, len(df), last, {'type': 'text', 'criteria': 'containing', 'value': 'متطابق', 'format': fmt_green})
        ws.conditional_format(1, last, len(df), last, {'type': 'text', 'criteria': 'containing', 'value': 'اختلاف', 'format': fmt_red})
        ws.conditional_format(1, last, len(df), last, {'type': 'text', 'criteria': 'containing', 'value': 'مفقود', 'format': fmt_yellow})
        
    return output.getvalue()

def generate_html_table(df):
    html = '<table class="custom-table">'
    html += '<thead><tr>'
    for col in df.columns:
        html += f'<th>{col}</th>'
    html += '</tr></thead>'
    html += '<tbody>'
    for index, row in df.iterrows():
        res = str(row['النتيجة'])
        bg_color, text_color = "#ffffff", "#000000"
        
        if 'متطابق' in res: bg_color, text_color = "#d4edda", "#155724"
        elif 'اختلاف' in res: bg_color, text_color = "#f8d7da", "#721c24"
        elif 'مفقود' in res: bg_color, text_color = "#fff3cd", "#856404"
            
        html += f'<tr style="background-color: {bg_color}; color: {text_color};">'
        for col in df.columns:
            html += f'<td>{row[col]}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    return html

# --- 4. الواجهة ---
st.markdown("<h1 style='text-align: center; color: #2c3e50;'>تطابق | Tatabaq</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #7f8c8d; font-size: 1rem;'>نظام التدقيق والمطابقة الذكي - Powered by Aymen</p>", unsafe_allow_html=True)

c1, c2 = st.columns(2, gap="medium")
df1, df2 = None, None

with c1:
    st.markdown('<div class="upload-card"><h3>📂 الملف الأساسي (1)</h3></div>', unsafe_allow_html=True)
    f1 = st.file_uploader("ملف 1", key="f1")
    with st.expander("⚙️ إعدادات (ملف 1)"):
        h1 = st.number_input("سطر العناوين", 0, 10, 0, key="h1")
    if f1:
        try:
            if f1.name.endswith('csv'):
                f1.seek(0)
                try: df1 = pd.read_csv(f1, header=h1, encoding='utf-8-sig')
                except: f1.seek(0); df1 = pd.read_csv(f1, header=h1, encoding='cp1256')
            else: df1 = pd.read_excel(f1, header=h1)
            df1.columns = df1.columns.astype(str).str.strip()
            st.success(f"تم قراءة {len(df1)} صف")
        except: st.error("خطأ في الملف")

with c2:
    st.markdown('<div class="upload-card"><h3>📂 الملف للمقارنة (2)</h3></div>', unsafe_allow_html=True)
    f2 = st.file_uploader("ملف 2", key="f2")
    with st.expander("⚙️ إعدادات (ملف 2)"):
        h2 = st.number_input("سطر العناوين", 0, 10, 0, key="h2")
    if f2:
        try:
            if f2.name.endswith('csv'):
                f2.seek(0)
                try: df2 = pd.read_csv(f2, header=h2, encoding='utf-8-sig')
                except: f2.seek(0); df2 = pd.read_csv(f2, header=h2, encoding='cp1256')
            else: df2 = pd.read_excel(f2, header=h2)
            df2.columns = df2.columns.astype(str).str.strip()
            st.success(f"تم قراءة {len(df2)} صف")
        except: st.error("خطأ في الملف")

# --- 5. التحليل ---
if df1 is not None and df2 is not None:
    st.divider()
    sc1, sc2 = st.columns(2)
    with sc1:
        n1 = st.selectbox("الاسم (1):", df1.columns, key="n1")
        v1 = st.selectbox("المقارنة (1):", df1.columns, index=1 if len(df1.columns)>1 else 0, key="v1")
    with sc2:
        n2 = st.selectbox("الاسم (2):", df2.columns, key="n2")
        v2 = st.selectbox("المقارنة (2):", df2.columns, index=1 if len(df2.columns)>1 else 0, key="v2")

    if st.button("🚀 بدء المطابقة"):
        try:
            w1 = pd.DataFrame({'N': df1[n1], 'V': df1[v1]})
            w2 = pd.DataFrame({'N': df2[n2], 'V': df2[v2]})
            w1['Key'] = w1['N'].apply(clean_text)
            w2['Key'] = w2['N'].apply(clean_text)
            w1 = w1.drop_duplicates(subset=['Key'])
            w2 = w2.drop_duplicates(subset=['Key'])
            
            merged = pd.merge(w1, w2, on='Key', how='outer', suffixes=('_1', '_2'))
            
            def analyze(row):
                if pd.isna(row['N_1']): return "مفقود في الملف الأول"
                if pd.isna(row['N_2']): return "مفقود في الملف الثاني"
                v1_r, v2_r = row['V_1'], row['V_2']
                
                try:
                    if float(str(v1_r).strip()) == float(str(v2_r).strip()): return "✅ متطابق"
                except: pass
                
                if str(v1_r).strip() == str(v2_r).strip(): return "✅ متطابق"
                return f"❌ اختلاف ({smart_format(v1_r)} vs {smart_format(v2_r)})"

            merged['النتيجة'] = merged.apply(analyze, axis=1)
            
            final = merged[['N_1', 'V_1', 'V_2', 'النتيجة']].copy()
            final['N_1'] = final['N_1'].fillna(merged['N_2'])
            
            lbl1, lbl2 = f"قيمة ({v1})", f"قيمة ({v2})"
            if lbl1 == lbl2: lbl1 += " (1)"; lbl2 += " (2)"
            final.columns = ['الاسم', lbl1, lbl2, 'النتيجة']
            final = final.fillna("-")
            final[lbl1] = final[lbl1].apply(smart_format)
            final[lbl2] = final[lbl2].apply(smart_format)

            st.success("تم تحليل البيانات بنجاح!")
            
            html_table = generate_html_table(final)
            st.markdown(html_table, unsafe_allow_html=True)
            
            excel_bytes = to_excel_styled(final)
            st.download_button("📥 تحميل التقرير (Excel)", excel_bytes, "Tatabaq_Report.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        except Exception as e:
            st.error(f"حدث خطأ: {e}")