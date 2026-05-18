import streamlit as st

# ページ全体の基本設定
st.set_page_config(
    page_title="放射線治療 診療報酬シミュレーター 2026",
    page_icon="⚛️",
    layout="wide"
)

# ========================================================
# 👇 【iPad Safari絶対防御】最下部フッターとFullscreenを完全に消滅させるCSS
# ========================================================
st.markdown("""
    <style>
    /* 1. 最下部のフッター・白帯・Fullscreenボタンを親要素ごと完全に破壊・消失させる */
    [data-testid="stAppDecoration"],
    .stAppDecoration,
    footer,
    [data-testid="stFooter"],
    #root > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div > div:last-child,
    .stApp > div:last-child {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        height: 0px !important;
        width: 0px !important;
        max-height: 0px !important;
        min-height: 0px !important;
        overflow: hidden !important;
        position: absolute !important;
        pointer-events: none !important;
    }
    
    /* 2. 画面最下部に不自然な余白（スクロールの遊び）が残らないように画面を詰める */
    .stApp3 {
        margin-bottom: 0px !important;
        padding-bottom: 0px !important;
    }
    .stMainBlockContainer {
        padding-bottom: 2rem !important;
    }

    /* 3. 右下の「Manage app」ボタンを強制非表示 */
    [data-testid="stManageAppButton"],
    div[data-testid="stManageAppButton"],
    button[data-testid="stManageAppButton"],
    #manage-app-button,
    .stManageAppButton {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        height: 0 !important;
        width: 0 !important;
    }

    /* 4. 計算内訳明細ボックス（縦幅320px拡張版） */
    .custom-detail-box,
    [class*="custom-detail-box"] {
        max-height: 320px;               
        overflow-y: auto;
        padding: 12px;
        border-radius: 8px;
        font-size: 13px !important;       
        line-height: 1.4 !important;      
        font-family: 'Consolas', monospace !important;
        user-select: none !important;
        -webkit-user-select: none !important;
        -webkit-touch-callout: none !important;
    }

    /* 🌗 ダークモード（背景黒）のときのボックス色 */
    @media (prefers-color-scheme: dark) {
        .custom-detail-box,
        [class*="custom-detail-box"] {
            background-color: #1E1E24 !important;
            color: #FFFFFF !important;
        }
    }

    /* ☀️ ライトモード（背景白）のときのボックス色 */
    @media (prefers-color-scheme: light) {
        .custom-detail-box,
        [class*="custom-detail-box"] {
            background-color: #F0F2F6 !important;
            color: #000000 !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ========================================================
# セッション状態（データ永続化・記憶用変数）の初期化
# ========================================================
if "saved_folder_path" not in st.session_state:
    st.session_state.saved_folder_path = ""
if "saved_favorites" not in st.session_state:
    st.session_state.saved_favorites = []
if "saved_reservation_list" not in st.session_state:
    st.session_state.saved_reservation_list = []

# 追加エリア（1回目・2回目）の入力状態保持用
if "saved_extra_1st_method" not in st.session_state:
    st.session_state.saved_extra_1st_method = "IMRT"
if "saved_extra_1st_count" not in st.session_state:
    st.session_state.saved_extra_1st_count = 1
if "saved_extra_1st_igrt" not in st.session_state:
    st.session_state.saved_extra_1st_igrt = "ハ.腫瘍"
if "saved_extra_1st_breath" not in st.session_state:
    st.session_state.saved_extra_1st_breath = "なし"

if "saved_extra_2nd_method" not in st.session_state:
    st.session_state.saved_extra_2nd_method = "1門照射"
if "saved_extra_2nd_count" not in st.session_state:
    st.session_state.saved_extra_2nd_count = 1
if "saved_extra_2nd_breath" not in st.session_state:
    st.session_state.saved_extra_2nd_breath = "なし"


# --- メインコンテンツ ---
st.markdown("## ⚛️ 放射線治療 診療報酬シミュレーター 2026")

col1, col2 = st.columns([1, 1])

# 一連算定項目と外来加算対象項目の定義
one_series_methods = ["前立腺VMAT", "全乳房(一連)", "肺定位SBRT", "脳定位SRT", "全身照射TBI", "緩和寡分割"]
outpatient_add_series = ["前立腺VMAT", "全乳房(一連)", "肺定位SBRT", "脳定位SRT", "緩和寡分割"]

with col1:
    st.subheader("📋 基本入力エリア")
    
    # 主たる照射方法選択
    methods = [
        "前立腺VMAT", "全乳房(一連)", "IMRT", "1門照射", 
        "対向2門", "非対向2門・3門照射", "4門以上・運動・原体照射", "全身照射TBI", 
        "緩和寡分割", "ケロイド", "肺定位SBRT", "脳定位SRT"
    ]
    selected_method = st.radio("主たる照射方法", methods, index=0, key="main_method_selection")
    
    st.markdown("---")
    
    # 負担割合
    ratio_str = st.segmented_control("患者負担割合", ["1割", "2割", "3割"], default="3割")
    ratio = int(ratio_str.replace("割", "")) if ratio_str else 3

    # 患者区分の制御 (脳定位SRTの場合は自動で入院に固定)
    if selected_method == "脳定位SRT":
        patient_type = st.radio("患者区分", ["外来", "入院"], index=1, disabled=True)
    else:
        patient_type = st.radio("患者区分", ["外来", "入院"], index=0, horizontal=True)

    # IGRT区分の表示制御
    no_igrt_list = [
        "1門照射", "対向2門", "非対向2門・3門照射", "ケロイド", "全乳房(一連)",
        "前立腺VMAT", "肺定位SBRT", "脳定位SRT", "全身照射TBI", "緩和寡分割"
    ]
    
    if selected_method not in no_igrt_list:
        default_igrt_idx = 3 if selected_method == "IMRT" else 0
        igrt_selection = st.radio("IGRT区分", ["なし", "イ.体表", "ロ.骨構造", "ハ.腫瘍"], index=default_igrt_idx, horizontal=True)
    else:
        igrt_selection = "なし"

    # 固定器具加算フレーム
    grid_fix_list = ["前立腺VMAT", "IMRT", "1門照射", "対向2門", "非対向2門・3門照射", "4門以上・運動・原体照射", "ケロイド"]
    default_fix = "作成あり" if selected_method == "前立腺VMAT" else "なし"
    fix_var = "なし"
    if selected_method in grid_fix_list:
        fix_var = st.segmented_control("体外照射用固定器具", ["なし", "作成あり"], default=default_fix)

    # 呼吸性移動対策フレーム
    breath_var = "なし"
    if selected_method in ["IMRT", "肺定位SBRT", "全乳房(一連)", "非対向2門・3門照射", "4門以上・運動・原体照射"]:
        breath_var = st.segmented_control("呼吸性移動対策", ["なし", "あり"], default="なし")

    # 全乳房専用IGRTフレーム
    breast_igrt_var = "なし"
    if selected_method == "全乳房(一連)":
        breast_igrt_var = st.segmented_control("IGRT(一連2400点)", ["なし", "あり"], default="なし")

    # 回数入力の制御
    count = 1
    if selected_method not in one_series_methods or (selected_method in outpatient_add_series and patient_type == "外来"):
        lbl_text = "外来治療回数 (加算用):" if selected_method in one_series_methods else "合計照射回数:"
        count = st.number_input(lbl_text, min_value=1, value=1, step=1)
    
    if selected_method in one_series_methods:
        st.info(f"💡 {selected_method} は一連算定項目です")

# --- 計算ロジック本体 (左側ベース用) ---
def calculate_base():
    formula = []
    total_pts = 0
    exclude_m000 = ["肺定位SBRT", "脳定位SRT", "全身照射TBI", "緩和寡分割"]
   
    if selected_method in exclude_m000:
        formula.append("・管理料(M000): 0点 (一連に含む)")
    else:
        if selected_method in ["1門照射", "ケロイド", "対向2門"]: 
            m000_pts = 2700
        elif selected_method == "非対向2門・3門照射":
            m000_pts = 3100
        elif "IMRT" in selected_method or "VMAT" in selected_method: 
            m000_pts = 5000
        elif selected_method == "全乳房(一連)":
            m000_pts = 4000
        else: 
            m000_pts = 4000
            
        total_pts += m000_pts
        formula.append(f"・管理料(M000): {m000_pts:,}点")
        total_pts += 330
        formula.append("・放射線治療専任加算: 330点")

    total_pts += 1100
    formula.append("・安全管理料2: 1,100点")
    if fix_var == "作成あり":
        total_pts += 1000
        formula.append("・体外照射用固定器具加算: 1,000点")

    if selected_method in one_series_methods:
        if selected_method == "肺定位SBRT":
            total_pts += 63000
            formula.append("・定位照射(一連): 63,000点")
            if breath_var == "あり":
                total_pts += 5000
                formula.append("・呼吸性移動対策加算: 5,000点")
        elif selected_method == "脳定位SRT":
            total_pts += 63000
            formula.append("・定位照射(一連): 63,000点")
        elif selected_method == "前立腺VMAT":
            total_pts += (96500 + 9000)
            formula.append("・照射料(一連): 96,500点\n・IGRT(ハ.腫瘍 一連): 9,000点")
        elif selected_method == "全乳房(一連)":
            total_pts += 41500
            formula.append("・照射料(一連): 41,500点")
            if breast_igrt_var == "あり":
                total_pts += 2400
                formula.append("・IGRT(一連): 2,400点")
            if breath_var == "あり":
                total_pts += 2400
                formula.append("・呼吸性移動対策加算(一連): 2,400点")
        elif selected_method == "全身照射TBI":
            total_pts += 30000
            formula.append("・全身照射(一連): 30,000点")
        elif selected_method == "緩和寡分割":
            total_pts += 8000
            formula.append("・緩和寡分割(一連): 8,000点")
        
        if patient_type == "外来" and selected_method in outpatient_add_series:
            outpatient_pts = count * 100
            total_pts += outpatient_pts
            formula.append(f"・外来放射線治療加算(100点) × {count}回: {outpatient_pts:,}点")
    else:
        if selected_method == "IMRT": base = 3000
        elif "4門以上・運動・原体照射" in selected_method: base = 1750
        elif selected_method in ["対向2門", "非対向2門・3門照射"]: base = 1750
        elif selected_method in ["1門照射", "ケロイド"]: base = 840
        else: base = 0
        
        igrt_map = {"なし": 0, "イ.体表": 150, "ロ.骨構造": 300, "ハ.腫瘍": 450}
        igrt_pts = igrt_map.get(igrt_selection, 0)

        breath_per_shot = 0
        if selected_method in ["IMRT", "非対向2門・3門照射", "4門以上・運動・原体照射"] and breath_var == "あり":
            breath_per_shot = 150
    
        total_pts += (base + igrt_pts + breath_per_shot) * count
        formula.append(f"・照射料({base}点) × {count}回: {base * count:,}点")
        if igrt_pts > 0:
            formula.append(f"・IGRT({igrt_pts}点) × {count}回: {igrt_pts * count:,}点")
        if breath_per_shot > 0:
            formula.append(f"・呼吸性移動対策({breath_per_shot}点) × {count}回: {breath_per_shot * count:,}点")
            
        if patient_type == "外来" and selected_method != "ケロイド":
            outpatient_pts = count * 100
            total_pts += outpatient_pts
            formula.append(f"・外来放射線治療加算(100点) × {count}回: {outpatient_pts:,}点")

    final_pay = total_pts * 10 * (ratio / 10)
    return total_pts, final_pay, formula

base_pts, final_pay, formula_list = calculate_base()

with col2:
    st.subheader("💰 会計計算結果")
    st.metric(label="概算窓口負担額", value=f"¥ {final_pay:,.0f}")
    
    # 計算内訳の表示
    full_formula_text = "\n".join(formula_list) + f"\n----------------------------\n合計点数: {base_pts:,} 点\n計算式: {base_pts:,}点 × 10円 × {ratio/10} = ¥{final_pay:,.0f}"
    st.caption("📋 計算内訳明細")
    html_text = full_formula_text.replace('\n', '<br>')
    st.html(f'<div class="custom-detail-box">{html_text}</div>')

    st.warning("⚠️ ※外来の場合、「外来放射線診療料（診察代）」が別途加算されます。\n\n※治療の進行状況やプラン変更により実際と異なる場合があります。")

st.markdown("---")

# --- 追加・変更シミュレーションエリア ---
is_expanded = st.checkbox("追加・変更分のシミュレーションを開く ≫")

if is_expanded:
    st.header("🔄 追加・変更シミュレーション")
    
    ex_col1, ex_col2 = st.columns([1, 1])
    
    with ex_col1:
        check_extra_2 = st.checkbox("2回目の計算として実行する (2回目会計)", value=False)
        
        extra_methods_1st = [
            "前立腺VMAT", "全乳房(一連)", "IMRT", "1門照射", 
            "対向2門", "非対向2門・3門照射", "4門以上・運動・原体照射", "ケロイド",
            "肺定位SBRT", "脳定位SRT", "全身照射TBI", "緩和寡分割"
        ]
        extra_methods_2nd = ["1門照射", "対向2門", "非対向2門・3門照射", "4門以上・運動・原体照射", "ケロイド"]
        
        if check_extra_2:
            st.subheader("追加する照射方法 (2回目)")
            try:
                idx_2nd = extra_methods_2nd.index(st.session_state.saved_extra_2nd_method)
            except ValueError:
                idx_2nd = 0
            
            selected_extra_method = st.radio("照射方法", extra_methods_2nd, index=idx_2nd, key="ex_method_2")
            st.session_state.saved_extra_2nd_method = selected_extra_method
            
            extra_count = st.number_input("2回目 照射回数:", min_value=1, value=int(st.session_state.saved_extra_2nd_count), step=1, key="ex_count_2")
            st.session_state.saved_extra_2nd_count = extra_count
            extra_igrt = "なし" 
            
            extra_breath_var = "なし"
            if selected_extra_method in ["非対向2門・3門照射", "4門以上・運動・原体照射"]:
                extra_breath_var = st.segmented_control("追加 呼吸性移動対策", ["なし", "あり"], default=st.session_state.saved_extra_2nd_breath, key="ex_breath_2")
                st.session_state.saved_extra_2nd_breath = extra_breath_var
        else:
            st.subheader("追加する照射方法 (1回目)")
            try:
                idx_1st = extra_methods_1st.index(st.session_state.saved_extra_1st_method)
            except ValueError:
                idx_1st = 0
            
            selected_extra_method = st.radio("照射方法", extra_methods_1st, index=idx_1st, key="ex_method_1")
            st.session_state.saved_extra_1st_method = selected_extra_method
            
            if selected_extra_method in one_series_methods:
                st.text_input("1回目 照射回数:", value="1 (一連算定のため固定)", disabled=True)
                extra_count = 1
                st.session_state.saved_extra_1st_count = 1
            else:
                extra_count = st.number_input("1回目 照射回数:", min_value=1, value=int(st.session_state.saved_extra_1st_count), step=1, key="ex_count_1")
                st.session_state.saved_extra_1st_count = extra_count
            
            if selected_extra_method not in no_igrt_list:
                try:
                    idx_igrt = ["なし", "イ.体表", "ロ.骨構造", "ハ.腫瘍"].index(st.session_state.saved_extra_1st_igrt)
                except ValueError:
                    idx_igrt = 0
                
                extra_igrt = st.radio("1回目 IGRT区分", ["なし", "イ.体表", "ロ.骨構造", "ハ.腫瘍"], index=idx_igrt, horizontal=True, key="ex_igrt_1")
                st.session_state.saved_extra_1st_igrt = extra_igrt
            else:
                extra_igrt = "なし"

            extra_breath_var = "なし"
            if selected_extra_method in ["IMRT", "非対向2門・3門照射", "4門以上・運動・原体照射"]:
                extra_breath_var = st.segmented_control("追加 呼吸性移動対策", ["なし", "あり"], default=st.session_state.saved_extra_1st_breath, key="ex_breath_1")
                st.session_state.saved_extra_1st_breath = extra_breath_var

    # 追加分の点数計算ロジック
    def get_extra_points(method, count, igrt_selection, is_second):
        formula_list_ex = []
        if is_second:
            pts_map = {"1門照射": 336, "対向2門": 700, "非対向2門・3門照射": 700, "4門以上・運動・原体照射": 700, "ケロイド": 336}
        else:
            pts_map = {
                "前立腺VMAT": 96500 + 9000, "全乳房(一連)": 41500, "IMRT": 3000, "1門照射": 840, "ケロイド": 840,
                "対向2門": 1750, "非対向2門・3門照射": 1750, "4門以上・運動・原体照射": 1750, "肺定位SBRT": 63000,
                "脳定位SRT": 63000, "全身照射TBI": 30000, "緩和寡分割": 8000
            }
        
        extra_base_pts = pts_map.get(method, 0)
        extra_total_pts = 0
        
        exclude_m000 = ["肺定位SBRT", "脳定位SRT", "全身照射TBI", "緩和寡分割"]
        if method in exclude_m000:
            formula_list_ex.append("・追加管理料(M000): 0点 (一連に含むため算定不可)")
        else:
            if method in ["1門照射", "ケロイド", "対向2門"]: m000_pts = 2700
            elif method == "非対向2門・3門照射": m000_pts = 3100
            elif "IMRT" in method or "VMAT" in method: m000_pts = 5000
            elif method == "全乳房(一連)": m000_pts = 4000
            else: m000_pts = 4000
            
            extra_total_pts += (m000_pts + 330)
            formula_list_ex.append(f"・追加管理料(M000): {m000_pts:,}点\n・追加放射線治療専任加算: 330点")

        if method in one_series_methods:
            extra_total_pts += extra_base_pts
            if method == "前立腺VMAT":
                formula_list_ex.append("・追加照射(前立腺VMAT 一連): 96,500点\n・追加IGRT(ハ.腫瘍 一連): 9,000点")
            else:
                prefix = "2回目" if is_second else "追加"
                formula_list_ex.append(f"・{prefix}照射({method}): {extra_base_pts:,}点")
        else:
            igrt_map = {"なし": 0, "イ.体表": 150, "ロ.骨構造": 300, "ハ.腫瘍": 450}
            extra_igrt_pts = igrt_map.get(igrt_selection, 0)
            
            extra_breath_per_shot = 0
            if is_second:
                if method in ["非対向2門・3門照射", "4門以上・運動・原体照射"] and extra_breath_var == "あり":
                    extra_breath_per_shot = 150
            else:
                if method in ["IMRT", "非対向2門・3門照射", "4門以上・運動・原体照射"] and extra_breath_var == "あり":
                    extra_breath_per_shot = 150

            shot_pts = extra_base_pts * count
            extra_total_pts += shot_pts
            
            prefix = "2回目" if is_second else "追加"
            formula_list_ex.append(f"・{prefix}照射({method}): {extra_base_pts:,}点 × {count}回 = {shot_pts:,}点")
            
            if extra_igrt_pts > 0:
                igrt_total_pts = extra_igrt_pts * count
                extra_total_pts += igrt_total_pts
                formula_list_ex.append(f"・追加IGRT({igrt_selection} {extra_igrt_pts}点) × {count}回 = {igrt_total_pts:,}点")

            if extra_breath_per_shot > 0:
                breath_total_pts = extra_breath_per_shot * count
                extra_total_pts += breath_total_pts
                formula_list_ex.append(f"・{prefix}呼吸性移動対策({extra_breath_per_shot}点) × {count}回 = {breath_total_pts:,}点")

        if not is_second and patient_type == "外来" and method != "ケロイド" and method not in one_series_methods:
            extra_outpatient_pts = count * 100
            extra_total_pts += extra_outpatient_pts
            formula_list_ex.append(f"・追加外来放射線治療加算(100点) × {count}回: {extra_outpatient_pts:,}点")

        return extra_total_pts, formula_list_ex

    extra_pts, extra_formula_list = get_extra_points(selected_extra_method, extra_count, extra_igrt, check_extra_2)
    extra_pay = extra_pts * 10 * (ratio / 10)

    # 総合計計算
    grand_total_pts = base_pts + extra_pts
    grand_final_pay = grand_total_pts * 10 * (ratio / 10)

    with ex_col2:
        title_prefix = "▼ 2回目" if check_extra_2 else "▼ 1回目"
        st.subheader(f"{title_prefix}追加分のみの計算結果")
        st.metric(label="追加分概算金額", value=f"¥ {extra_pay:,.0f}")
        
        ex_full_txt = "\n".join(extra_formula_list) + f"\n----------------------------\n追加点数: {extra_pts:,} 点\n計算式: {extra_pts:,}点 × 10円 × {ratio/10} = ¥{extra_pay:,.0f}"
        st.caption("📋 追加分内訳明細")
        ex_html_text = ex_full_txt.replace('\n', '<br>')
        st.html(f'<div class="custom-detail-box">{ex_html_text}</div>')

        # 総合計の大きなカード風表示
        st.markdown("---")
        if check_extra_2:
            st.success("#### 🟩 【左側会計 ＋ 2回目会計】総合計 (窓口負担額)")
            st.write(f"### **¥ {grand_final_pay:,.0f}** （概算）")
            st.info(f"総点数: {grand_total_pts:,} 点  \n(治療ベース: {base_pts:,}点 + 2回目追加: {extra_pts:,}点)")
        else:
            st.success("#### 🟩 差額合算後の総合計 (窓口負担額)")
            st.write(f"### **¥ {grand_final_pay:,.0f}** （概算）")
            st.info(f"総点数: {grand_total_pts:,} 点  \n(治療ベース: {base_pts:,}点 + 1回目追加: {extra_pts:,}点)")
